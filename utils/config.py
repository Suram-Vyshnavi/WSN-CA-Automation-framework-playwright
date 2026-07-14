import os

class Config:
    

    # Get user type from environment variable, default to 'student'
    USER_TYPE = os.getenv("USER_TYPE", "student").strip().lower()
    USER_TYPE.lower()  # Ensure it's in lowercase for consistency
    if "prod" in USER_TYPE:
        BASE_URL = "https://web.careeradvisor.wadhwanifoundation.org/en"
        ENVIRONMENT = "prod"
    else:
        BASE_URL = "https://dev.careeradvisor.wadhwanifoundation.org/en"
        ENVIRONMENT = "dev"

    # Title shown at the top of the generated HTML report.
    REPORT_TITLE = f"behave report for {ENVIRONMENT} environment"
    # Credentials based on user type
    if USER_TYPE == "dev":
        USERNAME = "ca-automation@yopmail.com"
        PASSWORD = "Demo@123"
    elif USER_TYPE == "prod":
        USERNAME = "ca_automation@yopmail.com"
        PASSWORD = "Demo@123"