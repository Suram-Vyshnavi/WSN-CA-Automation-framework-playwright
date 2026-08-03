---
name: report-no-green-pass
description: HTML test report styling must use Wadhwani brand colours only, no green for passed
metadata:
  type: feedback
---

The WF HTML test report must use only Wadhwani Foundation brand colours — red (#E2231A) and orange (#F58220) — and must NOT use green for passed status.

**Why:** Brand consistency; the user explicitly rejected green for pass.

**How to apply:** In `utils/wf_html_formatter.py`, passed = orange (WF_PASS), failed = red (WF_FAIL), error = dark red (#A30D08), skipped = grey. Overrides for the base `behave_html_formatter` green (`#65c400`/`#dbffb4`/`#3d7700`) are appended after the base CSS with `!important`.
