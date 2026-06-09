class myprofile_locators:
    # Header dropdown trigger. The bare avatar span is ambiguous on the profile
    # page (the large profile photo is also an avatar), so use the header
    # profile container — the same trigger the logout flow relies on.
    MY_PROFILE_ICON = "//div[contains(@class,'profile_container')]"
    MY_PROFILE_HEADER = "//h1[text()='My Profile']"
    FIRST_NAME_INPUT = "//input[@id='firstName']"
    LAST_NAME_INPUT = "//input[@id='lastName']"
    SELECT_STATE = "(//div[@class='ant-select-selection-overflow'])[1]"
    # State names render in Latin in both English and Hindi UIs, so a state can be
    # selected generically by its name. Used to restore the captured original state
    # during revert instead of hard-coding a single state.
    STATE_OPTION = "//span[text()='{state}']"
    # City is a free-text input, not a dropdown.
    CITY_NAME_INPUT = "//input[@id='cityName']"
    SELECT_GRADE = "(//div[@class='ant-select-selection-overflow'])[3]"
    CLASS_XI = "//span[text()='Class XI']"
    CLASS_X = "//span[text()='Class X']"
    PLATFORM_LANGUAGE = "(//div[@class='ant-select-selection-overflow'])[4]"
    # Option-scoped language locators. The option list renders the language in the
    # CURRENT UI language: English shows as "English" (English UI) or "अंग्रेज़ी"
    # (Hindi UI); Hindi shows as "Hindi" or "हिंदी". Scope to ant-select-item-option
    # so we never match the field's own selected-value span.
    ENGLISH_OPTION = ("//div[contains(@class,'ant-select-item-option')]"
                      "[.//span[normalize-space()='English' or normalize-space()='अंग्रेज़ी']]")
    HINDI_OPTION = ("//div[contains(@class,'ant-select-item-option')]"
                    "[.//span[normalize-space()='Hindi' or normalize-space()='हिंदी']]")
    SAVE_BUTTON = "//button[text()='Save']"

    # Hindi-UI fallbacks. Saving a Hindi platform language switches the whole app to
    # Hindi, so the revert flow can no longer rely on English text.
    MY_PROFILE_HEADER_HINDI = "//h1[text()='मेरी प्रोफ़ाइल']"
    SAVE_BUTTON_HINDI_UI = "//button[text()='सेव']"
    SAVE_BUTTON_BY_CLASS = "//button[contains(@class,'wf_default_button')]"

    # First <h1> in the open avatar dropdown (the "My Profile" item, language-
    # independent); and the first option in any open select list.
    PROFILE_MENU_ITEM = "//div[contains(@class,'ant-dropdown') and not(contains(@class,'ant-dropdown-hidden'))]//h1"
    SELECT_OPTION_ITEM = "//div[contains(@class,'ant-select-item-option')]"
    