import requests
import uuid
from datetime import datetime, timezone


# CONFIG

BASE_URL_QUOTE = "https://dev2-mt-quote-management.paas.telekom.hu"

AGREEMENT_HOST = "https://dev2-mt-agreement.paas.telekom.hu"
QUOTE_HOST = "https://dev2-mt-quote-management.paas.telekom.hu"

AGREEMENT_API_KEY = "TECH661389:d9eac975-7130-4496-ae4f-481e2be3dadb"
QUOTE_API_KEY = "TECH674279:922f3348-362f-492b-ad46-a21de08b91b7"

MONOGRAM = "KT"
CUSTOMER_ID = "495294470"
CREATED_BY = "toth1laszlo726"

COMMON_HEADERS = {
    "accept": "application/json",
    "x-request-session-id": "a",
    "x-request-tracking-id": "a",
    "x-request-id": "a",
    "x-channel-id": "IFE",
    "brand": "MT",
    "x-m2m-user-id": "ad",
    "Content-Type": "application/json",
    "x-api-key": "k8s:dev2-b2b-cm:9e25586b-9779-41f9-9aae-a26ac6621959",
    "X-Client-Version": "clientVersion123",
    "X-Client-Id": "clientId123",
}


# MANUAL INPUT


quoteId = "1000000885"


# GENERATED VALUES


now = datetime.now(timezone.utc)

current_timestamp = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
current_date = now.strftime("%Y-%m-%d %H:%M:%S")
compact_date = now.strftime("%Y%m%d%H%M%S")

GENERATED_ID = f"{MONOGRAM}{compact_date}"
SFA_CONTRACT_ID = f"TESZT-{compact_date}"
AGREEMENT_NAME = f"Teszt Kft - {current_date}"


print("GENERATED VALUES")

print(f"GENERATED_ID: {GENERATED_ID}")
print(f"SFA_CONTRACT_ID: {SFA_CONTRACT_ID}")
print(f"AGREEMENT_NAME: {AGREEMENT_NAME}")
print(f"TIMESTAMP: {current_timestamp}")
print()


# COMMON HELPERS


def new_guid():
    return str(uuid.uuid4())


AGREEMENT_HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": AGREEMENT_API_KEY,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}


# 1. CALCULATE MIN


calculate_min_headers = {
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
    "X-Api-Key": QUOTE_API_KEY,
    "x-channel-id": "12",
    "x-context-id": "123",
    "x-correlation-id": "1234",
    "x-m2m-user-id": "12345",
    "x-source-system": "123456",
    "x-source-system-user": "1234567",
    "x-parent-request-id": "12345678",
    "tenantId": "MT",
    "Content-Type": "application/json",
}

calculate_min_body = {"quoteId": quoteId}


print("1. CALCULATE MIN")


calculate_min_response = requests.post(
    f"{QUOTE_HOST}/quoteManagement/internal/v1/calculateMin",
    headers=calculate_min_headers,
    json=calculate_min_body,
)

print(f"STATUS: {calculate_min_response.status_code}")

calculate_min_response.raise_for_status()

calculate_min_json = calculate_min_response.json()

opportunity_entity = next(
    (
        entity
        for entity in calculate_min_json[0]["relatedEntities"]
        if entity["entityType"] == "Opportunity"
    ),
    None,
)

if not opportunity_entity:
    raise Exception("Opportunity entity not found in response")

OPPORTUNITY_ID = opportunity_entity["relatedEntityId"]
OPPORTUNITY_BUSINESS_ID = opportunity_entity["relatedEntityBusinessId"]

print(f"OPPORTUNITY_ID: {OPPORTUNITY_ID}")
print(f"OPPORTUNITY_BUSINESS_ID: {OPPORTUNITY_BUSINESS_ID}")
print()


# 2. AGREEMENT CREATE


