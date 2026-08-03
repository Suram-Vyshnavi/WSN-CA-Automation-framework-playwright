""""
Combine individual per-feature behave reports into one executive QA dashboard.

The combined report has two layers:

  1. An *executive dashboard* (KPIs, execution info, module coverage, pivot
     tables, charts and failure analysis) built from the structured behave JSON
     reports in ``reports/json-report``.  This is the "single source of truth"
     view for stakeholders.

  2. The original per-feature ``behave_html_formatter`` / WFHTMLFormatter
     reports, each rendered in its own tab (CSS + JS + screenshots inlined) for
     detailed drill-down.

Everything is inlined into one self-contained HTML file so it works offline and
can be emailed as-is.  No external chart libraries are used; all charts are
pure inline SVG / CSS.
"""
import os
import re
import sys
import json
import glob
import html
import base64
import platform
import datetime
from pathlib import Path

# Company logo (embedded as a data URI so the report stays self-contained).
LOGO_CANDIDATES = [
    "files/Wadhwani_Foundation.jpg",
    "files/wadhwani_logo.png",
    "files/logo.png",
]

MODULE_ORDER = [
    "login",
    "homepage",
    "newuser",
]

MODULE_LABELS = {
    "login":    "Login",
    "homepage": "Homepage",
    "newuser":  "New User Journey",
}

# Maps behave feature names (from the JSON report) to module keys.
FEATURE_NAME_TO_MODULE = {
    "Login validation":    "login",
    "Homepage validation": "homepage",
    "NewUser":             "newuser",
}

# Test account used, mirroring utils/config.py.  Password intentionally NOT
# stored here — it is masked in the report.
CREDENTIALS = {
    #           (dev username,                   prod username)
    "student": ("ca-automation@yopmail.com", "ca-automation@yopmail.com"),
}

APP_URLS = {
    "prod": "https://web.careeradvisor.wadhwanifoundation.org/en",
    "dev":  "https://dev.careeradvisor.wadhwanifoundation.org/en",
}

STATUS_ICONS = {"passed": "✅", "failed": "❌", "error": "⚠️", "skipped": "⏭️"}


# ─────────────────────────────────────────────────────────────────────────────
# Behave HTML extraction (per-feature tabs) — unchanged behaviour
# ─────────────────────────────────────────────────────────────────────────────
def _extract_body_and_head(html_text: str):
    """Return (styles, scripts, body_html) from a behave HTML report."""
    styles = re.findall(r"<style[^>]*>(.*?)</style>", html_text, re.DOTALL | re.IGNORECASE)
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html_text, re.DOTALL | re.IGNORECASE)
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html_text, re.DOTALL | re.IGNORECASE)
    body_html = body_match.group(1).strip() if body_match else html_text
    return styles, scripts, body_html


def _namespace_body_ids(body_html: str, prefix: str) -> str:
    """Prefix element IDs and toggle targets to avoid cross-tab collisions."""

    def _replace_id_attr(match: re.Match) -> str:
        return f'id="{prefix}__{match.group(1)}"'

    def _replace_toggle_target(match: re.Match) -> str:
        quote = match.group(1)
        target = match.group(2)
        return f"Collapsible_toggle({quote}{prefix}__{target}{quote})"

    namespaced = re.sub(r'\bid="([^"]+)"', _replace_id_attr, body_html)
    namespaced = re.sub(
        r"Collapsible_toggle\((['\"])([^'\"]+)\1\)",
        _replace_toggle_target,
        namespaced,
    )
    return namespaced


def _remove_behave_title(body_html: str) -> str:
    return re.sub(
        r"<h1>\s*Behave\s+Test\s+Report\s*</h1>", "", body_html, flags=re.IGNORECASE
    )


# ─────────────────────────────────────────────────────────────────────────────
# Structured JSON parsing (the dashboard data source)
# ─────────────────────────────────────────────────────────────────────────────
def _categorize_failure(error_text: str) -> str:
    """Bucket an error message into a coarse failure category."""
    t = (error_text or "").lower()
    if not t:
        return "Unknown"
    if "timeout" in t:
        return "Timeout"
    if "assert" in t:
        return "Assertion / Validation"
    if any(k in t for k in ("wait_for", "to be visible", "locator", "no element", "not found", "selector")):
        return "Element Not Found"
    if any(k in t for k in ("net::", "navigation", "err_", "connection", "dns")):
        return "Navigation / Network"
    if "expect" in t:
        return "Assertion / Validation"
    return "Application / Other"


def _short_reason(error_text: str, category: str) -> str:
    """Extract a concise, technical 'Failure Reason' from a raw error/traceback."""
    if not error_text or not error_text.strip():
        return "No technical details were captured."

    lines = [ln.strip() for ln in error_text.splitlines() if ln.strip()]

    exc_line = ""
    for ln in reversed(lines):
        if re.match(r"^[\w\.]*(Error|Exception)\b", ln):
            exc_line = ln
            break

    if not exc_line:
        for ln in reversed(lines):
            if any(k in ln.lower() for k in ("assert", "expect", "timeout", "not found", "not visible")):
                exc_line = ln
                break

    chosen = exc_line or lines[-1]
    chosen = re.sub(r"\b[\w\.]+\.(\w+(?:Error|Exception))\b", r"\1", chosen)
    chosen = re.sub(r"^(\w+(?:Error|Exception))\s*:\s*", r"\1 – ", chosen)
    chosen = " ".join(chosen.split())
    if len(chosen) > 220:
        chosen = chosen[:217] + "…"
    return chosen


def _friendly_result(s: dict) -> tuple:
    """Return ``(outcome, failure_reason)`` in plain, business-readable language."""
    status = s.get("status")
    if status == "passed":
        return ("Passed as expected", "")
    if status == "skipped":
        return ("Not executed in this run", "")

    subject = re.sub(r"\s*validation\s*$", "", s.get("name", ""), flags=re.IGNORECASE).strip()
    subject = subject or s.get("name", "scenario")
    category = s.get("category") or _categorize_failure(s.get("error", ""))
    reason = _short_reason(s.get("error", ""), category)

    if status == "failed":
        outcome = {
            "Assertion / Validation":
                f"{subject} did not match the expected result — a validation check failed.",
            "Element Not Found":
                f"{subject} could not be verified because an expected item was not present on the page.",
            "Timeout":
                f"{subject} did not reach the expected state within the allowed time.",
            "Navigation / Network":
                f"{subject} could not be confirmed due to a page navigation or network problem.",
        }.get(category, f"{subject} did not produce the expected result.")
        return (outcome, reason)

    outcome = {
        "Timeout":
            f"The {subject} process could not be completed because the application did not respond in time.",
        "Element Not Found":
            f"The {subject} process could not be completed because an expected screen element was missing.",
        "Navigation / Network":
            f"The {subject} process could not be completed due to a connectivity or navigation issue.",
        "Assertion / Validation":
            f"The {subject} process stopped due to an unexpected validation error.",
    }.get(category, f"The {subject} process could not be completed due to a technical issue.")
    return (outcome, reason)


