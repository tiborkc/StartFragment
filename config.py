import os
from dotenv import load_dotenv

load_dotenv()

PUBLISH_HOST = os.getenv("PUBLISH_HOST")

AGREEMENT_HOST = os.getenv("AGREEMENT_HOST")
QUOTE_HOST = os.getenv("QUOTE_HOST")

AGREEMENT_API_KEY = os.getenv("AGREEMENT_API_KEY")
QUOTE_API_KEY = os.getenv("QUOTE_API_KEY")

MONOGRAM = os.getenv("MONOGRAM")
CUSTOMER_ID = os.getenv("CUSTOMER_ID")
CREATED_BY = os.getenv("CREATED_BY")

PUBLISH_HEADERS = {
    "x-channel-id": os.getenv("PUBLISH_X_CHANNEL_ID"),
    "brand": os.getenv("PUBLISH_BRAND"),
    "x-m2m-user-id": os.getenv("PUBLISH_X_M2M_USER_ID"),
    "x-Client-Id": os.getenv("PUBLISH_X_CLIENT_ID"),
    "x-Client-Version": os.getenv("PUBLISH_X_CLIENT_VERSION"),
    "x-request-session-id": os.getenv("PUBLISH_X_REQUEST_SESSION_ID"),
    "Content-Type": "application/json",
    "x-api-key": os.getenv("PUBLISH_X_API_KEY"),
}
