# SOCi Solicitation Survey Dashboard

A standalone, live dashboard for SOCi's product-feedback **solicitation** surveys (the
"Are you interested in speaking with the Product Team?" guides). It pulls response data
straight from Pendo, labels each interested customer by user level, and shows a live
action queue of who to follow up with.

Self-contained: this repo has **no dependency on the pendo-slack-relay repo**.

## How it works

```
surveys.json  ->  fetch_pendo.py (Pendo API)  ->  build_dashboard.py  ->  dashboard_data.json
                                                                                |
                                            index.html (GitHub Pages) reads it, refreshes every 60s
```

- **GitHub Actions** runs on a schedule: pulls Pendo, builds `dashboard_data.json`, commits it.
- **GitHub Pages** serves `index.html`, which fetches the JSON and renders. Live without a server.
- **User levels come from Pendo** (`metadata.agent.role`): `Administrator` -> Administrator,
  `User` -> Manager (includes Group Managers), empty/missing -> User. No Snowflake, no manual refresh.

## One-time setup

### 1. Create the repo and push these files
A new GitHub repo (e.g. `soci-solicitation-dashboard`). Push everything here.

### 2. Add secrets
Repo -> Settings -> Secrets and variables -> Actions:
- `PENDO_INTEGRATION_KEY` — a Pendo integration key with aggregation read access (**required**)
- `ANTHROPIC_API_KEY` — optional; enables one-line suggested openers + backlog themes

No other credentials. No Snowflake.

### 3. Turn on GitHub Pages
Repo -> Settings -> Pages -> Source: Deploy from a branch -> branch `main`, folder `/ (root)`.
GitHub gives you a URL like `https://<org-or-user>.github.io/soci-solicitation-dashboard/`.
That URL is the dashboard. Share it internally only.

### 4. Run the workflow once
Actions tab -> "refresh dashboard" -> Run workflow. It fetches Pendo, writes
`dashboard_data.json`, and commits it. The page goes live with real data within a minute.

The schedule (`*/30 * * * *`, every 30 min) then keeps it fresh. Adjust the cron in
`.github/workflows/refresh.yml` to taste.

## Adding a new solicitation survey

When a new solicitation survey is deployed in Pendo, either:
- **In the dashboard:** open Admin -> profile -> section 1, fill guide ID + area, generate the
  block, paste it into the `surveys` array in `surveys.json`, commit. Or
- **Directly:** add to `surveys.json`:
  ```json
  { "guide_id": "<pendo guide id>", "area": "Listings", "status": "live", "interested_poll_value": 1 }
  ```

`interested_poll_value` defaults to `1` (the Reporting Suite pattern: PositiveNegative poll
where 1 = "I'm Interested"). All current solicitation surveys follow this, so usually you only
need the guide ID and area. Move the area out of `planned_areas` if it's listed there.

## Admin panel

Top-right "Admin" button. Default password: `SOCi-Pendo-Admin-2026`.
- **Section 1** — add a survey (generates the `surveys.json` block).
- **Section 2** — lists live surveys.
- **Section 3** — change the password (generates the hash line to paste into `index.html`).
- **Section 4** — explains the refresh.

Every field has a hover ("?") explaining what it's for.

Honest note: the password is a lightweight gate, not strong auth — fine for an internal-only
link because the panel holds no credentials or customer-private data. The admin login and the
copy/hash helpers need the **hosted https URL** (they don't work opening the raw file locally).
Anyone with the internal link can view the dashboard; if you later need true "approved members
only," put the site behind Cloudflare Access or SSO (not included here by design).

## Files
- `index.html` — dashboard + admin panel (served by Pages)
- `surveys.json` — the add-a-survey config
- `fetch_pendo.py` — pulls metrics + interested responses (with role) from Pendo
- `build_dashboard.py` — assembles `dashboard_data.json` (+ optional Anthropic enrichment)
- `dashboard_data.json` — generated output the page reads (committed by the Action)
- `.github/workflows/refresh.yml` — scheduled fetch + build + commit
- `gen_index.py` — regenerates `index.html` (only needed if you edit the template)

## What this dashboard does NOT do (by design)
- No Snowflake, no Group-Admin-vs-Manager split (those fold into "Manager").
- No reminder emails/Slack (dropped — there's no manual refresh to remind about).
- No membership enforcement (internal link + soft password only).
