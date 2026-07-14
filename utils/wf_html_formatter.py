# -*- coding: utf-8 -*-
"""
Wadhwani Foundation themed HTML formatter for behave.

Extends the upstream ``behave_html_formatter.HTMLFormatter`` to:

* Always show ``passed``, ``failed`` and ``error`` (and ``skipped``) counts in
  the summary totals, even when a count is zero -- so ``failed: 0`` and
  ``error: 0`` are always visible instead of being silently dropped.
* Render the scenario totals (``passed`` / ``failed`` / ``error`` / ``skipped``)
  as clickable links.  Clicking a status filters the report down to just the
  scenarios with that status; clicking the same status again clears the filter.
* Apply the Wadhwani Foundation brand colours (red and orange) to the report
  header and scenario headings.

Wire it up in ``behave.ini`` so ``-f html`` uses this formatter::

    [behave.formatters]
    html = utils.wf_html_formatter:WFHTMLFormatter
"""

import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from xml.sax.saxutils import escape

from behave_html_formatter.html import HTMLFormatter, ET_tostring

from utils.config import Config
from utils.run_metadata import RUN


# -- Wadhwani Foundation brand colours.
WF_RED = "#E2231A"
WF_ORANGE = "#F58220"
# Brand-only status palette (no green): orange = good/passed, red = bad/failed,
# dark red = error, grey = skipped.
WF_PASS = WF_ORANGE
WF_FAIL = WF_RED
WF_ERROR = "#A30D08"
WF_SKIP = "#888888"

# Statuses we always want to display (in this order), even if their count is 0.
ALWAYS_SHOWN_STATUSES = ("passed", "failed", "error", "skipped")