def _scenario_status(el: dict) -> str:
    status = (el.get("status") or "").lower()
    if status in ("passed", "failed", "error", "skipped", "untested"):
        return "skipped" if status == "untested" else status
    for step in el.get("steps", []):
        sstat = (step.get("result", {}) or {}).get("status", "")
        if sstat in ("failed", "error"):
            return sstat
    return "passed"


def load_failures(json_file: str) -> dict:
    """Load features/environment.py's failures.json (written in after_all), keyed by
    (feature name, scenario name).

    Steps that fail "softly" (caught and recorded by new_user_steps._run so the
    scenario keeps running instead of aborting) never show up as a failed step in
    behave's own JSON report - every step reports "passed" there - so
    load_modules() below has no error text to work with for those scenarios. This
    sidecar file is how the real failure reason (and screenshot path) recorded by
    the environment hooks reaches the dashboard.
    """
    failures_path = Path(json_file).parent / "failures.json"
    if not failures_path.exists():
        return {}
    try:
        items = json.loads(failures_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    out = {}
    for item in items or []:
        key = (item.get("feature") or "", item.get("scenario") or "")
        out[key] = item
    return out


def load_modules(json_file: str) -> dict:
    """Parse a single behave JSON report into per-module (per-feature) summary dicts."""
    try:
        data = json.loads(Path(json_file).read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        print(f"Could not parse JSON {json_file}: {e}")
        return {}

    failures_by_key = load_failures(json_file)
    out = {}
    for feature in (data if isinstance(data, list) else []):
        feature_name = feature.get("name", "")
        module_name = FEATURE_NAME_TO_MODULE.get(
            feature_name,
            re.sub(r"[^a-z0-9]+", "_", feature_name.lower()).strip("_"),
        )
        scenarios = []
        for el in feature.get("elements", []):
            if el.get("type") != "scenario":
                continue
            status = _scenario_status(el)
            duration = 0.0
            failed_step = ""
            error_text = ""
            steps = el.get("steps", []) or []
            step_total = len(steps)
            step_passed = 0
            step_failed = 0
            step_skipped = 0
            for step in steps:
                res = step.get("result", {}) or {}
                sstat = res.get("status", "")
                duration += float(res.get("duration") or 0.0)
                if sstat == "passed":
                    step_passed += 1
                elif sstat in ("failed", "error"):
                    step_failed += 1
                elif sstat in ("skipped", "untested", ""):
                    step_skipped += 1
                if sstat in ("failed", "error") and not failed_step:
                    failed_step = f"{step.get('keyword', '').strip()} {step.get('name', '').strip()}".strip()
                    msg = res.get("error_message")
                    error_text = "\n".join(msg) if isinstance(msg, list) else str(msg or "")

            scenario_name = el.get("name", "(unnamed scenario)")
            screenshot = None
            # Soft-fail scenarios (see new_user_steps._run): every individual step
            # reports "passed" in behave's JSON even though the scenario itself was
            # marked failed afterwards, so error_text is empty above. Recover the
            # real reason (and screenshot) from the sidecar failures.json instead.
            if status in ("failed", "error") and not error_text:
                match = failures_by_key.get((feature_name, scenario_name))
                if match:
                    error_text = match.get("error") or error_text
                    failed_step = failed_step or "(soft-fail — see failure reason)"
                    screenshot = match.get("screenshot")

            scenarios.append({
                "name": scenario_name,
                "feature": feature_name,
                "status": status,
                "duration": duration,
                "failed_step": failed_step,
                "error": error_text,
                "screenshot": screenshot,
                "category": _categorize_failure(error_text) if status in ("failed", "error") else "",
                "step_total": step_total,
                "step_passed": step_passed,
                "step_failed": step_failed,
                "step_skipped": step_skipped,
            })
        out[module_name] = {
            "scenarios": scenarios,
            "feature_name": feature_name,
            "total": len(scenarios),
            "passed": sum(1 for s in scenarios if s["status"] == "passed"),
            "failed": sum(1 for s in scenarios if s["status"] == "failed"),
            "errored": sum(1 for s in scenarios if s["status"] == "error"),
            "skipped": sum(1 for s in scenarios if s["status"] == "skipped"),
            "duration": sum(s["duration"] for s in scenarios),
            "step_total": sum(s["step_total"] for s in scenarios),
            "step_passed": sum(s["step_passed"] for s in scenarios),
            "step_failed": sum(s["step_failed"] for s in scenarios),
            "step_skipped": sum(s["step_skipped"] for s in scenarios),
        }
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Small formatting / chart helpers
# ─────────────────────────────────────────────────────────────────────────────
def _fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _pct(part: int, whole: int) -> float:
    return round(100.0 * part / whole, 1) if whole else 0.0


def _esc(text) -> str:
    return html.escape(str(text), quote=True)


def _health(pass_pct: float) -> tuple:
    """Return (label, css-class) for an overall-health badge."""
    if pass_pct >= 95:
        return ("HEALTHY", "health-good")
    if pass_pct >= 75:
        return ("NEEDS ATTENTION", "health-warn")
    return ("CRITICAL", "health-bad")


def _donut_svg(passed: int, failed: int, errored: int, skipped: int) -> str:
    """Pass/Fail/Error/Skip donut chart as pure SVG (no JS)."""
    segments = [
        (passed, "#1b9e4b", "Passed"),
        (failed, "#d32f2f", "Failed"),
        (errored, "#ef8e00", "Error"),
        (skipped, "#90a0bf", "Skipped"),
    ]
    total = sum(v for v, _, _ in segments) or 1
    r = 70
    cx = cy = 90
    circ = 2 * 3.14159265 * r
    offset = 0.0
    rings = []
    for value, color, _ in segments:
        if value <= 0:
            continue
        length = circ * value / total
        rings.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
            f'stroke-width="26" stroke-dasharray="{length:.2f} {circ - length:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        offset += length
    pass_pct = _pct(passed, total)
    legend = "".join(
        f'<div class="lg-item"><span class="lg-dot" style="background:{c}"></span>'
        f'{n} <b>{v}</b></div>'
        for v, c, n in segments
    )
    return (
        '<div class="chart-card"><div class="chart-title">Pass / Fail Distribution</div>'
        '<div class="donut-wrap">'
        f'<svg viewBox="0 0 180 180" width="180" height="180">{"".join(rings)}'
        f'<text x="90" y="84" text-anchor="middle" class="donut-num">{pass_pct}%</text>'
        f'<text x="90" y="104" text-anchor="middle" class="donut-lbl">PASS</text></svg>'
        f'<div class="legend">{legend}</div>'
        '</div></div>'
    )


def _module_bar_chart(rows: list) -> str:
    """Horizontal stacked pass/fail bars per module."""
    bars = []
    for r in rows:
        total = r["total"] or 1
        p = 100.0 * r["passed"] / total
        f = 100.0 * (r["failed"] + r["errored"]) / total
        sk = 100.0 * r["skipped"] / total
        bars.append(
            f'<div class="bar-row"><div class="bar-label">{_esc(r["label"])}</div>'
            f'<div class="bar-track">'
            f'<span class="seg seg-pass" style="width:{p:.1f}%" title="Passed {r["passed"]}"></span>'
            f'<span class="seg seg-fail" style="width:{f:.1f}%" title="Failed/Error {r["failed"] + r["errored"]}"></span>'
            f'<span class="seg seg-skip" style="width:{sk:.1f}%" title="Skipped {r["skipped"]}"></span>'
            f'</div><div class="bar-val">{r["pass_pct"]}%</div></div>'
        )
    return (
        '<div class="chart-card chart-wide"><div class="chart-title">Module-wise Results</div>'
        f'<div class="bar-chart">{"".join(bars)}</div>'
        '<div class="legend legend-row">'
        '<div class="lg-item"><span class="lg-dot" style="background:#1b9e4b"></span>Passed</div>'
        '<div class="lg-item"><span class="lg-dot" style="background:#d32f2f"></span>Failed/Error</div>'
        '<div class="lg-item"><span class="lg-dot" style="background:#90a0bf"></span>Skipped</div>'
        '</div></div>'
    )


def _failure_bar_chart(category_counts: dict) -> str:
    """Horizontal bars for failure categories."""
    if not category_counts:
        return (
            '<div class="chart-card"><div class="chart-title">Failure Distribution</div>'
            '<div class="empty-note">🎉 No failures recorded.</div></div>'
        )
    mx = max(category_counts.values()) or 1
    palette = ["#d32f2f", "#ef8e00", "#8e44ad", "#2980b9", "#16a085", "#7f8c8d"]
    rows = []
    for i, (cat, cnt) in enumerate(sorted(category_counts.items(), key=lambda x: -x[1])):
        w = 100.0 * cnt / mx
        c = palette[i % len(palette)]
        rows.append(
            f'<div class="bar-row"><div class="bar-label">{_esc(cat)}</div>'
            f'<div class="bar-track"><span class="seg" style="width:{w:.1f}%;background:{c}"></span></div>'
            f'<div class="bar-val">{cnt}</div></div>'
        )
    return (
        '<div class="chart-card"><div class="chart-title">Failure Distribution</div>'
        f'<div class="bar-chart">{"".join(rows)}</div></div>'
    )


def _trend_chart(history: list) -> str:
    """Mini bar trend of pass% over the last runs."""
    if len(history) < 2:
        return (
            '<div class="chart-card chart-wide"><div class="chart-title">Execution History (Pass %)</div>'
            '<div class="empty-note">Trend appears after at least two runs are recorded.</div></div>'
        )
    recent = history[-12:]
    bars = []
    bw = 100.0 / len(recent)
    for h in recent:
        pp = h.get("pass_pct", 0)
        color = "#1b9e4b" if pp >= 95 else ("#ef8e00" if pp >= 75 else "#d32f2f")
        label = h.get("date", "")[5:16]
        bars.append(
            f'<div class="trend-col" style="width:{bw:.2f}%" title="{_esc(label)} — {pp}%">'
            f'<div class="trend-bar" style="height:{max(pp, 2):.1f}%;background:{color}"></div>'
            f'<div class="trend-x">{pp:.0f}</div></div>'
        )
    return (
        '<div class="chart-card chart-wide"><div class="chart-title">Execution History (Pass %)</div>'
        f'<div class="trend-chart">{"".join(bars)}</div></div>'
    )


def _logo_html() -> str:
    """Return an <img> with the company logo embedded as a data URI, else a text mark."""
    for cand in LOGO_CANDIDATES:
        p = Path(cand)
        if p.exists():
            try:
                mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
                b64 = base64.b64encode(p.read_bytes()).decode("ascii")
                return f'<img class="wf-logo" src="data:{mime};base64,{b64}" alt="Wadhwani Foundation"/>'
            except Exception:
                break
    return '<div class="logo-badge">WF</div>'


def _scenario_table(modules: dict, ordered_names: list) -> str:
    """Detailed test execution table with rows filterable by status."""
    rows = ""
    for name in ordered_names:
        p = modules[name]
        label = MODULE_LABELS.get(name, name.replace("_", " ").title())
        for s in p["scenarios"]:
            st = s["status"]
            icon = STATUS_ICONS.get(st, "")
            outcome, reason = _friendly_result(s)
            reason_cell = _esc(reason) if reason else '<span class="muted">—</span>'
            steps_cell = f'{s["step_passed"]}/{s["step_total"]}'
            rows += (
                f'<tr data-status="{st}" data-module="{_esc(name)}">'
                f'<td>{_esc(s["name"])}</td>'
                f'<td>{_esc(label)}</td>'
                f'<td><span class="status-tag {st}">{icon} {st.title()}</span></td>'
                f'<td>{_esc(steps_cell)}</td>'
                f'<td>{_fmt_duration(s["duration"])}</td>'
                f'<td>{_esc(outcome)}</td>'
                f'<td class="reason-cell">{reason_cell}</td></tr>'
            )
    filters = (
        '<div class="filter-bar">'
        '<button class="filter-btn active" id="flt-all" onclick="filterScenarios(\'all\')">All</button>'
        '<button class="filter-btn" id="flt-passed" onclick="filterScenarios(\'passed\')">✅ Passed</button>'
        '<button class="filter-btn" id="flt-failed" onclick="filterScenarios(\'failed\')">❌ Failed / Error</button>'
        '<button class="filter-btn" id="flt-skipped" onclick="filterScenarios(\'skipped\')">⏭️ Skipped</button>'
        '</div>'
    )
    return (
        f'<a id="detailed"></a>{filters}'
        '<div class="panel"><table class="grid" id="scenario-table"><thead><tr>'
        '<th>Scenario</th><th>Module</th><th>Status</th><th>Steps (Passed/Total)</th><th>Execution Time</th>'
        '<th>Outcome</th><th>Failure Reason</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>'
    )


def _pivot_table(title: str, headers: list, rows: list) -> str:
    head = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        cells = "".join(f"<td>{c}</td>" for c in row)
        body += f"<tr>{cells}</tr>"
    return (
        f'<div class="pivot-card"><div class="pivot-title">{_esc(title)}</div>'
        f'<table class="pivot"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Execution history (for the trend chart)
# ─────────────────────────────────────────────────────────────────────────────
def update_history(history_path: Path, summary: dict, env: str, generated_at: str) -> list:
    history = []
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append({
        "date": generated_at,
        "env": env,
        "total": summary["total"],
        "passed": summary["passed"],
        "failed": summary["failed"] + summary["errored"],
        "skipped": summary["skipped"],
        "pass_pct": summary["pass_pct"],
    })
    history = history[-50:]
    try:
        history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Could not write history file: {e}")
    return history


# ─────────────────────────────────────────────────────────────────────────────
# Static CSS / JS (plain strings — literal braces, NOT f-strings)
# ─────────────────────────────────────────────────────────────────────────────
SHELL_CSS = """
/* ── Wadhwani Foundation brand palette (orange + red) ── */
:root {
  --wf-orange: #f47920;
  --wf-orange-dk: #d75f0c;
  --wf-red: #c1272d;
  --wf-red-dk: #9e1b20;
  --wf-bg: #fdf3ec;
  --wf-pass: #1b9e4b;
  --wf-fail: #d32f2f;
  --wf-warn: #ef8e00;
}
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; background: var(--wf-bg); color: #2a1f1a; }
.shell-header {
  background: #fff;
  border-bottom: 4px solid var(--wf-orange);
  color: var(--wf-red); padding: 14px 30px; display: flex; align-items: center;
  justify-content: space-between; box-shadow: 0 2px 10px rgba(0,0,0,0.12);
}
.brand { display: flex; align-items: center; gap: 18px; }
.wf-logo { height: 56px; width: auto; display: block; }
.logo-badge {
  width: 48px; height: 48px; border-radius: 10px;
  background: linear-gradient(135deg, var(--wf-orange) 0%, var(--wf-red) 100%);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 18px; color: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.shell-header h1 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: .3px; color: var(--wf-red); }
.detail-line { font-size: 13px; font-weight: 700; color: var(--wf-orange-dk); margin-top: 4px;
  text-transform: uppercase; letter-spacing: .6px; }
.shell-header .sub { font-size: 12px; color: #9a8a82; margin-top: 2px; }

.dash { padding: 22px 28px 8px; }
.section-title { font-size: 13px; font-weight: 800; letter-spacing: 1px; color: #5a6785;
  text-transform: uppercase; margin: 26px 0 12px; display: flex; align-items: center; gap: 8px; }
.section-title::before { content: ""; width: 4px; height: 16px; background: var(--wf-orange); border-radius: 2px; }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; }
.kpi-card { background: #fff; border-radius: 12px; padding: 16px 18px; box-shadow: 0 1px 4px rgba(20,30,80,0.08);
  border-top: 4px solid var(--wf-red); }
.kpi-card .kpi-val { font-size: 30px; font-weight: 800; line-height: 1; }
.kpi-card .kpi-lbl { font-size: 12px; color: #5a6785; margin-top: 6px; font-weight: 600; }
.kpi-card.total { border-top-color: var(--wf-orange); } .kpi-card.total .kpi-val { color: var(--wf-orange); }
.kpi-card.pass  { border-top-color: #1b9e4b; } .kpi-card.pass .kpi-val  { color: #1b9e4b; }
.kpi-card.fail  { border-top-color: #d32f2f; } .kpi-card.fail .kpi-val  { color: #d32f2f; }
.kpi-card.skip  { border-top-color: #90a0bf; } .kpi-card.skip .kpi-val  { color: #5a6785; }
.kpi-card.pct   { border-top-color: var(--wf-red); } .kpi-card.pct .kpi-val   { color: var(--wf-red); }
.kpi-card.dur   { border-top-color: #00838f; } .kpi-card.dur .kpi-val   { color: #00838f; font-size: 22px; }
.kpi-card.steps { border-top-color: #6a4fb3; } .kpi-card.steps .kpi-val { color: #6a4fb3; }
a.kpi-card { text-decoration: none; color: inherit; cursor: pointer; transition: box-shadow .15s, transform .15s; }
a.kpi-card:hover { box-shadow: 0 6px 16px rgba(20,30,80,0.16); transform: translateY(-2px); }

.mod-link { color: var(--wf-red); text-decoration: none; } .mod-link:hover { text-decoration: underline; }
a.pillp { text-decoration: none; cursor: pointer; }
a.pillp:hover { filter: brightness(0.94); text-decoration: underline; }
.filter-bar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.filter-btn { border: 1px solid #e6cdbb; background: #fff; color: #5a6785; padding: 6px 14px;
  border-radius: 18px; font-size: 12px; font-weight: 700; cursor: pointer; transition: all .12s; }
.filter-btn:hover { border-color: var(--wf-orange); color: var(--wf-orange-dk); }
.filter-btn.active { background: var(--wf-orange); border-color: var(--wf-orange); color: #fff; }
.fail-link { display: inline-block; margin-top: 8px; color: var(--wf-red); font-size: 12px;
  font-weight: 700; cursor: pointer; text-decoration: none; }
.fail-link:hover { text-decoration: underline; }

.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }
.info-item { background: #fff; border-radius: 10px; padding: 12px 14px; box-shadow: 0 1px 4px rgba(20,30,80,0.06); }
.info-item .k { font-size: 11px; color: #8a93ab; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; }
.info-item .v { font-size: 14px; font-weight: 600; margin-top: 3px; word-break: break-all; }
.info-item .v a { color: var(--wf-red); text-decoration: none; } .info-item .v a:hover { text-decoration: underline; }

.panel { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(20,30,80,0.08); overflow: hidden; }
table.grid { width: 100%; border-collapse: collapse; font-size: 13px; }
table.grid th { background: var(--wf-red); color: #fff; text-align: left; padding: 10px 14px; font-weight: 700; font-size: 12px; letter-spacing: .3px; }
table.grid td { padding: 9px 14px; border-bottom: 1px solid #eef1f7; }
table.grid tr:nth-child(even) td { background: #f7f9fd; }
table.grid tr:hover td { background: #eef3ff; }
.pillp { display:inline-block; min-width: 34px; text-align:center; padding: 2px 8px; border-radius: 10px; font-weight: 700; font-size: 12px; }
.pillp.g { background: #e3f6ea; color: #1b7a37; } .pillp.r { background: #fde6e6; color: #c62828; }
.pillp.y { background: #fff3df; color: #b36b00; }
.status-tag { font-weight: 700; }
.status-tag.passed { color: #1b9e4b; } .status-tag.failed { color: #d32f2f; }
.status-tag.error { color: #ef8e00; } .status-tag.skipped { color: #5a6785; }
.reason-cell { font-size: 12px; color: #8a4040; font-family: Consolas, 'Courier New', monospace; }
.muted { color: #b9c0d0; }

.cred-mask { letter-spacing: 2px; color: #8a93ab; }

.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.chart-card { background: #fff; border-radius: 12px; padding: 16px 18px; box-shadow: 0 1px 4px rgba(20,30,80,0.08); }
.chart-card.chart-wide { grid-column: 1 / -1; }
.chart-title { font-size: 13px; font-weight: 800; color: var(--wf-red); margin-bottom: 14px; }
.donut-wrap { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; }
.donut-num { font-size: 26px; font-weight: 800; fill: var(--wf-orange); }
.donut-lbl { font-size: 11px; font-weight: 700; fill: #8a93ab; letter-spacing: 2px; }
.legend { display: flex; flex-direction: column; gap: 8px; }
.legend.legend-row { flex-direction: row; gap: 18px; margin-top: 12px; }
.lg-item { font-size: 13px; color: #3a425a; display: flex; align-items: center; gap: 8px; }
.lg-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.bar-chart { display: flex; flex-direction: column; gap: 10px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-label { width: 130px; font-size: 12px; font-weight: 600; text-align: right; color: #3a425a; flex-shrink: 0; }
.bar-track { flex: 1; height: 18px; background: #eef1f7; border-radius: 9px; overflow: hidden; display: flex; }
.seg { height: 100%; display: inline-block; }
.seg-pass { background: #1b9e4b; } .seg-fail { background: #d32f2f; } .seg-skip { background: #90a0bf; }
.bar-val { width: 46px; font-size: 12px; font-weight: 700; color: #3a425a; }
.trend-chart { display: flex; align-items: flex-end; gap: 4px; height: 130px; padding-top: 8px; }
.trend-col { display: flex; flex-direction: column; justify-content: flex-end; align-items: center; height: 100%; }
.trend-bar { width: 70%; border-radius: 4px 4px 0 0; min-height: 2px; }
.trend-x { font-size: 10px; color: #8a93ab; margin-top: 4px; }
.empty-note { font-size: 13px; color: #8a93ab; padding: 16px 0; }

.pivots { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.pivot-card { background: #fff; border-radius: 12px; padding: 14px 16px; box-shadow: 0 1px 4px rgba(20,30,80,0.08); }
.pivot-title { font-size: 13px; font-weight: 800; color: var(--wf-red); margin-bottom: 10px; }
table.pivot { width: 100%; border-collapse: collapse; font-size: 13px; }
table.pivot th { background: #f0f3fb; color: #3a425a; text-align: left; padding: 7px 10px; font-size: 11px; text-transform: uppercase; letter-spacing: .3px; border-bottom: 2px solid #dde3f0; }
table.pivot td { padding: 7px 10px; border-bottom: 1px solid #f0f3fb; }
table.pivot tfoot td, table.pivot tr.total-row td { font-weight: 800; background: #f7f9fd; }

.fail-card { background: #fff; border-left: 4px solid #d32f2f; border-radius: 8px; padding: 12px 16px;
  margin-bottom: 10px; box-shadow: 0 1px 3px rgba(20,30,80,0.06); }
.fail-card.error { border-left-color: #ef8e00; }
.fail-head { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; align-items: baseline; }
.fail-name { font-weight: 700; font-size: 14px; }
.fail-meta { font-size: 12px; color: #8a93ab; }
.fail-cat { display:inline-block; background:#fde6e6; color:#c62828; border-radius: 10px; padding: 1px 9px; font-size: 11px; font-weight: 700; }
.fail-kind { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .4px; color: #c62828; background: #fde6e6; border-radius: 10px; padding: 2px 10px; margin: 8px 0 4px; }
.fail-card.error .fail-kind { color: #b36b00; background: #fff3df; }
.fail-outcome { font-size: 13px; color: #2a1f1a; margin: 6px 0 2px; }
.fail-reason { font-size: 12.5px; color: #3a425a; margin: 2px 0; }
.fail-reason b { color: var(--wf-red); }
.fail-step { font-size: 12px; color: #8a93ab; margin: 6px 0; }
.fail-step b { color: #5a6785; font-weight: 600; }
.fail-trace { background: #2b2f3a; color: #f3c7c7; font-family: Consolas, 'Courier New', monospace; font-size: 11.5px;
  padding: 10px 12px; border-radius: 6px; white-space: pre-wrap; overflow-x: auto; margin-top: 6px; max-height: 220px; }

.tab-bar { background: #fff; border-bottom: 2px solid #d0d8ed; padding: 0 20px; display: flex;
  flex-wrap: wrap; gap: 2px; overflow-x: auto; position: sticky; top: 0; z-index: 5; }
.tab-btn { border: none; background: transparent; padding: 11px 18px; font-size: 13px; font-weight: 600;
  cursor: pointer; color: #5a6785; border-bottom: 3px solid transparent; margin-bottom: -2px;
  transition: color .15s, border-color .15s; white-space: nowrap; }
.tab-btn:hover { color: var(--wf-orange-dk); }
.tab-btn.active { color: var(--wf-orange-dk); border-bottom-color: var(--wf-orange); }
.tab-btn.status-failed { color: #b71c1c; } .tab-btn.active.status-failed { border-bottom-color: #c62828; }
.tab-btn.status-error { color: #b36b00; } .tab-btn.active.status-error { border-bottom-color: #ef8e00; }
.tab-icon { font-style: normal; }
.tab-panel { display: none; padding: 20px; }
.tab-panel.active { display: block; }
.tab-content .behave #label h1 { display: none; }
.dash-footer { text-align: center; color: #8a93ab; font-size: 12px; padding: 18px; }
"""

SHELL_JS = """
function showTab(name, forceOpen) {
  var panel = document.getElementById('tab-' + name);
  var btn = document.getElementById('btn-' + name);
  var alreadyOpen = btn && btn.classList.contains('active');
  document.querySelectorAll('.tab-panel').forEach(function(p){ p.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function(b){ b.classList.remove('active'); });
  if (alreadyOpen && !forceOpen) return;
  if (panel) panel.classList.add('active');
  if (btn) btn.classList.add('active');
  if (panel) panel.scrollIntoView({behavior:'smooth', block:'start'});
}

function filterScenarios(status, module) {
  var rows = document.querySelectorAll('#scenario-table tbody tr');
  rows.forEach(function(r) {
    var st = r.getAttribute('data-status');
    var statusOk = (status === 'all') ||
                   (st === status) ||
                   (status === 'failed' && (st === 'failed' || st === 'error'));
    var moduleOk = !module || r.getAttribute('data-module') === module;
    r.style.display = (statusOk && moduleOk) ? '' : 'none';
  });
  document.querySelectorAll('.filter-btn').forEach(function(b){ b.classList.remove('active'); });
  var btn = document.getElementById('flt-' + status);
  if (btn) btn.classList.add('active');
  var sec = document.getElementById('detailed');
  if (sec) sec.scrollIntoView({behavior:'smooth', block:'start'});
}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard rendering
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard(modules: dict, env: str, generated_at: str, history: list) -> str:
    env_norm = (env or "").strip().lower()

    total = sum(p["total"] for p in modules.values())
    passed = sum(p["passed"] for p in modules.values())
    failed = sum(p["failed"] for p in modules.values())
    errored = sum(p["errored"] for p in modules.values())
    skipped = sum(p["skipped"] for p in modules.values())
    duration = sum(p["duration"] for p in modules.values())
    step_total = sum(p["step_total"] for p in modules.values())
    step_passed = sum(p["step_passed"] for p in modules.values())
    step_failed = sum(p["step_failed"] for p in modules.values())
    step_skipped = sum(p["step_skipped"] for p in modules.values())
    pass_pct = _pct(passed, total)
    summary = {
        "total": total, "passed": passed, "failed": failed, "errored": errored,
        "skipped": skipped, "duration": duration, "pass_pct": pass_pct,
        "step_total": step_total, "step_passed": step_passed,
        "step_failed": step_failed, "step_skipped": step_skipped,
    }

    ordered_names = [n for n in MODULE_ORDER if n in modules]
    ordered_names += [n for n in sorted(modules) if n not in MODULE_ORDER]

    module_rows = []
    for name in ordered_names:
        p = modules[name]
        module_rows.append({
            "name": name,
            "label": MODULE_LABELS.get(name, name.replace("_", " ").title()),
            "total": p["total"], "passed": p["passed"], "failed": p["failed"],
            "errored": p["errored"], "skipped": p["skipped"],
            "pass_pct": _pct(p["passed"], p["total"]),
            "duration": p["duration"],
            "step_total": p["step_total"], "step_passed": p["step_passed"],
            "step_failed": p["step_failed"], "step_skipped": p["step_skipped"],
        })

    # ── KPI cards ──
    kpis = (
        '<div class="kpi-grid">'
        f'<a class="kpi-card total" href="#detailed" onclick="filterScenarios(\'all\')"><div class="kpi-val">{total}</div><div class="kpi-lbl">Total Scenarios ▸</div></a>'
        f'<a class="kpi-card pass" href="#detailed" onclick="filterScenarios(\'passed\')"><div class="kpi-val">{passed}</div><div class="kpi-lbl">Passed ▸</div></a>'
        f'<a class="kpi-card fail" href="#detailed" onclick="filterScenarios(\'failed\')"><div class="kpi-val">{failed + errored}</div><div class="kpi-lbl">Failed / Error ▸</div></a>'
        f'<a class="kpi-card skip" href="#detailed" onclick="filterScenarios(\'skipped\')"><div class="kpi-val">{skipped}</div><div class="kpi-lbl">Skipped ▸</div></a>'
        f'<div class="kpi-card pct"><div class="kpi-val">{pass_pct}%</div><div class="kpi-lbl">Scenario Pass %</div></div>'
        f'<div class="kpi-card steps"><div class="kpi-val">{step_passed}/{step_total}</div><div class="kpi-lbl">Test Steps Passed ({_pct(step_passed, step_total)}%)</div></div>'
        f'<div class="kpi-card dur"><div class="kpi-val">{_fmt_duration(duration)}</div><div class="kpi-lbl">Execution Duration</div></div>'
        '</div>'
    )

    # ── Execution information ──
    exec_type = "Local"
    if os.getenv("GITHUB_ACTIONS"):
        exec_type = "GitHub Actions"
    elif os.getenv("JENKINS_URL") or os.getenv("BUILD_NUMBER"):
        exec_type = "Jenkins"
    app_url = APP_URLS.get(env_norm, os.getenv("BASE_URL", "—"))
    build_version = os.getenv("BUILD_VERSION") or os.getenv("GITHUB_SHA", "")[:8]
    os_name = f"{platform.system()} {platform.release()}"
    env_display = {"prod": "Production", "dev": "Development", "qa": "QA"}.get(env_norm, env_norm.upper() or "—")

    info_items = [
        ("Application URL", f'<a href="{_esc(app_url)}" target="_blank">{_esc(app_url)}</a>'),
        ("Environment", _esc(env_display)),
        ("Browser", "Chromium (Playwright)"),
        ("Operating System", _esc(os_name)),
        ("Framework", "Behave + Playwright (Python)"),
        ("Execution Type", _esc(exec_type)),
        ("Execution Date &amp; Time", _esc(generated_at)),
    ]
    if build_version:
        info_items.insert(6, ("Build Version", _esc(build_version)))
    exec_info = '<div class="info-grid">' + "".join(
        f'<div class="info-item"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in info_items
    ) + '</div>'

    # ── Credentials ──
    cred_rows = ""
    cred_idx = 0 if env_norm != "prod" else 1
    for role_key, creds in CREDENTIALS.items():
        username = creds[cred_idx]
        cred_rows += (
            f'<tr><td><b>{_esc(role_key.title())}</b></td><td>{_esc(username)}</td>'
            f'<td><span class="cred-mask">••••••••</span></td>'
            f'<td>{_esc(env_display)} Test Account</td></tr>'
        )
    credentials = (
        '<div class="panel"><table class="grid"><thead><tr>'
        '<th>User Role</th><th>Username / Email Used</th><th>Password</th><th>Test Account</th>'
        f'</tr></thead><tbody>{cred_rows}</tbody></table></div>'
    )

    # ── Module coverage table ──
    # "Pass %" is scenario-level (all-or-nothing per scenario), which reads as a
    # flat 0% for a module built from one long end-to-end scenario (e.g. New User
    # Journey) even when nearly every step in it succeeded. "Step Pass %" is
    # shown alongside it so that partial progress within a failed scenario is
    # still visible instead of looking like nothing ran.
    cov_rows = ""
    for r in module_rows:
        cls = "g" if r["pass_pct"] >= 95 else ("y" if r["pass_pct"] >= 75 else "r")
        step_pct = _pct(r["step_passed"], r["step_total"])
        step_cls = "g" if step_pct >= 95 else ("y" if step_pct >= 75 else "r")
        nm = r["name"]
        cov_rows += (
            f'<tr><td><a class="mod-link" href="#detailed" onclick="filterScenarios(\'all\',\'{nm}\')"><b>{_esc(r["label"])}</b></a></td><td>{r["total"]}</td>'
            f'<td>{r["step_total"]}</td>'
            f'<td><a class="pillp g" href="#detailed" onclick="filterScenarios(\'passed\',\'{nm}\')">{r["passed"]}</a></td>'
            f'<td><a class="pillp r" href="#detailed" onclick="filterScenarios(\'failed\',\'{nm}\')">{r["failed"] + r["errored"]}</a></td>'
            f'<td><span class="pillp {"g" if r["skipped"]==0 else "y"}">{r["skipped"]}</span></td>'
            f'<td><span class="pillp {cls}">{r["pass_pct"]}%</span></td>'
            f'<td><span class="pillp {step_cls}">{r["step_passed"]}/{r["step_total"]} ({step_pct}%)</span></td>'
            f'<td>{_fmt_duration(r["duration"])}</td></tr>'
        )
    cov_rows += (
        f'<tr class="total-row"><td>TOTAL</td><td>{total}</td><td>{step_total}</td><td>{passed}</td>'
        f'<td>{failed + errored}</td><td>{skipped}</td><td>{pass_pct}%</td>'
        f'<td>{step_passed}/{step_total} ({_pct(step_passed, step_total)}%)</td>'
        f'<td>{_fmt_duration(duration)}</td></tr>'
    )
    module_coverage = (
        '<div class="panel"><table class="grid"><thead><tr>'
        '<th>Module</th><th>Scenarios</th><th>Test Steps</th><th>Passed</th><th>Failed/Error</th><th>Skipped</th>'
        '<th>Scenario Pass %</th><th>Step Pass %</th><th>Duration</th>'
        f'</tr></thead><tbody>{cov_rows}</tbody></table></div>'
    )

    # ── Charts ──
    charts = (
        '<div class="charts">'
        + _donut_svg(passed, failed, errored, skipped)
        + _module_bar_chart(module_rows)
        + _trend_chart(history)
        + _failure_bar_chart(_failure_categories(modules))
        + '</div>'
    )

    # ── Pivot tables ──
    pivots = _render_pivots(module_rows, modules, env_display)

    # ── Failure analysis ──
    failure_analysis = _render_failures(modules, ordered_names)

    # ── Detailed test execution ──
    detailed = _scenario_table(modules, ordered_names)

    body = (
        '<div class="dash">'
        '<div class="section-title">Executive Dashboard</div>' + kpis
        + '<div class="section-title">Execution Information</div>' + exec_info
        + '<div class="section-title">Test Account &amp; Credentials</div>' + credentials
        + '<div class="section-title">Visualizations</div>' + charts
        + '<div class="section-title">Module Coverage Summary</div>' + module_coverage
        + '<div class="section-title">Pivot Summaries</div>' + pivots
        + '<div class="section-title">Failure Analysis</div>' + failure_analysis
        + '<div class="section-title">Detailed Test Execution</div>' + detailed
        + '<div class="empty-note">Tip: click any KPI card or a module\'s pass/fail count to filter this table. '
        'Open a feature tab below for full step-by-step logs and screenshots.</div>'
        '</div>'
    )
    return body, summary


def _failure_categories(modules: dict) -> dict:
    counts = {}
    for p in modules.values():
        for s in p["scenarios"]:
            if s["status"] in ("failed", "error") and s["category"]:
                counts[s["category"]] = counts.get(s["category"], 0) + 1
    return counts


def _render_pivots(module_rows: list, modules: dict, env_display: str) -> str:
    # Scenario Pass % is all-or-nothing per scenario, so a single long scenario
    # (e.g. New User Journey) reads as a flat 0% even when most of its steps
    # passed. Step Pass % is included so that partial progress is still visible.
    mvp = [
        [r["label"], r["passed"], r["failed"] + r["errored"], r["skipped"], f'{r["pass_pct"]}%',
         f'{r["step_passed"]}/{r["step_total"]} ({_pct(r["step_passed"], r["step_total"])}%)']
        for r in module_rows
    ]
    p1 = _pivot_table("Module vs Pass / Fail",
                      ["Module", "Passed", "Failed", "Skipped", "Scenario Pass %", "Step Pass %"], mvp)

    fec = [[r["label"], r["total"], r["step_total"]] for r in module_rows]
    p2 = _pivot_table("Feature vs Execution Count", ["Feature", "Scenarios Executed", "Test Steps Executed"], fec)

    tot_p = sum(r["passed"] for r in module_rows)
    tot_f = sum(r["failed"] + r["errored"] for r in module_rows)
    tot_s = sum(r["skipped"] for r in module_rows)
    p3 = _pivot_table("Environment vs Pass / Fail", ["Environment", "Passed", "Failed", "Skipped"],
                      [[env_display, tot_p, tot_f, tot_s]])

    cats = _failure_categories(modules)
    fc_rows = [[c, n] for c, n in sorted(cats.items(), key=lambda x: -x[1])] or [["No failures", 0]]
    p4 = _pivot_table("Failure Category vs Count", ["Category", "Count"], fc_rows)

    return '<div class="pivots">' + p1 + p2 + p3 + p4 + '</div>'


def _render_failures(modules: dict, ordered_names: list) -> str:
    cards = []
    for name in ordered_names:
        p = modules[name]
        label = MODULE_LABELS.get(name, name.replace("_", " ").title())
        for s in p["scenarios"]:
            if s["status"] not in ("failed", "error"):
                continue
            err = _esc(s["error"]) if s["error"] else "(no error message captured)"
            outcome, reason = _friendly_result(s)
            kind = ("Application / Validation failure" if s["status"] == "failed"
                    else "Automation / Environment error")
            shot = s.get("screenshot")
            shot_link = (
                f'<a class="fail-link" href="{_esc(shot)}" target="_blank">View failure screenshot ▸</a>'
                if shot else ""
            )
            cards.append(
                f'<div class="fail-card {"error" if s["status"]=="error" else ""}">'
                f'<div class="fail-head"><span class="fail-name">{_esc(s["name"])}</span>'
                f'<span class="fail-meta">Module: <b>{_esc(label)}</b> · '
                f'<span class="fail-cat">{_esc(s["category"] or "Unknown")}</span> · '
                f'Steps: <b>{s["step_passed"]}/{s["step_total"]}</b> · '
                f'{_fmt_duration(s["duration"])}</span></div>'
                f'<div class="fail-kind">{_esc(kind)}</div>'
                f'<div class="fail-outcome">What happened: {_esc(outcome)}</div>'
                f'<div class="fail-reason">Failure reason: <b>{_esc(reason)}</b></div>'
                f'<div class="fail-step">Technical step (for engineers): <b>{_esc(s["failed_step"] or "—")}</b></div>'
                f'<div class="fail-trace">{err}</div>'
                f'{shot_link}'
                f'<a class="fail-link" onclick="showTab(\'all\', true)">View full steps ▸</a></div>'
            )
    if not cards:
        return '<div class="empty-note">🎉 No failures — all executed scenarios passed.</div>'
    note = ('<div class="empty-note">Screenshots for each failure are attached inline in the '
            'feature tabs below and in the Allure results.</div>')
    return "".join(cards) + note


# ─────────────────────────────────────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────────────────────────────────────
def build_combined(json_file: str, html_file: str, output_file: str, env: str = ""):
    html_path = Path(html_file)
    if not html_path.exists():
        print(f"HTML report not found: {html_file}")
        return 1

    try:
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"Could not read HTML report {html_file}: {e}")
        return 1

    all_styles, all_scripts = set(), set()
    styles, scripts, body_html = _extract_body_and_head(html_text)
    for s in styles:
        all_styles.add(s.strip())
    for s in scripts:
        all_scripts.add(s.strip())
    body_html = _remove_behave_title(body_html)
    body_html = _namespace_body_ids(body_html, "all")
    tabs = [("all", "All Features", body_html)]

    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    env_norm = (env or "").strip().lower()

    modules = load_modules(json_file)
    if not modules:
        print(f"Warning: could not parse modules from {json_file}; dashboard metrics will be empty.")

    history_path = Path(output_file).parent / "history.json"

    if modules:
        prelim_total = sum(p["total"] for p in modules.values())
        prelim = {
            "total": prelim_total,
            "passed": sum(p["passed"] for p in modules.values()),
            "failed": sum(p["failed"] for p in modules.values()),
            "errored": sum(p["errored"] for p in modules.values()),
            "skipped": sum(p["skipped"] for p in modules.values()),
            "pass_pct": _pct(sum(p["passed"] for p in modules.values()), prelim_total),
        }
        history = update_history(history_path, prelim, env_norm, generated_at)
        dashboard_html, summary = render_dashboard(modules, env_norm, generated_at, history)
    else:
        dashboard_html = '<div class="dash"><div class="empty-note">No JSON reports available for dashboard.</div></div>'
        summary = None

    def _tab_status(name: str) -> str:
        if not modules:
            return "passed"
        failed_total = sum(p["failed"] for p in modules.values())
        errored_total = sum(p["errored"] for p in modules.values())
        if failed_total > 0:
            return "failed"
        if errored_total > 0:
            return "error"
        return "passed"

    tab_buttons_html = "\n".join(
        f'<button class="tab-btn status-{_tab_status(name)}" '
        f'onclick="showTab(\'{name}\')" id="btn-{name}">'
        f'<span class="tab-icon">{STATUS_ICONS.get(_tab_status(name), "✅")}</span> {label}</button>'
        for name, label, _ in tabs
    )
    tab_panels_html = "\n".join(
        f'<div class="tab-panel" id="tab-{name}">{body_html}</div>'
        for name, _, body_html in tabs
    )

    env_label_map = {"prod": "PROD", "dev": "DEV", "qa": "QA"}
    env_label = env_label_map.get(env_norm, env_norm.upper() or "ENV")
    env_display = {"prod": "Production", "dev": "Development", "qa": "QA"}.get(env_norm, env_norm.upper() or "—")

    merged_styles = "\n".join(all_styles)
    merged_scripts = "\n".join(all_scripts)

    summary_line = f"{env_display} Environment Execution Summary"
    header_html = (
        '<div class="shell-header">'
        '<div class="brand">' + _logo_html() +
        '<div><h1>WSN-CA Automation — QA Execution Dashboard</h1>'
        f'<div class="detail-line">{_esc(summary_line)}</div>'
        f'<div class="sub">Generated {_esc(generated_at)}</div></div></div>'
        '</div>'
    )

    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        f'<title>WSN-CA Automation — QA Dashboard [{env_label}]</title>'
        '<style>\n'
        '/* behave_html_formatter styles */\n' + merged_styles + '\n'
        '/* dashboard + shell styles */\n' + SHELL_CSS +
        '</style></head><body>'
        + header_html
        + dashboard_html
        + '<div class="tab-bar">' + tab_buttons_html + '</div>'
        + '<div class="tab-content">' + tab_panels_html + '</div>'
        + '<div class="dash-footer">WSN-CA Automation Framework · Behave + Playwright · '
        f'Report generated {_esc(generated_at)}</div>'
        + '<script>' + merged_scripts + '\n' + SHELL_JS + '</script>'
        + '</body></html>'
    )

    base = Path(output_file)
    file_ts = generated_at.replace(":", "-").replace(" ", "_")
    name_parts = [base.stem]
    if env_norm:
        name_parts.append(env_norm)
    name_parts.append(file_ts)
    out_path = base.with_name("_".join(name_parts) + base.suffix)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    print(f"Combined QA dashboard created: {out_path}")
    if summary:
        print(f"Scenarios: {summary['total']} | Passed: {summary['passed']} | "
              f"Failed/Error: {summary['failed'] + summary['errored']} | "
              f"Skipped: {summary['skipped']} | Pass: {summary['pass_pct']}% | "
              f"Steps: {summary['step_total']} (Passed: {summary['step_passed']}, "
              f"Failed: {summary['step_failed']}, Skipped: {summary['step_skipped']})")
    return 0


def main():
    json_file   = sys.argv[1] if len(sys.argv) > 1 else "reports/json-report/all.json"
    html_file   = sys.argv[2] if len(sys.argv) > 2 else "reports/html-report/features/all.html"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "reports/html-report/combined_report.html"
    env         = sys.argv[4] if len(sys.argv) > 4 else ""
    return build_combined(json_file, html_file, output_file, env)


if __name__ == "__main__":
    raise SystemExit(main())