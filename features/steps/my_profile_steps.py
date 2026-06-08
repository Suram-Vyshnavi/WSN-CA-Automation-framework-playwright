from behave import then

from pages.student.my_profile_page import MyProfilePage

# Name used while editing the profile. The original name is captured at runtime
# so it can be restored during the revert step.
EDITED_FIRST_NAME = "AutomationTest"


def _my_profile_page(context) -> MyProfilePage:
    if not hasattr(context, "my_profile_page"):
        context.my_profile_page = MyProfilePage(context.page)
    return context.my_profile_page


@then("user clicks on my profile icon")
def step_click_my_profile_icon(context):
    _my_profile_page(context).click_my_profile_icon()


@then("user clicks on my profile")
def step_click_my_profile(context):
    _my_profile_page(context).click_my_profile()


@then("user edits profile details such as name, state, city, grade and platform language")
def step_edit_profile_details(context):
    page = _my_profile_page(context)
    # Snapshot every field's original value so the revert step can restore them
    # and assert nothing was left changed.
    context.original_profile = {
        "first name": page.get_first_name(),
        "state": page.get_state(),
        "city": page.get_city(),
        "grade": page.get_grade(),
    }
    page.edit_profile_details(EDITED_FIRST_NAME)


@then("user revert back the changes to its orginal details")
def step_revert_profile_details(context):
    page = _my_profile_page(context)
    original = context.original_profile
    page.open_my_profile()
    page.revert_profile_details(original["first name"], original["city"])
    # Confirm name, state, city and grade are all back to their original values.
    page.verify_reverted(original)
