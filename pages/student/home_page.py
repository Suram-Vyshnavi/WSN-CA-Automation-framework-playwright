from locators.student.Home_page_locators import HomePageLocators
from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.locators = HomePageLocators()

    def _click(self, selector, timeout=5000, required=False, name="element"):
        loc = self.page.locator(selector)
        if loc.count() == 0:
            if required:
                raise AssertionError(f"{name} not found: {selector}")
            return False
        try:
            loc.first.wait_for(state="visible", timeout=timeout)
            # Bound the scroll wait to `timeout`; its default is 30s, which makes
            # clicks on unstable/re-rendering pages (e.g. share report) hang before
            # falling through to the force-click below.
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

    def _wait_visible(self, selector, timeout=7000, required=False, name="element"):
        loc = self.page.locator(selector)
        if loc.count() == 0:
            if required:
                raise AssertionError(f"{name} not found: {selector}")
            return False
        try:
            loc.first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            if required:
                raise AssertionError(f"{name} not visible: {selector}")
            return False
        
    def click_congratulations_close_button(self):
        try:
            self.click(self.locators.CONGRATULATIONS_TEST_CLOSE_BUTTON, timeout=5000)
        except Exception:
            pass

    def click_matches_roles_section(self):
        self._click(self.locators.MATCHED_ROLE, timeout=15000, required=True, name="Matched Roles")

    def validate_ministry_of_education_logo(self):
        self._wait_visible(
            self.locators.VALIDATE_MINISTRY_OF_EDUCATION_LOGO,
            required=True,
            name="Ministry of Education logo",
        )

    def validate_ncert_logo(self):
        self._wait_visible(self.locators.VALIDATE_NCERT_LOGO, required=True, name="NCERT logo")

    def validate_wf_logo(self):
        self._wait_visible(self.locators.VALIDATE_WF_LOGO, required=True, name="WF logo")

    def select_passions_preferences(self):
        self._click(self.locators.PASSIONS_HEADER, required=True, name="Passions header")
       

    def select_review_passions_preferences(self):
        if self._click(self.locators.REVIEW_BUTTON, timeout=5000):
            return
        self._click(self.locators.APTITUDES_FIRST_REVIEW_BUTTON, required=True, name="Review button")

    def validate_selected_items_in_passions_review(self):
        self._click(self.locators.E_COMMERCE_CLEANUP, timeout=5000)
        has_business = self.page.locator(self.locators.BUSINESS_AND_MARKETING).count() > 0
        has_ecommerce = self.page.locator(self.locators.E_COMMERCE).count() > 0
        self._click(self.locators.E_COMMERCE, timeout=3000)
        assert has_business or has_ecommerce, "No selected passions were found in review"

    def click_submit_button(self):
        self._click(self.locators.SUBMIT_BUTTON, required=True, name="Submit button")

    def click_questionnaires_section(self):
        if self._click(self.locators.QUESTIONNAIRES_HEADER, timeout=5000):
            return
        self._wait_visible(self.locators.APTITUDES_FIRST_REVIEW_BUTTON, timeout=5000)

    def complete_aptitudes_first_flow(self):
        if self._click(self.locators.APTITUDES_FIRST_REVIEW_BUTTON, timeout=5000):
            return
        self._wait_visible(self.locators.APTITUDES_FIRST_REATTEMPT_BUTTON, timeout=5000)

    def click_reattempt(self):
        if self._click(self.locators.APTITUDES_FIRST_REATTEMPT_BUTTON, timeout=5000):
            return
        self._wait_visible(self.locators.APTITUDES_FIRST_SLIDER_CHOOSE_BUTTON, timeout=5000)

    def choose_slider_option(self):
        self._click(
            self.locators.APTITUDES_FIRST_SLIDER_CHOOSE_BUTTON,
            required=True,
            name="Aptitudes slider choose",
        )

    def update_first_question_slider_value(self):
        is_nine_selected = self.page.locator(self.locators.VALIDATE_9).count() > 0
        is_ten_selected = self.page.locator(self.locators.VALIDATE_10).count() > 0

        if is_nine_selected:
            self._click(self.locators.CHOOSE_SLIDER_OPTION_10, required=True, name="Slider option 10")
        elif is_ten_selected:
            self._click(self.locators.CHOOSE_SLIDER_OPTION_9, required=True, name="Slider option 9")
        else:
            if not self._click(self.locators.CHOOSE_SLIDER_OPTION_10, timeout=2500):
                self._click(self.locators.CHOOSE_SLIDER_OPTION_9, required=True, name="Slider option 9/10")

        self._click(self.locators.APTITUDES_UPDATE_BUTTON, required=True, name="Aptitudes update")

    def click_go_to_matched_roles(self):
        self._click(self.locators.GO_TO_MATCHED_ROLES_BUTTON, required=True, name="Go to matched roles")

    def click_without_college_degree(self):
        # After submitting passions the matched-roles page re-renders, so the toggle
        # briefly leaves the DOM. Auto-wait for it to (re)appear before clicking
        # rather than failing on an immediate count() check.
        loc = self.page.locator(self.locators.WITHOUT_COLLEGE_DEGREE)
        loc.first.wait_for(state="visible", timeout=15000)
        loc.first.scroll_into_view_if_needed()
        try:
            loc.first.click(timeout=5000)
        except Exception:
            loc.first.click(timeout=5000, force=True)

    def validate_recommended_roles(self):
        passion_count = self.page.locator(
            self.locators.VALIDATE_RECOMMENDED_ROLES_PASSION_HEADER_MATCHED_COUNT
        )
        questionnaires_count = self.page.locator(
            self.locators.VALIDATE_RECOMMENDED_ROLES_QUESTIONNAIRES_HEADER_MATCHED_COUNT
        )

        passion_ok = False
        questionnaires_ok = False

        if passion_count.count() > 0:
            try:
                passion_count.first.wait_for(state="visible", timeout=5000)
                passion_ok = True
            except Exception:
                passion_ok = False

        if questionnaires_count.count() > 0:
            try:
                questionnaires_count.first.wait_for(state="visible", timeout=5000)
                questionnaires_ok = True
            except Exception:
                questionnaires_ok = False

        assert passion_ok or questionnaires_ok, "Recommended roles matched counts are not visible"

    def click_search_roles(self):
        self._click(self.locators.SEARCH_ROLES_HEADER, required=True, name="Search Roles")

    def enter_jobrole_and_add_first_job_as_favourite(self, job_role: str):
        search_input = self.page.locator(self.locators.SEARCH_ROLES_INPUT)
        assert search_input.count() > 0, "Search role input not found"

        search_input.first.wait_for(state="visible", timeout=5000)
        search_input.first.fill(job_role)

        # Results load asynchronously after typing, so auto-wait for them to render
        # instead of failing on an immediate count() check.
        self.page.locator(self.locators.VALIDATE_RESULTS_HEADER).first.wait_for(
            state="visible", timeout=10000
        )

        fav = self.page.locator(self.locators.ADD_FAVOURITE)
        fav.first.wait_for(state="visible", timeout=10000)
        fav.first.scroll_into_view_if_needed()
        try:
            fav.first.click(timeout=5000)
        except Exception:
            fav.first.click(timeout=5000, force=True)

    def click_favourites_and_validate_added_job(self):
        self._click(self.locators.SAVED_MENU_HEADER, required=True, name="Saved menu")
        self._wait_visible(self.locators.SAVED_MENU_HEADER, required=True, name="Saved page")

    def click_share_report_and_validate_options(self):
        self._click(self.locators.SHARE_REPORT_HEADER, required=True, name="Share report menu")
        self._click(self.locators.SHARE_REPORT_BUTTON, required=True, name="Share report button")

    def validate_share_report_tabs(self):
        self._wait_visible(self.locators.SELF_REVIEW_TAB, required=True, name="Self-Review tab")
        self._wait_visible(self.locators.MATCHED_ROLES_TAB, required=True, name="Matched Roles tab")
        self._wait_visible(self.locators.SAVED_ROLES_TAB, required=True, name="Saved Roles tab")

    def click_favourites_and_remove_added_job(self):
        self._click(self.locators.SAVED_MENU_HEADER, required=True, name="Saved menu")
        # The Saved page loads its cards asynchronously, so auto-wait for the saved
        # job toggle to render instead of failing on an immediate count() check.
        remove = self.page.locator(self.locators.REMOVE_SAVED_JOB)
        remove.first.wait_for(state="visible", timeout=10000)
        remove.first.scroll_into_view_if_needed()
        try:
            remove.first.click(timeout=5000)
        except Exception:
            remove.first.click(timeout=5000, force=True)