WF_CSS = f"""
/* -- Wadhwani Foundation branding -- */
.behave #behave-header,
td #behave-header,
th #behave-header {{
    background: linear-gradient(90deg, {WF_RED} 0%, {WF_ORANGE} 100%) !important;
    color: white !important;
}}
.behave .scenario h3,
td .scenario h3,
th .scenario h3,
.background h3 {{
    background: linear-gradient(90deg, {WF_RED} 0%, {WF_ORANGE} 100%) !important;
    color: white !important;
}}
/* Keep the totals readable on top of the coloured header. */
#summary #totals {{
    background: #ffffff;
    color: #333333;
    padding: 6px 12px;
    border-radius: 6px;
    display: inline-block;
}}
#summary #totals .total-passed  {{ color: {WF_PASS}; font-weight: bold; }}
#summary #totals .total-failed  {{ color: {WF_FAIL}; font-weight: bold; }}
#summary #totals .total-error   {{ color: {WF_ERROR}; font-weight: bold; }}
#summary #totals .total-skipped {{ color: {WF_SKIP}; }}
/* Clickable status links in the scenario totals. */
#summary #totals a.wf-status-link {{
    text-decoration: underline;
    cursor: pointer;
}}
#summary #totals a.wf-status-link.wf-active {{
    outline: 2px solid #333333;
    border-radius: 3px;
    padding: 0 3px;
}}
/* Environment banner shown at the very top of the report. */
.wf-env-banner {{
    background: linear-gradient(90deg, {WF_RED} 0%, {WF_ORANGE} 100%);
    color: #ffffff;
    font-weight: bold;
    font-size: 18px;
    text-align: center;
    padding: 10px 12px;
    margin: 0 0 8px 0;
    text-transform: capitalize;
}}

/* -- Run metadata / scope / failure panels -- */
.wf-panel {{
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin: 0 0 12px 0;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    overflow: hidden;
}}
.wf-panel > h2 {{
    margin: 0;
    padding: 8px 14px;
    font-size: 14px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #ffffff;
    background: linear-gradient(90deg, {WF_RED} 0%, {WF_ORANGE} 100%);
}}
.wf-panel-body {{ padding: 12px 14px; }}
.wf-cards {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }}
.wf-card {{
    flex: 1 1 90px;
    min-width: 90px;
    text-align: center;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 10px 6px;
}}
.wf-card .wf-num {{ font-size: 24px; font-weight: bold; display: block; }}
.wf-card .wf-lbl {{ font-size: 11px; color: #777; text-transform: uppercase; }}
.wf-card.wf-c-total  .wf-num {{ color: #333; }}
.wf-card.wf-c-passed .wf-num {{ color: {WF_PASS}; }}
.wf-card.wf-c-failed .wf-num {{ color: {WF_FAIL}; }}
.wf-card.wf-c-skipped .wf-num {{ color: {WF_SKIP}; }}
.wf-card.wf-c-rate   .wf-num {{ color: {WF_RED}; }}
.wf-kv {{ width: 100%; border-collapse: collapse; }}
.wf-kv td {{ padding: 4px 8px; border-bottom: 1px solid #f0f0f0; vertical-align: top; font-size: 13px; }}
.wf-kv td.wf-k {{ color: #777; width: 130px; white-space: nowrap; }}
.wf-cols {{ display: flex; flex-wrap: wrap; gap: 14px; }}
.wf-cols > div {{ flex: 1 1 280px; }}
.wf-scope-table, .wf-fail-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.wf-scope-table th, .wf-fail-table th {{
    text-align: left; padding: 6px 8px; background: #faf2ef; border-bottom: 2px solid {WF_ORANGE};
}}
.wf-scope-table td, .wf-fail-table td {{ padding: 6px 8px; border-bottom: 1px solid #f0f0f0; vertical-align: top; }}
.wf-fail-cat {{
    display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px;
    background: #fde8e6; color: {WF_RED}; white-space: nowrap;
}}
.wf-fail-table pre {{ margin: 0; white-space: pre-wrap; font-size: 11px; color: #444; max-height: 160px; overflow: auto; }}

/* -- Pivot summary tables -- */
.wf-pivot {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.wf-pivot th {{
    text-align: left; padding: 7px 10px; background: #faf2ef;
    border-bottom: 2px solid {WF_ORANGE}; white-space: nowrap;
}}
.wf-pivot td {{ padding: 7px 10px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }}
.wf-pivot tr:nth-child(even) td {{ background: #fbfbfb; }}
.wf-pivot td.num {{ text-align: center; font-variant-numeric: tabular-nums; width: 70px; }}
.wf-pivot tfoot td {{ font-weight: bold; background: #f3f3f3 !important; border-top: 2px solid #ddd; }}
.wf-num-passed  {{ color: {WF_PASS}; font-weight: bold; }}
.wf-num-failed  {{ color: {WF_FAIL}; font-weight: bold; }}
.wf-num-skipped {{ color: {WF_SKIP}; }}
.wf-num-zero    {{ color: #c8c8c8; }}

/* Status badges (color-coded, no green). */
.wf-badge {{
    display: inline-block; min-width: 64px; text-align: center;
    padding: 2px 10px; border-radius: 12px; font-size: 11px;
    font-weight: bold; text-transform: uppercase; color: #ffffff; letter-spacing: 0.5px;
}}
.wf-badge.passed  {{ background: {WF_PASS}; }}
.wf-badge.failed  {{ background: {WF_FAIL}; }}
.wf-badge.error   {{ background: {WF_ERROR}; }}
.wf-badge.skipped {{ background: {WF_SKIP}; }}
.wf-badge.untested, .wf-badge.undefined {{ background: #b58a00; }}

/* Mini pass-rate bar inside the feature pivot. */
.wf-bar {{ position: relative; height: 14px; background: #eee; border-radius: 7px; overflow: hidden; min-width: 90px; }}
.wf-bar > span {{ position: absolute; left: 0; top: 0; bottom: 0; background: {WF_ORANGE}; }}
.wf-bar > em {{
    position: relative; display: block; text-align: center; font-style: normal;
    font-size: 10px; line-height: 14px; color: #333; font-weight: bold;
}}

/* Statistics tiles (Features / Scenarios / Steps). */
.wf-stat-grid {{ display: flex; flex-wrap: wrap; gap: 12px; }}
.wf-stat {{ flex: 1 1 200px; border: 1px solid #eee; border-radius: 8px; padding: 12px 14px; }}
.wf-stat h3 {{ margin: 0 0 8px 0; font-size: 12px; text-transform: uppercase; color: #777; letter-spacing: 0.5px; }}
.wf-stat .wf-stat-total {{ font-size: 26px; font-weight: bold; color: #333; }}
.wf-stat .wf-stat-break {{ font-size: 12px; margin-top: 4px; }}
.wf-stat .wf-stat-break span {{ margin-right: 10px; }}

/* -- Override the base formatter's green "passed" styling with WF orange. -- */
.behave table td.passed, td table td.passed, th table td.passed,
.behave ol li.passed, td ol li.passed, th ol li.passed {{
    border-left: 5px solid {WF_ORANGE} !important;
    border-bottom: 1px solid {WF_ORANGE} !important;
    background: #fff1e6 !important;
    color: #9a4f12 !important;
}}
.behave .scenario h3.passed, td .scenario h3.passed,
th .scenario h3.passed, .background h3.passed,
.behave #behave-header.passed {{
    background: {WF_ORANGE} !important;
    color: #ffffff !important;
}}
"""

