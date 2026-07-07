#!/usr/bin/env python3
"""
fetch_pendo.py
==============
Pulls each LIVE solicitation survey's interested responses from Pendo, enriched with
each visitor's user level and account name. Aggregation API only (one integration key).

Level (Pendo-only):  role == "Administrator" -> Administrator
                     role == "User"          -> Manager
                     empty / missing / null  -> User
                     other                   -> Unknown

SYNTAX NOTES (from Pendo's own 400 messages):
  * No "in [list]" operator exists. Use == equality, combined with || (OR) for batches.
  * Poll responses: pollEvents source with guideId+pollId nested in the source.
  * We pull the interested list first, collect just those visitor/account IDs, then look
    up roles and account names in small OR-chunks. Bounded by the interested count, never
    by the whole visitor table.
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta

PENDO_KEY = os.environ.get("PENDO_INTEGRATION_KEY")
PENDO_BASE = "https://app.pendo.io/api/v1"
CHUNK = 40  # how many ids per OR-chained query


def _agg(pipeline):
    import requests
    body = {"response": {"mimeType": "application/json"}, "request": {"pipeline": pipeline}}
    r = requests.post(
        f"{PENDO_BASE}/aggregation",
        headers={"x-pendo-integration-key": PENDO_KEY, "content-type": "application/json"},
        json=body, timeout=120,
    )
    if r.status_code >= 400:
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


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



def resolve_poll_id(guide_id):
    """
    Auto-discover the guide's poll id via the aggregation `guides` source.
    The plain /guide/{id} REST endpoint 404s on an aggregation-scoped key, but the
    aggregation endpoint can read the guides source, which includes each guide's polls.
    Prefers a PositiveNegative poll; falls back to the first poll.
    """
    try:
        rows = _agg([
            {"source": {"guides": None}},
            {"filter": f'id == "{guide_id}"'},
            {"select": {"id": "id", "polls": "polls"}},
        ])
        polls = (rows[0].get("polls") if rows else None) or []
        if not polls:
            print(f"[warn] no polls found on guide {guide_id}", file=sys.stderr)
            return None
        for p in polls:
            attrs = p.get("attributes") or {}
            if (p.get("type") or attrs.get("type")) == "PositiveNegative":
                print(f"[info] auto-resolved poll id {p.get('id')} (PositiveNegative) for {guide_id}", file=sys.stderr)
                return p.get("id")
        pid = polls[0].get("id")
        print(f"[info] auto-resolved poll id {pid} (first poll) for {guide_id}", file=sys.stderr)
        return pid
    except Exception as e:
        print(f"[warn] poll id auto-resolution failed for {guide_id}: {e}", file=sys.stderr)
        return None


def fetch_visitor_info(visitor_ids):
    """
    {visitorId: {role, email, name}} for just these ids, via OR-chained equality in
    small chunks. Tries a rich select (role + email + name candidates from both
    agent- and auto-metadata); if Pendo rejects it, falls back to role-only so
    levels never break because of the identity enrichment.
    """
    out = {}
    rich_select = {
        "visitorId": "visitorId",
        "role": "metadata.agent.role",
        "email_agent": "metadata.agent.email",
        "email_auto": "metadata.auto.email",
        "name_agent": "metadata.agent.full_name",
        "name_auto": "metadata.auto.name",
    }
    basic_select = {"visitorId": "visitorId", "role": "metadata.agent.role"}
    for chunk in _chunks(visitor_ids, CHUNK):
        expr = " || ".join(f'visitorId == "{v}"' for v in chunk)
        rows = None
        try:
            rows = _agg([
                {"source": {"visitors": None}},
                {"filter": expr},
                {"select": rich_select},
            ])
        except Exception as e:
            print(f"[warn] rich visitor select failed ({e}); retrying role-only", file=sys.stderr)
            try:
                rows = _agg([
                    {"source": {"visitors": None}},
                    {"filter": expr},
                    {"select": basic_select},
                ])
            except Exception as e2:
                print(f"[warn] visitor chunk failed entirely: {e2}", file=sys.stderr)
                continue
        for r in rows or []:
            vid = str(r.get("visitorId"))
            email = r.get("email_agent") or r.get("email_auto") or ""
            if not email and "@" in vid:
                email = vid  # some subscriptions key visitors by email
            out[vid] = {
                "role": r.get("role"),
                "email": email,
                "name": r.get("name_agent") or r.get("name_auto") or "",
            }
    return out


def fetch_names_for(account_ids):
    """{accountId: name} for just these ids, via OR-chained equality in small chunks."""
    out = {}
    for chunk in _chunks(account_ids, CHUNK):
        expr = " || ".join(f'accountId == "{a}"' for a in chunk)
        try:
            rows = _agg([
                {"source": {"accounts": None}},
                {"filter": expr},
                {"select": {"accountId": "accountId", "name": "metadata.agent.name"}},
            ])
            for r in rows:
                out[str(r.get("accountId"))] = r.get("name") or str(r.get("accountId"))
        except Exception as e:
            print(f"[warn] account chunk failed: {e}", file=sys.stderr)
    return out


def fetch_interested(guide_id, poll_id, interested_value, days=365):
    pipeline = [
        {"source": {"pollEvents": {"guideId": guide_id, "pollId": poll_id},
                    "timeSeries": {"period": "dayRange", "first": _ms(days), "count": days}}},
        {"identified": "visitorId"},
        {"select": {"visitorId": "visitorId", "accountId": "accountId",
                    "response": "pollResponse", "ts": "browserTime"}},
    ]
    try:
        rows = _agg(pipeline)
    except Exception as e:
        print(f"[warn] interested fetch failed for {guide_id}: {e}", file=sys.stderr)
        return []

    interested = [r for r in rows if str(r.get("response")) == str(interested_value)]
    if not interested:
        return []

    # de-dupe to latest response per visitor first (shrinks the lookup sets)
    now = datetime.now(timezone.utc)
    by_visitor = {}
    for r in interested:
        vid = str(r.get("visitorId") or "")
        if not vid:
            continue
        ts = r.get("ts") or 0
        if vid not in by_visitor or ts > by_visitor[vid]["ts_ms"]:
            by_visitor[vid] = {
                "visitor": vid,
                "account_id": str(r.get("accountId")) if r.get("accountId") is not None else "",
                "ts_ms": ts,
            }

    visitor_ids = list(by_visitor.keys())
    account_ids = sorted({v["account_id"] for v in by_visitor.values() if v["account_id"]})
    info = fetch_visitor_info(visitor_ids)
    names = fetch_names_for(account_ids)
    with_role = sum(1 for v in visitor_ids if (info.get(v) or {}).get("role"))
    with_email = sum(1 for v in visitor_ids if (info.get(v) or {}).get("email"))
    print(f"[info] {guide_id}: {len(visitor_ids)} interested visitors, "
          f"{with_role} with a role value, {with_email} with an email", file=sys.stderr)

    out = []
    for vid, v in by_visitor.items():
        ts = v["ts_ms"]
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts else now
        vi = info.get(vid) or {}
        out.append({
            "visitor": vid,
            "email": vi.get("email") or "",
            "name": vi.get("name") or "",
            "account": names.get(v["account_id"], v["account_id"]),
            "date": dt.strftime("%Y-%m-%d"),
            "ts_ms": ts,
            "user_level": normalize_level(vi.get("role")),
        })
    return sorted(out, key=lambda x: x["ts_ms"], reverse=True)


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
        poll_id = s.get("poll_id") or resolve_poll_id(gid)
        if not poll_id:
            print(f"[warn] no poll_id for {gid} (not in surveys.json and auto-resolution failed); skipping", file=sys.stderr)
            result[gid] = {"area": s["area"], "metrics": {"views_12mo": 0, "responses_12mo": 0}, "interested": []}
            continue
        interested = fetch_interested(gid, poll_id, iv)
        result[gid] = {
            "area": s["area"],
            "metrics": {"views_12mo": 0, "responses_12mo": len(interested)},
            "interested": interested,
        }
    return result


if __name__ == "__main__":
    surveys = json.load(open("surveys.json")).get("surveys", [])
    print(json.dumps(fetch_all(surveys), indent=2, default=str))
