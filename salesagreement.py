from datetime import datetime, timezone, timedelta
import uuid
import requests
from config import (
    AGREEMENT_BASE_HEADERS,
    AGREEMENT_HOST,
    CALCULATE_MIN_BASE_HEADERS,
    CREATED_BY,
    MONOGRAM,
    PUBLISH_HEADERS,
    PUBLISH_HOST,
    QUOTE_HOST,
    TENANT_ID,
)

# MANUAL INPUT
quoteId = "1000001568"

# GENERATED VALUES
now = datetime.now(timezone.utc)
current_timestamp = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
current_date = now.strftime("%Y-%m-%d %H:%M:%S")
compact_date = now.strftime("%Y%m%d%H%M%S")

current_unix_ms = int(now.timestamp() * 1000)

GENERATED_ID = f"{MONOGRAM}{compact_date}"
AGREEMENT_NAME = f"Egyedi szolgáltatási szerződés"


def new_guid():
    return str(uuid.uuid4())


def update_unique_product_id(data):
    for item in data:
        for quote_item in item.get("quoteItems", []):
            for po in quote_item.get("productOfferings", []):
                for char in po.get("characteristics", []):
                    if char.get("name") == "uniqueProductId":
                        # Ha nincs "value" kulcs, vagy üres/None, akkor generálunk egyet
                        if not char.get("value"):
                            char["value"] = new_guid()

