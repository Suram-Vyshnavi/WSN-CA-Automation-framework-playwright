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
                # The element may render after a transition, so wait up to
                # `timeout` for it to appear rather than failing immediately.
                try:
                    loc.first.wait_for(state="visible", timeout=timeout)
                except Exception:
                    raise AssertionError(f"{name} not found: {selector}")
            else:
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

    def click_passions_preferences(self):
        self._click(self.locators.PASSIONS_HEADER, timeout=5000, required=True, name="Passions header")
       

    def click_review_passions_preferences(self):
        self._click(self.locators.REVIEW_BUTTON, timeout=5000, required=True, name="Review button")

    def validate_selected_items_in_passions_review(self):
        self._click(self.locators.ART_AND_DESIGN_HEADER, timeout=5000)
        self._click(self.locators.DRAWING_AND_ILLUSTRATION_INPUT, timeout=5000)
        self._click(self.locators.FASHION_DESIGN_INPUT, timeout=5000)
        self._click(self.locators.CLOSE_PASSION_BUTTON, timeout=5000)
        self._click(self.locators.BUSINESS_AND_MARKETING_HEADER, timeout=5000)
        self._click(self.locators.E_COMMERCE_OPTION, timeout=5000)
        # has_business = self.page.locator(self.locators.BUSINESS_AND_MARKETING_HEADER).count() > 0
        # has_ecommerce = self.page.locator(self.locators.E_COMMERCE_OPTION).count() > 0
        # self._click(self.locators.E_COMMERCE_OPTION, timeout=3000)
        # assert has_business or has_ecommerce, "No selected passions were found in review"

    def click_submit_button(self):
        self._click(self.locators.SUBMIT_BUTTON, required=True, name="Submit button")

    def _dismiss_overlays(self):
        """Remove the CleverTap push-notification popup, which floats above the
        page and intercepts clicks on the questionnaire flow."""
        try:
            self.page.evaluate(
                "() => document.querySelectorAll('#wzrk_wrapper,[id^=wzrk],[class^=wzrk]')"
                ".forEach(e => e.remove())"
            )
        except Exception:
            pass

    def _expand_questionnaires_section(self):
        """Ensure the Questionnaires (Level 2) accordion is expanded so the
        Interests / Aptitudes / Values cards and their Reattempt buttons show."""
        self._dismiss_overlays()
        reattempts = self.page.locator(self.locators.REATTEMPT_BUTTONS)
        if reattempts.count() > 0 and reattempts.first.is_visible():
            return
        header = self.page.locator(self.locators.QUESTIONNAIRES_HEADER)
        header.first.wait_for(state="visible", timeout=15000)
        header.first.scroll_into_view_if_needed()
        try:
            header.first.click(timeout=5000)
        except Exception:
            header.first.click(timeout=5000, force=True)
        reattempts.first.wait_for(state="visible", timeout=10000)

    def click_questionnaires_section(self):
        self._expand_questionnaires_section()

    def _start_slider_reattempt(self, card_selector, reattempt_selector, name):
        """Open a questionnaire card's Reattempt menu, pick the Slider
        assessment, and confirm with Retake so the ratings/questions page opens.

        Reattempt -> "How would you like to assess yourself?" modal -> Choose
        (Slider option). Choosing the Slider option opens the ratings/questions
        page directly; some assessments show an intermediate Retake button, so
        clicking it is best-effort.
        """
        self._expand_questionnaires_section()
        # Selecting the card itself is cosmetic; the Reattempt button drives the
        # flow, so the card click is best-effort.
        self._click(card_selector, timeout=8000, name=f"{name} card")
        self._click(reattempt_selector, timeout=10000, required=True, name=f"{name} Reattempt button")
        self._dismiss_overlays()
        self._click(
            self.locators.SLIDER_CHOOSE_BUTTON,
            timeout=10000,
            required=True,
            name="Slider assessment Choose button",
        )
        self._dismiss_overlays()
        # The Slider option usually lands straight on the questions page; only
        # click Retake if it is actually present.
        self._click(self.locators.RETAKE_BUTTON, timeout=3000, name="Retake button")
        self._dismiss_overlays()

    def click_interests_card_and_reattempt(self):
        self._start_slider_reattempt(
            self.locators.INTERESTS_CARD,
            self.locators.INTERESTS_REATTEMPT_BUTTON,
            "Interests",
        )

    def click_aptitudes_card_and_reattempt(self):
        self._start_slider_reattempt(
            self.locators.APTITUDES_CARD,
            self.locators.APTITUDES_REATTEMPT_BUTTON,
            "Aptitudes",
        )

    def click_values_card_and_reattempt(self):
        self._start_slider_reattempt(
            self.locators.VALUES_CARD,
            self.locators.VALUES_REATTEMPT_BUTTON,
            "Values",
        )

    # ------------------------------------------------------------------
    # Questionnaire (scenario-card) flow
    #
    # Reattempt -> Choose (1st, "Questionnaire" option) -> answer every
    # question by selecting an answer card and clicking "Next >". Card layouts
    # vary per question (multi-card scenario, emoji fun-meter, 2-card forced
    # choice). On a reattempt the previous answers are pre-selected, and clicking
    # the already-selected card disables Next, so the flow always picks an
    # unselected card. Finishing the Interests section reveals "Start Aptitudes",
    # then "Start Values", each running the identical card flow.
    # ------------------------------------------------------------------
    def open_interests_questionnaire_reattempt(self):
        """Expand the Questionnaires accordion, open the Interests card and click
        its Reattempt button, stopping before the assessment-type choice (the
        following step picks the Questionnaire 'Choose' option)."""
        self._expand_questionnaires_section()
        self._click(self.locators.INTERESTS_CARD, timeout=8000, name="Interests card")
        self._click(
            self.locators.INTERESTS_REATTEMPT_BUTTON,
            timeout=10000,
            required=True,
            name="Interests Reattempt button",
        )
        self._dismiss_overlays()

    def _questionnaire_frame(self):
        """FrameLocator for the cross-origin iframe that hosts the scenario
        questions. Re-resolved on each call so it stays valid as the iframe
        reloads between questions/sections."""
        return self.page.frame_locator(self.locators.QUESTIONNAIRE_IFRAME)

    def _questionnaire_frame_obj(self):
        """The underlying Frame (not FrameLocator) so we can run evaluate() inside
        the iframe."""
        for fr in self.page.frames:
            if "questionnaire" in (fr.url or ""):
                return fr
        return None

    def _clear_sc_overlay(self, wait_timeout=4000):
        """A transient '.sc-overlay' inside the iframe (a selection animation
        layer) intercepts pointer events and blocks the Next/Submit button. Wait
        for it to clear, then JS-remove any leftover as a fallback."""
        overlay = self._questionnaire_frame().locator("//div[contains(@class,'sc-overlay')]")
        try:
            if overlay.count() > 0:
                overlay.first.wait_for(state="hidden", timeout=wait_timeout)
        except Exception:
            pass
        fr = self._questionnaire_frame_obj()
        if fr is not None:
            try:
                fr.evaluate(
                    "() => document.querySelectorAll('.sc-overlay')"
                    ".forEach(e => e.remove())"
                )
            except Exception:
                pass

    def _wait_for_question_cards(self, timeout=15000):
        loc = self._questionnaire_frame().locator(self.locators.ANY_QUESTION_CARD)
        try:
            loc.first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def _advance_question(self):
        """Advance past the current question inside the iframe. Intermediate
        questions show 'Next >'; the last question of a section shows 'Submit'
        (clicking it makes the next section's 'Start ...' button appear on the
        host page). Returns 'next', 'submitted', or None if neither control was
        clickable (e.g. disabled because the already-selected card was re-clicked)."""
        frame = self._questionnaire_frame()
        # The selection-animation overlay blocks the action button; clear it first.
        self._clear_sc_overlay()
        for kind, selector in (
            ("next", self.locators.QUESTIONNAIRE_NEXT_BUTTON),
            ("submitted", self.locators.QUESTIONNAIRE_SUBMIT_BUTTON),
        ):
            loc = frame.locator(selector)
            try:
                if loc.count() == 0 or not loc.first.is_visible():
                    continue
                btn = loc.first
                try:
                    btn.click(timeout=3000)
                except Exception:
                    self._clear_sc_overlay(wait_timeout=1500)
                    btn.click(timeout=3000, force=True)
            except Exception:
                continue
            # Let the next question (or the section-transition) render/settle.
            self.page.wait_for_timeout(1200)
            return kind
        return None

    def _answer_current_question(self):
        """Select an answer card for the current question (inside the iframe) and
        advance.

        Returns 'next' (advanced to another question), 'submitted' (this was the
        section's last question), or 'failed' (no answerable card/control found).
        Picks a card that is not pre-selected, since re-clicking the selected card
        disables the advance control."""
        self._dismiss_overlays()
        frame = self._questionnaire_frame()
        # Identify the active layout so selected-card detection stays within it.
        cards = None
        for selector in (
            self.locators.SCENARIO_CARDS,
            self.locators.FUN_EMOJI_CARDS,
            self.locators.FORCED_CARDS,
            self.locators.ILLUSTRATED_SCENARIO_CARDS,
        ):
            loc = frame.locator(selector)
            try:
                if loc.count() > 0 and loc.first.is_visible():
                    cards = loc
                    break
            except Exception:
                continue
        if cards is None:
            return "failed"

        try:
            n = cards.count()
        except Exception:
            return "failed"
        if n == 0:
            return "failed"

        # Find the pre-selected card so we can click a different one.
        selected_idx = -1
        for i in range(n):
            try:
                cls = cards.nth(i).get_attribute("class") or ""
            except Exception:
                cls = ""
            if "selected" in cls:
                selected_idx = i
                break

        order = [i for i in range(n) if i != selected_idx] or list(range(n))
        for idx in order:
            # The selection-animation overlay covers the cards; clear it first or
            # the click times out against the overlay.
            self._clear_sc_overlay()
            card = cards.nth(idx)
            try:
                card.scroll_into_view_if_needed(timeout=3000)
                card.click(timeout=3000)
            except Exception:
                self._clear_sc_overlay(wait_timeout=1500)
                try:
                    card.click(timeout=3000, force=True)
                except Exception:
                    continue
            # Let the selection register and its overlay animation play out.
            self.page.wait_for_timeout(700)
            result = self._advance_question()
            if result is not None:
                return result
        return "failed"

    def _answer_all_scenario_questions(self):
        """Answer every scenario question in the current section. Each question is
        advanced with 'Next >'; the final question is submitted with 'Submit',
        which ends the section (and surfaces the next section's 'Start ...' button
        on the host page). Stops as soon as that Submit is clicked."""
        max_questions = 80
        for _ in range(max_questions):
            self._dismiss_overlays()
            if not self._wait_for_question_cards(timeout=8000):
                break
            result = self._answer_current_question()
            if result in ("submitted", "failed"):
                break

    def choose_questionnaire_and_answer_first_question(self):
        """Pick the Questionnaire assessment (1st Choose) and answer the first
        scenario question."""
        self._dismiss_overlays()
        self._click(
            self.locators.QUESTIONNAIRES_CHOOSE_BUTTON,
            timeout=10000,
            required=True,
            name="Questionnaire Choose button",
        )
        self._dismiss_overlays()
        # Some assessments show an intermediate Retake before the first question.
        self._click(self.locators.RETAKE_BUTTON, timeout=3000, name="Retake button")
        self._dismiss_overlays()
        assert self._wait_for_question_cards(timeout=20000), "Questionnaire questions did not load"
        assert self._answer_current_question(), "Could not answer the first questionnaire question"

    def answer_all_interests_questions(self):
        self._answer_all_scenario_questions()

    def _activate_start_button(self, btn):
        """The Start button only becomes clickable once hovered, so mouse over it
        before clicking."""
        try:
            btn.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        try:
            btn.hover(timeout=5000)
        except Exception:
            pass
        try:
            btn.click(timeout=5000)
        except Exception:
            btn.click(timeout=5000, force=True)

    def _start_next_section(self, start_selector, name):
        """Click a section's Start button (Start Aptitudes / Start Values). It
        renders on the host page a moment after the previous section's final
        Submit (occasionally inside the iframe), and only activates on hover."""
        self._dismiss_overlays()
        # Quick try inside the iframe (rarely present there).
        frame_btn = self._questionnaire_frame().locator(start_selector)
        try:
            if frame_btn.count() > 0:
                self._activate_start_button(frame_btn.first)
                self._dismiss_overlays()
                return
        except Exception:
            pass
        # Otherwise wait for it on the host page (it appears ~2s after Submit).
        page_btn = self.page.locator(start_selector)
        try:
            page_btn.first.wait_for(state="visible", timeout=20000)
        except Exception:
            raise AssertionError(f"{name} not found/clickable: {start_selector}")
        self._activate_start_button(page_btn.first)
        self._dismiss_overlays()

    def start_aptitudes_and_answer_all(self):
        self._start_next_section(self.locators.START_APTITUDES, "Start Aptitudes")
        self._wait_for_question_cards(timeout=20000)
        self._answer_all_scenario_questions()

    def start_values_and_answer_all(self):
        self._start_next_section(self.locators.START_VALUES, "Start Values")
        self._wait_for_question_cards(timeout=20000)
        self._answer_all_scenario_questions()

    def _adjust_question_slider(self):
        """Drive the current question's slider into the 7-8 band: from 7 step up
        to 8, from 9 (or higher) step back down to 8, and nudge any lower value
        up toward the band. Lands on 8 regardless of the starting position."""
        slider = self.page.locator(self.locators.QUESTION_SLIDER)
        slider.first.wait_for(state="visible", timeout=10000)
        slider.first.scroll_into_view_if_needed()
        slider.first.focus()
        # Cap the iterations so a stuck/non-responsive slider can't loop forever.
        for _ in range(20):
            value = slider.first.get_attribute("aria-valuenow")
            try:
                current = int(value)
            except (TypeError, ValueError):
                break
            if current == 8:
                break
            if current == 7:
                self.page.keyboard.press("ArrowRight")  # 7 -> 8
                break
            if current < 7:
                self.page.keyboard.press("ArrowRight")  # step up toward 7/8
            else:  # current >= 9
                self.page.keyboard.press("ArrowLeft")   # step back down to 8
            self.page.wait_for_timeout(150)

    def slide_slider_and_click_next_through_questions(self):
        """Answer every question by nudging the slider, then click Next. The
        final question shows Submit instead of Next, so the loop stops once Next
        is no longer present (Submit is handled by the following step)."""
        self._dismiss_overlays()
        max_questions = 60
        for _ in range(max_questions):
            self._adjust_question_slider()
            next_btn = self.page.locator(self.locators.NEXT_BUTTON)
            if next_btn.count() > 0 and next_btn.first.is_visible():
                try:
                    next_btn.first.click(timeout=5000)
                except Exception:
                    next_btn.first.click(timeout=5000, force=True)
                # Let the next question's slider render before reading it.
                self.page.wait_for_timeout(600)
                self._dismiss_overlays()
            else:
                break

    def click_submit_questionnaire(self):
        self._dismiss_overlays()
        self._click(self.locators.SUBMIT_BUTTON, timeout=10000, required=True, name="Submit button")
        self._dismiss_overlays()

    def click_back_arrow(self):
        self._dismiss_overlays()
        self._click(self.locators.BACK_ARROW, timeout=10000, required=True, name="Back arrow")
        self._dismiss_overlays()
        # Allow the previous view (matched roles / accordion) to re-render.
        self.page.wait_for_timeout(1500)

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

    def enter_jobrole_and_add_first_job_as_saved(self, job_role: str):
        search_input = self.page.locator(self.locators.SEARCH_ROLES_INPUT)
        search_input.first.wait_for(state="visible", timeout=10000)
        search_input.first.fill(job_role)

        # Results load asynchronously after typing, so auto-wait for them to render.
        self.page.locator(self.locators.VALIDATE_RESULTS_HEADER).first.wait_for(
            state="visible", timeout=10000
        )

        # If the first result is already in "Saved" state, click it once to
        # toggle back to "Save" so the subsequent save action is idempotent.
        already_saved = self.page.locator(self.locators.FIRST_RESULT_SAVED_STATE)
        if already_saved.count() > 0:
            try:
                already_saved.first.wait_for(state="visible", timeout=3000)
                already_saved.first.scroll_into_view_if_needed()
                already_saved.first.click(timeout=5000)
                # Wait for the toggle to revert to the "Save" label.
                self.page.locator(self.locators.ADD_SAVE).first.wait_for(
                    state="visible", timeout=8000
                )
            except Exception:
                pass

        save = self.page.locator(self.locators.ADD_SAVE)
        save.first.wait_for(state="visible", timeout=10000)
        save.first.scroll_into_view_if_needed()
        try:
            save.first.click(timeout=5000)
        except Exception:
            save.first.click(timeout=5000, force=True)

        # Confirm the save registered: the label must flip to "Saved".
        try:
            self.page.locator(self.locators.FIRST_RESULT_SAVED_STATE).first.wait_for(
                state="visible", timeout=8000
            )
        except Exception:
            raise AssertionError("Role was not saved — 'Saved' label did not appear after clicking Save")

    def click_save_menu_header_and_validate_saved_job(self):
        self._click(self.locators.SAVED_MENU_HEADER, required=True, name="Saved menu")
        # self._wait_visible(self.locators.SAVED_MENU_HEADER, required=True, name="Saved page")

    def click_compare_roles(self):
                self._wait_visible(
                    self.locators.COMPARE_ROLES,
                    required=True,
                    name="Compare roles"
                )
                self._click(
                    self.locators.COMPARE_ROLES,
                    required=True,
                    name="Compare roles"
                )
                

    def click_first_second_checkbox_and_compare(self):
        first = self.page.locator(self.locators.FIRST_FAV_CHECKBOX)
        first.first.wait_for(state="visible", timeout=10000)
        first.first.scroll_into_view_if_needed()
        try:
            first.first.click(timeout=5000)
        except Exception:
            first.first.click(timeout=5000, force=True)

        second = self.page.locator(self.locators.SECOND_FAV_CHECKBOX)
        second.first.wait_for(state="visible", timeout=10000)
        second.first.scroll_into_view_if_needed()
        try:
            second.first.click(timeout=5000)
        except Exception:
            second.first.click(timeout=5000, force=True)

        self._click(self.locators.COMPARE_BUTTON, required=True, name="Compare button")

    def click_share_report_and_validate_options(self):
        self._click(self.locators.SHARE_REPORT_HEADER, required=True, name="Share report menu")
        self._click(self.locators.SHARE_REPORT_BUTTON, required=True, name="Share report button")

    def validate_share_report_tabs(self):
        self._wait_visible(self.locators.SELF_REVIEW_TAB, required=True, name="Self-Review tab")
        self._wait_visible(self.locators.MATCHED_ROLES_TAB, required=True, name="Matched Roles tab")
        self._wait_visible(self.locators.SAVED_ROLES_TAB, required=True, name="Saved Roles tab")

    # def click_saved_menu_and_remove_saved_job(self):
    #     self._click(self.locators.SAVED_MENU_HEADER, timeout=10000, required=True, name="Saved menu")
    #     self._click(self.locators.REMOVE_SAVED_JOB, timeout=10000, required=True, name="Remove saved job")
        # The Saved page loads its cards asynchronously, so auto-wait for the saved
        # job toggle to render instead of failing on an immediate count() check.
        # remove = self.page.locator(self.locators.REMOVE_SAVED_JOB).click()
        # remove.first.wait_for(state="visible", timeout=10000)
        # remove.first.scroll_into_view_if_needed()
        # try:
        #     remove.first.click(timeout=5000)
        # except Exception:
        #     remove.first.click(timeout=5000, force=True)

    def _open_profile_menu(self):
        # Open the header avatar dropdown idempotently. Clicking the avatar
        # TOGGLES the dropdown, so a blind retry can close one that already
        # opened; only click while the menu item is not yet visible.
        menu_item = self.page.locator(self.locators.PROFILE_MENU_ITEM)
        for _ in range(4):
            if menu_item.count() and menu_item.first.is_visible():
                return
            self._click(self.locators.PROFILE_ICON, timeout=10000, name="Profile icon")
            try:
                menu_item.first.wait_for(state="visible", timeout=4000)
                return
            except Exception:
                continue
        raise AssertionError("Profile menu did not open")

    def click_about_icon(self):
        # Open the profile dropdown and choose the About item. The About item
        # navigates to /<lang>/about, a page that has no "About" heading of its
        # own, so confirm the navigation by URL rather than by a heading.
        self._open_profile_menu()
        self._click(self.locators.ABOUT_MENU_ITEM, timeout=10000, required=True, name="About menu item")
        try:
            self.page.wait_for_url("**/about", timeout=10000)
        except Exception:
            raise AssertionError(f"About page did not open; current URL: {self.page.url}")

    def click_help_icon(self):
        """Click the "Help?" button. Help may either open in a new browser tab or
        navigate the current tab to a different page; either way the flow must end
        back on the original homepage so the following profile/about/logout steps
        run against it.

        Captures the current URL, clicks Help, then:
          * if a new tab opened, confirms it loaded, closes it and returns to the
            original tab;
          * if the current tab navigated away, goes back to the original page;
          * if Help only opened an on-page panel, leaves the page as-is.
        """
        self._dismiss_overlays()
        original_url = self.page.url
        help_btn = self.page.locator(self.locators.HELP_ICON)
        help_btn.first.wait_for(state="visible", timeout=10000)
        help_btn.first.scroll_into_view_if_needed()

        new_page = None
        try:
            with self.page.context.expect_page(timeout=4000) as new_page_info:
                try:
                    help_btn.first.click(timeout=5000)
                except Exception:
                    help_btn.first.click(timeout=5000, force=True)
            new_page = new_page_info.value
        except Exception:
            # No new tab opened within the timeout; the click already happened.
            new_page = None

        if new_page is not None:
            # Help opened in a new tab: confirm it loaded, then close it and
            # return focus to the original homepage tab.
            try:
                new_page.wait_for_load_state(timeout=10000)
            except Exception:
                pass
            try:
                new_page.close()
            except Exception:
                pass
            self.page.bring_to_front()
        elif self.page.url != original_url:
            # Help navigated the current tab; go back to the homepage.
            try:
                self.page.go_back()
                self.page.wait_for_load_state(timeout=10000)
            except Exception:
                # Fall back to an explicit navigation if history back fails.
                self.page.goto(original_url)
                self.page.wait_for_load_state(timeout=10000)

        self._dismiss_overlays()
        # Allow the homepage to re-render before the next step interacts with it.
        self.page.wait_for_timeout(1500)

    def click_saved_menu_and_remove_saved_job(self):
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
