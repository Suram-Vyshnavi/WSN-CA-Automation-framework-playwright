import os
from pathlib import Path

import allure
from allure_commons.types import AttachmentType
from pages.student.login_page import LoginPage
from utils.playwright_factory import PlaywrightFactory
from utils.config import Config
from utils.wf_html_formatter import apply_branding

# Brand the stock behave HTML formatter (red/orange + full status totals) so the
# `-f behave_html_formatter:HTMLFormatter` command produces the themed report.
apply_branding()


def _resolve_report_dir(context):
    """Return the Allure results directory passed to behave via -o, if any."""
    for output in getattr(context.config, "outputs", []) or []:
        name = getattr(output, "name", None)
        if name and name not in ("-", "stdout", "stderr"):
            return os.path.abspath(name)
    return None


def before_scenario(context, scenario):
    factory = PlaywrightFactory()
    context.playwright, context.browser, context.context, context.page = factory.start()
    context.login_page = LoginPage(context.page)
    context.login_page.goto(Config.BASE_URL)
    try:
        context.login_page.click_no_thanks()
    except Exception:
        pass


def after_scenario(context, scenario):
    status = str(getattr(scenario, "status", "")).lower()
    if status == "failed":
        allure.attach(
            context.page.screenshot(),
            name="Failure Screenshot",
            attachment_type=AttachmentType.PNG,
        )
    context.context.close()
    context.browser.close()
    context.playwright.stop()

    report_dir = _resolve_report_dir(context)
    if report_dir:
        link = Path(report_dir).as_uri()
        print(f"Allure report generated at: {link}")
    else:
        print("Allure report directory not found (run behave with -o <dir>).")