# JavaScript that filters scenarios by status when a totals link is clicked.
WF_JS = """
window.WF_filterStatus = function (status) {
    var body = document.body;
    var current = body.getAttribute('data-wf-filter') || '';
    var clear = (current === status);
    body.setAttribute('data-wf-filter', clear ? '' : status);

    var scenarios = document.querySelectorAll('.behave .scenario');
    for (var i = 0; i < scenarios.length; i++) {
        var s = scenarios[i].getAttribute('data-status') || 'passed';
        scenarios[i].style.display = (clear || s === status) ? '' : 'none';
    }

    var links = document.querySelectorAll('#totals a.wf-status-link');
    for (var j = 0; j < links.length; j++) {
        var base = links[j].className.replace(/\\s*wf-active/g, '');
        var match = (links[j].getAttribute('data-status') === status);
        links[j].className = (!clear && match) ? base + ' wf-active' : base;
    }
    return false;
};
"""


def _inject_branding(self):
    """Append the brand stylesheet and the status-filter script to <head>, and
    add the environment banner ("behave report for <env> environment") to the
    top of <body>."""
    head = self.html.find("head")
    extra_style = ET.SubElement(head, "style", type="text/css")
    extra_style.append(ET.Comment(WF_CSS))
    script = ET.SubElement(head, "script", type="text/javascript")
    script.append(ET.Comment(WF_JS))

    body = self.html.find("body")
    if body is not None and body.find("div[@class='wf-env-banner']") is None:
        banner = ET.Element("div", {"class": "wf-env-banner"})
        banner.text = Config.REPORT_TITLE
        body.insert(0, banner)


def _fmt_dt(value):
    """Format a datetime for the report, or '-' if missing."""
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else "-"


def _fmt_duration(start, end):
    """Human-friendly elapsed time between two datetimes (e.g. '12m 42s')."""
    if not start or not end:
        return "-"
    total = int((end - start).total_seconds())
    minutes, seconds = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _badge(status):
    """Render a color-coded status badge span."""
    status = (status or "untested").lower()
    return f'<span class="wf-badge {escape(status)}">{escape(status)}</span>'


def _num_cell(count, status):
    """Render a numeric pivot cell, greyed out when zero."""
    cls = "wf-num-zero" if not count else f"wf-num-{status}"
    return f'<td class="num {cls}">{count}</td>'


def _pct(part, whole):
    """Percentage string, or '-' when there is nothing to divide."""
    return f"{(part / whole * 100):.0f}%" if whole else "-"


def _kv_rows(pairs):
    """Render (key, value) pairs as <tr> rows, skipping empties."""
    rows = ""
    for key, value in pairs:
        if value in (None, ""):
            value = "-"
        rows += f'<tr><td class="wf-k">{escape(str(key))}</td><td>{escape(str(value))}</td></tr>'
    return rows


