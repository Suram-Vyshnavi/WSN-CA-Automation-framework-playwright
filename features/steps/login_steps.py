from behave import given, then, when

from utils.config import Config


@given("user is on the login page")
def step_user_is_on_login_page(context):
    assert hasattr(context, "login_page"), "Login page is not initialized in hook"
    assert context.page.url.startswith(Config.BASE_URL), (
        f"Expected page to open under {Config.BASE_URL}, got {context.page.url}"
    )


@when("user enters valid credentials")
def step_user_enters_valid_credentials(context):
    context.login_page.ensure_logged_in(Config.USERNAME, Config.PASSWORD)


@then("user should be logged in successfully")
def step_user_should_be_logged_in_successfully(context):
    assert context.login_page.is_logged_in(), "User is not logged in successfully"


@then("user should be logged in and logout successfully")
def step_user_should_be_logged_in_and_logout_successfully(context):
    assert context.login_page.is_logged_in(), "User is not logged in successfully"
    context.login_page.logout()
    assert context.login_page.is_logged_out(), "User is not logged out successfully"