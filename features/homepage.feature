Feature: Homepage validation
  # NOTE ON ORDERING:
  # The scenarios below are split by functional area for readability and
  # reporting clarity. Scenarios tagged @sequential share application state
  # (e.g. completed questionnaires, search results, saved jobs) that is
  # built up by the scenario before it. They must be executed in the order
  # they appear in this file (e.g. `behave --tags=sequential features/`)
  # and are NOT safe to run independently or in parallel.
  #
  # Every scenario includes "Given user is on homepage" even within the
  # @sequential chain: before_scenario always resets navigation to the
  # homepage (context.login_page.goto(Config.BASE_URL)) regardless of what
  # the previous scenario left on screen, so each scenario must re-reach the
  # Matched Roles page itself via this step. What DOES persist across
  # scenarios is server-side state (saved jobs, completed assessments) —
  # only the in-browser navigation position resets.
  @logos
  Scenario: Validate homepage logos
    Given user is on homepage
    Then user validates the ministry of education logo in homepage
    Then user validates the ncert logo in homepage
    Then user validates the wf logo in homepage
  @sequential @passions
  Scenario: Passions and preferences validation
    # Given user is on homepage
    Then user clicks on matches roles section
    Then user clicks passions preferences
    Then user clicks review passions preferences
    Then user validates the selected items in passions review section
    Then user click on submit button in passions section
  @sequential @questionnaires @interests
  Scenario: Complete interests questionnaire
    # Given user is on homepage
    Then user clicks on questionnaires section
    Then user clicks on interests card in questionnaires section and clicks on reattempt button
    Then user clicks on questionnaries choose button and clicks on question cards and click on next button
    Then user attempts all the questions in interests section and clicks on next button
  @sequential @questionnaires @aptitudes
  Scenario: Complete aptitudes questionnaire
    # Given user is on homepage
    Then user clicks start aptitudes and answer all the questions in aptitudes section and clicks on next button
  @sequential @questionnaires @values
  Scenario: Complete values questionnaire
    Given user is on homepage
    Then user clicks on start values and answer all the questions in values section and clicks on next button
  @sequential @reattempt @interests
  Scenario: Reattempt interests section
    # Given user is on homepage
    Then user clicks on interests card and clicks on reattempt button
    Then user slides the slider to 7 or 8 or 8 or 7 and clicks on next button
    Then user clicks on submit button in interests section
    Then user clicks on backarrow button
  @sequential @reattempt @aptitudes
  Scenario: Reattempt aptitudes section
    # Given user is on homepage
    Then user clicks on aptitudes card and clicks on reattempt button
    Then user slides the slider to 7 or 8 or 8 or 7 and clicks on next button
    Then user clicks on submit button in aptitudes section
    Then user clicks on backarrow button
  @sequential @reattempt @values
  Scenario: Reattempt values section
    # Given user is on homepage
    Then user clicks on values card and clicks on reattempt button
    Then user slides the slider to 7 or 8 or 8 or 7 and clicks on next button
    Then user clicks on submit button in values section
    Then user clicks on backarrow button
  @sequential @roles
  Scenario: Validate recommended roles without college degree
    # Given user is on homepage
    Then user clicks on without college degree and validate the recommended roles
  @sequential @roles @search
  Scenario: Search roles and save a job
    # Given user is on homepage
    Then user clicks on search roles
    Then user enters jobrole and add the first job as add saved
    Then user clicks on save menu header and validates the saved job
    Then user clicks on compare roles
    Then user clicks on first and second checkbox in search results and clicks on compare button
  @sequential @roles @compare
  Scenario: Compare roles
    # Given user is on homepage
    Then user clicks on compare roles
    Then user clicks on first and second checkbox in search results and clicks on compare button
  @sequential @share-report
  Scenario: Share report validation
    # Given user is on homepage
    Then user clicks on share report and click and validates the share report options
    Then user validates self review, matched roles, and favourite roles tabs in share report section
    Then user clicks on Saved menu and removes the saved job from favourites
  @help
  Scenario: Help icon validation
    # Given user is on homepage
    Then user clicks on help icon
  @profile
  Scenario: Profile validation
    # Given user is on homepage
    Then user clicks on my profile icon
    Then user clicks on my profile
    Then user edits profile details such as name, state, city, grade and platform language
    Then user revert back the changes to its orginal details
    # Then user clicks on about icon
    Then user logout