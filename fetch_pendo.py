#!/usr/bin/env python3
"""
fetch_pendo.py
==============
Talks to Pendo directly (aggregation API) for each LIVE solicitation survey in
surveys.json and returns, per guide:
  - funnel metrics (views, unique visitors, accounts, responses, completion, dismissal)
  - the list of "interested" responses, each with visitor email, account, timestamp,
    and the visitor's Pendo role (used to derive Administrator / Manager / User)

Level derivation (Pendo-only, confirmed mapping):
    role == "Administrator"  -> Administrator
    role == "User"           -> Manager        (incl. Group Managers)
    role empty / missing     -> User
    anything else            -> Unknown

Requires env var PENDO_INTEGRATION_KEY (aggregation-scoped).
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta

PENDO_KEY = os.environ.get("PENDO_INTEGRATION_KEY")
PENDO_BASE = "https://app.pendo.io/api/v1"
SUB_ID = os.environ.get("PENDO_SUB_ID", "6230324726202368")


def _post_aggregation(pipeline):
    """Run a Pendo aggregation pipeline; return list of result rows."""
    import requests
    body = {"response": {"mimeType": "application/json"},
            "request": {"pipeline": pipeline}}
    r = requests.post(
        f"{PENDO_BASE}/aggregation",
        headers={"x-pendo-integration-key": PENDO_KEY, "content-type": "application/json"},
        json=body, timeout=60,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def normalize_level(role):
    """Map a raw Pendo role to the 3-level model. Empty/missing -> User."""
    if role is None:
        return "User"
    r = str(role).strip()
    if r == "":
        return "User"
    if r == "Administrator":
        return "Administrator"
    if r == "User":
        return "Manager"
    return "Unknown"


def fetch_guide_metrics(guide_id, days=365):
    """Funnel metrics for a guide over the trailing window, via guidePollEvents +
    guideEvents aggregations. Returns a dict; missing pieces default to 0."""
    now = datetime.now(timezone.utc)
    first = int((now - timedelta(days=days)).timestamp() * 1000)
    # Poll responses (count) for the guide
    try:
        poll_rows = _post_aggregation([
            {"source": {"pollEvents": None, "timeSeries": {
                "period": "dayRange", "first": first, "count": days}},
             "filter": f'guideId == "{guide_id}"'},
            {"reduce": [{"count": None}]},
            {"identified": "visitorId"},
        ])
    except Exception as e:
        print(f"[warn] poll metrics failed for {guide_id}: {e}", file=sys.stderr)
        poll_rows = []
    # Guide views/visitors/accounts
    try:
        view_rows = _post_aggregation([
            {"source": {"guideEvents": None, "timeSeries": {
                "period": "dayRange", "first": first, "count": days}},
             "filter": f'guideId == "{guide_id}" && type == "guideSeen"'},
            {"reduce": [{"count": None}]},
        ])
    except Exception as e:
        print(f"[warn] view metrics failed for {guide_id}: {e}", file=sys.stderr)
        view_rows = []
    return {
        "responses_12mo": (poll_rows[0].get("count", 0) if poll_rows else 0),
        "views_12mo": (view_rows[0].get("count", 0) if view_rows else 0),
    }


def fetch_interested(guide_id, interested_value, days=540):
    """Return the list of 'interested' poll responses for a guide, with visitor role.
    A poll response counts as interested when its value == interested_value."""
    now = datetime.now(timezone.utc)
    first = int((now - timedelta(days=days)).timestamp() * 1000)
    try:
        rows = _post_aggregation([
            {"source": {"pollEvents": None, "timeSeries": {
                "period": "dayRange", "first": first, "count": days}},
             "filter": f'guideId == "{guide_id}"'},
            {"select": {
                "visitorId": "visitorId",
                "accountId": "accountId",
                "pollResponse": "pollResponse",
                "ts": "browserTime",
            }},
        ])
    except Exception as e:
        print(f"[warn] interested fetch failed for {guide_id}: {e}", file=sys.stderr)
        return []

    # Keep only the "interested" answers
    interested = [r for r in rows if str(r.get("pollResponse")) == str(interested_value)]
    if not interested:
        return []

    # Look up role + account name for the visitors in one pass
    visitor_ids = sorted({r["visitorId"] for r in interested if r.get("visitorId")})
    roles = fetch_visitor_roles(visitor_ids)
    account_ids = sorted({str(r["accountId"]) for r in interested if r.get("accountId")})
    account_names = fetch_account_names(account_ids)

    out = []
    for r in interested:
        vid = r.get("visitorId")
        aid = str(r.get("accountId")) if r.get("accountId") is not None else None
        ts = r.get("ts")
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts else now
        out.append({
            "visitor": vid or "",
            "account": account_names.get(aid, aid or ""),
            "date": dt.strftime("%Y-%m-%d"),
            "ts_ms": ts or 0,
            "user_level": normalize_level(roles.get(vid)),
        })
    out.sort(key=lambda x: x["ts_ms"], reverse=True)
    return out


def fetch_visitor_roles(visitor_ids):
    """{visitorId: role} for the given visitors, via a single visitor-metadata aggregation."""
    if not visitor_ids:
        return {}
    id_list = '", "'.join(v.replace('"', '') for v in visitor_ids)
    try:
        rows = _post_aggregation([
            {"source": {"visitors": None}},
            {"filter": f'visitorId in ("{id_list}")'},
            {"select": {"visitorId": "visitorId", "role": "metadata.agent.role"}},
        ])
        return {r.get("visitorId"): r.get("role") for r in rows}
    except Exception as e:
        print(f"[warn] role lookup failed: {e}", file=sys.stderr)
        return {}


def fetch_account_names(account_ids):
    """{accountId: accountName} for the given accounts."""
    if not account_ids:
        return {}
    id_list = '", "'.join(a.replace('"', '') for a in account_ids)
    try:
        rows = _post_aggregation([
            {"source": {"accounts": None}},
            {"filter": f'accountId in ("{id_list}")'},
            {"select": {"accountId": "accountId", "name": "metadata.agent.name"}},
        ])
        return {str(r.get("accountId")): (r.get("name") or str(r.get("accountId"))) for r in rows}
    except Exception as e:
        print(f"[warn] account lookup failed: {e}", file=sys.stderr)
        return {}


def fetch_all(surveys):
    """For each LIVE survey, return its metrics + interested list."""
    if not PENDO_KEY:
        print("[error] PENDO_INTEGRATION_KEY not set", file=sys.stderr)
        return {}
    result = {}
    for s in surveys:
        if s.get("status") != "live":
            continue
        gid = s["guide_id"]
        iv = s.get("interested_poll_value", 1)
        metrics = fetch_guide_metrics(gid)
        interested = fetch_interested(gid, iv)
        result[gid] = {"area": s["area"], "metrics": metrics, "interested": interested}
        time.sleep(0.5)  # be gentle on the API
    return result


if __name__ == "__main__":
    surveys = json.load(open("surveys.json")).get("surveys", [])
    print(json.dumps(fetch_all(surveys), indent=2, default=str))