agreement_create_body = {
    "id": GENERATED_ID,
    "name": AGREEMENT_NAME,
    "businessId": GENERATED_ID,
    "status": "draft",
    "completionDate": current_timestamp,
    "type": "commercial",
    "subType": "salesAgreement",
    "characteristics": [{"name": "isFrameAgreement", "value": "false"}],
    "relatedParties": [
        {
            "entityReferredType": "Customer",
            "id": CUSTOMER_ID,
            "role": "contrOrgInactive",
        }
    ],
    "relatedEntities": [
        {"entityType": "SFAContract", "relatedEntityId": SFA_CONTRACT_ID},
        {
            "entityType": "Opportunity",
            "relatedEntityId": OPPORTUNITY_ID,
            "role": "originalOpportunity",
        },
    ],
    "termOrConditions": [
        {"name": "expirationIndefinitive", "type": "expirationType"},
        {"type": "leadTime", "characteristics": [{"name": "day", "value": "15"}]},
        {"type": "paymentDueDate", "characteristics": [{"name": "day", "value": "8"}]},
        {"type": "paymentPeriod", "characteristics": [{"name": "month", "value": "1"}]},
        {"type": "noticePeriod", "characteristics": [{"name": "day", "value": "30"}]},
    ],
    "audit": {
        "createdBy": CREATED_BY,
        "createdDate": current_timestamp,
        "changedBy": "SalesForcePublication",
        "changedDate": current_timestamp,
    },
}


print("2. AGREEMENT CREATE")


agreement_create_response = requests.post(
    f"{AGREEMENT_HOST}/agreements/internal/v1/agreements",
    headers=AGREEMENT_HEADERS,
    json=agreement_create_body,
)

print(f"STATUS: {agreement_create_response.status_code}")
print()


# 3. KAFKA SAVE DRAFT


kafka_draft_body = {
    "header": {
        "masterId": GENERATED_ID,
        "associationId": {},
        "tenantId": "MT",
        "trackingId": new_guid(),
        "messageId": new_guid(),
        "producerId": {},
        "eventType": "AgreementCreated",
        "operation": "CREATE",
        "masterTimestamp": 0,
    },
    "body": {
        "Agreement": {
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "draft",
            "type": "commercial",
            "subType": "salesAgreement",
            "characteristics": [
                {"name": "isFrameAgreement", "value": "false"},
                {"name": "deliveryCertificateRequiredPerPeriod", "value": ""},
                {"name": "externalOrderID", "value": ""},
                {"name": "paymentPeriod", "value": "1Month"},
                {"name": "processType", "value": "Webshop"},
            ],
            "agreementAuthorizations": [],
            "duration": None,
            "agreementPeriod": {
                "startDateTime": current_timestamp,
                "endDateTime": None,
            },
            "isProlongationAutomatic": None,
            "completionDate": current_timestamp,
            "associatedAgreements": [],
            "relatedParties": [
                {
                    "id": CUSTOMER_ID,
                    "entityReferredType": "Customer",
                    "role": "contrOrgActive",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "Opportunity",
                    "relatedEntityId": OPPORTUNITY_ID,
                    "role": "originalOpportunity",
                }
            ],
            "termOrConditions": [
                {"type": "expirationType", "name": "expirationIndefinitive"}
            ],
            "audit": {"createdBy": CREATED_BY, "createdDate": current_timestamp},
        }
    },
}


print("3. KAFKA SAVE DRAFT")


kafka_draft_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_draft_body,
)

print(f"STATUS: {kafka_draft_response.status_code}")
print()


# 4. AGREEMENT PATCH


agreement_patch_body = {
    "id": GENERATED_ID,
    "name": AGREEMENT_NAME,
    "businessId": GENERATED_ID,
    "status": "draft",
    "completionDate": current_timestamp,
    "type": "commercial",
    "subType": "salesAgreement",
    "characteristics": [{"name": "isFrameContract", "value": "false"}],
    "relatedParties": [
        {
            "entityReferredType": "Customer",
            "id": CUSTOMER_ID,
            "role": "contrOrgInactive",
        }
    ],
    "relatedEntities": [
        {"entityType": "SFAContract", "relatedEntityId": SFA_CONTRACT_ID},
        {
            "entityType": "Opportunity",
            "relatedEntityId": OPPORTUNITY_ID,
            "relatedEntityBusinessId": OPPORTUNITY_BUSINESS_ID,
            "role": "originalOpportunity",
        },
    ],
    "audit": {
        "createdBy": CREATED_BY,
        "createdDate": current_timestamp,
        "changedBy": "SalesForcePublication",
        "changedDate": current_timestamp,
    },
}


