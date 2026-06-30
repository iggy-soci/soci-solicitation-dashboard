#!/usr/bin/env python3
"""
build_dashboard.py
==================
Builds dashboard_data.json for the SOCi Solicitation Survey dashboard.

Flow:
  surveys.json  ->  fetch_pendo.fetch_all()  ->  assemble  ->  dashboard_data.json

Levels come straight from Pendo (Administrator / Manager / User), so there is no
Snowflake step and no static lookup. Response data is live on the Pendo key.

Optional: if ANTHROPIC_API_KEY is set, adds a one-line suggested_opener per contact
(tailored to user level) and 3 backlog themes. The key is read from the environment
inside the Action only; it is never written into the output or the page.
"""

import os
import sys
import json
from datetime import datetime, timezone

import fetch_pendo

OUT_PATH = os.environ.get("DASHBOARD_JSON", "dashboard_data.json")
LEVELS = ["Administrator", "Manager", "User"]


def sla_bucket(age_days):
    if age_days <= 7:
        return "green"
    if age_days <= 30:
        return "amber"
    return "red"


def ai_enrich(contacts):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not contacts:
        return contacts, []
    try:
        import requests
        roster = "\n".join(
            f'{i}. level={c["user_level"]}, account={c["account"]}, days_waiting={c["age_days"]}'
            for i, c in enumerate(contacts)
        )
        prompt = (
            "You are helping a SOCi Product Manager prepare outreach to customers who asked "
            "to speak with Product about a product area. For each contact, write a one-sentence "
            "opener tailored to their user level (Administrator = account-wide ROI/governance; "
            "Manager = the locations/reports they run day to day and time saved; User = the "
            "specific task, kept concrete; Unknown = neutral and friendly). Then give 3 short "
            "themes describing the backlog overall.\n\n"
            f"Contacts:\n{roster}\n\n"
            'Respond ONLY with JSON: {"openers": {"0":"...","1":"..."}, "themes":["...","...","..."]}. '
            "No prose, no markdown."
        )
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-sonnet-4-6", "max_tokens": 8000,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        resp.raise_for_status()
        text = "".join(b.get("text", "") for b in resp.json().get("content", []))
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(text)
        openers = parsed.get("openers", {})
        for i, c in enumerate(contacts):
            c["suggested_opener"] = openers.get(str(i), "")
        return contacts, parsed.get("themes", [])
    except Exception as e:
        print(f"[warn] AI enrichment failed ({e}); continuing without it", file=sys.stderr)
        return contacts, []


def main():
    now = datetime.now(timezone.utc)
    cfg = json.load(open("surveys.json"))
    surveys = cfg.get("surveys", [])
    planned_areas = cfg.get("planned_areas", [])

    pdata = fetch_pendo.fetch_all(surveys)

    # Build area list: live areas (from surveys) + planned placeholders
    areas = []
    live_areas = []
    all_contacts = []
    per_area = {}
    for s in surveys:
        if s.get("status") != "live":
            continue
        gid = s["guide_id"]
        area = s["area"]
        live_areas.append(area)
        d = pdata.get(gid, {"metrics": {}, "interested": []})
        interested = d.get("interested", [])
        # add SLA + age
        for c in interested:
            dt = datetime.strptime(c["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            c["age_days"] = (now - dt).days
            c["sla"] = sla_bucket(c["age_days"])
            c["area"] = area
            c.pop("ts_ms", None)
        all_contacts.extend(interested)
        m = d.get("metrics", {})
        per_area[area] = {
            "guide_id": gid,
            "views_12mo": m.get("views_12mo", 0),
            "responses_12mo": m.get("responses_12mo", 0),
            "interested": len(interested),
        }
        areas.append({"name": area, "status": "live"})

    for a in planned_areas:
        areas.append({"name": a, "status": "planned"})

    all_contacts.sort(key=lambda c: c["date"], reverse=True)

    # Optional AI enrichment across the whole backlog
    all_contacts, themes = ai_enrich(all_contacts)

    # Aggregates
    from collections import Counter
    level_counts = Counter(c["user_level"] for c in all_contacts)
    sla_counts = Counter(c["sla"] for c in all_contacts)
    acct_counts = Counter(c["account"] for c in all_contacts if c["account"])
    repeat = sorted([(a, n) for a, n in acct_counts.items() if n > 1], key=lambda x: -x[1])

    out = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M UTC"),
        "areas": areas,
        "per_area": per_area,
        "contacts": all_contacts,
        "level_counts": {lvl: level_counts.get(lvl, 0) for lvl in LEVELS},
        "level_counts_extra": {k: v for k, v in level_counts.items() if k not in LEVELS},
        "sla_counts": dict(sla_counts),
        "total_interested": len(all_contacts),
        "oldest_age": max((c["age_days"] for c in all_contacts), default=0),
        "repeat_accounts": repeat,
        "themes": themes,
        "live_count": len(live_areas),
        "planned_count": len(planned_areas),
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_PATH}: {len(all_contacts)} interested across {len(live_areas)} live area(s), "
          f"levels={out['level_counts']}, sla={dict(sla_counts)}, ai={'on' if themes else 'off'}")


if __name__ == "__main__":
    main()
