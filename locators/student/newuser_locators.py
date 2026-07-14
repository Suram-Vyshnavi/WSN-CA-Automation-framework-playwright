class newuser_locators:
    CREATE_NOW_BUTTON = "//button[text()='Create Now']"
    EMAIL_INPUT = "//input[@id='email']"
    GENERATE_OTP_BUTTON = "//button[text()='Generate OTP']"
    OTP_SUBMIT_BUTTON = "//button[text()='Submit']"
    ADD_NEW_PASSWORD_INPUT = "//input[@id='password1']"
    CONFIRM_NEW_PASSWORD_INPUT = "//input[@id='password2']"
    SET_PASSWORD_BUTTON = "//button[text()='Set Password']"
    FIRST_NAME_INPUT = "//input[@id='firstName']"
    LAST_NAME_INPUT = "//input[@id='lastName']"
    STATE_SEARCH_INPUT = "//div[@id='Select State-search-input']"
    KARNATAKA_OPTION = "//span[text()='Karnataka']"
    #city is a free text input, not a dropdown.
    CITY_INPUT = "//input[@placeholder='Enter your city, town or village']"
    # Grade / Platform Language use the same search-input id pattern as State
    # (confirmed visible in the DOM); the positional selection-overflow index
    # resolved to hidden nodes and could not be clicked.
    SELECT_GRADE = "//div[@id='Select Grade-search-input']"
    CLASS_XI = "//span[text()='Class XI']"
    #school is a free text input, not a dropdown.
    SCHOOL_NAME_INPUT = "//input[@id='schoolName']"
    PLATFORM_LANGUAGE = "//div[@id='Platform Language-search-input']"
    ENGLISH_OPTION = "//span[text()='English']"
    SUBMIT_BUTTON = "//button[text()='Submit']"
    WELCOME_IMAGE_POPUP = "//img[@class='wm-welcome-img']"
    # The welcome popup advances with a "Next" span; the feedback popup further
    # down uses a "Next" button. Both were named NEXT_BUTTON, so the later button
    # definition shadowed this span and the welcome step could not find its Next.
    # Keep distinct names so each flow targets the right control.
    WELCOME_NEXT_BUTTON = "//span[text()='Next']"
    NEXT_BUTTON = "//span[text()='Next']"
    PASSIONS_CARD_START_NOW_BUTTON = "//span[text()='Start Now']"
    # Passions are grouped under <h4> category headers (confirmed in the DOM - there
    # are no input elements); clicking a category expands its sub-passions, which are
    # <div> text items (same shape as the home review page). Category text is
    # "Arts & Design" (plural).
    ART_AND_DESIGN_HEADER = "//span[text()='Arts & Design']"
    DRAWING_AND_ILLUSTRATION_INPUT = "//span[text()='Drawing & Illustration']"
    FASHION_DESIGN_INPUT = "//span[text()='Fashion Design']"
    CLOSE_PASSION_BUTTON = "//button[text()='✕']"
    BUSINESS_AND_MARKETING_HEADER = "//span[text()='Business & Marketing']"
    E_COMMERCE_OPTION = "//span[text()='E‑commerce']"
    SUBMIT_BUTTON = "//button[text()='Submit']"
    QUESTIONNARIES_START_NOW_BUTTON = "(//span[text()='Start Now'])[3]"
    PICK_MALE_CHARACTER_IMAGE = "//div[contains(@class,'cs-char-img-wrap--male')]"
    START_NOW_BUTTON = "//button[text()='Start Now']"
    QUESTIONNARIES_IFRAME = "iframe.qv2-iframe"
    CHOOSE_ONE_CARD= "(//div[@class='scenario-card'])[1]"
    QUESTIONNAIRE_NEXT_BUTTON = "//span[text()='Next >']"
    FUN_EMOJI_CARD="(//div[@class='fun-meter-card-h'])[2]"
    TWO_CARDS_PRESENT="(//div[@class='forced-card selected'])[1]"
    # Answer-card layouts vary per question (multi-card scenario, emoji fun-meter,
    # 2-card forced choice). Match every card in each layout - selected or not - so
    # the flow can pick an unselected one and keep the Next button enabled.
    SCENARIO_CARDS = "//div[contains(@class,'scenario-card')]"
    FUN_EMOJI_CARDS = "//div[contains(@class,'fun-meter-card-h')]"
    FORCED_CARDS = "//div[contains(@class,'forced-card')]"
    ANY_QUESTION_CARD = ("//div[contains(@class,'scenario-card') or "
                         "contains(@class,'fun-meter-card-h') or "
                         "contains(@class,'forced-card') or (//span[@class='MuiIconButton-label'])[1]")
    # Final scenario question shows "Submit" (a span, inside the iframe) instead
    # of "Next >". Distinct name so the slider flow's button-based SUBMIT_BUTTON
    # further down doesn't shadow it.
    QUESTIONNAIRE_SUBMIT_BUTTON = "//span[text()='Submit']"
    #after completing the aptitude questionnaire, the Start Aptitudes button appears
    START_APTITUDES = "//span[text()='Start Aptitudes']"
    #after completing the values questionnaire, the Start Values button appears
    START_VALUES = "//span[text()='Start Values']"
    PICK_ROLES_CARD = "//span[text()='Pick roles']"
    GOT_IT_BUTTON = "//button[text()='Got It']"
    FIRST_JOBSECTOR_CONTAINER = "(//div[@class='sector-container'])[1]"
    LIKE_THIS_IMAGE = "//td[@class='imgTd']"
    FIRST_SAVE_BUTTON = "//span[text()='Save']"
    FIRST_BACK_BUTTON = "//button[@class='jrd-subnav__back']"
    #the feedback popup appears at anytime if the popup comes below are the locators till close button
    FEEDBACK_POPUP = "//div[@class='mca-step active']"
    MCA_STARS = "//div[@id='mca-stars']"
    # Feedback popup's own "Next" (a button), kept separate from the welcome
    # popup's "Next" span above.
    FEEDBACK_NEXT_BUTTON = "//button[text()='Next']"
    NEXT_BUTTON = "//button[text()='Next']"
    CLOSE_BUTTON="//button[text()='Close']"
    SECOND_JOBSECTOR_CONTAINER = "(//div[@class='sector-container'])[2]"
    SECOND_SAVE_BUTTON = "//span[text()='Save']"
    SECOND_BACK_BUTTON = "//button[@class='jrd-subnav__back']"
    THIRD_JOBSECTOR_CONTAINER = "(//div[@class='sector-container'])[3]"
    THIRD_SAVE_BUTTON = "//span[text()='Save']"
    THIRD_BACK_BUTTON = "//button[@class='jrd-subnav__back']"
    CONGRATULATIONS_CA_POPUP = "//div[@class='ant-modal-body']"
    CLOSE_CONGRATULATIONS_CA_POPUP_BUTTON = "//button[text()='✕']"
    # Logout: open the header profile menu, then click Logout. Returns to the
    # login/landing page (Login button visible).
    PROFILE_ICON = "//div[contains(@class,'profile_container')]"
    # Clicking the avatar TOGGLES the dropdown; this detects that the menu is
    # actually open. The items (My Profile / About / Logout) all render as <h1>
    # inside the ant-dropdown (matches Home_page_locators / login_locators).
    PROFILE_MENU_ITEM = ("//div[contains(@class,'ant-dropdown') and "
                         "not(contains(@class,'ant-dropdown-hidden'))]//h1")
    # Logout entry, scoped to the open dropdown so it can't collide with any other
    # "Logout" text on the page.
    LOGOUT_BUTTON = ("//div[contains(@class,'ant-dropdown') and "
                     "not(contains(@class,'ant-dropdown-hidden'))]//h1[text()='Logout']")
    LOGIN_BUTTON = "(//button[text()='Login'])[1]"



