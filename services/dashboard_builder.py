"""
services/dashboard_builder.py

Tool 3 — dashboard_builder
  Input : JSON string — list of enriched panel specs
          (output of sql_executor, one entry per KPI)
  Output: JSON string  { "html": "<full self-contained HTML>", "panel_count": N }

The generated HTML is completely self-contained:
  - Chart.js loaded from cdnjs CDN
  - KPI stat cards for single-value panels
  - Chart canvases for bar / line / pie / doughnut panels
  - Clean, readable layout — dark-mode aware via CSS variables
  - No external dependencies beyond Chart.js
"""

from __future__ import annotations

import json
import re
from services.kpi_planner import _strip_fences


# Chart.js color palette — cycles across panels
_PALETTE = [
    ("rgba(127,119,221,0.75)", "rgba(127,119,221,1)"),   # purple
    ("rgba(29,158,117,0.75)",  "rgba(29,158,117,1)"),    # teal
    ("rgba(186,117,23,0.75)",  "rgba(186,117,23,1)"),    # amber
    ("rgba(216,90,48,0.75)",   "rgba(216,90,48,1)"),     # coral
    ("rgba(55,138,221,0.75)",  "rgba(55,138,221,1)"),    # blue
    ("rgba(99,153,34,0.75)",   "rgba(99,153,34,1)"),     # green
    ("rgba(212,83,126,0.75)",  "rgba(212,83,126,1)"),    # pink
]


def build_dashboard(panels_json: str) -> str:
    """
    Assemble a self-contained HTML dashboard from enriched panel specs.
    Called by the dashboard_builder LangChain Tool.
    Returns JSON: { "html": "...", "panel_count": N }
    """
    try:
        clean = _strip_fences(panels_json)
        panels = json.loads(clean)
        if not isinstance(panels, list):
            panels = [panels]
    except Exception as exc:
        return json.dumps({"error": f"Invalid panels JSON: {exc}"})

    # Split into stat cards (single value) and chart panels
    stat_panels   = [p for p in panels if p.get("chart_type") == "stat" and not p.get("error")]
    chart_panels  = [p for p in panels if p.get("chart_type") != "stat" and not p.get("error")]
    failed_panels = [p for p in panels if p.get("error")]

    html = _render_html(stat_panels, chart_panels, failed_panels)

    return json.dumps({"html": html, "panel_count": len(panels)})


# ── HTML renderer ──────────────────────────────────────────────

