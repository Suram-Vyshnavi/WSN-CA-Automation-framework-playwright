class HomePageLocators:
    CONGRATULATIONS_TEST_CLOSE_BUTTON = "//button[@class='cm-close-btn']"
    VALIDATE_MINISTRY_OF_EDUCATION_LOGO = "//img[@class='wf_image header-image false no-js-MinistryLogoImage-BOa82aeV']"
    VALIDATE_NCERT_LOGO = "//img[@class='wf_image header-image false no-js-NcertLogoImage-AywozVcO']"
    VALIDATE_WF_LOGO = "//img[@class='wf_image header-image false no-js-WfLogoImage-BAZ2fEjy']"
    MATCHED_ROLE = "//div[text()='Matched Roles']"
    PASSIONS_HEADER = "//h4[text()='Passions']"
    REVIEW_BUTTON = "//button[text()='Review']"
    ART_AND_DESIGN_HEADER = "//span[text()='Arts & Design']"
    DRAWING_AND_ILLUSTRATION_INPUT = "//span[text()='Drawing & Illustration']"
    FASHION_DESIGN_INPUT = "//span[text()='Fashion Design']"
    CLOSE_PASSION_BUTTON = "//button[text()='✕']"
    BUSINESS_AND_MARKETING_HEADER = "//span[text()='Business & Marketing']"
    E_COMMERCE_OPTION = "//span[text()='E‑commerce']"
    SUBMIT_BUTTON = "//button[text()='Submit']"
    # The Profile (Level 2) accordion header inside the Self Review panel.
    # Expanding it reveals the Interests / Aptitudes / Values cards. The text node
    # carries surrounding whitespace, so match with normalize-space().
    PROFILE_HEADER = "//h4[normalize-space()='Profile']"

    # Profile cards (one per assessment)
    INTERESTS_CARD = "(//img[@class='wf_image qmc-icon no-js-svg%3e'])[1]"
    APTITUDES_CARD = "(//div[@class='questionnaire-mini-card qmc-completed'])[2]"
    VALUES_CARD = "(//div[@class='questionnaire-mini-card qmc-completed'])[3]"

    # Reattempt buttons (one per card, indexed in the same order as the cards)
    REATTEMPT_BUTTONS = "//button[text()='Reattempt']"
    INTERESTS_REATTEMPT_BUTTON = "(//button[text()='Reattempt'])[1]"
    APTITUDES_REATTEMPT_BUTTON = "(//button[text()='Reattempt'])[2]"
    VALUES_REATTEMPT_BUTTON = "(//button[text()='Reattempt'])[3]"
    QUESTIONNAIRES_CHOOSE_BUTTON = "(//button[text()='Choose'])[1]"
    # The questionnaire (scenario) questions render inside a cross-origin iframe;
    # all cards / Next button live in this frame, so interactions must target it.
    QUESTIONNAIRE_IFRAME = "iframe.qv2-iframe"
    #already there will be answers according to the cards selected, so according to the locators if the user clicks on same card the next button will disabled so at that moment it has to click on card again to visible the next button
    CHOOSE_ONE_CARD= "(//div[@class='scenario-card'])[1]"
    # The questionnaire (scenario) flow advances with a "Next >" span; the slider
    # flow further down uses a "Next" button, so keep them under distinct names
    # (otherwise the later NEXT_BUTTON definition shadows this one).
    # QUESTIONNAIRE_NEXT_BUTTON = "//span[text()='Next >']"
    FUN_EMOJI_CARD="(//div[@class='fun-meter-card-h'])[2]"
    TWO_CARDS_PRESENT="(//div[@class='forced-card selected'])[1]"
    # Answer-card layouts vary per question (multi-card scenario, emoji fun-meter,
    # 2-card forced choice). Match every card in each layout - selected or not - so
    # the flow can pick an unselected one and keep the Next button enabled.
    SCENARIO_CARDS = "//div[contains(@class,'scenario-card')]"
    FUN_EMOJI_CARDS = "//div[contains(@class,'fun-meter-card-h')]"
    FORCED_CARDS = "//div[contains(@class,'forced-card')]"
    ILLUSTRATED_SCENARIO_CARDS = "(//div[@class='illustrated-scenario-card'])[1]"
    ANY_QUESTION_CARD = ("//div[contains(@class,'scenario-card') or "
                         "contains(@class,'fun-meter-card-h') or "
                         "contains(@class,'forced-card')]")
    # Final scenario question shows "Submit" (a span, inside the iframe) instead
    # of "Next >". Distinct name so the slider flow's button-based SUBMIT_BUTTON
    # further down doesn't shadow it.
    # QUESTIONNAIRE_SUBMIT_BUTTON = "//span[text()='Submit']"
    #after completing the aptitude questionnaire, the Start Aptitudes button appears
    START_APTITUDES = "(//button[text()='Choose'])[1]"
    # #after completing the values questionnaire, the Start Values button appears
    START_VALUES = "(//button[text()='Choose'])[1]"


    # Shared questionnaire flow elements (identical across all three assessments)
    # Reattempt opens a "How would you like to assess yourself?" modal with two
    # options; the Slider option is the 2nd Choose button. Choosing it then shows
    # a Retake button that opens the ratings/questions page.
    SLIDER_CHOOSE_BUTTON = "(//button[text()='Choose'])[2]"
    RETAKE_BUTTON = "//button[text()='Retake']"
    CHOOSING_SLIDER = "//div[@class='ant-slider ant-slider-horizontal']"
    # If it is on 7 slide it to 8, if it is on 8 slide it to 7. Answer every
    # question the same way, clicking Next until the Submit button appears.
    QUESTION_SLIDER = "//div[@role='slider']"
    CHOOSE_SLIDER_OPTION_9 = "//div[@role='slider']"
    NEXT_BUTTON = "//button[text()='Next']"
    SUBMIT_BUTTON = "//button[text()='Submit']"
    BACK_ARROW = "//img[@class='wf_image back-arrow no-js-svg%3e']"
    GO_TO_MATCHED_ROLES_BUTTON = "//span[text()='Go to Matched Roles']"
    # CAREER_PLANNING_POPUP="//div[@class='mca-step active']"
    # STARS_RATING="//div[@ID='mca-stars']"
    # NEXT_BUTTON="//button[text()='Next']"
    # FEEDBACK_POPUP="//div[@class='mca-step active']"
    # CLOSE_BUTTON="//button[text()='Close']"

    WITHOUT_COLLEGE_DEGREE = "//span[text()='Without College Degree']"
    VALIDATE_RECOMMENDED_ROLES_PASSION_HEADER_MATCHED_COUNT = "(//span[@class='header-count'])[1]"
    VALIDATE_RECOMMENDED_ROLES_QUESTIONNAIRES_HEADER_MATCHED_COUNT = "(//span[@class='header-count'])[2]"
    # JOB_ROLE_FIRST_ROLE_CONTAINER = "(//div[@class='role-container'])[1]"
    # ABOUT_HEADER = "//div[text()='About']"
    # JOB_DESCRIPTION_DOWN_ARROW_BUTTON="(//img[@class='wf_image accordion_icon no-js-svg%3e'])[1]"
    # JOB_DESCRIPTION_AUDIO_BUTTON_IMAGE = "(//img[@class='audio-button-image false'])[1]"
    # DAY_AT_WORK_DOWN_ARROW_BUTTON = "(//img[@class='wf_image accordion_icon no-js-svg%3e'])[2]"
    # ATTRACTIONS_OF_THIS_JOB_DOWN_ARROW_BUTTON = "(//img[@class='wf_image accordion_icon no-js-svg%3e'])[3]"
    # CHALLENGES_OF_THIS_JOB_DOWN_ARROW_BUTTON = "(//img[@class='wf_image accordion_icon no-js-svg%3e'])[4]"
    # HOW_TO_PREPARE_FOR_THIS_JOB_DOWN_ARROW_BUTTON = "(//img[@class='wf_image accordion_icon no-js-svg%3e'])[5]"
    # VIEW_ALL_BUTTON = "//button[text()='View All']"
    # CAREER_PATHWAYS_HEADER = "//div[text()='Career Pathways']"
    # TECHNICAL_SPECIALIST_PATHWAY = "//h4[text()='Technical Specialist Pathway']"
    # PROJECT_MANAGEMENT_PATHWAY = "//h4[text()='Project Management Pathway']"
    # ENTREPRENEURIAL_PATHWAY = "//h4[text()='Entrepreneurial Pathway']"
    # PERSONAL_TRAITS_HEADER = "//div[text()='Personal Traits']"
    # TOP_APTITUDES = "//h4[text()='Top Aptitudes']"
    # TOP_INTERESTS = "//h4[text()='Top Interests']"
    # TOP_VALUES = "//h4[text()='Top Values']"
    # EMPLOYERS_HEADER = "//div[text()='Employers']"
    # POTENTIAL_EMPLOYERS = "//h4[text()='Potential Employers']"

    SEARCH_ROLES_HEADER="//div[text()='Search Roles']"
    SEARCH_ROLES_INPUT = "//input[@placeholder='Search for a Job Role']"
    VALIDATE_RESULTS_HEADER = "//h4[text()='Results']/following::h4[1]"
    ADD_SAVE = "(//h4[text()='Save'])[1]"
    FIRST_RESULT_SAVED_STATE = "(//h4[text()='Saved'])[1]"
    SAVED_MENU_HEADER="//div[text()='Saved']"
    COMPARE_ROLES = "//button[@class='compare-sticky-strip__btn']"
    FIRST_FAV_CHECKBOX = "(//div[@class='fav-checkbox'])[1]"
    SECOND_FAV_CHECKBOX = "(//div[@class='fav-checkbox'])[2]"
    COMPARE_BUTTON = "//button[contains(text(),'Compare')]"
    SHARE_REPORT_HEADER= "//div[text()='Share Report']"
    SHARE_REPORT_BUTTON = "//span[text()='Share']"
    SELF_REVIEW_TAB = "//div[text()='Self Review']"
    MATCHED_ROLES_TAB = "(//div[text()='Matched Roles'])[2]"
    SAVED_ROLES_TAB = "//div[@class='menu-container  selected']"
    REMOVE_SAVED_JOB = "//h4[text()='Saved']"
    HELP_ICON = "//button[text()='Help?']"
    ABOUT_HEADER = "//h1[text()='About']"

    # Header avatar dropdown trigger (the same container the profile / logout
    # flows rely on).
    PROFILE_ICON = "//div[contains(@class,'profile_container')]"
    # First <h1> in the open avatar dropdown - used to detect that the menu
    # actually opened (the items "My Profile" / "About" / "Logout" all render as
    # <h1>).
    PROFILE_MENU_ITEM = ("//div[contains(@class,'ant-dropdown') and "
                         "not(contains(@class,'ant-dropdown-hidden'))]//h1")
    # The "About" item inside the open dropdown. Scoped to the open dropdown so
    # it does not collide with the About page heading of the same text.
    ABOUT_MENU_ITEM = ("//div[contains(@class,'ant-dropdown') and "
                       "not(contains(@class,'ant-dropdown-hidden'))]//h1[text()='About']")








