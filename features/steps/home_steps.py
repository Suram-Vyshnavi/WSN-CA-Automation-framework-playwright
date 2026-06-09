from behave import given, then

from pages.student.home_page import HomePage
from utils.config import Config


def _home_page(context) -> HomePage:
    if not hasattr(context, "home_page"):
        context.home_page = HomePage(context.page)
    return context.home_page


@given("user is on homepage")
def step_user_is_on_homepage(context):
    context.login_page.ensure_logged_in(Config.USERNAME, Config.PASSWORD)
    _home_page(context).click_congratulations_close_button()
    _home_page(context).click_matches_roles_section()


@then("user validates the ministry of education logo in homepage")
def step_validate_ministry_logo(context):
    _home_page(context).validate_ministry_of_education_logo()


@then("user validates the ncert logo in homepage")
def step_validate_ncert_logo(context):
    _home_page(context).validate_ncert_logo()


@then("user validates the wf logo in homepage")
def step_validate_wf_logo(context):
    _home_page(context).validate_wf_logo()


@then("user clicks on matches roles section")
def step_click_matches_roles_section(context):
    _home_page(context).click_matches_roles_section()


@then("user selects passions preferences")
def step_select_passions_preferences(context):
    _home_page(context).select_passions_preferences()


@then("user selects review passions preferences")
def step_select_review_passions_preferences(context):
    _home_page(context).select_review_passions_preferences()


@then("user validates the selected items in passions review section")
def step_validate_selected_items_in_passions_review(context):
    _home_page(context).validate_selected_items_in_passions_review()


@then("user click on submit button in passions section")
def step_click_submit_button(context):
    _home_page(context).click_submit_button()


@then("user clicks on questionnaires section")
def step_click_questionnaires_section(context):
    _home_page(context).click_questionnaires_section()


@then("user clicks on interests card in questionnaires section and clicks on reattempt button")
def step_click_interests_card_questionnaire_reattempt(context):
    _home_page(context).open_interests_questionnaire_reattempt()


@then("user clicks on questionnaries choose button and clicks on question cards and click on next button")
def step_choose_questionnaire_and_answer_first(context):
    _home_page(context).choose_questionnaire_and_answer_first_question()


@then("user attempts all the questions in interests section and clicks on next button")
def step_answer_all_interests_questions(context):
    _home_page(context).answer_all_interests_questions()


@then("user clicks start aptitudes and answer all the questions in aptitudes section and clicks on next button")
def step_start_aptitudes_and_answer_all(context):
    _home_page(context).start_aptitudes_and_answer_all()


@then("user clicks on start values and answer all the questions in values section and clicks on next button")
def step_start_values_and_answer_all(context):
    _home_page(context).start_values_and_answer_all()


@then("user clicks on interests card and clicks on reattempt button")
def step_click_interests_card_and_reattempt(context):
    _home_page(context).click_interests_card_and_reattempt()


@then("user clicks on aptitudes card and clicks on reattempt button")
def step_click_aptitudes_card_and_reattempt(context):
    _home_page(context).click_aptitudes_card_and_reattempt()


@then("user clicks on values card and clicks on reattempt button")
def step_click_values_card_and_reattempt(context):
    _home_page(context).click_values_card_and_reattempt()


@then("user slides the slider to 7 or 8 or 8 or 7 and clicks on next button")
def step_slide_slider_and_click_next(context):
    _home_page(context).slide_slider_and_click_next_through_questions()


@then("user clicks on submit button in interests section")
def step_click_submit_interests_section(context):
    _home_page(context).click_submit_questionnaire()


@then("user clicks on submit button in aptitudes section")
def step_click_submit_aptitudes_section(context):
    _home_page(context).click_submit_questionnaire()


@then("user clicks on submit button in values section")
def step_click_submit_values_section(context):
    _home_page(context).click_submit_questionnaire()


@then("user clicks on backarrow button")
def step_click_back_arrow(context):
    _home_page(context).click_back_arrow()


@then("user clicks on review button in aptitudes section")
def step_click_first_aptitudes_review_button(context):
    _home_page(context).complete_aptitudes_first_flow()


@then("user clicks on reattempt")
def step_click_reattempt(context):
    _home_page(context).click_reattempt()


@then("user chooses slider option in aptitudes section")
def step_choose_slider_option_aptitudes(context):
    _home_page(context).choose_slider_option()


@then("user clicks on 1st question and changes the slider value to 9 or 10 and clicks on update")
def step_update_first_slider_value(context):
    _home_page(context).update_first_question_slider_value()


@then("user clicks on Go to matched roles")
def step_click_go_to_matched_roles(context):
    _home_page(context).click_go_to_matched_roles()


@then("user clicks on without college degree and validate the recommended roles")
def step_click_without_college_degree_and_validate_roles(context):
    _home_page(context).click_without_college_degree()
    _home_page(context).validate_recommended_roles()


@then("user clicks on search roles")
def step_click_search_roles(context):
    _home_page(context).click_search_roles()


@then("user enters jobrole and add the first job as add saved")
def step_enter_jobrole_and_add_first_job_as_saved(context):
    job_role = "Automation"
    _home_page(context).enter_jobrole_and_add_first_job_as_saved(job_role)


@then("user clicks on save menu header and validates the saved job")
def step_click_save_menu_header_and_validate_saved_job(context):
    _home_page(context).click_save_menu_header_and_validate_saved_job()


@then("user clicks on compare roles and validates the compare roles header")
def step_click_compare_roles_and_validate_header(context):
    _home_page(context).click_compare_roles_and_validate_header()


@then("user clicks on first and second checkbox in search results and clicks on compare button")
def step_click_first_second_checkbox_and_compare(context):
    _home_page(context).click_first_second_checkbox_and_compare()


@then("user clicks on share report and click and validates the share report options")
def step_click_share_report_and_validate_options(context):
    _home_page(context).click_share_report_and_validate_options()


@then("user validates self review, matched roles, and favourite roles tabs in share report section")
def step_validate_share_report_tabs(context):
    _home_page(context).validate_share_report_tabs()


@then("user clicks on Favourites and removes the added job from favourites")
def step_click_favourites_and_remove_added_job(context):
    _home_page(context).click_favourites_and_remove_added_job()


@then("user clicks on help icon")
def step_click_help_icon(context):
    _home_page(context).click_help_icon()


@then("user clicks on about icon")
def step_click_about_icon(context):
    _home_page(context).click_about_icon()


@then("user logout")
def step_user_logout(context):
    context.login_page.logout()
