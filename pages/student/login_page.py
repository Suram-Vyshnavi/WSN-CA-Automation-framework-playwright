from locators.student.login_locators import login_locators
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.locators = login_locators()

    def click_no_thanks(self):
        btn = self._first_visible(self.locators.NO_THANKS_BUTTON, timeout=15000)
        try:
            btn.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        try:
            btn.click(timeout=5000)
        except Exception:
            btn.click(timeout=5000, force=True)

    def click_login_button(self):
        login_btn = self.page.locator(self.locators.LOGIN_BUTTON).first
        login_btn.wait_for(state="visible", timeout=5000)
        try:
            login_btn.click(timeout=5000)
        except Exception:
            login_btn.click(timeout=5000, force=True)

    def _first_visible(self, xpath, timeout=10000):
        """Return whichever match for xpath is actually visible.

        This app renders duplicate elements sharing the same text/id (e.g. a
        hidden Sign Up tab's "Continue with Email" alongside the visible
        Login tab's), so a fixed ordinal index (.first / .last / [2]) is
        unreliable and can silently target the wrong, invisible copy —
        especially when force=True click fallbacks mask the mismatch.
        """
        locator = self.page.locator(xpath)
        locator.first.wait_for(state="attached", timeout=timeout)
        count = locator.count()
        for i in range(count):
            candidate = locator.nth(i)
            try:
                if candidate.is_visible():
                    return candidate
            except Exception:
                continue
        return locator.first

    def enter_email(self, email):
        continue_btn = self._first_visible(self.locators.CONTINUE_WITH_EMAIL)
        continue_btn.scroll_into_view_if_needed(timeout=5000)
        try:
            continue_btn.click(timeout=5000)
        except Exception:
            continue_btn.click(timeout=5000, force=True)

        email_input = self._first_visible(self.locators.EMAIL_INPUT, timeout=10000)
        email_input.fill(email)
        self.click(self.locators.NEXT_BUTTON, timeout=5000)

    def enter_password(self, password):
        self.fill(self.locators.PASSWORD_INPUT, password)

    def click_login(self):
        sign_in_btn = self.page.locator(self.locators.LOGIN_BUTTON).first
        # Use the dedicated LOGIN locator for the modal's submit button
        # instead of indexing LOGIN_BUTTON with .last — relying on
        # positional ordering is fragile if the DOM structure shifts.
        login_submit_btn = self.page.locator(self.locators.LOGIN)

        try:
            sign_in_btn.wait_for(state="visible", timeout=3000)
            try:
                sign_in_btn.click(timeout=5000)
            except Exception:
                sign_in_btn.click(timeout=5000, force=True)
            return
        except Exception:
            pass

        login_submit_btn.wait_for(state="visible", timeout=5000)
        try:
            login_submit_btn.click(timeout=5000)
        except Exception:
            login_submit_btn.click(timeout=5000, force=True)

    def wait_for_login_success(self, timeout=30000):
        self.page.locator(self.locators.MY_PROFILE).first.wait_for(
            state="visible",
            timeout=timeout,
        )

    def open_profile_menu(self):
        # MY_PROFILE is the profile container that opens the menu when
        # clicked. PROFILE_MENU was referenced here previously but was
        # never defined in login_locators, which would raise an
        # AttributeError as soon as logout() ran.
        profile = self.page.locator(self.locators.MY_PROFILE).first
        profile.wait_for(state="visible", timeout=15000)
        try:
            profile.click(timeout=5000)
        except Exception:
            profile.click(timeout=5000, force=True)

    def click_logout(self):
        logout = self.page.locator(self.locators.LOGOUT).first
        logout.wait_for(state="visible", timeout=15000)
        try:
            logout.click(timeout=5000)
        except Exception:
            logout.click(timeout=5000, force=True)

    def logout(self):
        self.open_profile_menu()
        self.click_logout()

    def login_with_credentials(self, username, password):
        self.enter_email(username)
        self.enter_password(password)
        self.click_login()

    def ensure_logged_in(self, username, password):
        if self.is_logged_in():
            return

        if not self.is_login_form_open():
            self.click_login_button()

        # Wait for a *visible* "Continue with Email" — not just any match,
        # since a hidden duplicate can be attached without the real modal
        # having opened. See _first_visible() for why ordinal indexing
        # (.first/.last) isn't reliable here.
        try:
            self._first_visible(self.locators.CONTINUE_WITH_EMAIL, timeout=10000)
        except Exception:
            raise Exception("Login form did not open. Cannot log in.")

        self.login_with_credentials(username, password)
        self.wait_for_login_success(timeout=30000)

    def is_login_form_open(self):
        try:
            self._first_visible(self.locators.CONTINUE_WITH_EMAIL, timeout=1000)
            return True
        except Exception:
            return False

    def is_logged_in(self):
        # A plain instantaneous is_visible() races against the app's
        # post-login redirect (login confirmation -> dashboard), which can
        # briefly unmount the profile icon and produce a false negative right
        # after a successful login. Give it a short grace period instead.
        try:
            self.page.locator(self.locators.MY_PROFILE).first.wait_for(
                state="visible", timeout=5000
            )
            return True
        except Exception:
            return False

    def is_logged_out(self):
        try:
            self.page.locator(self.locators.LOGIN_BUTTON).first.wait_for(
                state="visible",
                timeout=10000,
            )
            return True
        except Exception:
            return False