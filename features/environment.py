import allure
from allure_commons.types import AttachmentType
from pages.student.login_page import LoginPage
from utils.playwright_factory import PlaywrightFactory
from utils.config import Config


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
