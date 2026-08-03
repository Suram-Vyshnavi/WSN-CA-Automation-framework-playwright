import re
from pathlib import Path

from behave import then

from pages.student.new_user_page import NewUserPage

SCREENSHOT_DIR = Path("reports/html-report/screenshots")

# NOTE: Steps for answering the interests/aptitudes/values questionnaires use the
# same wording as the homepage scenario, so they are already defined in
# home_steps.py. Behave registers step definitions globally, so re-defining them
# here would raise an AmbiguousStep error. They are reused as-is (running through
# HomePage); only the steps unique to the new-user journey are defined below.
#
# Each new-user step runs through _run(), which validates the step's result and -
# if anything fails - records the failure and CONTINUES instead of aborting, so a
# failure in one step does not block the remaining steps. All collected failures
# are reported at the end of the scenario (see features/environment.py).


def _new_user_page(context) -> NewUserPage:
    if not hasattr(context, "new_user_page"):
        context.new_user_page = NewUserPage(context.page)
    return context.new_user_page


def _run(context, action, name):
    """Run a step action softly: log the outcome, and on failure record it and keep
    going so subsequent steps still execute."""
    if not hasattr(context, "step_failures"):
        context.step_failures = []
    try:
        action()
        print(f"[PASS] {name}")
    except Exception as exc:  # noqa: BLE001 - intentionally broad: keep the run going
        print(f"[FAIL] {name}: {exc}")
        context.step_failures.append(f"{name}: {exc}")
        # environment.py's after_scenario only screenshots once, at the very end
        # of the whole scenario - by then later steps have moved the page well
        # past whatever was actually on screen when THIS step failed. Capture
        # one here, at the moment of failure, so a soft-failure that happens
        # mid-journey (e.g. the first job's Save/Back buttons never appearing)
        # can actually be diagnosed instead of guessed at.
        try:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", name)[:80]
            context.page.screenshot(path=str(SCREENSHOT_DIR / f"stepfail_{slug}.png"))
        except Exception:
            pass


@then("user clicks on create new button and enters the email")
def step_click_create_new_and_enter_email(context):
    _run(context, _new_user_page(context).click_create_new_and_enter_email,
         "create new + enter email")


@then("user clicks on generate OTP button and enters the OTP and clicks on verify button")
def step_click_generate_otp_enter_otp_submit(context):
    _run(context, _new_user_page(context).click_generate_otp_enter_otp_submit,
         "generate OTP + OTP + verify + set password")


@then("user fills all the details name,state,grade, school name,checkbox and clicks on submit button")
def step_fill_personal_details(context):
    _run(context, _new_user_page(context).fill_personal_details, "fill personal details")


@then("user validates welcome popup image and clicks on next button")
def step_validate_welcome_popup_and_next(context):
    _run(context, _new_user_page(context).validate_welcome_popup_and_next, "welcome popup + next")


@then("user clicks on passion card startnow button")
def step_click_passion_card_start_now(context):
    _run(context, _new_user_page(context).click_passion_card_start_now, "passions Start Now")


@then("user clicks on selected passions items and clicks on submit button")
def step_select_passions_and_submit(context):
    _run(context, _new_user_page(context).select_passions_and_submit, "select passions + submit")


@then("user clicks on questionnaire card startnow button")
def step_click_questionnaire_card_start_now(context):
    _run(context, _new_user_page(context).click_questionnaire_card_start_now,
         "questionnaire Start Now")


@then("user clicks on one pick male character image")
def step_pick_male_character_and_start_now(context):
    _run(context, _new_user_page(context).pick_male_character_and_start_now,
         "pick male character + Start Now")


@then("user answers all the questionnaire questions until the profile setup is completed")
def step_answer_all_questionnaire_questions(context):
    _run(context, _new_user_page(context).answer_all_questionnaire_questions,
         "answer all questionnaire questions")


@then("user clicks on pick roles card")
def step_click_pick_roles_card(context):
    _run(context, _new_user_page(context).click_pick_roles_card, "pick roles card")


@then("user clicks on got it button")
def step_click_got_it_button(context):
    _run(context, _new_user_page(context).click_got_it_button, "Got It button")


@then("user clicks on firstjob role and clicks on like image button and clicks on first save button")
def step_click_first_job_and_save(context):
    _run(context, _new_user_page(context).click_first_job_and_save, "first job + like + save")


@then("user clicks on first back button")
def step_click_first_back(context):
    _run(context, _new_user_page(context).click_first_back, "first back")


@then("user clicks on secondjob role and clicks on second save button")
def step_click_second_job_and_save(context):
    _run(context, _new_user_page(context).click_second_job_and_save, "second job + save")


@then("user clicks on second back button")
def step_click_second_back(context):
    _run(context, _new_user_page(context).click_second_back, "second back")


@then("user clicks on thirdjob role and clicks on third save button")
def step_click_third_job_and_save(context):
    _run(context, _new_user_page(context).click_third_job_and_save, "third job + save")


@then("user clicks on third back button")
def step_click_third_back(context):
    _run(context, _new_user_page(context).click_third_back, "third back")


@then("user validates the feedback popup and clicks on mca stars button and clicks on next button and closes the popup")
def step_validate_feedback_popup_and_close(context):
    _run(context, _new_user_page(context).validate_feedback_popup_and_close, "feedback popup")


@then("user clicks on profile icon and clicks on logout button")
def step_logout(context):
    _run(context, _new_user_page(context).logout, "logout")
