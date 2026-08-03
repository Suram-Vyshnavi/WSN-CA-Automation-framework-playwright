Feature: NewUser
    Scenario: New user journey
        Given user is on the login page
        Then user clicks on create new button and enters the email
        Then user clicks on generate OTP button and enters the OTP and clicks on verify button
        Then user fills all the details name,state,grade, school name,checkbox and clicks on submit button
        Then user clicks on selected passions items and clicks on submit button
        Then user clicks on one pick male character image
        Then user answers all the questionnaire questions until the profile setup is completed
        Then user clicks on pick roles card
        Then user clicks on got it button
        Then user clicks on firstjob role and clicks on like image button and clicks on first save button
        Then user clicks on first back button
        Then user clicks on secondjob role and clicks on second save button
        Then user clicks on second back button
        Then user clicks on thirdjob role and clicks on third save button
        Then user clicks on third back button
        #feedbackpop will appear anytime if it appears then validate the below steps
        Then user validates the feedback popup and clicks on mca stars button and clicks on next button and closes the popup
        Then user clicks on profile icon and clicks on logout button
