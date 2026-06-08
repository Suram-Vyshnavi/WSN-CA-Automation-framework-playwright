class myprofile_locators:
    # Header dropdown trigger. The bare avatar span is ambiguous on the profile
    # page (the large profile photo is also an avatar), so use the header
    # profile container — the same trigger the logout flow relies on.
    MY_PROFILE_ICON = "//div[contains(@class,'profile_container')]"
    MY_PROFILE_HEADER = "//h1[text()='My Profile']"
    FIRST_NAME_INPUT = "//input[@id='firstName']"
    LAST_NAME_INPUT = "//input[@id='lastName']"
    SELECT_STATE = "(//div[@class='ant-select-selection-overflow'])[1]"
    SELECT_STATE_OPTION = "//span[text()='Karnataka']"
    SELECT_STATE_TELANGANA_OPTION = "//span[text()='Telangana']"
    # City is a free-text input, not a dropdown.
    CITY_NAME_INPUT = "//input[@id='cityName']"
    SELECT_GRADE = "(//div[@class='ant-select-selection-overflow'])[3]"
    CLASS_XI = "//span[text()='Class XI']"
    CLASS_X = "//span[text()='Class X']"
    PLATFORM_LANGUAGE = "(//div[@class='ant-select-selection-overflow'])[4]"
    ENGLISH_LANGUAGE = "//span[text()='English']"
    HINDI_LANGUAGE = "//span[text()='Hindi']"
    SAVE_BUTTON = "//button[text()='Save']"

    # Hindi-UI fallbacks. Saving a Hindi platform language switches the whole app to
    # Hindi, so the revert flow can no longer rely on English text. State names
    # ("Karnataka"/"Telangana") stay in Latin in both UIs, but these labels do not.
    MY_PROFILE_HEADER_HINDI = "//h1[text()='मेरी प्रोफ़ाइल']"
    ENGLISH_LANGUAGE_HINDI_UI = "//span[text()='अंग्रेज़ी']"
    SAVE_BUTTON_HINDI_UI = "//button[text()='सेव']"
    SAVE_BUTTON_BY_CLASS = "//button[contains(@class,'wf_default_button')]"

    # First <h1> in the open avatar dropdown (the "My Profile" item, language-
    # independent); and the first option in any open select list.
    PROFILE_MENU_ITEM = "//div[contains(@class,'ant-dropdown') and not(contains(@class,'ant-dropdown-hidden'))]//h1"
    SELECT_OPTION_ITEM = "//div[contains(@class,'ant-select-item-option')]"
