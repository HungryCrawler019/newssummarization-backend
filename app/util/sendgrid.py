import sendgrid
import os
from dotenv import load_dotenv
load_dotenv()
sendgrid_client = sendgrid.SendGridAPIClient(
    api_key=os.getenv('SENDGRID_API_KEY'))
from_mail = os.getenv("SENDGRID_FROM_EMAIL")