print("4. AGREEMENT PATCH")


agreement_patch_response = requests.patch(
    f"{AGREEMENT_HOST}/agreements/internal/v2/agreements/{GENERATED_ID}?fields=*",
    headers=AGREEMENT_HEADERS,
    json=agreement_patch_body,
)

print(f"STATUS: {agreement_patch_response.status_code}")
print()


# 5. KAFKA SAVE IN PROCESS


kafka_inprocess_body = {
    "header": {
        "masterId": SFA_CONTRACT_ID,
        "associationId": {},
        "tenantId": "MT",
        "trackingId": new_guid(),
        "messageId": new_guid(),
        "producerId": {},
        "eventType": "AgreementUpdated",
        "operation": "UPDATE",
        "masterTimestamp": 0,
    },
    "body": {
        "Agreement": {
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "inProcess",
            "type": "commercial",
            "subType": "salesAgreement",
            "characteristics": [
                {
                    "name": "isFrameAgreement",
                    "value": "false",
                },
                {
                    "name": "deliveryCertificateRequiredPerPeriod",
                    "value": "",
                },
                {
                    "name": "externalOrderID",
                    "value": "",
                },
                {
                    "name": "paymentPeriod",
                    "value": "1Month",
                },
                {
                    "name": "processType",
                    "value": "Webshop",
                },
            ],
            "agreementAuthorizations": [],
            "duration": None,
            "agreementPeriod": {
                "startDateTime": current_timestamp,
                "endDateTime": None,
            },
            "isProlongationAutomatic": None,
            "completionDate": current_timestamp,
            "associatedAgreements": [],
            "relatedParties": [
                {
                    "id": CUSTOMER_ID,
                    "entityReferredType": "Customer",
                    "role": "contrOrgInactive",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "Opportunity",
                    "relatedEntityId": OPPORTUNITY_ID,
                    "role": "originalOpportunity",
                    "relatedEntityBusinessId": OPPORTUNITY_BUSINESS_ID,
                }
            ],
            "termOrConditions": [
                {
                    "type": "expirationType",
                    "name": "expirationIndefinitive",
                },
                {
                    "type": "leadTime",
                    "duration": {
                        "timePeriod": 15,
                        "type": "day",
                    },
                },
                {
                    "type": "paymentDueDate",
                    "duration": {
                        "timePeriod": 8,
                        "type": "day",
                    },
                },
                {
                    "type": "paymentPeriod",
                    "duration": {
                        "timePeriod": 1,
                        "type": "month",
                    },
                },
                {
                    "type": "noticePeriod",
                    "duration": {
                        "timePeriod": 30,
                        "type": "day",
                    },
                },
            ],
            "audit": {
                "createdBy": CREATED_BY,
                "createdDate": current_timestamp,
            },
        }
    },
}


print("5. KAFKA SAVE IN PROCESS")


kafka_inprocess_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_inprocess_body,
)

print(f"STATUS: {kafka_inprocess_response.status_code}")
print()


# 6. KAFKA SAVE SIGNED


