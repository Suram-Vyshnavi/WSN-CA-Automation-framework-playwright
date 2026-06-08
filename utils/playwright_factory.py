from playwright.sync_api import sync_playwright


class PlaywrightFactory:
    def start(self, headless: bool = False):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=headless,
            args=["--start-maximized"],
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        return playwright, browser, context, page