AGREEMENT_HEADERS = {
    **AGREEMENT_BASE_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

calculate_min_headers = {
    **CALCULATE_MIN_BASE_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

# --- 0. GET SOURCE QUOTE & PATCH UNIQUE PRODUCT ID ---

print("0. GET SOURCE QUOTE & UPDATE UNIQUE PRODUCT ID")

get_headers = {
    **calculate_min_headers,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

get_response = requests.get(
    f"{QUOTE_HOST}/quoteManagement/int/v1/quotes/{quoteId}",
    headers=get_headers,
)

print(f"GET Quote STATUS: {get_response.status_code}")
get_response.raise_for_status()

source_quote_json = get_response.json()
source_quote_data = (
    source_quote_json if isinstance(source_quote_json, list) else [source_quote_json]
)

update_unique_product_id(source_quote_data)

patch_source_headers = {
    **calculate_min_headers,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
    "Connection": "close",
}

patch_source_response = requests.patch(
    f"{QUOTE_HOST}/quoteManagement/int/v1/quotes/{quoteId}",
    headers=patch_source_headers,
    json=source_quote_data[0],
)

print(f"Source Quote PATCH STATUS: {patch_source_response.status_code}")
if patch_source_response.status_code != 200:
    print(f"Body: {patch_source_response.text}")
patch_source_response.raise_for_status()
print()


# --- 1. CALCULATE MIN & EXTRACT DATA FROM QUOTE RESPONSE ---

print("1. CALCULATE MIN")

calculate_min_body = {"quoteId": quoteId}

calculate_min_response = requests.post(
    f"{QUOTE_HOST}/quoteManagement/internal/v1/calculateMin",
    headers=calculate_min_headers,
    json=calculate_min_body,
)

print(f"STATUS: {calculate_min_response.status_code}")
print(f"GENERATED ID: {GENERATED_ID}")
print()

calculate_min_response.raise_for_status()
calculate_min_json = calculate_min_response.json()

quote_resp = calculate_min_json[0]

customer_id = next(
    (party.get("id") for party in quote_resp.get("relatedParties", []) if party.get("role") == "owner" and party.get("entityReferredType") == "Customer"),
    "494910914"
)

opportunity_entity = next(
    (entity for entity in quote_resp.get("relatedEntities", []) if entity.get("entityType") == "Opportunity"),
    {}
)
opportunity_id = opportunity_entity.get("relatedEntityId", "HU-MT~0069M00000jkZ0rQAE")
opportunity_business_id = opportunity_entity.get("relatedEntityBusinessId", "8067158")


# --- 2. SALES AGREEMENT CREATE (DRAFT) ---

agreement_create_body = {
    "id": GENERATED_ID,
    "name": AGREEMENT_NAME,
    "businessId": GENERATED_ID,
    "status": "draft",
    "salesModel": "NORMAL",
    "duration": {
        "timePeriod": 36,
        "type": "month"
    },
    "agreementPeriod": {
        "startDateTime": current_timestamp,
        "endDateTime": "2029-07-21T21:59:59Z"
    },
    "type": "commercial",
    "subType": "salesAgreement",
    "agreementAuthorizations": [
        {
            "date": current_timestamp,
            "authorizedBy": {
                "entityReferredType": "Customer",
                "id": customer_id  
            },
            "signatureRepresentation": "paper",
            "state": "signed",
            "type": "authorization"
        }
    ],
    "characteristics": [
        {"name": "isFrameAgreement", "value": "false"},
        {"name": "paymentPeriod", "value": "1Month"},
        {"name": "isProjectStartWithoutContract", "value": "false"},
        {"name": "processType", "value": "Webshop"},
        {"name": "businessContext", "value": "greenfield"}
    ],
    "relatedParties": [
        {
            "entityReferredType": "Customer",
            "id": customer_id,
            "role": "contractOwner"
        }
    ],
    "relatedEntities": [
        {
            "entityType": "Opportunity",
            "relatedEntityId": opportunity_id,
            "relatedEntityBusinessId": opportunity_business_id,
            "role": "originalOpportunity",
            "characteristics": [
                {
                    "name": "type",
                    "value": "IT / SI monthly NEW / ACQUISITION"
                }
            ]
        }         
    ],
    "budgets": [],
    "termOrConditions": [
        {
            "name": "agreementDetails",
            "characteristics": [
                {"name": "paymentDueDays", "value": "15"},
                {"name": "leadTimeDays", "value": "30"},
                {"name": "noticePeriodDurationType", "value": "day"},
                {"name": "noticePeriodDuration", "value": "30"}
            ]
        }
    ]
}

print("2. AGREEMENT CREATE (DRAFT)")

agreement_create_response = requests.post(
    f"{AGREEMENT_HOST}/agreements/internal/v2/agreements/actions/submit-agreement",
    headers=AGREEMENT_HEADERS,
    json=agreement_create_body,
)

print(f"STATUS: {agreement_create_response.status_code}")
agreement_create_response.raise_for_status()
current_response_json = agreement_create_response.json()
print()


# --- 3. AGREEMENT UPDATE (INPROCESS) ---

print("3. AGREEMENT UPDATE (INPROCESS)")

current_response_json["status"] = "inProcess"

update_headers = {
    **AGREEMENT_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

agreement_inprocess_response = requests.post(
    f"{AGREEMENT_HOST}/agreements/internal/v2/agreements/actions/submit-agreement",
    headers=update_headers,
    json=current_response_json,
)

print(f"STATUS: {agreement_inprocess_response.status_code}")

if agreement_inprocess_response.status_code != 200:
    print(f"Body: {agreement_inprocess_response.text}")
agreement_inprocess_response.raise_for_status()
current_response_json = agreement_inprocess_response.json()
print()


# --- 4. AGREEMENT UPDATE (SIGNED) ---

print("4. AGREEMENT UPDATE (SIGNED)")

current_response_json["status"] = "signed"

update_headers = {
    **AGREEMENT_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

agreement_signed_response = requests.post(
    f"{AGREEMENT_HOST}/agreements/internal/v2/agreements/actions/submit-agreement",
    headers=update_headers,
    json=current_response_json,
)

print(f"STATUS: {agreement_signed_response.status_code}")
if agreement_signed_response.status_code != 200:
    print(f"Body: {agreement_signed_response.text}")
agreement_signed_response.raise_for_status()
current_response_json = agreement_signed_response.json()
print()

# --- 5. KAFKA SAVE ACTIVE ---

print("5. KAFKA SAVE ACTIVE")

kafka_active_body = {
    "header": {
        "masterId": GENERATED_ID,
        "associationId": GENERATED_ID,
        "tenantId": TENANT_ID,
        "trackingId": new_guid(),
        "messageId": new_guid(),
        "producerId": {"name": "SalesForce"},
        "eventType": "AgreementUpdated",
        "operation": "UPDATE",
        "masterTimestamp": current_unix_ms,
    },
    "body": {
        "Agreement": {
            "id": GENERATED_ID,
            "name": AGREEMENT_NAME,
            "status": "active",
            "type": "commercial",
            "subType": "salesAgreement",
            "characteristics": [
                {"name": "isFrameAgreement", "value": "false"},
                {"name": "paymentPeriod", "value": "1Month"},
                {"name": "isProjectStartWithoutContract", "value": "false"},
                {"name": "processType", "value": "Webshop"},
                {"name": "businessContext", "value": "greenfield"}
            ],
            "agreementAuthorizations": [
                {
                    "authorizedBy": {
                        "entityReferredType": "Customer",
                        "id": customer_id,
                    },
                    "date": current_timestamp,
                    "type": "authorization",
                    "signatureRepresentation": "paper",
                    "state": "signed",
                }
            ],
            "duration": {
                "timePeriod": 36,
                "type": "month"
            },
            "agreementPeriod": {
                "startDateTime": current_timestamp,
                "endDateTime": "2029-07-21T21:59:59Z",
            },
            "isProlongationAutomatic": None,
            "completionDate": current_timestamp,
            "associatedAgreements": [],
            "relatedParties": [
                {
                    "id": customer_id,
                    "entityReferredType": "Customer",
                    "role": "contractOwner",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "Opportunity",
                    "relatedEntityId": opportunity_id,
                    "role": "originalOpportunity",
                    "relatedEntityBusinessId": opportunity_business_id,
                }
            ],
            "termOrConditions": [
                {
                    "name": "agreementDetails",
                    "characteristics": [
                        {"name": "paymentDueDays", "value": "15"},
                        {"name": "leadTimeDays", "value": "30"},
                        {"name": "noticePeriodDurationType", "value": "day"},
                        {"name": "noticePeriodDuration", "value": "30"}
                    ]
                }
            ],
            "audit": {
                "createdBy": CREATED_BY,
                "createdDate": current_timestamp,
            },
        }
    },
}

kafka_active_headers = {
    **AGREEMENT_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

agreement_active_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=kafka_active_headers,
    json=kafka_active_body,
)

print(f"STATUS: {agreement_active_response.status_code}")
if agreement_active_response.status_code != 200:
    print(f"Body: {agreement_active_response.text}")
print(agreement_active_response.text)
agreement_active_response.raise_for_status()
print()

# --- 6. PUBLISH ---

payload = {
    "agreementId": GENERATED_ID,
    "method": "CREATE",
}

response = requests.post(PUBLISH_HOST, headers=PUBLISH_HEADERS, json=payload)
print("PUBLISH STATUS:", response.status_code)

