from locators.student.login_locators import login_locators
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.locators = login_locators()

    def click_no_thanks(self):
        self.click(self.locators.NO_THANKS_BUTTON, timeout=15000)

    def click_login_button(self):
        login_btn = self.page.locator(self.locators.LOGIN_BUTTON).first
        login_btn.wait_for(state="visible", timeout=5000)
        try:
            login_btn.click(timeout=5000)
        except Exception:
            login_btn.click(timeout=5000, force=True)

    def enter_email(self, EMAIL):
        self.click(self.locators.CONTINUE_WITH_EMAIL, timeout=5000)
        self.fill(self.locators.EMAIL_INPUT, EMAIL)
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
        self.wait_for_login_success()

    def ensure_logged_in(self, username, password):
        if self.is_logged_in():
            return

        if not self.is_login_form_open():
            self.click_login_button()

        self.login_with_credentials(username, password)

    def is_login_form_open(self):
        return self.page.locator(self.locators.EMAIL_INPUT).last.is_visible()

    def is_logged_in(self):
        return self.page.locator(self.locators.MY_PROFILE).first.is_visible()

    def is_logged_out(self):
        try:
            self.page.locator(self.locators.LOGIN_BUTTON).first.wait_for(
                state="visible",
                timeout=10000,
            )
            return True
        except Exception:
            return False