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
        # Then user clicks on questionnaires section
        # Then user clicks on review button in aptitudes section
        # Then user clicks on reattempt
        # Then user chooses slider option in aptitudes section
        # Then user clicks on 1st question and changes the slider value to 9 or 10 and clicks on update
        # Then user click on submit button in passions section
        # Then user clicks on Go to matched roles
        Then user clicks on without college degree and validate the recommended roles
        Then user clicks on search roles
        Then user enters jobrole and add the first job as favourite
        Then user clicks Favourites and validates the added job
        Then user clicks on share report and click and validates the share report options
        Then user validates self review, matched roles, and favourite roles tabs in share report section
        Then user clicks on Favourites and removes the added job from favourites
        Then user clicks on my profile icon
        Then user clicks on my profile
        Then user edits profile details such as name, state, city, grade and platform language
        Then user revert back the changes to its orginal details
