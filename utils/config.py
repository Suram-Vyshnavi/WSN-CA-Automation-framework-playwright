import os

class Config:
    

    # Get user type from environment variable, default to 'student'
    USER_TYPE = os.getenv("USER_TYPE", "student").strip().lower()
    USER_TYPE.lower()  # Ensure it's in lowercase for consistency
    if "prod" in USER_TYPE:
        BASE_URL = "https://web.careeradvisor.wadhwanifoundation.org/en"
        
    else:
        BASE_URL = "https://dev.careeradvisor.wadhwanifoundation.org/en"

    USERNAME="ca-automation@yopmail.com"
    PASSWORD="Demo@123"