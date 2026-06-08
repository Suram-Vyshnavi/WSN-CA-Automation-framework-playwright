from locators.student.login_locators import login_locators
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.locators = login_locators()

    def click_no_thanks(self):
        try:
            self.click(self.locators.NO_THANKS_BUTTON, timeout=5000)
        except Exception:
            pass

    def click_login_button(self):
        if self.is_login_form_open():
            return
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        try:
            loc = self.page.locator(self.locators.LOGIN_BUTTON)
            loc.first.wait_for(state="visible", timeout=15000)
            loc.first.click(timeout=5000)
            self.page.locator(self.locators.EMAIL_INPUT).last.wait_for(
                state="attached", timeout=8000
            )
        except Exception:
            pass

    def click_no_thanks(self):
        try:
            self.click(self.locators.NO_THANKS_BUTTON, timeout=5000)
        except Exception:
            pass

    def enter_email(self, email):
        self.fill(self.locators.EMAIL_INPUT, email)

    def enter_password(self, password):
        self.fill(self.locators.PASSWORD_INPUT, password)

    def click_login(self):
        loc = self.page.locator(self.locators.LOGIN)
        loc.wait_for(state="attached", timeout=5000)
        try:
            # Dismiss CleverTap/notification overlay if present
            overlay = self.page.locator("#wzrk_wrapper")
            if overlay.count() > 0:
                self.page.evaluate("document.getElementById('wzrk_wrapper').style.display='none'")
        except Exception:
            pass
        try:
            loc.click(timeout=5000)
        except Exception:
            loc.click(timeout=5000, force=True)

    def wait_for_login_success(self, timeout=30000):
        self.page.locator(self.locators.MY_PROFILE).first.wait_for(
            state="visible",
            timeout=timeout,
        )

    def open_profile_menu(self):
        profile = self.page.locator(self.locators.MY_PROFILE)
        profile.wait_for(state="visible", timeout=15000)
        try:
            profile.click(timeout=5000)
        except Exception:
            profile.click(timeout=5000, force=True)

    def click_logout(self):
        logout = self.page.locator(self.locators.LOGOUT)
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

        # Wait for login form to be ready
        try:
            self.page.locator(self.locators.EMAIL_INPUT).last.wait_for(
                state="attached", timeout=10000
            )
        except Exception:
            raise Exception("Login form did not open. Cannot log in.")

        self.login_with_credentials(username, password)
        self.wait_for_login_success(timeout=30000)

    def is_login_form_open(self):
        return self.page.locator(self.locators.EMAIL_INPUT).count() > 0

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