def _render_html(
    stat_panels: list,
    chart_panels: list,
    failed_panels: list,
) -> str:
    stat_cards_html  = _render_stat_cards(stat_panels)
    chart_blocks_html = _render_chart_blocks(chart_panels)
    chart_js_configs  = _build_chart_js_configs(chart_panels)
    failed_html       = _render_failed(failed_panels)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KPI Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:       #f8f8f6;
    --surface:  #ffffff;
    --border:   #e4e3dc;
    --text-1:   #1a1a18;
    --text-2:   #5f5e5a;
    --text-3:   #888780;
    --radius:   12px;
    --shadow:   0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
  }}



  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text-1);
    padding: 32px 24px;
    min-height: 100vh;
  }}

  h1 {{
    font-size: 20px;
    font-weight: 500;
    color: var(--text-1);
    margin-bottom: 24px;
    letter-spacing: -0.01em;
  }}

  .section-label {{
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-3);
    margin-bottom: 12px;
  }}

  /* ── stat cards ── */
  .stat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
  }}

  .stat-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 20px 18px;
    box-shadow: var(--shadow);
  }}

  .stat-card .label {{
    font-size: 12px;
    color: var(--text-2);
    margin-bottom: 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .stat-card .value {{
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.03em;
    line-height: 1;
    color: var(--text-1);
  }}

  .stat-card .sub {{
    font-size: 11px;
    color: var(--text-3);
    margin-top: 6px;
  }}

  /* ── chart panels ── */
  .chart-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
  }}

  .chart-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
  }}

  .chart-card .chart-title {{
    font-size: 14px;
    font-weight: 500;
    color: var(--text-1);
    margin-bottom: 4px;
  }}

  .chart-card .chart-desc {{
    font-size: 12px;
    color: var(--text-3);
    margin-bottom: 16px;
    line-height: 1.4;
  }}

  .chart-card canvas {{
    width: 100% !important;
    max-height: 280px;
  }}

  /* ── failed panels ── */
  .failed-list {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 24px;
  }}

  .failed-item {{
    font-size: 12px;
    color: var(--text-3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
  }}

  .failed-item strong {{ color: var(--text-2); }}
</style>
</head>
<body>
<h1>KPI Dashboard</h1>

{stat_cards_html}
{chart_blocks_html}
{failed_html}

<script>
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
Chart.defaults.font.size = 12;
//Chart.defaults.color = getComputedStyle(document.documentElement)
// .getPropertyValue('--text-2').trim() || '#5f5e5a';

// Force light theme for charts
Chart.defaults.color = '#5f5e5a';          // axis + labels
Chart.defaults.borderColor = '#e4e3dc';   // grid lines
Chart.defaults.backgroundColor = '#ffffff';
const configs = {chart_js_configs};

configs.forEach(function(cfg) {{
  const canvas = document.getElementById(cfg.id);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  new Chart(ctx, cfg.config);
}});
</script>
</body>
</html>"""


def _render_stat_cards(panels: list) -> str:
    if not panels:
        return ""

    cards = []
    for i, panel in enumerate(panels):
        rows = panel.get("rows", [])
        value = "—"
        if rows and rows[0]:
            raw = rows[0][0]
            value = _fmt_number(raw)

        color = _PALETTE[i % len(_PALETTE)][1]
        cards.append(f"""
  <div class="stat-card" style="border-top: 3px solid {color}">
    <div class="label">{_esc(panel.get('kpi_name', panel.get('keyword', 'KPI')))}</div>
    <div class="value">{value}</div>
    <div class="sub">{_esc(panel.get('description', ''))}</div>
  </div>""")

    return f"""<div class="section-label">Key metrics</div>
<div class="stat-grid">{''.join(cards)}
</div>"""


def _render_chart_blocks(panels: list) -> str:
    if not panels:
        return ""

    blocks = []
    for panel in panels:
        pid = _panel_id(panel)
        blocks.append(f"""
  <div class="chart-card">
    <div class="chart-title">{_esc(panel.get('kpi_name', panel.get('keyword', 'Chart')))}</div>
    <div class="chart-desc">{_esc(panel.get('description', ''))}</div>
    <canvas id="{pid}"></canvas>
  </div>""")

    return f"""<div class="section-label">Charts</div>
<div class="chart-grid">{''.join(blocks)}
</div>"""


def _build_chart_js_configs(panels: list) -> str:
    """Return a JS array literal of {{id, config}} objects."""
    entries = []
    for i, panel in enumerate(panels):
        pid = _panel_id(panel)
        chart_type = _map_chart_type(panel.get("chart_type", "bar"))
        rows = panel.get("rows", [])
        columns = panel.get("columns", [])

        if not rows:
            continue

        labels, datasets = _extract_chart_data(rows, columns, chart_type, i)

        # Chart.js config
        config = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": datasets,
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
                "plugins": {
                    "legend": {
                        "display": chart_type in ("pie", "doughnut"),
                        "position": "bottom",
                    },
                    "title": {"display": False},
                },
                "scales": {} if chart_type in ("pie", "doughnut") else {
                    "x": {
                        "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 12},
                        "grid": {"display": False},
                    },
                    "y": {
                        "beginAtZero": True,
                        "ticks": {"maxTicksLimit": 6},
                        "grid": {"color": "rgba(136,135,128,0.15)"},
                    },
                },
            },
        }

        entries.append(json.dumps({"id": pid, "config": config}, default=str))

    return f"[{', '.join(entries)}]"


def _extract_chart_data(
    rows: list,
    columns: list,
    chart_type: str,
    palette_idx: int,
) -> tuple[list, list]:
    """
    Convert rows + columns → Chart.js labels + datasets.
    Handles 2-column (label, value) and multi-column (label, val1, val2…) data.
    """
    if not rows:
        return [], []

    n_cols = len(rows[0])
    fill, border = _PALETTE[palette_idx % len(_PALETTE)]

    if n_cols == 1:
        # Single-column: treat row index as label, value as data
        labels = [str(i + 1) for i in range(len(rows))]
        values = [_to_num(rows[i][0]) for i in range(len(rows))]
        datasets = [{"label": columns[0] if columns else "Value",
                     "data": values,
                     "backgroundColor": fill,
                     "borderColor": border,
                     "borderWidth": 1.5}]

    elif n_cols == 2:
        labels = [str(r[0])[:30] for r in rows]
        values = [_to_num(r[1]) for r in rows]

        if chart_type in ("pie", "doughnut"):
            # Multi-color slices
            colors = [_PALETTE[j % len(_PALETTE)][0] for j in range(len(labels))]
            datasets = [{"data": values, "backgroundColor": colors, "borderWidth": 1}]
        else:
            datasets = [{"label": columns[1] if len(columns) > 1 else "Value",
                         "data": values,
                         "backgroundColor": fill,
                         "borderColor": border,
                         "borderWidth": 1.5,
                         "fill": chart_type == "line",
                         "tension": 0.3 if chart_type == "line" else 0}]

    else:
        # Multi-column: first col = labels, rest = datasets
        labels = [str(r[0])[:30] for r in rows]
        datasets = []
        for col_i in range(1, n_cols):
            p = _PALETTE[(palette_idx + col_i - 1) % len(_PALETTE)]
            datasets.append({
                "label": columns[col_i] if len(columns) > col_i else f"Series {col_i}",
                "data": [_to_num(r[col_i]) for r in rows],
                "backgroundColor": p[0],
                "borderColor": p[1],
                "borderWidth": 1.5,
                "tension": 0.3 if chart_type == "line" else 0,
            })

    return labels, datasets


def _render_failed(panels: list) -> str:
    if not panels:
        return ""
    items = "".join(
        f'<div class="failed-item"><strong>{_esc(p.get("kpi_name", p.get("keyword", "?")))}:</strong>'
        f' {_esc(str(p.get("error", "unknown error")))}</div>'
        for p in panels
    )
    return f'<div class="failed-list">{items}</div>'


# ── tiny helpers ───────────────────────────────────────────────

def _panel_id(panel: dict) -> str:
    slug = re.sub(r"[^a-z0-9]", "_", panel.get("keyword", "panel").lower())
    return f"chart_{slug}_{id(panel) % 99999}"


def _map_chart_type(t: str) -> str:
    return {"bar": "bar", "line": "line", "pie": "pie",
            "doughnut": "doughnut", "stat": "bar"}.get(t, "bar")


def _to_num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _fmt_number(v) -> str:
    try:
        n = float(v)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        if n == int(n):
            return str(int(n))
        return f"{n:.2f}"
    except (TypeError, ValueError):
        return str(v)


def _esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))