def _build_run_panels(all_features):
    """Build the metadata / summary / scope / failure panels as a single XHTML
    fragment, returned as a list of ElementTree elements ready to insert into
    <body> beneath the environment banner."""
    # -- Flatten scenarios for the summary counts.
    scenarios = [s for f in all_features for s in f.scenarios]
    counter = Counter(s.status.name for s in scenarios)
    total = len(scenarios)
    passed = counter.get("passed", 0)
    failed = counter.get("failed", 0) + counter.get("error", 0)
    skipped = counter.get("skipped", 0)
    rate = f"{(passed / total * 100):.1f}%" if total else "-"

    # -- Execution summary cards.
    cards = (
        '<div class="wf-cards">'
        f'<div class="wf-card wf-c-total"><span class="wf-num">{total}</span><span class="wf-lbl">Total</span></div>'
        f'<div class="wf-card wf-c-passed"><span class="wf-num">{passed}</span><span class="wf-lbl">Passed</span></div>'
        f'<div class="wf-card wf-c-failed"><span class="wf-num">{failed}</span><span class="wf-lbl">Failed</span></div>'
        f'<div class="wf-card wf-c-skipped"><span class="wf-num">{skipped}</span><span class="wf-lbl">Skipped</span></div>'
        f'<div class="wf-card wf-c-rate"><span class="wf-num">{rate}</span><span class="wf-lbl">Pass Rate</span></div>'
        "</div>"
    )
    summary_kv = _kv_rows(
        [
            ("Environment", (RUN.get("env") or "").upper()),
            ("Started", _fmt_dt(RUN.get("start"))),
            ("Finished", _fmt_dt(RUN.get("end"))),
            ("Duration", _fmt_duration(RUN.get("start"), RUN.get("end"))),
        ]
    )
    summary_panel = (
        '<div class="wf-panel"><h2>Execution Summary</h2><div class="wf-panel-body">'
        f'{cards}<table class="wf-kv">{summary_kv}</table>'
        "</div></div>"
    )

    # -- Environment + credentials/owner side by side.
    env_kv = _kv_rows(
        [
            ("Application URL", RUN.get("url")),
            ("Browser", RUN.get("browser")),
            ("Operating System", RUN.get("os")),
            ("Execution Type", RUN.get("exec_type")),
            ("Git Branch", RUN.get("branch")),
            ("Git Commit", RUN.get("commit")),
        ]
    )
    cred_kv = _kv_rows(
        [
            ("User Role", RUN.get("role")),
            ("Test Account", RUN.get("user")),
            ("Execution Owner", RUN.get("owner")),
            ("Report Generated", _fmt_dt(RUN.get("end") or RUN.get("start"))),
        ]
    )
    context_panel = (
        '<div class="wf-panel"><h2>Test Environment &amp; Credentials</h2>'
        '<div class="wf-panel-body wf-cols">'
        f'<div><table class="wf-kv">{env_kv}</table></div>'
        f'<div><table class="wf-kv">{cred_kv}</table></div>'
        "</div></div>"
    )

    # -- Execution scope: one row per feature (module) with scenario/step counts.
    scope_rows = ""
    for feature in all_features:
        feat_scenarios = list(feature.scenarios)
        step_count = sum(len(s.steps) for s in feat_scenarios)
        feat_counter = Counter(s.status.name for s in feat_scenarios)
        feat_failed = feat_counter.get("failed", 0) + feat_counter.get("error", 0)
        result = "PASS" if feat_failed == 0 else f"{feat_failed} FAILED"
        scope_rows += (
            "<tr>"
            f"<td>{escape(feature.name or '')}</td>"
            f"<td>{len(feat_scenarios)}</td>"
            f"<td>{step_count}</td>"
            f"<td>{escape(result)}</td>"
            "</tr>"
        )
    scope_panel = (
        '<div class="wf-panel"><h2>Execution Scope</h2><div class="wf-panel-body">'
        '<table class="wf-scope-table"><tr><th>Module / Feature</th><th>Scenarios</th>'
        f"<th>Steps</th><th>Result</th></tr>{scope_rows}</table>"
        "</div></div>"
    )

    # ------------------------------------------------------------------
    # Pivot-style overview: quick read of the whole run before the details.
    # ------------------------------------------------------------------
    all_steps = [st for s in scenarios for st in s.steps]

    # 1) Test-result statistics tiles: Features / Scenarios / Steps.
    def _stat_tile(title, items):
        c = Counter(i.status.name for i in items)
        p = c.get("passed", 0)
        f = c.get("failed", 0) + c.get("error", 0)
        sk = c.get("skipped", 0)
        return (
            f'<div class="wf-stat"><h3>{escape(title)}</h3>'
            f'<div class="wf-stat-total">{len(items)}</div>'
            '<div class="wf-stat-break">'
            f'<span class="wf-num-passed">{p} passed</span>'
            f'<span class="wf-num-failed">{f} failed</span>'
            f'<span class="wf-num-skipped">{sk} skipped</span>'
            "</div></div>"
        )

    stats_panel = (
        '<div class="wf-panel"><h2>Test Result Statistics</h2>'
        '<div class="wf-panel-body wf-stat-grid">'
        f"{_stat_tile('Features', all_features)}"
        f"{_stat_tile('Scenarios', scenarios)}"
        f"{_stat_tile('Steps', all_steps)}"
        "</div></div>"
    )

    # 2) Feature vs Passed/Failed pivot, with a totals footer and pass-rate bar.
    feat_rows = ""
    tot_sc = tot_p = tot_f = tot_sk = 0
    for feature in all_features:
        fs = list(feature.scenarios)
        c = Counter(s.status.name for s in fs)
        p = c.get("passed", 0)
        f = c.get("failed", 0) + c.get("error", 0)
        sk = c.get("skipped", 0)
        tot_sc += len(fs); tot_p += p; tot_f += f; tot_sk += sk
        rate = _pct(p, len(fs))
        width = (p / len(fs) * 100) if fs else 0
        feat_rows += (
            "<tr>"
            f"<td>{escape(feature.name or '')}</td>"
            f'<td class="num">{len(fs)}</td>'
            f"{_num_cell(p, 'passed')}"
            f"{_num_cell(f, 'failed')}"
            f"{_num_cell(sk, 'skipped')}"
            f'<td><div class="wf-bar"><span style="width:{width:.0f}%"> </span><em>{rate}</em></div></td>'
            "</tr>"
        )
    feat_panel = (
        '<div class="wf-panel"><h2>Feature vs Passed / Failed Scenarios</h2>'
        '<div class="wf-panel-body">'
        '<table class="wf-pivot"><thead><tr>'
        "<th>Feature</th><th>Scenarios</th><th>Passed</th><th>Failed</th>"
        "<th>Skipped</th><th>Pass Rate</th></tr></thead><tbody>"
        f"{feat_rows}</tbody>"
        "<tfoot><tr><td>Total</td>"
        f'<td class="num">{tot_sc}</td>'
        f"{_num_cell(tot_p, 'passed')}"
        f"{_num_cell(tot_f, 'failed')}"
        f"{_num_cell(tot_sk, 'skipped')}"
        f'<td><div class="wf-bar"><span style="width:{(tot_p / tot_sc * 100) if tot_sc else 0:.0f}%"> </span>'
        f"<em>{_pct(tot_p, tot_sc)}</em></div></td></tr></tfoot>"
        "</table></div></div>"
    )

    # 3) Scenario vs Execution Status pivot.
    scn_rows = ""
    for feature in all_features:
        for s in feature.scenarios:
            dur = getattr(s, "duration", None)
            dur_txt = f"{dur:.2f}s" if isinstance(dur, (int, float)) else "-"
            scn_rows += (
                "<tr>"
                f"<td>{escape(feature.name or '')}</td>"
                f"<td>{escape(s.name or '')}</td>"
                f"<td>{_badge(s.status.name)}</td>"
                f'<td class="num">{len(s.steps)}</td>'
                f'<td class="num">{dur_txt}</td>'
                "</tr>"
            )
    scn_panel = (
        '<div class="wf-panel"><h2>Scenario vs Execution Status</h2>'
        '<div class="wf-panel-body">'
        '<table class="wf-pivot"><thead><tr>'
        "<th>Feature</th><th>Scenario</th><th>Status</th><th>Steps</th>"
        "<th>Duration</th></tr></thead><tbody>"
        f"{scn_rows}</tbody></table></div></div>"
    )

    # -- Failure analysis (only when there are failures).
    panels = summary_panel + context_panel + scope_panel + stats_panel + feat_panel + scn_panel
    failures = RUN.get("failures") or []
    if failures:
        fail_rows = ""
        for item in failures:
            shot = item.get("screenshot")
            shot_cell = (
                f'<a href="{escape(shot)}" target="_blank">View</a>' if shot else "-"
            )
            error = escape(item.get("error") or "-")
            fail_rows += (
                "<tr>"
                f"<td>{escape(item.get('feature') or '')}</td>"
                f"<td>{escape(item.get('scenario') or '')}</td>"
                f'<td><span class="wf-fail-cat">{escape(item.get("category") or "Needs triage")}</span></td>'
                f"<td><pre>{error}</pre></td>"
                f"<td>{shot_cell}</td>"
                "</tr>"
            )
        fail_panel = (
            '<div class="wf-panel"><h2>Failure Analysis</h2><div class="wf-panel-body">'
            '<table class="wf-fail-table"><tr><th>Feature</th><th>Scenario</th>'
            "<th>Category</th><th>Error</th><th>Screenshot</th></tr>"
            f"{fail_rows}</table></div></div>"
        )
        panels += fail_panel

    wrapper = ET.fromstring(f"<div>{panels}</div>")
    return list(wrapper)


