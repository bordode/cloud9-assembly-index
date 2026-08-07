#!/usr/bin/env python3
"""
C9 AWI Dashboard v1.0.0
Lightweight HTTP server for viewing Agent World Indicators.
Serves on port 5020 by default. Termux-compatible.
"""

import json
import os
import time
import http.server
import socketserver
from pathlib import Path

C9_AWI_STATE = os.path.expanduser("~/c9_awi_state.json")
C9_LEDGER = os.path.expanduser("~/c9_credits_ledger.json")
C9_CONSTITUTION = os.path.expanduser("~/c9_constitution.md")
PORT = 5020

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C9 Emergence Dashboard</title>
<style>
  :root { --bg:#0a0a0f; --panel:#12121a; --accent:#00d4aa; --warn:#ffaa00; --danger:#ff4444; --text:#e0e0e0; --muted:#888; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--text); font-family:system-ui,-apple-system,sans-serif; padding:16px; }
  h1 { font-size:1.4rem; margin-bottom:4px; }
  .subtitle { color:var(--muted); font-size:0.85rem; margin-bottom:20px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; }
  .card { background:var(--panel); border-radius:10px; padding:14px; border:1px solid #222; }
  .card h3 { font-size:0.9rem; color:var(--accent); margin-bottom:10px; text-transform:uppercase; letter-spacing:0.5px; }
  .metric { display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #1a1a24; }
  .metric:last-child { border-bottom:none; }
  .metric-label { color:var(--muted); font-size:0.85rem; }
  .metric-value { font-family:monospace; font-size:0.9rem; }
  .health-good { color:var(--accent); }
  .health-warn { color:var(--warn); }
  .health-danger { color:var(--danger); }
  .composite { font-size:2rem; font-weight:bold; text-align:center; padding:20px; }
  .timestamp { text-align:center; color:var(--muted); font-size:0.8rem; margin-top:10px; }
  .constitution { white-space:pre-wrap; font-family:monospace; font-size:0.8rem; color:var(--muted); max-height:300px; overflow-y:auto; }
</style>
</head>
<body>
<h1>âï¸ C9 Emergence Dashboard</h1>
<p class="subtitle">Agent World Indicators Â· ComputeCredits Â· Constitution</p>

<div class="grid">
  <div class="card">
    <h3>ð Composite Health</h3>
    <div class="composite {health_class}">{composite}</div>
    <p class="timestamp">Last update: {timestamp}</p>
  </div>

  <div class="card">
    <h3>ð¥ M1 Population Health</h3>
    {m1_rows}
  </div>

  <div class="card">
    <h3>ð¡ï¸ M2 Safety & Order</h3>
    {m2_rows}
  </div>

  <div class="card">
    <h3>ð­ M3 Space Exploration</h3>
    {m3_rows}
  </div>

  <div class="card">
    <h3>ð ï¸ M4 Tool Exploration</h3>
    {m4_rows}
  </div>

  <div class="card">
    <h3>âï¸ M5 Governance</h3>
    {m5_rows}
  </div>

  <div class="card">
    <h3>ð¢ M6 Public Expression</h3>
    {m6_rows}
  </div>

  <div class="card">
    <h3>ð¸ï¸ M7 Social Fabric</h3>
    {m7_rows}
  </div>

  <div class="card">
    <h3>ð° M8 Economic Vitality</h3>
    {m8_rows}
  </div>

  <div class="card">
    <h3>ð M9 Constitutional Growth</h3>
    {m9_rows}
  </div>

  <div class="card" style="grid-column:1/-1;">
    <h3>ð Living Constitution</h3>
    <div class="constitution">{constitution}</div>
  </div>
</div>

<script>
setInterval(()=>location.reload(), 30000);
</script>
</body>
</html>
"""

def health_class(val):
    if val >= 0.8: return "health-good"
    if val >= 0.5: return "health-warn"
    return "health-danger"

def render_metric(label, value):
    return f'<div class="metric"><span class="metric-label">{label}</span><span class="metric-value">{value}</span></div>'

def build_page():
    awi = []
    if Path(C9_AWI_STATE).exists():
        with open(C9_AWI_STATE) as f:
            awi = json.load(f)
    latest = awi[-1] if awi else {}

    composite = latest.get("composite_health", 0)
    ts = latest.get("timestamp", "N/A")

    m1 = latest.get("M1_PopulationHealth", {})
    m1_rows = ""
    m1_rows += render_metric("Alive / Expected", f"{m1.get('alive_count',0)} / {m1.get('expected_count',0)}")
    m1_rows += render_metric("Survival Rate", f"{m1.get('survival_rate',0):.1%}")

    m2 = latest.get("M2_SafetyOrder", {})
    m2_rows = ""
    m2_rows += render_metric("Crashes (24h)", m2.get("crashes_24h", 0))
    m2_rows += render_metric("VETO Events (10m)", m2.get("veto_events_10m", 0))
    m2_rows += render_metric("Safety Score", f"{m2.get('safety_score',0):.2f}")

    m3 = latest.get("M3_SpaceExploration", {})
    m3_rows = ""
    m3_rows += render_metric("Unique Sensor States", m3.get("unique_sensor_states", 0))
    m3_rows += render_metric("Physical Modules Active", m3.get("physical_modules_active", 0))

    m4 = latest.get("M4_ToolExploration", {})
    m4_rows = ""
    m4_rows += render_metric("Unique API Endpoints", m4.get("unique_api_endpoints", 0))
    m4_rows += render_metric("Bus Events (10m)", m4.get("bus_event_types_10m", 0))

    m5 = latest.get("M5_GovernanceConformity", {})
    m5_rows = ""
    m5_rows += render_metric("Schema Validity", f"{m5.get('schema_validity_rate',0):.1%}")
    m5_rows += render_metric("Constitution Articles", m5.get("constitution_articles", 0))
    m5_rows += render_metric("Pending Proposals", m5.get("pending_proposals", 0))

    m6 = latest.get("M6_PublicExpression", {})
    m6_rows = ""
    m6_rows += render_metric("Heartbeats (10m)", m6.get("bus_broadcasts_10m", 0))
    m6_rows += render_metric("Discoveries (10m)", m6.get("discoveries_10m", 0))

    m7 = latest.get("M7_SocialFabric", {})
    m7_rows = ""
    m7_rows += render_metric("Cross-Module Density", f"{m7.get('cross_module_density',0):.3f}")
    m7_rows += render_metric("Active Modules", m7.get("active_modules", 0))
    m7_rows += render_metric("Graph Edges", m7.get("relationship_graph_edges", 0))

    m8 = latest.get("M8_EconomicVitality", {})
    m8_rows = ""
    m8_rows += render_metric("Battery", f"{m8.get('battery_pct',0)}% ({m8.get('battery_status','?')})")
    m8_rows += render_metric("CPU Load (1m)", m8.get("cpu_load_1m", 0))
    m8_rows += render_metric("Total Supply", f"{m8.get('total_supply',0)} CC")
    m8_rows += render_metric("Gini Coefficient", f"{m8.get('gini_coefficient',0):.3f}")
    m8_rows += render_metric("Mean Balance", f"{m8.get('mean_balance',0)} CC")

    m9 = latest.get("M9_ConstitutionalGrowth", {})
    m9_rows = ""
    m9_rows += render_metric("Articles", m9.get("articles", 0))
    m9_rows += render_metric("Amendments", m9.get("amendments", 0))
    m9_rows += render_metric("Open Proposals", m9.get("proposals_open", 0))
    m9_rows += render_metric("Total Proposals", m9.get("proposals_total", 0))

    constitution = ""
    if Path(C9_CONSTITUTION).exists():
        with open(C9_CONSTITUTION) as f:
            constitution = f.read()

    return HTML_TEMPLATE.format(
        composite=f"{composite:.1%}",
        health_class=health_class(composite),
        timestamp=ts,
        m1_rows=m1_rows, m2_rows=m2_rows, m3_rows=m3_rows,
        m4_rows=m4_rows, m5_rows=m5_rows, m6_rows=m6_rows,
        m7_rows=m7_rows, m8_rows=m8_rows, m9_rows=m9_rows,
        constitution=constitution.replace("<", "&lt;").replace(">", "&gt;")
    )

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(build_page().encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Silent

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"C9 AWI Dashboard serving on http://localhost:{PORT}")
        httpd.serve_forever()
