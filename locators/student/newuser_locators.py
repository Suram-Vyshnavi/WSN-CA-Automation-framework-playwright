class newuser_locators:
    CREATE_NOW_BUTTON = "(//button[text()='Create Now'])[1]"
    CONTINUE_WITH_EMAIL ="(//span[text()='Continue with Email'])[2]"
    EMAIL_INPUT = "(//input[@placeholder='Enter your Email ID'])[2]"
    NEXT_BUTTON ="(//button[text()='Next'])[2]"
    GENERATE_OTP_BUTTON = "//input[@inputmode='numeric' and @maxlength='6']"
    OTP_SUBMIT_BUTTON = "//button[text()='Verify']"
    ADD_NEW_PASSWORD_INPUT = "(//input[@placeholder='Add New Password'])[2]"
    CONFIRM_NEW_PASSWORD_INPUT = "(//input[@placeholder='Confirm Password'])[2]"
    SET_PASSWORD_BUTTON = "(//button[text()='Next'])[2]"
    FIRST_NAME_INPUT = "(//input[@placeholder='First Name'])[2]"
    LAST_NAME_INPUT = "(//input[@placeholder='Last Name'])[2]"
    SELECT_GRADE = "//span[text()='Select Grade']"
    CLASS_IX = "//span[text()='Class IX']"
    #school is a free text input, not a dropdown.
    SCHOOL_NAME_INPUT = "(//input[@placeholder='School Name'])[2]"
    CHECKBOX = "(//input[@type='checkbox'])[2]"
    SUBMIT_BUTTON = "(//button[text()='Submit'])[2]"
    ART_AND_DESIGN_HEADER = "//span[text()='Arts & Design']"
    DRAWING_AND_ILLUSTRATION_INPUT = "//span[text()='Drawing & Illustration']"
    FASHION_DESIGN_INPUT = "//span[text()='Fashion Design']"
    CLOSE_PASSION_BUTTON = "//button[text()='✕']"
    BUSINESS_AND_MARKETING_HEADER = "//span[text()='Business & Marketing']"
    E_COMMERCE_OPTION = "//span[text()='E‑commerce']"
    PASSIONS_SUBMIT_BUTTON = "//button[text()='Submit']"
    PICK_MALE_CHARACTER_IMAGE = "//div[contains(@class,'cs-char-img-wrap--male')]"
    QUESTIONNARIES_IFRAME = "iframe.qv2-iframe"
    CHOOSE_ONE_CARD= "(//div[@class='scenario-card'])[1]"
    FUN_EMOJI_CARD="(//div[@class='fun-meter-card-h'])[2]"
    TWO_CARDS_PRESENT="(//div[@class='forced-card selected'])[1]"
    # Answer-card layouts vary per question (multi-card scenario, emoji fun-meter,
    # 2-card forced choice). Match every card in each layout - selected or not - so
    # the flow can pick an unselected one and keep the Next button enabled.
    SCENARIO_CARDS = "//div[contains(@class,'scenario-card')]"
    FUN_EMOJI_CARDS = "//div[contains(@class,'fun-meter-card-h')]"
    FORCED_CARDS = "//div[contains(@class,'forced-card')]"
    ILLUSTRATED_SCENARIO_CARDS = "//div[@class='illustrated-scenario-card']"
    ANY_QUESTION_CARD = ("//div[contains(@class,'scenario-card') or "
                         "contains(@class,'fun-meter-card-h') or "
                         "contains(@class,'forced-card') or "
                         "contains(@class,'illustrated-scenario-card')]")
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



