class BasePage:
    def __init__(self, page):
        self.page = page
    def goto(self, url):
        self.page.goto(url)
    def click(self, locator,timeout=5000):
        self.page.locator(locator).wait_for(state="attached",timeout=timeout)
        self.page.locator(locator).click()
    def fill(self, locator, text, timeout=5000):
        element = self.page.locator(locator).last
        element.wait_for(state="attached", timeout=timeout)
        try:
            element.fill(text, timeout=timeout)
        except Exception:
            element.fill(text, timeout=timeout, force=True)
    def get_text(self, locator, timeout=5000):
        self.page.locator(locator).wait_for(state="visible",timeout=timeout)
        return self.page.locator(locator).inner_text()
    def wait_for_element(self, locator, state="visible", timeout=5000):
        self.page.locator(locator).wait_for(state=state, timeout=timeout)