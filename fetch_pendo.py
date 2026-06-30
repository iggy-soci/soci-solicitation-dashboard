#!/usr/bin/env python3
"""
fetch_pendo.py
==============
Talks to Pendo's Aggregation API for each LIVE solicitation survey in surveys.json.

Returns, per guide:
  - funnel metrics (views, responses) from guide + poll aggregations
  - the list of "interested" responses (visitor email, account, date, user level)

Level (Pendo-only):  role == "Administrator" -> Administrator
                     role == "User"          -> Manager
                     empty / missing         -> User
                     other                   -> Unknown

Requires env var PENDO_INTEGRATION_KEY (aggregation-scoped).

NOTE on Pendo aggregation syntax: poll responses live in the `pollEvents` source, which
must be wrapped in a `pollsSeen`-style pipeline. We use the documented shape:
  source.pollEvents.guideId / pollId  +  timeSeries with first(ms)+count(days).
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta

PENDO_KEY = os.environ.get("PENDO_INTEGRATION_KEY")
PENDO_BASE = "https://app.pendo.io/api/v1"


def _agg(pipeline):
    import requests
    body = {"response": {"mimeType": "application/json"}, "request": {"pipeline": pipeline}}
    r = requests.post(
        f"{PENDO_BASE}/aggregation",
        headers={"x-pendo-integration-key": PENDO_KEY, "content-type": "application/json"},
        json=body, timeout=60,
    )
    if r.status_code >= 400:
        # surface Pendo's error message to the log so we can see WHY
        print(f"[warn] aggregation {r.status_code}: {r.text[:300]}", file=sys.stderr)
        r.raise_for_status()
    return r.json().get("results", [])


def normalize_level(role):
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


def _ms(days_ago):
    return int((datetime.now(timezone.utc) - timedelta(days=days_ago)).timestamp() * 1000)


def fetch_interested(guide_id, poll_id, interested_value, days=365):
    """
    Pull poll responses for a guide/poll over the window, keep the 'interested' answers,
    and enrich with visitor role + account name.

    Pipeline: pollEvents source filtered to the guide+poll, expanded per event, then we
    select visitorId, accountId, the response value, and the browser time.
    """
    pipeline = [
        {"source": {"pollEvents": {"guideId": guide_id, "pollId": poll_id},
                    "timeSeries": {"period": "dayRange", "first": _ms(days), "count": days}}},
        {"identified": "visitorId"},
        {"select": {
            "visitorId": "visitorId",
            "accountId": "accountId",
            "response": "pollResponse",
            "ts": "browserTime",
        }},
    ]
    try:
        rows = _agg(pipeline)
    except Exception as e:
        print(f"[warn] interested fetch failed for {guide_id}: {e}", file=sys.stderr)
        return []

    interested = [r for r in rows if str(r.get("response")) == str(interested_value)]
    if not interested:
        return []

    visitor_ids = sorted({r["visitorId"] for r in interested if r.get("visitorId")})
    account_ids = sorted({str(r["accountId"]) for r in interested if r.get("accountId") is not None})
    roles = fetch_visitor_roles(visitor_ids)
    names = fetch_account_names(account_ids)

    now = datetime.now(timezone.utc)
    out = []
    for r in interested:
        vid = r.get("visitorId") or ""
        aid = str(r.get("accountId")) if r.get("accountId") is not None else ""
        ts = r.get("ts")
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts else now
        out.append({
            "visitor": vid,
            "account": names.get(aid, aid),
            "date": dt.strftime("%Y-%m-%d"),
            "ts_ms": ts or 0,
            "user_level": normalize_level(roles.get(vid)),
        })
    # de-dupe: keep latest response per visitor
    latest = {}
    for c in out:
        if c["visitor"] not in latest or c["ts_ms"] > latest[c["visitor"]]["ts_ms"]:
            latest[c["visitor"]] = c
    result = sorted(latest.values(), key=lambda x: x["ts_ms"], reverse=True)
    return result


def fetch_visitor_roles(visitor_ids):
    """{visitorId: role} via the visitors source, filtered to our ids."""
    if not visitor_ids:
        return {}
    ids = json.dumps(visitor_ids)  # JSON array -> valid list literal in the expression
    pipeline = [
        {"source": {"visitors": None}},
        {"filter": f"visitorId in {ids}"},
        {"select": {"visitorId": "visitorId", "role": "metadata.agent.role"}},
    ]
    try:
        rows = _agg(pipeline)
        return {r.get("visitorId"): r.get("role") for r in rows}
    except Exception as e:
        print(f"[warn] role lookup failed: {e}", file=sys.stderr)
        return {}


def fetch_account_names(account_ids):
    """{accountId: name} via the accounts source."""
    if not account_ids:
        return {}
    ids = json.dumps(account_ids)
    pipeline = [
        {"source": {"accounts": None}},
        {"filter": f"accountId in {ids}"},
        {"select": {"accountId": "accountId", "name": "metadata.agent.name"}},
    ]
    try:
        rows = _agg(pipeline)
        return {str(r.get("accountId")): (r.get("name") or str(r.get("accountId"))) for r in rows}
    except Exception as e:
        print(f"[warn] account lookup failed: {e}", file=sys.stderr)
        return {}


def fetch_guide_metrics(guide_id, poll_id, days=365):
    """
    Views + responses for the funnel. Responses come from counting pollEvents;
    views from guideEvents (guideSeen). Both via aggregation.
    """
    # responses
    resp_pipeline = [
        {"source": {"pollEvents": {"guideId": guide_id, "pollId": poll_id},
                    "timeSeries": {"period": "dayRange", "first": _ms(days), "count": days}}},
        {"reduce": [{"count": "visitorId"}]},
    ]
    # views
    view_pipeline = [
        {"source": {"guideEvents": {"guideId": guide_id},
                    "timeSeries": {"period": "dayRange", "first": _ms(days), "count": days}}},
        {"filter": "type == \"guideSeen\""},
        {"reduce": [{"count": "visitorId"}]},
    ]
    responses = views = 0
    try:
        rr = _agg(resp_pipeline)
        responses = rr[0].get("count", 0) if rr else 0
    except Exception as e:
        print(f"[warn] poll metrics failed for {guide_id}: {e}", file=sys.stderr)
    try:
        vr = _agg(view_pipeline)
        views = vr[0].get("count", 0) if vr else 0
    except Exception as e:
        print(f"[warn] view metrics failed for {guide_id}: {e}", file=sys.stderr)
    return {"responses_12mo": responses, "views_12mo": views}


def fetch_guide_poll_id(guide_id):
    """Look up the guide's first poll id (so we don't have to hardcode it)."""
    import requests
    try:
        r = requests.get(
            f"{PENDO_BASE}/guide/{guide_id}",
            headers={"x-pendo-integration-key": PENDO_KEY},
            timeout=30,
        )
        r.raise_for_status()
        polls = r.json().get("polls", [])
        return polls[0]["id"] if polls else None
    except Exception as e:
        print(f"[warn] could not fetch poll id for {guide_id}: {e}", file=sys.stderr)
        return None


def fetch_all(surveys):
    if not PENDO_KEY:
        print("[error] PENDO_INTEGRATION_KEY not set", file=sys.stderr)
        return {}
    result = {}
    for s in surveys:
        if s.get("status") != "live":
            continue
        gid = s["guide_id"]
        iv = s.get("interested_poll_value", 1)
        poll_id = s.get("poll_id") or fetch_guide_poll_id(gid)
        if not poll_id:
            print(f"[warn] no poll id for {gid}; skipping", file=sys.stderr)
            result[gid] = {"area": s["area"], "metrics": {"views_12mo": 0, "responses_12mo": 0}, "interested": []}
            continue
        metrics = fetch_guide_metrics(gid, poll_id)
        interested = fetch_interested(gid, poll_id, iv)
        result[gid] = {"area": s["area"], "metrics": metrics, "interested": interested}
        time.sleep(0.4)
    return result


if __name__ == "__main__":
    surveys = json.load(open("surveys.json")).get("surveys", [])
    print(json.dumps(fetch_all(surveys), indent=2, default=str))
