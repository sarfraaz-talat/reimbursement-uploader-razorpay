import os
from dotenv import load_dotenv

load_dotenv()

razorpay_username = os.environ.get('RAZORPAY_USERNAME')
razorpay_password = os.environ.get('RAZORPAY_PASSWORD')
openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_model = os.environ.get('OPENAI_MODEL')
default_month= os.environ.get('DEFAULT_MONTH')
default_year= os.environ.get('DEFAULT_YEAR')