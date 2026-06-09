Feature: Homepage validation
    Scenario: Homepage validation
        Given user is on homepage
        Then user validates the ministry of education logo in homepage
        Then user validates the ncert logo in homepage
        Then user validates the wf logo in homepage
        Then user clicks on matches roles section
        Then user selects passions preferences
        Then user selects review passions preferences
        Then user validates the selected items in passions review section
        Then user click on submit button in passions section
        Then user clicks on questionnaires section
        Then user clicks on interests card in questionnaires section and clicks on reattempt button
        Then user clicks on questionnaries choose button and clicks on question cards and click on next button 
        Then user attempts all the questions in interests section and clicks on next button
        Then user clicks start aptitudes and answer all the questions in aptitudes section and clicks on next button
        Then user clicks on start values and answer all the questions in values section and clicks on next button
        Then user clicks on interests card and clicks on reattempt button
        Then user slides the slider to 7 or 8 or 8 or 7 and clicks on next button
        Then user clicks on submit button in interests section
        Then user clicks on backarrow button 
        Then user clicks on aptitudes card and clicks on reattempt button
        Then user slides the slider to 7 or 8 or 8 or 7 and clicks on next button
        Then user clicks on submit button in aptitudes section
        Then user clicks on backarrow button
        Then user clicks on values card and clicks on reattempt button
        Then user slides the slider to 7 or 8 or 8 or 7 and clicks on next button
        Then user clicks on submit button in values section
        Then user clicks on backarrow button
        Then user clicks on without college degree and validate the recommended roles
        Then user clicks on search roles
        Then user enters jobrole and add the first job as add saved
        Then user clicks on save menu header and validates the saved job
        Then user clicks on compare roles and validates the compare roles header
        Then user clicks on first and second checkbox in search results and clicks on compare button
        Then user clicks on share report and click and validates the share report options
        Then user validates self review, matched roles, and favourite roles tabs in share report section
        Then user clicks on Favourites and removes the added job from favourites
        Then user clicks on help icon
        Then user clicks on my profile icon
        Then user clicks on my profile
        Then user edits profile details such as name, state, city, grade and platform language
        Then user revert back the changes to its orginal details
        Then user clicks on about icon
        Then user logout