def apply_branding():
    """Monkey-patch the upstream ``HTMLFormatter`` so the stock
    ``-f behave_html_formatter:HTMLFormatter`` command produces the Wadhwani
    Foundation themed report with full status totals and clickable status links.

    Call this from ``environment.py`` (loaded before formatters are created).
    """
    if getattr(HTMLFormatter, "_wf_branded", False):
        return

    original_init = HTMLFormatter.__init__

    def branded_init(self, stream, config):
        original_init(self, stream, config)
        _inject_branding(self)

    HTMLFormatter.__init__ = branded_init
    HTMLFormatter._fill_totals = WFHTMLFormatter._fill_totals
    HTMLFormatter._tag_scenario_statuses = WFHTMLFormatter._tag_scenario_statuses
    HTMLFormatter.close = WFHTMLFormatter.close
    HTMLFormatter._wf_branded = True


class WFHTMLFormatter(HTMLFormatter):
    """HTML formatter with Wadhwani Foundation branding and full status totals."""

    name = "html"
    description = "Wadhwani Foundation themed HTML formatter"

    def __init__(self, stream, config):
        super().__init__(stream, config)
        # Append the brand stylesheet/script after the base theme so they win.
        _inject_branding(self)

    def _fill_totals(self, element, label, items, linkable=False):
        """Render ``label`` + per-status counts, always including the core statuses.

        When ``linkable`` is true each status is rendered as an ``<a>`` that
        filters the report down to scenarios with that status (handled by the
        ``WF_filterStatus`` script).
        """
        counter = Counter(item.status.name for item in items)

        # Core statuses first (so failed:0 / error:0 always render), then any
        # extra statuses that actually occurred (e.g. undefined).
        ordered = list(ALWAYS_SHOWN_STATUSES)
        ordered += [s for s in counter if s not in ALWAYS_SHOWN_STATUSES]

        element.text = label + " "
        last = len(ordered) - 1
        for index, status in enumerate(ordered):
            text = f"{status}: {counter.get(status, 0)}"
            if linkable:
                node = ET.SubElement(
                    element,
                    "a",
                    {
                        "class": f"total-{status} wf-status-link",
                        "data-status": status,
                        "href": "#",
                        "onclick": f"return WF_filterStatus('{status}')",
                    },
                )
            else:
                node = ET.SubElement(element, "span", {"class": f"total-{status}"})
            node.text = text
            if index != last:
                node.tail = ", "

    def _tag_scenario_statuses(self, scenarios):
        """Stamp each scenario ``<div>`` with its final status so the status
        links can show/hide them.

        Scenario ``<div>`` elements appear in document order, matching the order
        of the flattened ``scenarios`` list, so we can pair them up positionally.
        """
        scenario_els = [
            el
            for el in self.suite.iter("div")
            if "scenario" in (el.get("class") or "").split()
        ]
        for el, scenario in zip(scenario_els, scenarios):
            status = scenario.status.name
            el.set("data-status", status)
            existing = el.get("class", "")
            if f"wf-status-{status}" not in existing.split():
                el.set("class", f"{existing} wf-status-{status}".strip())

    def close(self):
        if not hasattr(self, "all_features"):
            self.all_features = []
        self.duration.text = (
            f"Finished in {sum(x.duration for x in self.all_features):0.1f} seconds"
        )

        # check if self.last_scenario is failed
        self._check_last_scenario_status()

        # -- Features summary
        self._fill_totals(self.current_feature_totals, "Features:", self.all_features)

        # -- Scenarios summary (clickable status links)
        scenarios_list = [x.scenarios for x in self.all_features]
        scenarios = [x for subl in scenarios_list for x in subl] if scenarios_list else []
        self._fill_totals(self.scenario_totals, "Scenarios:", scenarios, linkable=True)
        self._tag_scenario_statuses(scenarios)

        # -- Steps summary
        step_list = [x.steps for x in scenarios]
        steps = [x for subl in step_list for x in subl] if step_list else []
        self._fill_totals(self.step_totals, "Steps:", steps)

        # -- Insert the run metadata / scope / failure panels just beneath the
        # environment banner so the report opens as a single source of truth.
        body = self.html.find("body")
        if body is not None and self.all_features:
            insert_at = 1 if body.find("div[@class='wf-env-banner']") is not None else 0
            for offset, panel in enumerate(_build_run_panels(self.all_features)):
                body.insert(insert_at + offset, panel)

        # Sending the report to stream
        if len(self.all_features) > 0:
            self.stream.write("<!DOCTYPE HTML>")
            self.stream.write(ET_tostring(self.html, pretty_print=False))
