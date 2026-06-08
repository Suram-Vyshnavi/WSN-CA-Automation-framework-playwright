"""Debug script to inspect login form and find correct button/locators."""
from playwright.sync_api import sync_playwright
import time

URL = "https://dev.careeradvisor.wadhwanifoundation.org/en"
EMAIL = "ca-st1p-may4@yopmail.com"
PASSWORD = "Demo@123"


def fill_react_input(page, selector, value):
    """Fill a React-controlled input by triggering native events."""
    js = """
    (args) => {
        const el = args[0];
        const val = args[1];
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(el, val);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    """
    el = page.locator(selector).last
    el.scroll_into_view_if_needed()
    page.evaluate(js, [el.element_handle(), value])


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()

    print("Navigating to URL...")
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"Initial URL: {page.url}")

    # Dismiss popups
    for btn_text in ["No thanks", "Allow", "Block"]:
        try:
            btn = page.locator(f"//button[text()='{btn_text}']")
            if btn.is_visible(timeout=1000):
                print(f"Clicking '{btn_text}'...")
                btn.click()
                page.wait_for_timeout(1000)
        except Exception:
            pass

    print("\n--- INITIAL PAGE STATE ---")
    print(f"URL: {page.url}")

    # Inspect ALL buttons on page
    all_btns = page.locator("button")
    print(f"\nAll buttons on page: {all_btns.count()}")
    for i in range(min(all_btns.count(), 20)):
        btn = all_btns.nth(i)
        try:
            text = btn.inner_text().strip()[:30]
            cls = (btn.get_attribute('class') or '')[:50]
            typ = btn.get_attribute('type') or ''
            vis = btn.is_visible()
            print(f"  [{i}] visible={vis} type={typ!r} text={text!r} class={cls!r}")
        except Exception:
            pass

    # Inspect spans that might be login triggers
    span_login = page.locator("//span[contains(text(),'Login')]")
    print(f"\nSpan elements with 'Login': {span_login.count()}")
    for i in range(span_login.count()):
        el = span_login.nth(i)
        try:
            cls = el.get_attribute('class') or ''
            vis = el.is_visible()
            parent_tag = el.evaluate('e=>e.parentElement.tagName')
            print(f"  [{i}] visible={vis} parent={parent_tag} class={cls!r}")
        except Exception:
            pass

    # Check email input state
    email_el = page.locator("//input[@id='email']")
    print(f"\nEmail input count: {email_el.count()}")
    if email_el.count() > 0:
        el = email_el.last
        print(f"  visible: {el.is_visible()}")
        try:
            style = el.evaluate('e=>window.getComputedStyle(e).display')
            vis_style = el.evaluate('e=>window.getComputedStyle(e).visibility')
            print(f"  computed display: {style}, visibility: {vis_style}")
            # Walk up to find hidden parent
            print("  Checking parent chain for hidden elements:")
            result = el.evaluate("""
                e => {
                    let el = e;
                    let chain = [];
                    while (el && el !== document.body) {
                        const s = window.getComputedStyle(el);
                        chain.push({
                            tag: el.tagName,
                            class: el.className.substring(0,50),
                            display: s.display,
                            visibility: s.visibility,
                            opacity: s.opacity
                        });
                        el = el.parentElement;
                    }
                    return chain;
                }
            """)
            for item in result[:8]:
                if item['display'] == 'none' or item['visibility'] == 'hidden' or item['opacity'] == '0':
                    print(f"    HIDDEN: {item}")
        except Exception as e:
            print(f"  Error inspecting: {e}")

    print("\n--- TRYING DIFFERENT LOGIN APPROACHES ---")

    # Try clicking each Login button and check if email becomes visible
    login_btns = page.locator("//button[text()='Login']")
    n = login_btns.count()
    print(f"Login buttons: {n}")

    for btn_idx in range(n):
        print(f"\n-- Trying Login button [{btn_idx}] --")
        # Reload fresh page
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        for txt in ["No thanks"]:
            try:
                b = page.locator(f"//button[text()='{txt}']")
                if b.is_visible(timeout=1000):
                    b.click()
                    page.wait_for_timeout(500)
            except Exception:
                pass

        try:
            btns = page.locator("//button[text()='Login']")
            btns.nth(btn_idx).click(timeout=5000)
            print(f"  Clicked button [{btn_idx}]")
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  Click failed: {e}")
            continue

        email_el = page.locator("//input[@id='email']")
        visible = email_el.last.is_visible() if email_el.count() > 0 else False
        print(f"  Email input count: {email_el.count()}, visible: {visible}")
        if visible:
            print(f"  SUCCESS! Button [{btn_idx}] opens the form!")
            break

    print("\n--- ATTEMPTING PROPER LOGIN ---")
    page.wait_for_timeout(1000)

    # If email is visible, fill it properly
    email_el = page.locator("//input[@id='email']")
    if email_el.last.is_visible():
        print("Filling email (visible input)...")
        email_el.last.click()
        email_el.last.fill(EMAIL)
        print("Email filled.")
    else:
        print("Email not visible, trying React native event fill...")
        try:
            fill_react_input(page, "//input[@id='email']", EMAIL)
            print("Email filled via React events.")
        except Exception as e:
            print(f"React fill failed: {e}")

    pwd_el = page.locator("//input[@id='password']")
    if pwd_el.last.is_visible():
        print("Filling password (visible input)...")
        pwd_el.last.click()
        pwd_el.last.fill(PASSWORD)
        print("Password filled.")
    else:
        print("Password not visible, trying React native event fill...")
        try:
            fill_react_input(page, "//input[@id='password']", PASSWORD)
            print("Password filled via React events.")
        except Exception as e:
            print(f"React fill failed: {e}")

    page.wait_for_timeout(1000)

    # Check if submit is enabled
    submit = page.locator("//button[text()='Login']")
    print(f"Submit button count: {submit.count()}")
    if submit.count() > 0:
        disabled = submit.last.get_attribute('disabled')
        print(f"Submit disabled: {disabled}")

    # Hide overlay and click submit
    try:
        page.evaluate("var w=document.getElementById('wzrk_wrapper'); if(w) w.style.display='none';")
    except Exception:
        pass

    try:
        submit.last.click(timeout=5000)
        print("Submit clicked (normal).")
    except Exception as e:
        print(f"Normal click failed: {e}")
        submit.last.click(force=True)
        print("Submit force-clicked.")

    print("Waiting 10s after submit...")
    page.wait_for_timeout(10000)
    print(f"URL after login: {page.url}")

    profile = page.locator("//div[@class='ant-dropdown-trigger ml-3 profile_container']")
    print(f"MY_PROFILE visible: {profile.first.is_visible() if profile.count() > 0 else False}")

    # Print all elements with 'profile' in class
    profile_els = page.locator("[class*='profile']")
    print(f"Elements with 'profile': {profile_els.count()}")
    for i in range(min(profile_els.count(), 5)):
        el = profile_els.nth(i)
        print(f"  [{i}] class={el.get_attribute('class')!r}, visible={el.is_visible()}")

    print("\nDone.")
    time.sleep(20)
    browser.close()
