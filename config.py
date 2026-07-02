import os
from dotenv import load_dotenv

load_dotenv(override=True)

ENV = "DEV2"

# 1. Környezet-specifikus
PUBLISH_HOST = os.getenv(f"{ENV}_PUBLISH_HOST")
AGREEMENT_HOST = os.getenv(f"{ENV}_AGREEMENT_HOST")
QUOTE_HOST = os.getenv(f"{ENV}_QUOTE_HOST")
AGREEMENT_API_KEY = os.getenv(f"{ENV}_AGREEMENT_API_KEY")
QUOTE_API_KEY = os.getenv(f"{ENV}_QUOTE_API_KEY")
PUBLISH_X_API_KEY = os.getenv(f"{ENV}_PUBLISH_X_API_KEY")

# 2. Globális
TENANT_ID = os.getenv("TENANT_ID", "MT")
MONOGRAM = os.getenv("MONOGRAM")
CUSTOMER_ID = os.getenv("CUSTOMER_ID")
CREATED_BY = os.getenv("CREATED_BY")

# 3. FIX FEJLÉCEK
PUBLISH_HEADERS = {
    "x-channel-id": os.getenv("PUBLISH_X_CHANNEL_ID"),
    "brand": os.getenv("PUBLISH_BRAND"),
    "x-m2m-user-id": os.getenv("PUBLISH_X_M2M_USER_ID"),
    "x-Client-Id": os.getenv("PUBLISH_X_CLIENT_ID"),
    "x-Client-Version": os.getenv("PUBLISH_X_CLIENT_VERSION"),
    "x-request-session-id": os.getenv("PUBLISH_X_REQUEST_SESSION_ID"),
    "Content-Type": "application/json",
    "x-api-key": PUBLISH_X_API_KEY,
}

# Agreement alap fejléc
AGREEMENT_BASE_HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": AGREEMENT_API_KEY,
}

# Calculate Min alap fejléc
CALCULATE_MIN_BASE_HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": QUOTE_API_KEY,
    "x-channel-id": "12",
    "x-context-id": "123",
    "x-correlation-id": "1234",
    "x-m2m-user-id": "12345",
    "x-source-system": "123456",
    "x-source-system-user": "1234567",
    "x-parent-request-id": "12345678",
    "tenantId": TENANT_ID,
}
