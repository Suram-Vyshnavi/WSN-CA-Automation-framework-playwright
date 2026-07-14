# -*- coding: utf-8 -*-
"""Shared, process-wide run metadata for the Wadhwani Foundation HTML report.

``environment.py`` populates :data:`RUN` in ``before_all`` / ``after_all`` /
``after_scenario`` and the :class:`WFHTMLFormatter` reads it in ``close()`` to
render the metadata, scope and failure-analysis panels.  A plain module-level
dict is used so the formatter (created independently by behave) and the
environment hooks share the same state without threading it through ``context``.
"""

# Populated by features/environment.py; consumed by utils/wf_html_formatter.py.
RUN = {
    # -- Environment / execution context (filled in before_all)
    "env": None,            # e.g. "dev" / "prod"
    "url": None,            # application base URL under test
    "browser": None,        # e.g. "Chromium 120.0.6099.71"
    "os": None,             # e.g. "Windows 11"
    "exec_type": None,      # "Local" or "CI/CD"
    "owner": None,          # who ran it
    "role": None,           # user role exercised, e.g. "student"
    "user": None,           # masked username/email
    "branch": None,         # git branch
    "commit": None,         # git short commit
    # -- Timing (start in before_all, end in after_all)
    "start": None,          # datetime
    "end": None,            # datetime
    # -- Failure analysis (appended in after_scenario)
    # Each entry: {"feature", "scenario", "category", "error", "screenshot"}
    "failures": [],
}


def mask_email(value):
    """Mask the local part of an email/username for the report.

    ``ca-automation@yopmail.com`` -> ``ca-***@yopmail.com``.  Falls back to a
    generic mask for non-email values so secrets never leak into the report.
    """
    if not value:
        return value
    if "@" in value:
        local, _, domain = value.partition("@")
        keep = local[:2] if len(local) > 2 else local[:1]
        return f"{keep}***@{domain}"
    return value[:2] + "***"
