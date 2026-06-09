from locators.student.my_profile_locators import myprofile_locators
from pages.base_page import BasePage


class MyProfilePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.locators = myprofile_locators()

    # ------------------------------------------------------------------ helpers
    def _click(self, selector, timeout=10000, required=True, name="element"):
        loc = self.page.locator(selector)
        if loc.count() == 0:
            if required:
                raise AssertionError(f"{name} not found: {selector}")
            return False
        try:
            loc.first.wait_for(state="visible", timeout=timeout)
            loc.first.scroll_into_view_if_needed(timeout=timeout)
            loc.first.click(timeout=timeout)
            return True
        except Exception:
            try:
                loc.first.click(timeout=timeout, force=True)
                return True
            except Exception:
                if required:
                    raise AssertionError(f"Unable to click {name}: {selector}")
                return False

    def _wait_visible(self, selector, timeout=15000, required=True, name="element"):
        loc = self.page.locator(selector)
        try:
            loc.first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            if required:
                raise AssertionError(f"{name} not visible: {selector}")
            return False

    def _open_select(self, dropdown_selector, name, timeout=10000):
        # Open an ant-select and confirm its option list actually rendered. A single
        # click is unreliable: if the dropdown was already open (e.g. left open by a
        # prior interaction), the click TOGGLES it shut and every option lookup then
        # fails. Retry the open once if no options appear. This is what previously
        # left the profile stuck in Hindi when the language revert silently failed.
        options = self.page.locator(".ant-select-item-option")
        self._click(dropdown_selector, name=name)
        try:
            options.first.wait_for(state="visible", timeout=3000)
            return
        except Exception:
            self._click(dropdown_selector, name=name)
            options.first.wait_for(state="visible", timeout=timeout)

    def _select_option(self, dropdown_selector, option_selector, dropdown_name, option_name):
        # Open the field, then wait for the target option to render in its portal
        # rather than relying on an immediate count() check (which races the
        # dropdown animation). State/grade/language are plain (non-search) selects.
        self._click(dropdown_selector, name=dropdown_name)
        option = self.page.locator(option_selector).first
        try:
            option.wait_for(state="visible", timeout=10000)
            option.scroll_into_view_if_needed(timeout=10000)
            option.click(timeout=10000)
        except Exception:
            try:
                option.click(timeout=10000, force=True)
            except Exception:
                raise AssertionError(f"{option_name} not selectable: {option_selector}")

    def _click_first_available(self, selectors, name, timeout=10000):
        # Try each selector in order; used for controls whose text is localized
        # (English vs Hindi after a Hindi platform-language save).
        for selector in selectors:
            loc = self.page.locator(selector)
            if loc.count() == 0:
                continue
            try:
                loc.first.wait_for(state="visible", timeout=timeout)
                loc.first.scroll_into_view_if_needed(timeout=timeout)
                loc.first.click(timeout=timeout)
                return True
            except Exception:
                try:
                    loc.first.click(timeout=timeout, force=True)
                    return True
                except Exception:
                    continue
        raise AssertionError(f"Unable to click {name}; tried: {selectors}")

    def _is_grade_disabled(self):
        # Grade is the 3rd ant-select (state, mobile, grade, language). Querying it
        # directly is more reliable than walking ancestors of a positional overflow
        # node, which can momentarily mis-resolve during the state-change re-render.
        # Default to "disabled" on any uncertainty so we never fail on a locked field.
        try:
            return self.page.locator(".ant-select").nth(2).evaluate(
                "e => e.classList.contains('ant-select-disabled')"
            )
        except Exception:
            return True

    # ------------------------------------------------------------------ navigation
    def _open_profile_menu(self):
        # Open the header avatar dropdown idempotently. Clicking the avatar TOGGLES
        # the dropdown, so a blind "retry click" can close one that already opened
        # (after a Hindi save the re-render makes timing unpredictable). Only click
        # while the menu item is not yet visible; retry the open a few times.
        menu_item = self.page.locator(self.locators.PROFILE_MENU_ITEM)
        for _ in range(4):
            if menu_item.count() and menu_item.first.is_visible():
                return
            self._click(self.locators.MY_PROFILE_ICON, timeout=10000, name="My Profile icon")
            try:
                menu_item.first.wait_for(state="visible", timeout=4000)
                return
            except Exception:
                continue
        raise AssertionError("My Profile menu did not open")

    def click_my_profile_icon(self):
        self._open_profile_menu()

    def click_my_profile(self):
        # Ensure the dropdown is open (idempotent), then click the "My Profile" item.
        # Scope it to the open dropdown so it does not collide with the page heading.
        # Match English text, then the Hindi-UI text, then the first dropdown item
        # (language-independent).
        self._open_profile_menu()
        menu = ("//div[contains(@class,'ant-dropdown') and "
                "not(contains(@class,'ant-dropdown-hidden'))]")
        self._click_first_available(
            [
                menu + self.locators.MY_PROFILE_HEADER,
                menu + self.locators.MY_PROFILE_HEADER_HINDI,
                self.locators.PROFILE_MENU_ITEM,
            ],
            "My Profile menu item",
            timeout=15000,
        )
        self._wait_visible(self.locators.FIRST_NAME_INPUT, name="My Profile page")

    def open_my_profile(self):
        self.click_my_profile()

    # ------------------------------------------------------------------ read
    def get_first_name(self):
        loc = self.page.locator(self.locators.FIRST_NAME_INPUT).first
        loc.wait_for(state="visible", timeout=10000)
        return loc.input_value()

    def get_city(self):
        loc = self.page.locator(self.locators.CITY_NAME_INPUT).first
        loc.wait_for(state="visible", timeout=10000)
        return loc.input_value()

    def get_state(self):
        loc = self.page.locator(self.locators.SELECT_STATE).first
        loc.wait_for(state="visible", timeout=10000)
        return loc.inner_text().strip()

    def get_grade(self):
        loc = self.page.locator(self.locators.SELECT_GRADE).first
        loc.wait_for(state="visible", timeout=10000)
        return loc.inner_text().strip()

    # ------------------------------------------------------------------ edit
    def edit_first_name(self, new_name):
        loc = self.page.locator(self.locators.FIRST_NAME_INPUT).first
        loc.wait_for(state="visible", timeout=10000)
        try:
            loc.fill(new_name, timeout=10000)
        except Exception:
            loc.fill(new_name, timeout=10000, force=True)

    def select_state(self, state_name):
        # Generic state selection. State names are Latin in both UIs, so we match by
        # name; this lets the revert restore whatever state was captured as original
        # rather than assuming a single hard-coded baseline.
        self._select_option(
            self.locators.SELECT_STATE,
            self.locators.STATE_OPTION.format(state=state_name),
            "State dropdown",
            f"{state_name} option",
        )

    def set_city(self, city_name):
        # City is a free-text input (not a dropdown). It re-renders and clears
        # when the state changes, so wait for it to become visible again.
        loc = self.page.locator(self.locators.CITY_NAME_INPUT).first
        loc.wait_for(state="visible", timeout=10000)
        try:
            loc.fill(city_name, timeout=10000)
        except Exception:
            loc.fill(city_name, timeout=10000, force=True)

    def select_grade_class_xi(self):
        # Grade is disabled for this profile and cannot be edited.
        if self._is_grade_disabled():
            print("[MyProfile] Grade field is disabled; skipping grade change.")
            return
        self._select_option(
            self.locators.SELECT_GRADE,
            self.locators.CLASS_XI,
            "Grade dropdown",
            "Class XI option",
        )

    def select_grade_class_x(self):
        if self._is_grade_disabled():
            print("[MyProfile] Grade field is disabled; skipping grade revert.")
            return
        self._select_option(
            self.locators.SELECT_GRADE,
            self.locators.CLASS_X,
            "Grade dropdown",
            "Class X option",
        )

    def select_platform_language_hindi(self):
        # Open reliably, then pick Hindi by its localized option label, falling back
        # to the second option (Hindi in either UI).
        self._open_select(self.locators.PLATFORM_LANGUAGE, "Platform language dropdown")
        self._click_first_available(
            [
                self.locators.HINDI_OPTION,
                self.locators.SELECT_OPTION_ITEM + "[2]",
            ],
            "Hindi language option",
        )

    def select_platform_language_english(self):
        # Runs during revert when the UI may already be Hindi, where "English"
        # renders as "अंग्रेज़ी". Open reliably, then pick English by its localized
        # option label, falling back to the first option (English in either UI).
        self._open_select(self.locators.PLATFORM_LANGUAGE, "Platform language dropdown")
        self._click_first_available(
            [
                self.locators.ENGLISH_OPTION,
                self.locators.SELECT_OPTION_ITEM,
            ],
            "English language option",
        )

    def click_save(self):
        # The Save button text is localized (Hindi after a Hindi save), so try the
        # English label, the Hindi-UI label, then its stable CSS class.
        self._click_first_available(
            [
                self.locators.SAVE_BUTTON,
                self.locators.SAVE_BUTTON_HINDI_UI,
                self.locators.SAVE_BUTTON_BY_CLASS,
            ],
            "Save button",
        )

    # ------------------------------------------------------------------ flows
    def edit_profile_details(self, new_name, new_state, new_city):
        self.edit_first_name(new_name)
        self.select_state(new_state)
        self.set_city(new_city)
        self.select_grade_class_xi()
        self.select_platform_language_hindi()
        self.click_save()

    def revert_profile_details(self, original_name, original_state, original_city):
        # Restore the captured original values (state included) so the profile
        # returns to exactly what it was, regardless of the starting state.
        self.edit_first_name(original_name)
        self.select_state(original_state)
        self.set_city(original_city)
        self.select_grade_class_x()
        self.select_platform_language_english()
        self.click_save()

    def verify_reverted(self, original):
        # Re-open the profile so we read the persisted values, then assert every
        # field is back to its captured original. Grade is read-only, so it is
        # unchanged throughout and is verified here for completeness.
        self.open_my_profile()
        actual = {
            "first name": self.get_first_name(),
            "state": self.get_state(),
            "city": self.get_city(),
            "grade": self.get_grade(),
        }
        mismatches = {k: (actual[k], original[k]) for k in original if actual[k] != original[k]}
        assert not mismatches, f"Profile did not fully revert: {mismatches}"
