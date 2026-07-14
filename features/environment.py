import datetime
import os
import platform
import re
import subprocess
from pathlib import Path

import allure
from allure_commons.types import AttachmentType
from pages.student.login_page import LoginPage
from utils.playwright_factory import PlaywrightFactory
from utils.config import Config
from utils.run_metadata import RUN, mask_email
from utils.wf_html_formatter import apply_branding

# Brand the stock behave HTML formatter (red/orange + full status totals) so the
# `-f behave_html_formatter:HTMLFormatter` command produces the themed report.
apply_branding()

# Screenshots for the HTML report live next to report.html so the report can
# link to them with a simple relative path.
HTML_REPORT_DIR = Path("reports/html-report")
SCREENSHOT_DIR = HTML_REPORT_DIR / "screenshots"

# Scenario tag -> failure category shown in the report's Failure Analysis panel.
FAILURE_CATEGORIES = {
    "app-issue": "Application Issue",
    "script-issue": "Test Script Issue",
    "env-issue": "Environment Issue",
}


def _git(*args):
    """Return the stripped output of a git command, or None if git is unavailable."""
    try:
        return subprocess.check_output(
            ["git", *args], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return None


def _browser_version():
    """Launch a throwaway headless browser just to read its real version string."""
    try:
        playwright, browser, ctx, _ = PlaywrightFactory().start(headless=True)
        version = f"{browser.browser_type.name.title()} {browser.version}"
        ctx.close()
        browser.close()
        playwright.stop()
        return version
    except Exception:
        return None


def _failure_category(scenario):
    """Map a scenario's tags to a failure category, defaulting to 'Needs triage'."""
    for tag in getattr(scenario, "tags", []) or []:
        if tag in FAILURE_CATEGORIES:
            return FAILURE_CATEGORIES[tag]
    return "Needs triage"


def _scenario_error(scenario):
    """Concatenate error messages from the scenario's failed steps."""
    messages = []
    for step in getattr(scenario, "steps", []) or []:
        if str(getattr(step, "status", "")).lower() in ("failed", "error"):
            msg = getattr(step, "error_message", None)
            messages.append(f"{step.keyword} {step.name}\n{msg}" if msg else f"{step.keyword} {step.name}")
    return "\n\n".join(messages) if messages else None


def before_all(context):
    """Capture the execution context, start the shared browser and login once."""
    RUN["start"] = datetime.datetime.now()
    RUN["env"] = Config.ENVIRONMENT
    RUN["url"] = Config.BASE_URL
    RUN["os"] = f"{platform.system()} {platform.release()}"
    RUN["exec_type"] = "CI/CD" if os.getenv("CI") else "Local"
    RUN["owner"] = os.getenv("EXEC_OWNER") or os.getenv("USERNAME") or os.getenv("USER")
    RUN["role"] = Config.USER_TYPE
    RUN["user"] = mask_email(Config.USERNAME)
    RUN["branch"] = _git("rev-parse", "--abbrev-ref", "HEAD")
    RUN["commit"] = _git("rev-parse", "--short", "HEAD")
    RUN["browser"] = _browser_version()

    # Open the browser ONCE and login — shared across every scenario in the run.
    factory = PlaywrightFactory()
    context.playwright, context.browser, context.context, context.page = factory.start()
    context.login_page = LoginPage(context.page)
    context.login_page.goto(Config.BASE_URL)
    try:
        context.login_page.click_no_thanks()
    except Exception:
        pass
    context.login_page.ensure_logged_in(Config.USERNAME, Config.PASSWORD)


def after_all(context):
    """Stamp the end time, logout and close the shared browser."""
    RUN["end"] = datetime.datetime.now()
    try:
        if context.login_page.is_logged_in():
            context.login_page.logout()
    except Exception:
        pass
    try:
        context.context.close()
        context.browser.close()
        context.playwright.stop()
    except Exception:
        pass


def _resolve_report_dir(context):
    """Return the Allure results directory passed to behave via -o, if any."""
    for output in getattr(context.config, "outputs", []) or []:
        name = getattr(output, "name", None)
        if name and name not in ("-", "stdout", "stderr"):
            return os.path.abspath(name)
    return None


def before_scenario(context, scenario):
    context.step_failures = []
    # Navigate to the base URL to reset page state before each scenario.
    context.login_page.goto(Config.BASE_URL)
    try:
        context.login_page.click_no_thanks()
    except Exception:
        pass
    # The New User journey must start from the login page while logged out
    # (it registers a fresh account). For every other scenario, ensure the
    # shared session is still authenticated.
    if getattr(scenario.feature, "name", "") == "NewUser":
        try:
            if context.login_page.is_logged_in():
                context.login_page.logout()
        except Exception:
            pass
    else:
        context.login_page.ensure_logged_in(Config.USERNAME, Config.PASSWORD)


def after_scenario(context, scenario):
    status = str(getattr(scenario, "status", "")).lower()
    # Soft step failures: steps that validated their result, failed, but let the
    # run continue so later steps still executed (see new_user_steps._run).
    soft_failures = getattr(context, "step_failures", [])
    if status == "failed" or soft_failures:
        screenshot_bytes = None
        try:
            screenshot_bytes = context.page.screenshot()
            allure.attach(
                screenshot_bytes,
                name="Failure Screenshot",
                attachment_type=AttachmentType.PNG,
            )
        except Exception:
            pass

        # Also drop the screenshot next to report.html so the WF HTML report can
        # link to it, and record this failure for the Failure Analysis panel.
        screenshot_rel = None
        if screenshot_bytes:
            try:
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", scenario.name)[:80]
                shot_path = SCREENSHOT_DIR / f"{slug}.png"
                shot_path.write_bytes(screenshot_bytes)
                screenshot_rel = f"screenshots/{shot_path.name}"
            except Exception:
                screenshot_rel = None

        RUN["failures"].append(
            {
                "feature": getattr(getattr(scenario, "feature", None), "name", ""),
                "scenario": scenario.name,
                "category": _failure_category(scenario),
                "error": "\n".join(str(f) for f in soft_failures) or _scenario_error(scenario),
                "screenshot": screenshot_rel,
            }
        )

    # Browser is kept open — it is closed once in after_all.
    report_dir = _resolve_report_dir(context)
    if report_dir:
        link = Path(report_dir).as_uri()
        print(f"Allure report generated at: {link}")
    else:
        print("Allure report directory not found (run behave with -o <dir>).")

    if soft_failures:
        print("\n==== STEP FAILURES (run continued past these) ====")
        for failure in soft_failures:
            print(f" - {failure}")
        print("==================================================")
        # Mark the scenario failed now that every step has had a chance to run.
        try:
            scenario.set_status("failed")
        except Exception:
            pass
