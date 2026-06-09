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
from collections import Counter

from behave_html_formatter.html import HTMLFormatter, ET_tostring


# -- Wadhwani Foundation brand colours.
WF_RED = "#E2231A"
WF_ORANGE = "#F58220"

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
#summary #totals .total-passed  {{ color: #1f7a1f; font-weight: bold; }}
#summary #totals .total-failed  {{ color: {WF_RED}; font-weight: bold; }}
#summary #totals .total-error   {{ color: {WF_ORANGE}; font-weight: bold; }}
#summary #totals .total-skipped {{ color: #888888; }}
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
    """Append the brand stylesheet and the status-filter script to <head>."""
    head = self.html.find("head")
    extra_style = ET.SubElement(head, "style", type="text/css")
    extra_style.append(ET.Comment(WF_CSS))
    script = ET.SubElement(head, "script", type="text/javascript")
    script.append(ET.Comment(WF_JS))


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

        # Sending the report to stream
        if len(self.all_features) > 0:
            self.stream.write("<!DOCTYPE HTML>")
            self.stream.write(ET_tostring(self.html, pretty_print=False))