kafka_signed_body = {
    "header": {
        "masterId": SFA_CONTRACT_ID,
        "associationId": {},
        "tenantId": "MT",
        "trackingId": new_guid(),
        "messageId": new_guid(),
        "producerId": {},
        "eventType": "AgreementUpdated",
        "operation": "UPDATE",
        "masterTimestamp": 0,
    },
    "body": {
        "Agreement": {
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "signed",
            "type": "commercial",
            "subType": "salesAgreement",
            "characteristics": [
                {"name": "isFrameAgreement", "value": "false"},
                {"name": "deliveryCertificateRequiredPerPeriod", "value": ""},
                {"name": "externalOrderID", "value": ""},
                {"name": "paymentPeriod", "value": "1Month"},
                {"name": "processType", "value": "Webshop"},
            ],
            "agreementAuthorizations": [
                {
                    "authorizedBy": {
                        "entityReferredType": "Customer",
                        "id": CUSTOMER_ID,
                    },
                    "date": current_timestamp,
                    "type": "authorization",
                    "signatureRepresentation": "paper",
                    "state": "signed",
                }
            ],
            "duration": None,
            "agreementPeriod": {
                "startDateTime": current_timestamp,
                "endDateTime": None,
            },
            "isProlongationAutomatic": None,
            "completionDate": current_timestamp,
            "associatedAgreements": [],
            "relatedParties": [
                {
                    "id": CUSTOMER_ID,
                    "entityReferredType": "Customer",
                    "role": "contrOrgInactive",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "Opportunity",
                    "relatedEntityId": OPPORTUNITY_ID,
                    "role": "originalOpportunity",
                    "relatedEntityBusinessId": OPPORTUNITY_BUSINESS_ID,
                },
                {
                    "entityType": "Document",
                    "relatedEntityId": "647da14a40b6c830af516314",
                    "name": "Keretszerződés IAAS",
                    "role": "frameContract",
                    "characteristics": [
                        {
                            "name": "documentType",
                            "value": "contract",
                        }
                    ],
                },
            ],
            "termOrConditions": [
                {
                    "type": "expirationType",
                    "name": "expirationIndefinitive",
                }
            ],
            "audit": {
                "createdBy": CREATED_BY,
                "createdDate": current_timestamp,
            },
        }
    },
}


print("6. KAFKA SAVE SIGNED")


kafka_signed_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_signed_body,
)

print(f"STATUS: {kafka_signed_response.status_code}")
print()


# 7. KAFKA SAVE ACTIVE


kafka_active_body = {
    "header": {
        "masterId": GENERATED_ID,
        "associationId": {},
        "tenantId": "MT",
        "trackingId": new_guid(),
        "messageId": new_guid(),
        "producerId": {},
        "eventType": "AgreementUpdated",
        "operation": "UPDATE",
        "masterTimestamp": 0,
    },
    "body": {
        "Agreement": {
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "active",
            "type": "commercial",
            "subType": "salesAgreement",
            "characteristics": [
                {"name": "isFrameAgreement", "value": "false"},
                {"name": "deliveryCertificateRequiredPerPeriod", "value": ""},
                {"name": "externalOrderID", "value": ""},
                {"name": "paymentPeriod", "value": "1Month"},
                {"name": "processType", "value": "Webshop"},
            ],
            "agreementAuthorizations": [
                {
                    "authorizedBy": {
                        "entityReferredType": "Customer",
                        "id": CUSTOMER_ID,
                    },
                    "date": current_timestamp,
                    "type": "authorization",
                    "signatureRepresentation": "paper",
                    "state": "signed",
                }
            ],
            "duration": None,
            "agreementPeriod": {
                "startDateTime": current_timestamp,
                "endDateTime": None,
            },
            "isProlongationAutomatic": None,
            "completionDate": current_timestamp,
            "associatedAgreements": [],
            "relatedParties": [
                {
                    "id": CUSTOMER_ID,
                    "entityReferredType": "Customer",
                    "role": "contrOrgInactive",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "Opportunity",
                    "relatedEntityId": OPPORTUNITY_ID,
                    "role": "originalOpportunity",
                    "relatedEntityBusinessId": OPPORTUNITY_BUSINESS_ID,
                },
                {
                    "entityType": "Document",
                    "relatedEntityId": "647da14a40b6c830af516314",
                    "name": "Keretszerződés IAAS",
                    "role": "frameContract",
                    "characteristics": [
                        {
                            "name": "documentType",
                            "value": "contract",
                        }
                    ],
                },
            ],
            "termOrConditions": [
                {
                    "type": "expirationType",
                    "name": "expirationIndefinitive",
                }
            ],
            "audit": {
                "createdBy": CREATED_BY,
                "createdDate": current_timestamp,
            },
        }
    },
}


print("7. KAFKA SAVE ACTIVE")


kafka_active_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_active_body,
)

print(f"STATUS: {kafka_active_response.status_code}")
print()


print("FLOW FINISHED")
