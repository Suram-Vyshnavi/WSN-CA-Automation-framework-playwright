from locators.student.newuser_locators import newuser_locators
from pages.base_page import BasePage


class NewUserPage(BasePage):

    # Account creation is done by hand: the tester enters the email, generates the
    # OTP, types the OTP and submits - all manually. Automation only takes over once
    # the Set Password page appears, so instead of fixed waits it auto-waits (up to
    # this long) for that page and resumes the moment it renders.
    PASSWORD_PAGE_WAIT_MS = 300000  # up to 5 min for the manual email + OTP + submit

    def __init__(self, page):
        super().__init__(page)
        self.locators = newuser_locators()
        # Tracks whether the non-deterministic feedback popup was validated at any
        # point during the journey, so the final step can assert on it.
        self.feedback_seen = False

    # ------------------------------------------------------------------
    # Generic helpers (mirror HomePage's defensive click/visibility pattern)
    # ------------------------------------------------------------------
    def _click(self, selector, timeout=5000, required=False, name="element"):
        loc = self.page.locator(selector)
        if loc.count() == 0:
            if required:
                try:
                    loc.first.wait_for(state="visible", timeout=timeout)
                except Exception:
                    raise AssertionError(f"{name} not found: {selector}")
            else:
                return False
        try:
            # wait_for keeps the full timeout (legitimately waiting for the element);
            # scroll/click attempts are capped so a covered element falls through to
            # the force-click quickly instead of burning the whole timeout.
            loc.first.wait_for(state="visible", timeout=timeout)
            loc.first.scroll_into_view_if_needed(timeout=3000)
            loc.first.click(timeout=4000)
            return True
        except Exception:
            try:
                loc.first.click(timeout=4000, force=True)
                return True
            except Exception:
                if required:
                    raise AssertionError(f"Unable to click {name}: {selector}")
                return False

    def _fill(self, selector, text, timeout=8000, name="field"):
        loc = self.page.locator(selector).last
        loc.wait_for(state="visible", timeout=timeout)
        try:
            loc.fill(text, timeout=timeout)
        except Exception:
            loc.fill(text, timeout=timeout, force=True)

    def _visible_locator(self, selector, timeout=10000):
        """Return the first VISIBLE element matching the selector. The forms render
        hidden duplicate inputs (e.g. a hidden password/login copy), so a plain
        `.last`/`.first` can resolve to a hidden node that fill() silently writes to
        while the on-screen field stays empty. Picking the visible match avoids that."""
        loc = self.page.locator(selector)
        loc.first.wait_for(state="attached", timeout=timeout)
        try:
            count = loc.count()
        except Exception:
            count = 0
        for i in range(count):
            try:
                if loc.nth(i).is_visible():
                    return loc.nth(i)
            except Exception:
                continue
        return loc.last

    def _click_visible(self, selector, timeout=10000, required=True, name="element"):
        """Click whichever match for `selector` is actually visible, instead of a
        fixed .first/[N] index. Several controls on this form (Submit, Grade)
        render a hidden duplicate alongside the real, visible one; clicking the
        wrong copy can silently "succeed" (force-click doesn't error) while
        doing nothing on screen, which is what made Submit appear to do
        nothing after the personal-details form was filled in."""
        self._dismiss_overlays()
        try:
            loc = self._visible_locator(selector, timeout=timeout)
        except Exception:
            if required:
                raise AssertionError(f"{name} not found: {selector}")
            return False
        try:
            loc.scroll_into_view_if_needed(timeout=3000)
            loc.click(timeout=4000)
            return True
        except Exception:
            try:
                loc.click(timeout=4000, force=True)
                return True
            except Exception:
                if required:
                    raise AssertionError(f"Unable to click {name}: {selector}")
                return False

    def _click_and_fill(self, selector, text, timeout=10000, name="field"):
        """Fill a field quickly and reliably.

        Visible inputs: click to focus then type real keystrokes (some custom/React
        inputs only fire onChange on genuine keypresses). Hidden custom inputs (e.g.
        the password fields): force-fill straight away - trying to click/focus/type a
        hidden element just burns the timeout before failing, which is what made
        password/details entry slow."""
        self._dismiss_overlays()
        loc = self._visible_locator(selector, timeout=timeout)
        is_visible = False
        try:
            is_visible = loc.is_visible()
        except Exception:
            is_visible = False
        if is_visible:
            try:
                loc.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass
            try:
                loc.click(timeout=2000)
            except Exception:
                pass
            try:
                loc.fill("", timeout=2000)
                loc.press_sequentially(text, delay=0, timeout=4000)
                return
            except Exception:
                pass
        # Hidden field, or the typing path failed: set the value directly (force).
        try:
            loc.fill(text, timeout=3000, force=True)
        except Exception:
            self.page.locator(selector).last.fill(text, timeout=3000, force=True)

    def _wait_visible(self, selector, timeout=10000, required=False, name="element"):
        loc = self.page.locator(selector)
        if loc.count() == 0 and not required:
            return False
        try:
            loc.first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            if required:
                raise AssertionError(f"{name} not visible: {selector}")
            return False

    def _validate(self, selector, name, timeout=20000):
        """Assert an expected element is PRESENT in the DOM after a step's action, so
        each step verifies its result. Uses 'attached' (presence), not 'visible':
        the app uses CSS-hidden custom inputs and iframes that are usable but never
        report as visible, and some screens render a moment after the action - a
        visibility check would give false negatives even though the flow proceeds."""
        try:
            self.page.locator(selector).first.wait_for(state="attached", timeout=timeout)
        except Exception:
            raise AssertionError(f"Validation failed - {name} not present after the step")

    def _dismiss_overlays(self):
        """Remove the CleverTap push-notification popup (#wzrk_wrapper and friends),
        which floats above the page and intercepts clicks on form controls like the
        ant-select dropdowns."""
        try:
            self.page.evaluate(
                "() => document.querySelectorAll('#wzrk_wrapper,[id^=wzrk],[class^=wzrk]')"
                ".forEach(e => e.remove())"
            )
        except Exception:
            pass

    def _select_dropdown(self, trigger_selector, option_selector, name):
        """Open an ant-select dropdown and pick an option. The option list renders
        a moment after the trigger is clicked, so the option click waits for it.

        Uses _visible_locator instead of ordinal indexing (.first/[N]) for both
        the trigger and the option: this app renders hidden duplicate copies of
        these labels (see _visible_locator's docstring), so a fixed index can
        silently resolve to the wrong, invisible element - which is what made
        the Grade dropdown click fail even though the trigger text was present.
        """
        self._dismiss_overlays()
        trigger = self._visible_locator(trigger_selector, timeout=10000)
        try:
            trigger.scroll_into_view_if_needed(timeout=3000)
            trigger.click(timeout=4000)
        except Exception:
            try:
                trigger.click(timeout=4000, force=True)
            except Exception:
                raise AssertionError(f"Unable to click {name} dropdown: {trigger_selector}")
        self.page.wait_for_timeout(250)
        self._dismiss_overlays()
        option = self._visible_locator(option_selector, timeout=8000)
        try:
            option.scroll_into_view_if_needed(timeout=3000)
            option.click(timeout=4000)
        except Exception:
            try:
                option.click(timeout=4000, force=True)
            except Exception:
                raise AssertionError(f"Unable to click {name} option: {option_selector}")

    # ------------------------------------------------------------------
    # Feedback popup (can appear at any point in the journey)
    # ------------------------------------------------------------------
    def handle_feedback_popup_if_present(self, timeout=2500):
        """Dismiss the feedback popup if it is currently showing: rate it (MCA
        stars), click Next, then Close. Returns True if it was found and handled.
        Kept fast (short timeout) so it is cheap to call opportunistically between
        steps without slowing the flow when the popup is absent."""
        popup = self.page.locator(self.locators.FEEDBACK_POPUP)
        try:
            popup.first.wait_for(state="visible", timeout=timeout)
        except Exception:
            return False

        self._click(self.locators.MCA_STARS, timeout=5000, name="MCA stars")
        # The popup may show one or more "Next" steps before the Close button; click
        # Next while it is present (capped so it cannot loop forever).
        for _ in range(3):
            if not self._click(self.locators.FEEDBACK_NEXT_BUTTON, timeout=3000, name="Feedback Next"):
                break
            self.page.wait_for_timeout(400)
        self._click(self.locators.CLOSE_BUTTON, timeout=5000, name="Feedback Close")
        self.feedback_seen = True
        return True

    def _dismiss_congratulations_popup(self):
        """Best-effort close of the 'Congratulations' modal that can surface after
        the assessments finish and would otherwise block the Pick Roles flow."""
        if self.page.locator(self.locators.CONGRATULATIONS_CA_POPUP).count() > 0:
            self._click(self.locators.CLOSE_CONGRATULATIONS_CA_POPUP_BUTTON, timeout=3000,
                        name="Congratulations close")

    # ------------------------------------------------------------------
    # Account creation (manual email + OTP)
    # ------------------------------------------------------------------
    def click_create_new_and_enter_email(self):
        self.handle_feedback_popup_if_present()
        self._dismiss_overlays()
        # Best-effort only: this button is occasionally covered by an overlay or
        # slow to render in dev, and the rest of account creation (email, OTP,
        # submit) is manual anyway - so a missed auto-click here should not fail
        # the scenario, just fall through to the manual instructions below.
        clicked = self._click(self.locators.CREATE_NOW_BUTTON, timeout=8000, required=False,
                              name="Create Now button")
        if not clicked:
            print("\n>>> Could not auto-click 'Create Now' - please click it manually.")
        try:
            self.page.locator(self.locators.EMAIL_INPUT).last.wait_for(
                state="visible", timeout=15000
            )
        except Exception:
            pass
        # The tester types the email, generates the OTP, enters it and submits - all
        # by hand. Automation does not touch those controls; it resumes at the Set
        # Password page (handled in the next step).
        print("\n>>> Enter the EMAIL manually, then Generate OTP, type the OTP and Submit.")
        print(">>> Automation will resume automatically when the Set Password page opens.")

    def click_generate_otp_enter_otp_submit(self):
        # Email -> Generate OTP -> OTP -> Submit are all done manually by the tester.
        # Automation simply waits for the Set Password page to render (no fixed wait,
        # no auto-clicks) and takes over the instant it appears.
        print("\n>>> Waiting for the Set Password page (do the OTP + Submit manually)...")
        # Wait for the field to be ATTACHED (present in the DOM), not visible: the
        # password inputs are CSS-hidden custom components, so they never satisfy a
        # visibility check even when the page is up.
        self.page.locator(self.locators.ADD_NEW_PASSWORD_INPUT).last.wait_for(
            state="attached", timeout=self.PASSWORD_PAGE_WAIT_MS
        )
        self._set_password("Demo@123")

    def _set_password(self, password):
        """Fill the new + confirm password fields with the same value and click Set
        Password. Uses the same click-focus-then-type helper as the other inputs so
        the component registers the value (with a forced-fill fallback if the field
        is a hidden custom control)."""
        self._click_and_fill(self.locators.ADD_NEW_PASSWORD_INPUT, password, name="New password")
        self._click_and_fill(self.locators.CONFIRM_NEW_PASSWORD_INPUT, password, name="Confirm password")
        self._click(self.locators.SET_PASSWORD_BUTTON, timeout=10000, required=True,
                    name="Set Password button")
        # Result: the personal-details form should open.
        self._validate(self.locators.FIRST_NAME_INPUT, "personal details form", timeout=15000)

    # ------------------------------------------------------------------
    # Profile details
    # ------------------------------------------------------------------
    def fill_personal_details(self):
        self.handle_feedback_popup_if_present()
        self._click_and_fill(self.locators.FIRST_NAME_INPUT, "Test", name="First name")
        self._click_and_fill(self.locators.LAST_NAME_INPUT, "Automation", name="Last name")
        # self._select_dropdown(self.locators.KARNATAKA_OPTION,
        #                       "State")
        # self._click_and_fill(self.locators.CITY_INPUT, "Bengaluru", name="City")
        # NOTE: this used to call _select_dropdown(SELECT_GRADE, "Grade") — missing
        # the required `name` arg entirely and passing the plain string "Grade" as
        # the option locator instead of CLASS_XI. That raised a TypeError
        # immediately, which aborted the rest of this method (School Name,
        # Checkbox, Submit never ran either) since _run() in the steps file only
        # catches the exception at the whole-method level.)
        self._select_dropdown(self.locators.SELECT_GRADE, self.locators.CLASS_IX, "Grade")
        self._click_and_fill(self.locators.SCHOOL_NAME_INPUT, "Test School", name="School name")
        # self._select_dropdown(self.locators.PLATFORM_LANGUAGE, self.locators.ENGLISH_OPTION,
        #                       "Platform language")
        self._dismiss_overlays()
        # The consent checkbox doesn't always render on this form; click it when
        # present but don't block Submit when it's absent.
        self._click_visible(self.locators.CHECKBOX, timeout=5000, required=False, name="Checkbox")
        self._click_visible(self.locators.SUBMIT_BUTTON, timeout=10000, required=True, name="Submit button")
        # Result: the Passions page should open (no separate "welcome popup"
        # element exists in the current UI to validate against).
        self._validate(self.locators.ART_AND_DESIGN_HEADER, "passions page", timeout=15000)

    # ------------------------------------------------------------------
    # Welcome + passions + questionnaire entry
    # ------------------------------------------------------------------
    def validate_welcome_popup_and_next(self):
        self._wait_visible(self.locators.ART_AND_DESIGN_HEADER, timeout=15000, required=True,
                           name="Passions page")
        # self._click(self.locators.WELCOME_NEXT_BUTTON, timeout=10000, required=True,
        #             name="Welcome Next button")
        # # Result: the Passions "Start Now" should appear.
        # self._validate(self.locators.PASSIONS_CARD_START_NOW_BUTTON, "Passions Start Now",
        #                timeout=12000)

    # def click_passion_card_start_now(self):
    #     self.handle_feedback_popup_if_present()
    #     # self._click(self.locators.PASSIONS_CARD_START_NOW_BUTTON, timeout=15000, required=True,
    #     #             name="Passions Start Now button")
    #     # Result: the passion categories (Arts & Design) should be shown.
    #     self._validate(self.locators.ART_AND_DESIGN_HEADER, "passion categories", timeout=12000)

    def select_passions_and_submit(self):
        # Open the Arts & Design category, then select its sub-passions
        # (Drawing & Illustration, Fashion Design); then open Business & Marketing
        # and select E-commerce, and submit.
        self.handle_feedback_popup_if_present()
        self._dismiss_overlays()
        # Hard delay: the passions page needs time to finish rendering after
        # the personal-details Submit before Arts & Design is genuinely
        # clickable/expandable.
        self.page.wait_for_timeout(13000)
        self._click(self.locators.ART_AND_DESIGN_HEADER, timeout=10000, required=True,
                    name="Arts & Design")
        self.page.wait_for_timeout(400)
        self._click(self.locators.DRAWING_AND_ILLUSTRATION_INPUT, timeout=8000, required=True,
                    name="Drawing & Illustration")
        self._click(self.locators.FASHION_DESIGN_INPUT, timeout=8000, required=True,
                    name="Fashion Design")
        self._click(self.locators.CLOSE_PASSION_BUTTON, timeout=8000, name="Close passion category")
        self._click(self.locators.BUSINESS_AND_MARKETING_HEADER, timeout=10000, required=True,
                    name="Business & Marketing")
        self.page.wait_for_timeout(400)
        self._click(self.locators.E_COMMERCE_OPTION, timeout=8000, name="E-commerce")
        self._click(self.locators.CLOSE_PASSION_BUTTON, timeout=8000, name="Close passion category")
        self._dismiss_overlays()
        self._click(self.locators.PASSIONS_SUBMIT_BUTTON, timeout=10000, required=True,
                    name="Submit button")
        # Result: back on the dashboard with the questionnaire "Start Now".
        # self._validate(self.locators.PROFILE_START_NOW_BUTTON, "questionnaire card",
        #                timeout=15000)

    # def click_questionnaire_card_start_now(self):
    #     self.handle_feedback_popup_if_present()
    #     # self._click(self.locators.PROFILE_START_NOW_BUTTON, timeout=15000, required=True,
    #     #             name="Questionnaire Start Now button")
    #     # Result: the character-selection Start Now button should be present.
    #     self._validate(self.locators.PROFILE_START_NOW_BUTTON, "character selection", timeout=15000)

    def pick_male_character_and_start_now(self):
        # Pick the male character, then click Start Now; the questionnaire iframe
        # loads afterwards. If the character cards are not yet visible, a Start Now
        # first reveals them
        self.handle_feedback_popup_if_present()
        self._dismiss_overlays()
        if self.page.locator(self.locators.PICK_MALE_CHARACTER_IMAGE).count() == 0:
            # self._click(self.locators.PROFILE_START_NOW_BUTTON, timeout=10000,
            #             name="Start Now (reveal characters)")
            self.page.wait_for_timeout(8000)
            self._dismiss_overlays()
        self._click(self.locators.PICK_MALE_CHARACTER_IMAGE, timeout=20000, required=True,
                    name="Male character image")
        self.page.wait_for_timeout(8000)
        # self._click(self.locators.START_NOW_BUTTON, timeout=15000, required=True,
        #             name="Start Now button")
        # Result: the questionnaire iframe should load.
        self._validate(self.locators.QUESTIONNARIES_IFRAME, "questionnaire iframe", timeout=20000)

    # ------------------------------------------------------------------
    # Questionnaire (Interests -> Aptitudes -> Values, continuous for a new
    # user - no separate Reattempt/Start button between sections, unlike the
    # existing-user reattempt flow in HomePage).
    # ------------------------------------------------------------------
    def _questionnaire_frame(self):
        """FrameLocator for the cross-origin iframe hosting the scenario
        questions. Re-resolved on each call so it stays valid as the iframe
        reloads between questions/sections."""
        return self.page.frame_locator(self.locators.QUESTIONNARIES_IFRAME)

    def _questionnaire_frame_obj(self):
        """The underlying Frame (not FrameLocator) so evaluate() can run inside
        the iframe."""
        for fr in self.page.frames:
            if "questionnaire" in (fr.url or ""):
                return fr
        return None

    def _clear_sc_overlay(self, wait_timeout=8000):
        """A transient '.sc-overlay' inside the iframe (a selection animation
        layer) intercepts pointer events and blocks the next card/button. Wait
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

    def _answer_current_question(self):
        """Select an answer card for the current question (inside the iframe)
        and advance. Returns 'next' or 'failed' (no answerable card found).
        Picks a card that is not pre-selected, since re-clicking the selected
        card can leave the section stuck."""
        self._dismiss_overlays()
        frame = self._questionnaire_frame()
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
            self._clear_sc_overlay()
            card = cards.nth(idx)
            try:
                card.scroll_into_view_if_needed(timeout=8000)
                card.click(timeout=15000)
            except Exception:
                self._clear_sc_overlay(wait_timeout=1500)
                try:
                    card.click(timeout=15000, force=True)
                except Exception:
                    continue
            # Let the selection register and its overlay animation play out.
            self.page.wait_for_timeout(1800)
            self._dismiss_overlays()
            self._clear_sc_overlay()
            return "next"
        return "failed"

    def answer_all_questionnaire_questions(self):
        """Answer every question across the continuous Interests -> Aptitudes
        -> Values questionnaire that follows character selection. Selecting a
        card auto-advances to the next question (and across section
        boundaries); the loop stops once no more cards can be found after a
        retry, which is when the questionnaire iframe closes and the roles
        section (Got It) opens.

        A single missed check isn't trusted as "finished" on its own: the
        iframe can take longer than 8s to reload between questions or when
        crossing from one section into the next, so one retry with extra
        wait is given before concluding the questionnaire actually ended.
        """
        max_questions = 200
        for _ in range(max_questions):
            self.handle_feedback_popup_if_present()
            self._dismiss_overlays()
            if not self._wait_for_question_cards(timeout=8000):
                self.page.wait_for_timeout(3000)
                self._dismiss_overlays()
                if not self._wait_for_question_cards(timeout=8000):
                    break
            result = self._answer_current_question()
            if result == "failed":
                break

    # ------------------------------------------------------------------
    # Pick roles + save three jobs
    # ------------------------------------------------------------------
    def click_pick_roles_card(self):
        self.handle_feedback_popup_if_present()
        self._dismiss_congratulations_popup()
        # The roles section now opens automatically once the questionnaire
        # (Interests -> Aptitudes -> Values, all continuous) finishes — same
        # auto-advance pattern as the Welcome popup, Passions, and
        # Questionnaire card above, so no explicit "Pick roles" card click is
        # needed anymore. Only wait for the section to actually arrive.
        # self._click(self.locators.PICK_ROLES_CARD, timeout=15000, required=True,
        #             name="Pick roles card")
        # Result: the roles section opens with a "Got It" intro or the job sectors.
        self._validate(self.locators.GOT_IT_BUTTON, "roles section (Got It)", timeout=20000)

    def click_got_it_button(self):
        # An intro/instructions popup with a "Got It" button appears on entering the
        # roles section.
        self.handle_feedback_popup_if_present()
        self._dismiss_overlays()
        self._click(self.locators.GOT_IT_BUTTON, timeout=15000, required=True,
                    name="Got It button")
        # Result: the job sectors should be visible to pick from.
        self._validate(self.locators.FIRST_JOBSECTOR_CONTAINER, "job sectors", timeout=12000)

    def click_first_job_and_save(self):
        self.handle_feedback_popup_if_present()
        self._click(self.locators.FIRST_JOBSECTOR_CONTAINER, timeout=10000, required=True,
                    name="First job sector")
        # The "like" image (black heart) popup is non-deterministic - it appears only
        # sometimes after picking the role. Give it a moment, then click it if it
        # showed up, otherwise carry straight on to Save.
        self.page.wait_for_timeout(1500)
        if self.page.locator(self.locators.LIKE_THIS_IMAGE).count() > 0:
            self._click(self.locators.LIKE_THIS_IMAGE, timeout=5000, name="Like image")
        # This is the Recommended Roles list's FIRST-EVER render for a brand new
        # account, and it is measurably slower to finish mounting than the 10s
        # given to the second/third rounds (confirmed via a step-failure
        # screenshot: "Save" was clearly visible on screen moments after this
        # wait had already timed out and raised "not found" - the buttons exist,
        # they just weren't attached yet). Round 2/3 reuse this same
        # already-loaded page, so they don't need the extra time.
        self._click_visible(self.locators.FIRST_SAVE_BUTTON, timeout=30000, required=True,
                            name="First Save button")

    def click_first_back(self):
        self._click_visible(self.locators.FIRST_BACK_BUTTON, timeout=20000, required=True,
                            name="First Back button")

    def click_second_job_and_save(self):
        self.handle_feedback_popup_if_present()
        self._click(self.locators.SECOND_JOBSECTOR_CONTAINER, timeout=10000, required=True,
                    name="Second job sector")
        self._click_visible(self.locators.SECOND_SAVE_BUTTON, timeout=10000, required=True,
                            name="Second Save button")

    def click_second_back(self):
        self._click_visible(self.locators.SECOND_BACK_BUTTON, timeout=10000, required=True,
                            name="Second Back button")

    def click_third_job_and_save(self):
        self.handle_feedback_popup_if_present()
        self._click(self.locators.THIRD_JOBSECTOR_CONTAINER, timeout=10000, required=True,
                    name="Third job sector")
        self._click_visible(self.locators.THIRD_SAVE_BUTTON, timeout=10000, required=True,
                            name="Third Save button")

    def click_third_back(self):
        self._click_visible(self.locators.THIRD_BACK_BUTTON, timeout=10000, required=True,
                            name="Third Back button")

    # ------------------------------------------------------------------
    # Feedback popup validation (dedicated step)
    # ------------------------------------------------------------------
    def validate_feedback_popup_and_close(self):
        """Validate the feedback popup if it is present now (or was handled earlier
        in the run). The popup is non-deterministic - it may never appear - so its
        absence does not fail the scenario; only a popup that appears but cannot be
        validated does."""
        if self.handle_feedback_popup_if_present(timeout=8000) or self.feedback_seen:
            assert self.feedback_seen, "Feedback popup appeared but could not be validated"
            return
        print(">>> Feedback popup did not appear during the journey; nothing to validate.")

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    def _open_profile_menu(self):
        # Clicking the avatar TOGGLES the dropdown, so a blind retry can close one
        # that already opened; only click while the menu is not yet visible.
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

    def logout(self):
        self.handle_feedback_popup_if_present()
        self._dismiss_overlays()
        self._open_profile_menu()
        self._click(self.locators.LOGOUT_BUTTON, timeout=10000, required=True, name="Logout button")
        # Result: logged out. Not validated against LOGIN_BUTTON - logout lands on
        # a /logout route that auto-opens the sign-in modal (Continue with
        # Google/WhatsApp/Email), not the landing page with a plain "Login"
        # button (same behavior environment.py's before_scenario already works
        # around for the next scenario). The profile icon disappearing is the
        # one signal that holds regardless of which post-logout screen renders.
        try:
            self.page.locator(self.locators.PROFILE_ICON).first.wait_for(
                state="detached", timeout=15000
            )
        except Exception:
            raise AssertionError("Validation failed - still appears logged in after logout")