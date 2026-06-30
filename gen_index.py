#!/usr/bin/env python3
"""Generates index.html for the fresh standalone dashboard."""

PW_HASH = "02f57263f66f397611410a418be8befb7a646e8eb74a6b37a0cc683adaa4c3f2"

HTML = r'''<!doctype html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>SOCi · Solicitation Survey Control Room</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --brand-green:#29CC91; --brand-green-soft:#7FE0BD; --brand-white:#FFFFFF; --brand-black:#0C0C0D;
    --brand-calamine:#5BCEE4; --brand-red:#EA5B59; --brand-helvetia:#213B61; --brand-gray:#C9CED6;
  }
  :root, [data-theme="light"] {
    --bg:#F4F6F8; --surface:#FFFFFF; --surface-2:#F0F3F6; --surface-3:#E7ECF1;
    --ink:#0C0C0D; --ink-2:#3A4150; --muted:#6B7280; --hairline:#E2E7EC; --hairline-soft:#EEF1F4;
    --accent:#29CC91; --accent-bg:rgba(41,204,145,.10); --on-accent:#0C0C0D;
    --green:#15A772; --green-bg:rgba(41,204,145,.12); --amber:#C8841E; --amber-bg:rgba(232,179,65,.16);
    --red:#D8413F; --red-bg:rgba(234,91,89,.12); --shadow:0 2px 8px rgba(12,12,13,.05),0 8px 24px rgba(12,12,13,.04);
  }
  [data-theme="dark"] {
    --bg:#0C0C0D; --surface:#15161A; --surface-2:#1C1E23; --surface-3:#25282F;
    --ink:#F4F6FA; --ink-2:#B8BEC9; --muted:#7A828F; --hairline:#262A31; --hairline-soft:#1E2127;
    --accent:#29CC91; --accent-bg:rgba(41,204,145,.14); --on-accent:#0C0C0D;
    --green:#29CC91; --green-bg:rgba(41,204,145,.14); --amber:#E8B341; --amber-bg:rgba(232,179,65,.14);
    --red:#EA5B59; --red-bg:rgba(234,91,89,.14); --shadow:0 2px 8px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.25);
  }
  @media (prefers-color-scheme: dark) { [data-theme="auto"] {
    --bg:#0C0C0D; --surface:#15161A; --surface-2:#1C1E23; --surface-3:#25282F;
    --ink:#F4F6FA; --ink-2:#B8BEC9; --muted:#7A828F; --hairline:#262A31; --hairline-soft:#1E2127;
    --accent:#29CC91; --accent-bg:rgba(41,204,145,.14); --on-accent:#0C0C0D;
    --green:#29CC91; --green-bg:rgba(41,204,145,.14); --amber:#E8B341; --amber-bg:rgba(232,179,65,.14);
    --red:#EA5B59; --red-bg:rgba(234,91,89,.14); --shadow:0 2px 8px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.25);
  } }
  @media (prefers-color-scheme: light) { [data-theme="auto"] {
    --bg:#F4F6F8; --surface:#FFFFFF; --surface-2:#F0F3F6; --surface-3:#E7ECF1;
    --ink:#0C0C0D; --ink-2:#3A4150; --muted:#6B7280; --hairline:#E2E7EC; --hairline-soft:#EEF1F4;
    --accent:#29CC91; --accent-bg:rgba(41,204,145,.10); --green:#15A772; --green-bg:rgba(41,204,145,.12);
    --amber:#C8841E; --amber-bg:rgba(232,179,65,.16); --red:#D8413F; --red-bg:rgba(234,91,89,.12);
    --shadow:0 2px 8px rgba(12,12,13,.05),0 8px 24px rgba(12,12,13,.04);
  } }
  * { box-sizing:border-box; }
  html,body { margin:0; padding:0; background:var(--bg); transition:background .3s; }
  body { font-family:'Inter',system-ui,sans-serif; color:var(--ink); font-size:14px; line-height:1.5; -webkit-font-smoothing:antialiased; }
  .wrap { max-width:1400px; margin:0 auto; padding:24px 28px 64px; }
  .topbar { display:flex; align-items:center; justify-content:space-between; padding-bottom:18px; margin-bottom:24px; border-bottom:1px solid var(--hairline); }
  .brand { display:flex; align-items:center; gap:13px; }
  .brand-logo { width:30px; height:30px; border-radius:8px; background:var(--brand-green); display:flex; align-items:center; justify-content:center; }
  .brand-logo svg { width:17px; height:17px; }
  .brand-mark { font-family:'JetBrains Mono',monospace; font-weight:700; font-size:14px; }
  .brand-sub { font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--muted); }
  .topbar-right { display:flex; align-items:center; gap:16px; }
  .heartbeat { display:flex; align-items:center; gap:8px; font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--green); text-transform:uppercase; }
  .pulse { width:8px; height:8px; border-radius:50%; background:var(--green); animation:hb 2s infinite; }
  @keyframes hb { 0%{box-shadow:0 0 0 0 rgba(41,204,145,.4);} 70%{box-shadow:0 0 0 8px rgba(41,204,145,0);} 100%{box-shadow:0 0 0 0 rgba(41,204,145,0);} }
  .updated { font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--muted); }
  .updated b { color:var(--ink-2); font-weight:500; }
  .admin-entry { display:flex; align-items:center; gap:6px; font-family:'JetBrains Mono',monospace; font-size:11px; padding:6px 12px; border-radius:8px; background:var(--surface-2); border:1px solid var(--hairline); color:var(--ink-2); cursor:pointer; }
  .admin-entry:hover { border-color:var(--accent); color:var(--accent); }
  .admin-entry svg { width:14px; height:14px; }
  .theme-toggle { display:flex; gap:2px; background:var(--surface-2); border:1px solid var(--hairline); border-radius:8px; padding:3px; }
  .theme-btn { background:none; border:none; width:30px; height:26px; border-radius:6px; cursor:pointer; color:var(--muted); display:flex; align-items:center; justify-content:center; }
  .theme-btn.active { background:var(--surface); color:var(--accent); box-shadow:var(--shadow); }
  .theme-btn svg { width:15px; height:15px; }
  .goal { background:var(--surface); border:1px solid var(--hairline); border-left:3px solid var(--red); border-radius:10px; padding:18px 22px; margin-bottom:24px; box-shadow:var(--shadow); }
  .goal-eyebrow { font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:6px; }
  .goal-text { font-size:15px; } .goal-text b { color:var(--red); font-weight:700; }
  .kpi-row { display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:28px; }
  .kpi { background:var(--surface); border:1px solid var(--hairline); border-radius:10px; padding:16px 18px; box-shadow:var(--shadow); }
  .kpi-label { font-family:'JetBrains Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); margin-bottom:10px; }
  .kpi-value { font-family:'JetBrains Mono',monospace; font-size:30px; font-weight:600; line-height:1; }
  .kpi-value.alert{color:var(--red);} .kpi-value.warn{color:var(--amber);} .kpi-value.good{color:var(--green);}
  .kpi-foot { display:flex; gap:6px; margin-top:10px; font-size:11px; color:var(--muted); }
  .section-head { display:flex; align-items:baseline; justify-content:space-between; margin:0 0 14px; }
  .section-title { font-size:15px; font-weight:600; }
  .section-eyebrow { font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); }
  .level-panel { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:28px; }
  .level-card { background:var(--surface); border:1px solid var(--hairline); border-radius:10px; padding:16px 18px; box-shadow:var(--shadow); position:relative; overflow:hidden; cursor:pointer; transition:transform .15s,border-color .15s; }
  .level-card:hover { transform:translateY(-2px); }
  .level-card.active { border-color:var(--accent); }
  .level-bar { position:absolute; left:0; top:0; bottom:0; width:3px; }
  .level-name { font-size:13px; font-weight:600; margin-bottom:4px; }
  .level-count { font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:600; line-height:1; margin-bottom:8px; }
  .level-desc { font-size:11px; color:var(--muted); line-height:1.4; }
  .level-pct { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--ink-2); margin-top:8px; }
  .anomaly { background:var(--red-bg); border:1px solid var(--red); border-radius:10px; padding:14px 18px; margin-bottom:28px; display:flex; align-items:center; gap:14px; }
  .anomaly-icon { font-size:18px; color:var(--red); }
  .anomaly-text { font-size:13px; } .anomaly-text b { color:var(--red); }
  .sla-strip { display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:12px; margin-bottom:28px; }
  .sla-bar-card { background:var(--surface); border:1px solid var(--hairline); border-radius:10px; padding:16px 18px; box-shadow:var(--shadow); }
  .sla-bar-track { display:flex; height:28px; border-radius:6px; overflow:hidden; margin-bottom:12px; background:var(--surface-3); }
  .sla-seg { height:100%; display:flex; align-items:center; justify-content:center; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; color:#fff; }
  .sla-seg.green{background:var(--green);} .sla-seg.amber{background:var(--amber);} .sla-seg.red{background:var(--red);}
  .sla-legend { display:flex; gap:16px; font-size:11px; color:var(--ink-2); flex-wrap:wrap; }
  .sla-legend span { display:flex; align-items:center; gap:6px; }
  .ldot { width:8px; height:8px; border-radius:2px; } .ldot.green{background:var(--green);} .ldot.amber{background:var(--amber);} .ldot.red{background:var(--red);}
  .sla-stat { background:var(--surface); border:1px solid var(--hairline); border-radius:10px; padding:16px 18px; box-shadow:var(--shadow); }
  .sla-stat-val { font-family:'JetBrains Mono',monospace; font-size:26px; font-weight:600; line-height:1; }
  .sla-stat-val.red{color:var(--red);} .sla-stat-val.amber{color:var(--amber);} .sla-stat-val.green{color:var(--green);}
  .sla-stat-lbl { font-family:'JetBrains Mono',monospace; font-size:10px; text-transform:uppercase; color:var(--muted); margin-top:8px; }
  .grid-controls { display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap; }
  .filter-chip { font-family:'JetBrains Mono',monospace; font-size:11px; padding:6px 12px; border-radius:7px; background:var(--surface); border:1px solid var(--hairline); color:var(--ink-2); cursor:pointer; }
  .filter-chip.active { background:var(--accent-bg); border-color:var(--accent); color:var(--accent); }
  .area-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:32px; }
  .area-card { background:var(--surface); border:1px solid var(--hairline); border-radius:10px; padding:16px; text-align:left; font-family:inherit; box-shadow:var(--shadow); transition:transform .15s,border-color .15s; }
  .area-live { cursor:pointer; border-color:var(--accent); }
  .area-live:hover { transform:translateY(-2px); }
  .area-planned { border-style:dashed; opacity:.62; }
  .area-top { display:flex; align-items:center; gap:7px; margin-bottom:12px; }
  .area-status-dot { width:7px; height:7px; border-radius:50%; }
  .area-status-dot.live{background:var(--green);} .area-status-dot.planned{background:var(--muted);}
  .area-status-label { font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:.1em; }
  .area-status-label.live{color:var(--green);} .area-status-label.planned{color:var(--muted);}
  .area-name { font-size:14px; font-weight:600; margin-bottom:14px; min-height:34px; }
  .area-metrics { display:flex; gap:18px; margin-bottom:12px; }
  .planned-metrics { opacity:.4; }
  .am { display:flex; flex-direction:column; gap:2px; }
  .am-val { font-family:'JetBrains Mono',monospace; font-size:18px; font-weight:600; }
  .am-lbl { font-family:'JetBrains Mono',monospace; font-size:9px; text-transform:uppercase; color:var(--muted); }
  .area-foot { font-size:11px; color:var(--muted); border-top:1px solid var(--hairline-soft); padding-top:10px; }
  .queue-wrap { background:var(--surface); border:1px solid var(--hairline); border-radius:10px; overflow:hidden; box-shadow:var(--shadow); }
  .queue-head { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; border-bottom:1px solid var(--hairline); flex-wrap:wrap; gap:10px; }
  .queue-title { font-size:14px; font-weight:600; display:flex; align-items:center; gap:10px; }
  .queue-live-badge { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--green); border:1px solid var(--green); padding:2px 7px; border-radius:4px; }
  .queue-filters { display:flex; gap:8px; flex-wrap:wrap; }
  .qf { font-family:'JetBrains Mono',monospace; font-size:10px; padding:4px 10px; border-radius:6px; background:var(--surface-2); border:1px solid var(--hairline); color:var(--ink-2); cursor:pointer; }
  .qf.active { background:var(--accent-bg); border-color:var(--accent); color:var(--accent); }
  table.queue { width:100%; border-collapse:collapse; }
  table.queue th { text-align:left; padding:10px 18px; font-family:'JetBrains Mono',monospace; font-size:10px; text-transform:uppercase; color:var(--muted); border-bottom:1px solid var(--hairline); font-weight:500; background:var(--surface-2); }
  table.queue td { padding:11px 18px; border-bottom:1px solid var(--hairline-soft); font-size:12.5px; }
  .q-row:hover { background:var(--surface-2); }
  .q-date { font-family:'JetBrains Mono',monospace; color:var(--muted); white-space:nowrap; }
  .q-visitor { font-family:'JetBrains Mono',monospace; font-size:11.5px; color:var(--ink-2); }
  .q-account { font-weight:500; }
  .level-tag { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:600; padding:2px 8px; border-radius:10px; white-space:nowrap; }
  .sla-pill { font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:600; padding:2px 8px; border-radius:10px; }
  .sla-green{background:var(--green-bg);color:var(--green);} .sla-amber{background:var(--amber-bg);color:var(--amber);} .sla-red{background:var(--red-bg);color:var(--red);}
  .opener { font-size:11px; color:var(--muted); font-style:italic; margin-top:3px; }
  .empty-note { padding:40px; text-align:center; color:var(--muted); font-size:13px; }
  /* admin */
  .admin-overlay { position:fixed; inset:0; background:var(--bg); display:none; z-index:300; overflow-y:auto; }
  .admin-overlay.open { display:block; }
  .admin-inner { max-width:920px; margin:0 auto; padding:28px; }
  .admin-bar { display:flex; align-items:center; justify-content:space-between; padding-bottom:18px; margin-bottom:24px; border-bottom:1px solid var(--hairline); }
  .admin-bar h1 { font-size:17px; margin:0; font-weight:700; }
  .admin-back { font-family:'JetBrains Mono',monospace; font-size:11px; padding:7px 14px; border-radius:8px; background:var(--surface-2); border:1px solid var(--hairline); color:var(--ink-2); cursor:pointer; }
  .login-card { max-width:380px; margin:8vh auto 0; background:var(--surface); border:1px solid var(--hairline); border-radius:14px; padding:32px; box-shadow:var(--shadow); text-align:center; }
  .login-logo { width:44px; height:44px; border-radius:11px; background:var(--brand-green); display:flex; align-items:center; justify-content:center; margin:0 auto 16px; }
  .login-logo svg { width:24px; height:24px; }
  .login-card h2 { font-size:18px; margin:0 0 6px; }
  .login-card p { font-size:13px; color:var(--muted); margin:0 0 20px; }
  .login-input { width:100%; padding:11px 14px; border-radius:8px; border:1px solid var(--hairline); background:var(--surface-2); color:var(--ink); font-size:14px; font-family:inherit; margin-bottom:12px; }
  .login-input:focus { outline:none; border-color:var(--accent); }
  .login-btn { width:100%; padding:11px; border-radius:8px; border:none; background:var(--brand-green); color:#0C0C0D; font-weight:600; font-size:14px; cursor:pointer; }
  .login-err { color:var(--red); font-size:12px; margin-top:12px; min-height:16px; }
  .login-note { font-size:11px; color:var(--muted); margin-top:18px; line-height:1.5; }
  .prof-section { background:var(--surface); border:1px solid var(--hairline); border-radius:12px; padding:22px 24px; margin-bottom:18px; box-shadow:var(--shadow); }
  .prof-section h3 { font-size:14px; margin:0 0 4px; font-weight:700; display:flex; align-items:center; gap:9px; }
  .prof-section .sec-sub { font-size:12.5px; color:var(--muted); margin:0 0 18px; line-height:1.5; }
  .prof-section code { font-family:'JetBrains Mono',monospace; font-size:11.5px; background:var(--surface-3); padding:1px 5px; border-radius:3px; color:var(--ink); }
  .prof-num { width:24px; height:24px; border-radius:7px; background:var(--accent-bg); color:var(--accent); font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; display:inline-flex; align-items:center; justify-content:center; }
  .field-row { display:flex; gap:16px; flex-wrap:wrap; align-items:flex-end; }
  .field { display:flex; flex-direction:column; gap:6px; flex:1; min-width:200px; }
  .field label { font-family:'JetBrains Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); display:flex; align-items:center; gap:6px; }
  .field input, .field select { padding:10px 12px; border-radius:8px; border:1px solid var(--hairline); background:var(--surface-2); color:var(--ink); font-size:13.5px; font-family:inherit; }
  .field input:focus, .field select:focus { outline:none; border-color:var(--accent); }
  .prof-btn { padding:10px 16px; border-radius:8px; border:none; background:var(--brand-green); color:#0C0C0D; font-weight:600; font-size:13px; cursor:pointer; white-space:nowrap; }
  .prof-btn.secondary { background:var(--surface-2); border:1px solid var(--hairline); color:var(--ink-2); }
  .code-block { position:relative; margin-top:6px; }
  .code-block pre { background:var(--surface-2); border:1px solid var(--hairline); border-radius:8px; padding:16px; padding-top:40px; overflow-x:auto; font-family:'JetBrains Mono',monospace; font-size:11.5px; line-height:1.5; color:var(--ink-2); margin:0; white-space:pre; max-height:300px; }
  .copy-btn { position:absolute; top:8px; right:8px; font-family:'JetBrains Mono',monospace; font-size:10px; padding:5px 11px; border-radius:6px; background:var(--surface-3); border:1px solid var(--hairline); color:var(--ink-2); cursor:pointer; z-index:2; }
  .copy-btn.copied { background:var(--accent-bg); border-color:var(--accent); color:var(--accent); }
  .gen-out { margin-top:14px; }
  /* hover tooltip */
  .hint { position:relative; display:inline-flex; align-items:center; justify-content:center; width:14px; height:14px; border-radius:50%; background:var(--surface-3); color:var(--muted); font-size:9px; font-weight:700; cursor:help; font-family:'JetBrains Mono',monospace; }
  .hint:hover .hint-pop { display:block; }
  .hint-pop { display:none; position:absolute; bottom:130%; left:50%; transform:translateX(-50%); width:240px; background:var(--brand-black); color:#fff; font-family:'Inter',sans-serif; font-weight:400; text-transform:none; letter-spacing:normal; font-size:11.5px; line-height:1.5; padding:10px 12px; border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,.3); z-index:10; }
  .hint-pop::after { content:''; position:absolute; top:100%; left:50%; transform:translateX(-50%); border:5px solid transparent; border-top-color:var(--brand-black); }
  .drill-overlay { position:fixed; inset:0; background:rgba(12,13,14,.6); backdrop-filter:blur(4px); display:none; align-items:center; justify-content:center; z-index:200; padding:24px; }
  .drill-overlay.open { display:flex; }
  .drill { background:var(--surface); border:1px solid var(--hairline); border-radius:14px; max-width:720px; width:100%; max-height:86vh; overflow-y:auto; box-shadow:0 24px 64px rgba(0,0,0,.3); }
  .drill-head { display:flex; justify-content:space-between; padding:22px 24px 18px; border-bottom:1px solid var(--hairline); position:sticky; top:0; background:var(--surface); }
  .drill-title { font-size:18px; font-weight:700; }
  .drill-sub { font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--muted); margin-top:4px; }
  .drill-close { background:var(--surface-3); border:none; color:var(--ink-2); width:30px; height:30px; border-radius:8px; cursor:pointer; font-size:16px; }
  .drill-body { padding:22px 24px; }
  .funnel { display:flex; flex-direction:column; gap:8px; margin-bottom:24px; }
  .funnel-step { position:relative; background:var(--surface-2); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; overflow:hidden; }
  .funnel-fill { position:absolute; left:0; top:0; bottom:0; background:var(--accent-bg); border-left:2px solid var(--accent); }
  .funnel-lbl { position:relative; font-size:13px; } .funnel-val { position:relative; font-family:'JetBrains Mono',monospace; font-weight:600; }
  .drill-section-title { font-size:13px; font-weight:600; margin:22px 0 10px; }
  .level-break { display:flex; flex-direction:column; gap:8px; }
  .lb-row { display:flex; align-items:center; gap:12px; }
  .lb-bar-track { flex:1; height:22px; background:var(--surface-3); border-radius:5px; overflow:hidden; }
  .lb-bar { height:100%; border-radius:5px; display:flex; align-items:center; padding-left:8px; font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700; color:#fff; }
  .lb-label { width:110px; font-size:12px; }
  .repeat-list { list-style:none; padding:0; margin:0; }
  .repeat-list li { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--hairline-soft); font-size:13px; }
  footer { margin-top:40px; padding-top:18px; border-top:1px solid var(--hairline); font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); text-align:center; line-height:1.7; }
  .footer-warn { color:var(--red); }
  @media (max-width:1100px){ .kpi-row{grid-template-columns:repeat(2,1fr);} .sla-strip,.level-panel{grid-template-columns:repeat(2,1fr);} .area-grid{grid-template-columns:repeat(2,1fr);} }
  @media (max-width:640px){ .wrap{padding:16px;} .kpi-row,.area-grid,.sla-strip,.level-panel{grid-template-columns:1fr;} .topbar{flex-direction:column;gap:12px;align-items:flex-start;} }
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <div class="brand">
      <div class="brand-logo"><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="6" fill="#0C0C0D"/></svg></div>
      <div><div class="brand-mark">Solicitation Survey Control Room</div><div class="brand-sub">SOCi Voice-of-Customer · product feedback program</div></div>
    </div>
    <div class="topbar-right">
      <div class="heartbeat"><span class="pulse"></span><span id="liveLabel">Live</span></div>
      <div class="updated">Updated <b id="updatedTs">—</b></div>
      <button class="admin-entry" onclick="openAdmin()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z"/></svg>Admin</button>
      <div class="theme-toggle">
        <button class="theme-btn" data-mode="light" title="Day"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
        <button class="theme-btn" data-mode="auto" title="Auto"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 000 18z" fill="currentColor"/></svg></button>
        <button class="theme-btn" data-mode="dark" title="Night"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg></button>
      </div>
    </div>
  </div>

  <div class="goal">
    <div class="goal-eyebrow">Program objective</div>
    <div class="goal-text" id="goalText">No customer who raises their hand goes un-contacted.</div>
  </div>

  <div class="kpi-row" id="kpiRow"></div>

  <div class="section-head"><div class="section-title">Who is raising their hand</div><div class="section-eyebrow">By customer user level · the conversation differs per level</div></div>
  <div class="level-panel" id="levelPanel"></div>

  <div class="anomaly" id="anomaly" style="display:none"><div class="anomaly-icon">&#9888;</div><div class="anomaly-text" id="anomalyText"></div></div>

  <div class="section-head"><div class="section-title">Follow-up SLA health</div><div class="section-eyebrow">Time since customer raised hand</div></div>
  <div class="sla-strip" id="slaStrip"></div>

  <div class="section-head"><div class="section-title" id="areaTitle">Product areas</div><div class="section-eyebrow">One solicitation survey per area</div></div>
  <div class="grid-controls" id="gridControls"></div>
  <div class="area-grid" id="areaGrid"></div>

  <div class="queue-wrap">
    <div class="queue-head">
      <div class="queue-title">Live action queue <span class="queue-live-badge">AUTO</span></div>
      <div class="queue-filters" id="queueFilters"></div>
    </div>
    <table class="queue"><thead><tr><th>Date</th><th>Visitor</th><th>Account</th><th>User level</th><th>SLA age</th></tr></thead><tbody id="queueBody"></tbody></table>
  </div>

  <footer>
    <div class="footer-warn">Internal use only · Contains SOCi customer contact information</div>
    <div id="footMeta">Live solicitation-survey monitor · data from Pendo</div>
  </footer>
</div>

<!-- ADMIN LOGIN -->
<div class="admin-overlay" id="adminLogin">
  <div class="admin-inner">
    <div class="admin-bar"><h1>&#128274; Admin access</h1><button class="admin-back" onclick="closeAdmin()">&larr; Back to dashboard</button></div>
    <div class="login-card">
      <div class="login-logo"><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="6" fill="#0C0C0D"/></svg></div>
      <h2>Enter admin password</h2><p>This area is for the dashboard administrator.</p>
      <input class="login-input" type="password" id="adminPw" placeholder="Password" onkeydown="if(event.key==='Enter')tryLogin()" />
      <button class="login-btn" onclick="tryLogin()">Unlock</button>
      <div class="login-err" id="loginErr"></div>
      <div class="login-note">Lightweight gate, not strong security. It keeps the admin panel out of casual view. The panel holds no credentials or customer-private data, only setup instructions.</div>
    </div>
  </div>
</div>

<!-- ADMIN PROFILE -->
<div class="admin-overlay" id="adminProfile">
  <div class="admin-inner">
    <div class="admin-bar"><h1>&#9881; Admin profile</h1><button class="admin-back" onclick="closeAdmin()">&larr; Back to dashboard</button></div>

    <div class="prof-section">
      <h3><span class="prof-num">1</span> Add a solicitation survey</h3>
      <p class="sec-sub">When a new solicitation survey is deployed in Pendo, add it here. Fill the fields, generate the block, and paste it into the <code>surveys</code> array in <code>surveys.json</code> in the repo, then commit. Next refresh, its card goes live and its interested users flow into the queue.</p>
      <div class="field-row">
        <div class="field"><label>Pendo guide ID <span class="hint">?<span class="hint-pop">The guide's ID in Pendo (the long string in the guide URL, e.g. rILFx33CEJlliM0_2euuyYzqhFY). This is how the dashboard knows which survey to pull.</span></span></label><input type="text" id="svId" placeholder="rILFx..." /></div>
        <div class="field"><label>Product area <span class="hint">?<span class="hint-pop">The product area this survey belongs to, exactly as you want it shown on its card (e.g. "Listings" or "Ads / Boost").</span></span></label><input type="text" id="svArea" placeholder="Listings" /></div>
        <div class="field" style="flex:0 0 150px;"><label>Interested value <span class="hint">?<span class="hint-pop">Which poll answer counts as "interested". For all current solicitation surveys this is 1 (the Reporting Suite pattern). Leave as 1 unless a survey differs.</span></span></label><input type="number" id="svVal" value="1" /></div>
        <button class="prof-btn" onclick="genSurvey()">Generate block</button>
      </div>
      <div class="gen-out" id="svOut" style="display:none">
        <div class="code-block"><button class="copy-btn" onclick="copyBlock('svBlock',this)">Copy</button><pre id="svBlock"></pre></div>
        <p class="sec-sub" style="margin-top:10px">Paste this object into the <code>surveys</code> array in <code>surveys.json</code> and commit.</p>
      </div>
    </div>

    <div class="prof-section">
      <h3><span class="prof-num">2</span> Live surveys</h3>
      <p class="sec-sub">Surveys currently pulling data from Pendo.</p>
      <div id="liveSurveys"></div>
    </div>

    <div class="prof-section">
      <h3><span class="prof-num">3</span> Change admin password</h3>
      <p class="sec-sub">Type a new password to get its hash, then paste the line over the <code>ADMIN_PW_SHA256</code> constant near the top of this file's script and re-deploy. <span class="hint">?<span class="hint-pop">The password is stored only as a SHA-256 hash in the page, never in plain text. Changing it requires editing the file and re-deploying, since a hosted static page can't save settings by itself.</span></span></p>
      <div class="field-row">
        <div class="field"><label>New password</label><input type="text" id="newPw" placeholder="choose a strong password" /></div>
        <button class="prof-btn secondary" onclick="hashNewPw()">Get hash</button>
      </div>
      <div class="gen-out" id="pwOut" style="display:none"><div class="code-block"><button class="copy-btn" onclick="copyBlock('pwBlock',this)">Copy</button><pre id="pwBlock"></pre></div></div>
    </div>

    <div class="prof-section">
      <h3><span class="prof-num">4</span> How data refreshes</h3>
      <p class="sec-sub">This dashboard reads <code>dashboard_data.json</code>, which a GitHub Action rebuilds from Pendo on a schedule. User levels (Administrator / Manager / User) come straight from Pendo, so there is nothing to refresh manually. To change how often it updates, edit the cron in <code>.github/workflows/refresh.yml</code>.</p>
    </div>
  </div>
</div>

<!-- DRILL -->
<div class="drill-overlay" id="drillOverlay" onclick="if(event.target===this)closeDrill()">
  <div class="drill">
    <div class="drill-head"><div><div class="drill-title" id="drillTitle">—</div><div class="drill-sub" id="drillSub">—</div></div><button class="drill-close" onclick="closeDrill()">&times;</button></div>
    <div class="drill-body">
      <div class="drill-section-title">Conversion funnel</div>
      <div class="funnel" id="drillFunnel"></div>
      <div class="drill-section-title">Interested by user level</div>
      <div class="level-break" id="drillLevels"></div>
      <div class="drill-section-title">Accounts with multiple interested users</div>
      <ul class="repeat-list" id="drillRepeat"></ul>
    </div>
  </div>
</div>

<script>
  const DATA_URL = "dashboard_data.json"; // same-folder; the Action commits this
  const ADMIN_PW_SHA256 = "__PWHASH__";
  let DATA = null, adminAuthed = false, activeLevel = null, activeSla = 'all';
  const LEVELS = ["Administrator","Manager","User"];
  const LEVEL_COLOR = { "Administrator":"#213B61", "Manager":"#29CC91", "User":"#C9CED6", "Unknown":"#9AA0AB" };
  const LEVEL_DESC = {
    "Administrator":"Account-wide decision maker. Frame around portfolio ROI, rollout, and governance.",
    "Manager":"Runs locations/groups day to day. Frame around the reports they use weekly and time saved.",
    "User":"Baseline access. Frame around the one task they were doing; keep it short and concrete."
  };

  // theme
  function setTheme(m){ document.documentElement.setAttribute('data-theme',m); try{localStorage.setItem('soci-theme',m);}catch(e){} document.querySelectorAll('.theme-btn').forEach(b=>b.classList.toggle('active',b.dataset.mode===m)); }
  document.querySelectorAll('.theme-btn').forEach(b=>b.addEventListener('click',()=>setTheme(b.dataset.mode)));
  (function(){ let s='auto'; try{s=localStorage.getItem('soci-theme')||'auto';}catch(e){} setTheme(s); })();

  function pct(n,d){ return d? Math.round(n/d*100):0; }

  function renderKpis(){
    const t=DATA.total_interested, red=(DATA.sla_counts.red||0);
    document.getElementById('goalText').innerHTML = t? `No customer who raises their hand goes un-contacted. Right now <b>${red} of ${t}</b> interested customers are past the 30-day follow-up window.` : 'No customer who raises their hand goes un-contacted.';
    const rs = DATA.per_area[Object.keys(DATA.per_area)[0]] || {};
    document.getElementById('kpiRow').innerHTML = `
      <div class="kpi"><div class="kpi-label">Awaiting follow-up</div><div class="kpi-value alert">${t}</div><div class="kpi-foot">across ${DATA.live_count} live area(s)</div></div>
      <div class="kpi"><div class="kpi-label">Oldest unactioned</div><div class="kpi-value warn">${DATA.oldest_age}<span style="font-size:14px;color:var(--muted)">d</span></div><div class="kpi-foot">since first interest</div></div>
      <div class="kpi"><div class="kpi-label">Breached SLA</div><div class="kpi-value alert">${DATA.sla_counts.red||0}</div><div class="kpi-foot">over 30 days</div></div>
      <div class="kpi"><div class="kpi-label">Areas live</div><div class="kpi-value">${DATA.live_count}<span style="font-size:16px;color:var(--muted)">/${DATA.live_count+DATA.planned_count}</span></div><div class="kpi-foot">+${DATA.planned_count} planned</div></div>
      <div class="kpi"><div class="kpi-label">12-mo responses</div><div class="kpi-value">${(rs.responses_12mo||0).toLocaleString()}</div><div class="kpi-foot">${(rs.views_12mo||0).toLocaleString()} views</div></div>`;
  }
  function renderLevels(){
    const lc=DATA.level_counts, t=DATA.total_interested||1;
    document.getElementById('levelPanel').innerHTML = LEVELS.map(lvl=>`
      <div class="level-card" data-level="${lvl}" onclick="filterByLevel('${lvl}',this)">
        <div class="level-bar" style="background:${LEVEL_COLOR[lvl]}"></div>
        <div class="level-name">${lvl}</div>
        <div class="level-count" style="color:${LEVEL_COLOR[lvl]}">${lc[lvl]||0}</div>
        <div class="level-desc">${LEVEL_DESC[lvl]}</div>
        <div class="level-pct">${pct(lc[lvl]||0,t)}% of backlog</div>
      </div>`).join('');
  }
  function renderAnomaly(){
    const t=DATA.total_interested, red=(DATA.sla_counts.red||0);
    const el=document.getElementById('anomaly');
    if(t && red){ el.style.display='flex'; document.getElementById('anomalyText').innerHTML = `<b>Anomaly:</b> ${red} of ${t} interested contacts (${pct(red,t)}%) have breached the 30-day SLA. The collection mechanism is healthy; follow-up is the gap.`; }
    else el.style.display='none';
  }
  function renderSla(){
    const s=DATA.sla_counts, t=DATA.total_interested||1, g=s.green||0,a=s.amber||0,r=s.red||0;
    document.getElementById('slaStrip').innerHTML = `
      <div class="sla-bar-card"><div class="sla-bar-track">
        ${g?`<div class="sla-seg green" style="width:${g/t*100}%">${g}</div>`:''}
        ${a?`<div class="sla-seg amber" style="width:${a/t*100}%">${a}</div>`:''}
        ${r?`<div class="sla-seg red" style="width:${r/t*100}%">${r}</div>`:''}
      </div><div class="sla-legend"><span><span class="ldot green"></span>On time (&lt;7d)</span><span><span class="ldot amber"></span>At risk (7-30d)</span><span><span class="ldot red"></span>Breached (&gt;30d)</span></div></div>
      <div class="sla-stat"><div class="sla-stat-val green">${g}</div><div class="sla-stat-lbl">Within SLA</div></div>
      <div class="sla-stat"><div class="sla-stat-val amber">${a}</div><div class="sla-stat-lbl">At risk</div></div>
      <div class="sla-stat"><div class="sla-stat-val red">${r}</div><div class="sla-stat-lbl">Breached</div></div>`;
  }
  function renderAreas(filter){
    filter=filter||'all';
    document.getElementById('areaTitle').textContent=`Product areas · ${DATA.live_count} live, ${DATA.planned_count} planned`;
    document.getElementById('gridControls').innerHTML = `
      <button class="filter-chip ${filter==='all'?'active':''}" onclick="renderAreas('all')">All (${DATA.live_count+DATA.planned_count})</button>
      <button class="filter-chip ${filter==='live'?'active':''}" onclick="renderAreas('live')">Live (${DATA.live_count})</button>
      <button class="filter-chip ${filter==='planned'?'active':''}" onclick="renderAreas('planned')">Planned (${DATA.planned_count})</button>`;
    document.getElementById('areaGrid').innerHTML = DATA.areas.filter(a=> filter==='all'||a.status===filter).map(a=>{
      if(a.status==='live'){ const m=DATA.per_area[a.name]||{};
        return `<button class="area-card area-live" onclick="openDrill('${a.name.replace(/'/g,"\\'")}')">
          <div class="area-top"><span class="area-status-dot live"></span><span class="area-status-label live">LIVE</span></div>
          <div class="area-name">${a.name}</div>
          <div class="area-metrics"><div class="am"><span class="am-val">${m.interested||0}</span><span class="am-lbl">interested</span></div><div class="am"><span class="am-val">${(m.responses_12mo||0).toLocaleString()}</span><span class="am-lbl">responses</span></div></div>
          <div class="area-foot">click to drill in</div></button>`;
      }
      return `<div class="area-card area-planned"><div class="area-top"><span class="area-status-dot planned"></span><span class="area-status-label planned">PLANNED</span></div>
        <div class="area-name">${a.name}</div>
        <div class="area-metrics planned-metrics"><div class="am"><span class="am-val">—</span><span class="am-lbl">interested</span></div><div class="am"><span class="am-val">—</span><span class="am-lbl">responses</span></div></div>
        <div class="area-foot">Deploy pending · add Pendo guide ID</div></div>`;
    }).join('');
  }
  function renderQueue(){
    document.getElementById('queueFilters').innerHTML = `
      <span class="qf ${activeSla==='all'?'active':''}" onclick="setSla('all')">All ${DATA.total_interested}</span>
      <span class="qf ${activeSla==='red'?'active':''}" onclick="setSla('red')">Breached ${DATA.sla_counts.red||0}</span>
      <span class="qf ${activeSla==='amber'?'active':''}" onclick="setSla('amber')">At risk ${DATA.sla_counts.amber||0}</span>`;
    const body=document.getElementById('queueBody');
    if(!DATA.contacts.length){ body.innerHTML=`<tr><td colspan="5"><div class="empty-note">No interested responses yet. The next refresh will populate this from Pendo.</div></td></tr>`; return; }
    body.innerHTML = DATA.contacts.map(c=>{
      const lvl=c.user_level||'User', color=LEVEL_COLOR[lvl]||'#C9CED6', txt=(lvl==='User')?'#0C0C0D':'#fff';
      const opener = c.suggested_opener? `<div class="opener">${c.suggested_opener}</div>`:'';
      return `<tr class="q-row" data-sla="${c.sla}" data-level="${lvl}">
        <td class="q-date">${c.date}</td>
        <td class="q-visitor">${c.visitor}</td>
        <td class="q-account">${c.account}${opener}</td>
        <td><span class="level-tag" style="background:${color};color:${txt}">${lvl}</span></td>
        <td><span class="sla-pill sla-${c.sla}">${c.age_days}d</span></td></tr>`;
    }).join('');
    applyQueueFilters();
  }
  function setSla(m){ activeSla=m; renderQueue(); }
  function filterByLevel(lvl,el){ if(activeLevel===lvl){activeLevel=null; el.classList.remove('active');} else { activeLevel=lvl; document.querySelectorAll('.level-card').forEach(c=>c.classList.toggle('active',c.dataset.level===lvl)); } applyQueueFilters(); }
  function applyQueueFilters(){ document.querySelectorAll('#queueBody .q-row').forEach(r=>{ const s=activeSla==='all'||r.dataset.sla===activeSla; const l=!activeLevel||r.dataset.level===activeLevel; r.style.display=(s&&l)?'':'none'; }); }

  function openDrill(area){
    const m=DATA.per_area[area]; if(!m) return;
    document.getElementById('drillTitle').textContent=area;
    document.getElementById('drillSub').textContent=`Guide ${m.guide_id||''}`;
    const v=m.views_12mo||0, resp=m.responses_12mo||0, intr=m.interested||0;
    document.getElementById('drillFunnel').innerHTML = `
      <div class="funnel-step"><div class="funnel-fill" style="width:100%"></div><span class="funnel-lbl">Views</span><span class="funnel-val">${v.toLocaleString()}</span></div>
      <div class="funnel-step"><div class="funnel-fill" style="width:${v?Math.max(resp/v*100,2):0}%"></div><span class="funnel-lbl">Responses</span><span class="funnel-val">${resp.toLocaleString()}</span></div>
      <div class="funnel-step"><div class="funnel-fill" style="width:${v?Math.max(intr/v*100,1):0}%"></div><span class="funnel-lbl">Interested</span><span class="funnel-val">${intr.toLocaleString()}</span></div>`;
    const areaContacts=DATA.contacts.filter(c=>c.area===area);
    const lc={}; LEVELS.forEach(l=>lc[l]=0); areaContacts.forEach(c=>{lc[c.user_level]=(lc[c.user_level]||0)+1;});
    const max=Math.max(...Object.values(lc),1);
    document.getElementById('drillLevels').innerHTML = LEVELS.map(l=>{const n=lc[l]||0; const txt=(l==='User')?'#0C0C0D':'#fff'; return `<div class="lb-row"><div class="lb-label">${l}</div><div class="lb-bar-track"><div class="lb-bar" style="width:${Math.max(n/max*100,6)}%;background:${LEVEL_COLOR[l]};color:${txt}">${n}</div></div></div>`;}).join('');
    document.getElementById('drillRepeat').innerHTML = (DATA.repeat_accounts||[]).length? DATA.repeat_accounts.map(([a,n])=>`<li><span>${a}</span><span style="font-family:'JetBrains Mono',monospace;color:var(--accent);font-weight:600">${n}</span></li>`).join('') : '<li style="color:var(--muted)">None yet</li>';
    document.getElementById('drillOverlay').classList.add('open');
  }
  function closeDrill(){ document.getElementById('drillOverlay').classList.remove('open'); }

  // admin
  async function sha256hex(str){ if(window.crypto&&window.crypto.subtle){ const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(str)); return Array.from(new Uint8Array(b)).map(x=>x.toString(16).padStart(2,'0')).join(''); } return null; }
  function openAdmin(){ if(adminAuthed){ showView('adminProfile'); renderProfile(); } else { showView('adminLogin'); setTimeout(()=>{const p=document.getElementById('adminPw'); if(p)p.focus();},50); } }
  function closeAdmin(){ document.querySelectorAll('.admin-overlay').forEach(o=>o.classList.remove('open')); }
  function showView(id){ document.querySelectorAll('.admin-overlay').forEach(o=>o.classList.remove('open')); document.getElementById(id).classList.add('open'); }
  async function tryLogin(){ const err=document.getElementById('loginErr'); const h=await sha256hex(document.getElementById('adminPw').value); if(h===null){err.textContent='Login needs the hosted (https) dashboard.';return;} if(h===ADMIN_PW_SHA256){adminAuthed=true;document.getElementById('adminPw').value='';err.textContent='';showView('adminProfile');renderProfile();} else err.textContent='Incorrect password.'; }
  function renderProfile(){
    const live=DATA.areas.filter(a=>a.status==='live');
    document.getElementById('liveSurveys').innerHTML = live.length? live.map(a=>{const m=DATA.per_area[a.name]||{}; return `<div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--hairline-soft);font-size:13px"><span><b>${a.name}</b> <span style="font-family:'JetBrains Mono',monospace;color:var(--muted);font-size:11px">${m.guide_id||''}</span></span><span style="font-family:'JetBrains Mono',monospace;color:var(--accent)">${m.interested||0} interested</span></div>`;}).join('') : '<p class="sec-sub">None live yet.</p>';
  }
  function genSurvey(){
    const id=document.getElementById('svId').value.trim(), area=document.getElementById('svArea').value.trim(), val=parseInt(document.getElementById('svVal').value,10)||1;
    const obj={guide_id:id, area:area, status:"live", interested_poll_value:val};
    document.getElementById('svBlock').textContent=JSON.stringify(obj,null,2);
    document.getElementById('svOut').style.display='block';
  }
  async function hashNewPw(){ const pw=document.getElementById('newPw').value; if(!pw)return; const h=await sha256hex(pw); document.getElementById('pwBlock').textContent=(h===null)?'Hashing needs the hosted (https) dashboard.':'const ADMIN_PW_SHA256 = "'+h+'";'; document.getElementById('pwOut').style.display='block'; }
  function copyBlock(id,btn){ const text=document.getElementById(id).textContent; const done=()=>{const o=btn.textContent;btn.textContent='Copied';btn.classList.add('copied');setTimeout(()=>{btn.textContent=o;btn.classList.remove('copied');},1400);}; if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(done).catch(()=>fb(text,done));} else fb(text,done); }
  function fb(text,done){ const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select(); try{document.execCommand('copy');done();}catch(e){} document.body.removeChild(ta); }
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'){closeAdmin();closeDrill();} });

  function renderAll(){ if(!DATA)return; renderKpis(); renderLevels(); renderAnomaly(); renderSla(); renderAreas('all'); renderQueue(); document.getElementById('updatedTs').textContent=DATA.generated_at||'—'; document.getElementById('footMeta').textContent=`Live solicitation-survey monitor · ${DATA.live_count} live, ${DATA.planned_count} planned · data from Pendo · generated ${DATA.generated_at||''}`; }

  async function load(){
    try{ const r=await fetch(DATA_URL,{cache:'no-store'}); if(r.ok){ DATA=await r.json(); renderAll(); const l=document.getElementById('liveLabel'); l.textContent='Live · synced'; setTimeout(()=>l.textContent='Live',1200);} }
    catch(e){ console.warn('load failed',e); if(!DATA){ document.getElementById('kpiRow').innerHTML='<div class="empty-note">Could not load dashboard_data.json yet.</div>'; } }
  }
  load();
  setInterval(load, 60000);
</script>
</body>
</html>'''

HTML = HTML.replace("__PWHASH__", PW_HASH)
with open("index.html", "w") as f:
    f.write(HTML)
print(f"index.html written: {len(HTML):,} chars")
