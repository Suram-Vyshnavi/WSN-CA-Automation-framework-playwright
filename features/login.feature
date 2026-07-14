Feature: Login validation
    Scenario: Valid login
        Given user is on the login page
        When user enters valid credentials
        Then user should be logged in successfully

    
