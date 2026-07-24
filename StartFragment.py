import requests
import uuid
from datetime import datetime, timezone

from config import (
    PUBLISH_HOST,
    PUBLISH_HEADERS,
    AGREEMENT_HOST,
    QUOTE_HOST,
    TENANT_ID,
    MONOGRAM,
    CREATED_BY,
    AGREEMENT_BASE_HEADERS,
    CALCULATE_MIN_BASE_HEADERS,
)

# MANUAL INPUT
quoteId = "1000001132"

# GENERATED VALUES
now = datetime.now(timezone.utc)
current_timestamp = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
current_date = now.strftime("%Y-%m-%d %H:%M:%S")
compact_date = now.strftime("%Y%m%d%H%M%S")

current_unix_ms = int(now.timestamp() * 1000)

GENERATED_ID = f"{MONOGRAM}{compact_date}"
SFA_CONTRACT_ID = f"TESZT-{compact_date}"
AGREEMENT_NAME = f"Teszt Kft - {current_date}"


# COMMON HELPERS
def new_guid():
    return str(uuid.uuid4())


# Agreement fejlécek
AGREEMENT_HEADERS = {
    **AGREEMENT_BASE_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

# Calculate Min fejlécek
calculate_min_headers = {
    **CALCULATE_MIN_BASE_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

calculate_min_body = {"quoteId": quoteId}

print("1. CALCULATE MIN")


calculate_min_response = requests.post(
    f"{QUOTE_HOST}/quoteManagement/internal/v1/calculateMin",
    headers=calculate_min_headers,
    json=calculate_min_body,
)

print(f"STATUS: {calculate_min_response.status_code}")
print(GENERATED_ID)
print()

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

related_parties = calculate_min_json[0].get("relatedParties", [])

if not related_parties:
    raise Exception("No related parties found in calculateMin response")

CUSTOMER_ID = related_parties[0]["id"]

print(f"CUSTOMER_ID: {CUSTOMER_ID}")
print()


# 2. AGREEMENT CREATE


agreement_create_body = {
    "id": GENERATED_ID,
    "name": AGREEMENT_NAME,
    "businessId": GENERATED_ID,
    "status": "draft",
    "completionDate": current_timestamp,
    "type": "commercial",
    "subType": "frameAgreement",
    "characteristics": [
        {"name": "migrMethod", "value": "MOVE"},
        {"name": "legacyID", "value": "536979013"},
        {"name": "isPublicProcurementContract", "value": "false"},
        {"name": "isDkuContract", "value": "false"},
        {"name": "isEcoContract", "value": "false"},
        {"name": "authentSetupMaster", "value": "495012014"},
        {"name": "cidMaster", "value": "495012014"},
        {"name": "isProductConstraintDisabled", "value": "false"},
        {"name": "isConfidential", "value": "false"},
        {"name": "dealerID", "value": "hamis.00001"},
    ],
    "relatedParties": [
        {
            "entityReferredType": "Customer",
            "id": CUSTOMER_ID,
            "role": "contractOwner",
        },
        {
            "entityReferredType": "ContactParty",
            "id": "65e72f378f77b322dc860da2",
            "role": "businessContact",
        },
    ],
    "relatedEntities": [
        {"entityType": "SFContract", "relatedEntityId": SFA_CONTRACT_ID},
        {
            "entityType": "Opportunity",
            "relatedEntityId": OPPORTUNITY_ID,
            "role": "originalOpportunity",
        },
        {
            "entityType": "IccmWorkflow",
            "relatedEntityId": "2345654",
            "role": "CONTRACT",
        },
        {
            "entityType": "IccmWorkflow",
            "relatedEntityId": "3454324",
            "role": "ADJUSTMENT",
        },
    ],
    "budgets": [
        {
            "id": "a7167203-8953-47f2-95d6-abd75f4fc969",
            "priority": "10",
            "type": "poolSubsidy",
            "settlement": {"type": "financial", "units": "HUF"},
            "budgetValues": [{"type": "initial", "value": 5000000}],
            "budgetPeriod": {
                "startDateTime": "2019-07-03T22:00:00Z",
                "endDateTime": "2023-07-03T21:59:59Z",
            },
            "characteristics": [{"name": "approver"}],
            "termOrConditions": [
                {
                    "name": "coveragePercentageMax",
                    "description": "A kedvezmény mértékének maximális felhasználása százalékban.",
                    "type": "limit",
                    "characteristics": [
                        {"name": "coveragePercentageMax", "value": "70"},
                        {"name": "coverageBase", "value": "invoiceTotal"},
                    ],
                },
                {
                    "name": "budgetPenalty",
                    "description": "A keret felhasználás kötbér képzéssel jár.",
                    "type": "penalty",
                    "characteristics": [{"name": "budgetPenalty", "value": "Y"}],
                },
                {
                    "name": "priceDiscountEligibilityCodes",
                    "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                    "type": "restriction",
                    "characteristics": [
                        {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_12"},
                        {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_24"},
                    ],
                },
                {
                    "name": "usageModeDiscountCodes",
                    "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                    "type": "restriction",
                    "characteristics": [
                        {
                            "name": "JAZZ_DISCOUNTCODE",
                            "value": "SUBPOOL KESZ KEDV",
                        }
                    ],
                },
            ],
            "relatedParties": [
                {
                    "entityReferredType": "Customer",
                    "id": CUSTOMER_ID,
                    "role": "contrOrgActive",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "agreement",
                    "relatedEntityId": OPPORTUNITY_ID,
                }
            ],
        },
        {
            "id": "327583d5-cc9c-4b79-ab5f-a0600b51150d",
            "priority": "10",
            "type": "poolSubsidy",
            "settlement": {"type": "financial", "units": "HUF"},
            "budgetValues": [{"type": "initial", "value": 12000000}],
            "budgetPeriod": {
                "startDateTime": "2020-07-03T22:00:00Z",
                "endDateTime": "2028-07-03T21:59:59Z",
            },
            "characteristics": [{"name": "approver"}],
            "termOrConditions": [
                {
                    "name": "coveragePercentageMax",
                    "description": "A kedvezmény mértékének maximális felhasználása százalékban.",
                    "type": "limit",
                    "characteristics": [
                        {"name": "coveragePercentageMax", "value": "70"},
                        {"name": "coverageBase", "value": "invoiceTotal"},
                    ],
                },
                {
                    "name": "budgetPenalty",
                    "description": "A keret felhasználás kötbér képzéssel jár.",
                    "type": "penalty",
                    "characteristics": [{"name": "budgetPenalty", "value": "Y"}],
                },
                {
                    "name": "priceDiscountEligibilityCodes",
                    "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                    "type": "restriction",
                    "characteristics": [
                        {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_12"},
                        {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_24"},
                    ],
                },
                {
                    "name": "usageModeDiscountCodes",
                    "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                    "type": "restriction",
                    "characteristics": [
                        {
                            "name": "JAZZ_DISCOUNTCODE",
                            "value": "SUBPOOL KESZ KEDV",
                        }
                    ],
                },
            ],
            "relatedParties": [
                {
                    "entityReferredType": "Customer",
                    "id": CUSTOMER_ID,
                    "role": "contrOrgActive",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "agreement",
                    "relatedEntityId": OPPORTUNITY_ID,
                }
            ],
        },
    ],
    "termOrConditions": [
        {
            "name": "Inflációkövető díjkorrekció",
            "type": "inflationAdjustmentRule",
            "characteristics": [
                {"name": "customCorrectionRule", "value": "true"},
                {"name": "adjustmentPeriodicity", "value": "yearly"},
                {"name": "validFromYear", "value": "2026"},
                {"name": "validToYear", "value": "2028"},
                {"name": "adjustmentDate", "value": "08-01"},
                {"name": "appliesToChargeType", "value": "recurring"},
                {"name": "applyInflationPercentage", "value": "5"},
                {"name": "maxIncreasePercentage", "value": "5"},
            ],
        },
        {
            "validFor": {"startDateTime": "2019-07-04T21:59:59Z"},
            "duration": {"timePeriod": 30, "type": "day"},
            "type": "activation",
        },
        {"name": "expirationFixExt", "type": "expirationType"},
        {
            "validFor": {"endDateTime": "2028-07-03T21:59:59Z"},
            "duration": {"timePeriod": 60, "type": "month"},
            "type": "autoprolongation",
        },
        {"type": "termination"},
        {
            "type": "paymentDueDate",
            "characteristics": [
                {"name": "unit", "value": "day"},
                {"name": "amount", "value": "30"},
            ],
        },
        {
            "validFor": {
                "startDateTime": "2019-07-03T22:00:00Z",
                "endDateTime": "2021-07-03T21:59:59Z",
            },
            "duration": {"timePeriod": 24},
            "type": "confidentialityClause",
            "characteristics": [{"name": "penaltyAmount", "value": "1200000"}],
        },
        {
            "type": "usageCommitment",
            "characteristics": [
                {"name": "voiceFee", "value": "50000"},
                {"name": "voiceType", "value": "individual"},
                {"name": "otherFee", "value": "200000"},
                {"name": "otherType", "value": "extraServiceMonthlyFee"},
                {"name": "dataFee", "value": "100000"},
                {"name": "currency", "value": "HUF"},
                {"name": "applicableTo", "value": "all"},
            ],
        },
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
        "masterId": SFA_CONTRACT_ID,
        "associationId": {},
        "tenantId": TENANT_ID,
        "trackingId": new_guid(),
        "messageId": new_guid(),
        "producerId": {"name": "SalesForce"},
        "eventType": "AgreementCreated",
        "operation": "CREATE",
        "masterTimestamp": current_unix_ms,
    },
    "body": {
        "Agreement": {
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "draft",
            "type": "commercial",
            "subType": "frameAgreement",
            "characteristics": [
                {"name": "migrMethod", "value": "MOVE"},
                {"name": "legacyID", "value": "536979013"},
                {"name": "isPublicProcurementContract", "value": "false"},
                {"name": "isDkuContract", "value": "false"},
                {"name": "isEcoContract", "value": "false"},
                {"name": "authentSetupMaster", "value": "495012014"},
                {"name": "cidMaster", "value": "495012014"},
                {"name": "isProductConstraintDisabled", "value": "false"},
                {"name": "isConfidential", "value": "false"},
                {"name": "dealerID", "value": "hamis.00001"},
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
                    "role": "contractOwner",
                }
            ],
            "relatedEntities": [
                {
                    "entityType": "Opportunity",
                    "relatedEntityId": OPPORTUNITY_ID,
                    "role": "originalOpportunity",
                },
                {
                    "entityType": "SFContract",
                    "relatedEntityId": SFA_CONTRACT_ID,
                    "role": "originalSFContract",
                },
                {
                    "entityType": "IccmWorkflow",
                    "relatedEntityId": "2345654",
                    "role": "CONTRACT",
                },
                {
                    "entityType": "IccmWorkflow",
                    "relatedEntityId": "3454324",
                    "role": "ADJUSTMENT",
                },
            ],
            "budgets": [
                {
                    "id": "a7167203-8953-47f2-95d6-abd75f4fc969",
                    "priority": "10",
                    "type": "poolSubsidy",
                    "settlement": {"type": "financial", "units": "HUF"},
                    "budgetValues": [{"type": "initial", "value": 5000000}],
                    "budgetPeriod": {
                        "startDateTime": "2019-07-03T22:00:00Z",
                        "endDateTime": "2023-07-03T21:59:59Z",
                    },
                    "characteristics": [{"name": "approver"}],
                    "termOrConditions": [
                        {
                            "name": "coveragePercentageMax",
                            "description": "A kedvezmény mértékének maximális felhasználása százalékban.",
                            "type": "limit",
                            "characteristics": [
                                {"name": "coveragePercentageMax", "value": "70"},
                                {"name": "coverageBase", "value": "invoiceTotal"},
                            ],
                        },
                        {
                            "name": "budgetPenalty",
                            "description": "A keret felhasználás kötbér képzéssel jár.",
                            "type": "penalty",
                            "characteristics": [
                                {"name": "budgetPenalty", "value": "Y"}
                            ],
                        },
                        {
                            "name": "priceDiscountEligibilityCodes",
                            "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                            "type": "restriction",
                            "characteristics": [
                                {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_12"},
                                {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_24"},
                            ],
                        },
                        {
                            "name": "usageModeDiscountCodes",
                            "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                            "type": "restriction",
                            "characteristics": [
                                {
                                    "name": "JAZZ_DISCOUNTCODE",
                                    "value": "SUBPOOL KESZ KEDV",
                                }
                            ],
                        },
                    ],
                    "relatedParties": [
                        {
                            "entityReferredType": "Customer",
                            "id": CUSTOMER_ID,
                            "role": "contrOrgActive",
                        }
                    ],
                    "relatedEntities": [
                        {
                            "entityType": "agreement",
                            "relatedEntityId": OPPORTUNITY_ID,
                        }
                    ],
                },
                {
                    "id": "327583d5-cc9c-4b79-ab5f-a0600b51150d",
                    "priority": "10",
                    "type": "poolSubsidy",
                    "settlement": {"type": "financial", "units": "HUF"},
                    "budgetValues": [{"type": "initial", "value": 12000000}],
                    "budgetPeriod": {
                        "startDateTime": "2020-07-03T22:00:00Z",
                        "endDateTime": "2028-07-03T21:59:59Z",
                    },
                    "characteristics": [{"name": "approver"}],
                    "termOrConditions": [
                        {
                            "name": "coveragePercentageMax",
                            "description": "A kedvezmény mértékének maximális felhasználása százalékban.",
                            "type": "limit",
                            "characteristics": [
                                {"name": "coveragePercentageMax", "value": "70"},
                                {"name": "coverageBase", "value": "invoiceTotal"},
                            ],
                        },
                        {
                            "name": "budgetPenalty",
                            "description": "A keret felhasználás kötbér képzéssel jár.",
                            "type": "penalty",
                            "characteristics": [
                                {"name": "budgetPenalty", "value": "Y"}
                            ],
                        },
                        {
                            "name": "priceDiscountEligibilityCodes",
                            "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                            "type": "restriction",
                            "characteristics": [
                                {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_12"},
                                {"name": "JAZZ_DISCOUNTCODE", "value": "KKV_24"},
                            ],
                        },
                        {
                            "name": "usageModeDiscountCodes",
                            "description": "Azon kedvezménykódok, amely kódokkal a keret felhasználható.",
                            "type": "restriction",
                            "characteristics": [
                                {
                                    "name": "JAZZ_DISCOUNTCODE",
                                    "value": "SUBPOOL KESZ KEDV",
                                }
                            ],
                        },
                    ],
                    "relatedParties": [
                        {
                            "entityReferredType": "Customer",
                            "id": CUSTOMER_ID,
                            "role": "contrOrgActive",
                        }
                    ],
                    "relatedEntities": [
                        {
                            "entityType": "agreement",
                            "relatedEntityId": OPPORTUNITY_ID,
                        }
                    ],
                },
            ],
            "termOrConditions": [
                {
                    "name": "Inflációkövető díjkorrekció",
                    "type": "inflationAdjustmentRule",
                    "characteristics": [
                        {"name": "customCorrectionRule", "value": "true"},
                        {"name": "adjustmentPeriodicity", "value": "yearly"},
                        {"name": "validFromYear", "value": "2026"},
                        {"name": "validToYear", "value": "2028"},
                        {"name": "adjustmentDate", "value": "08-01"},
                        {"name": "appliesToChargeType", "value": "recurring"},
                        {"name": "applyInflationPercentage", "value": "5"},
                        {"name": "maxIncreasePercentage", "value": "5"},
                    ],
                },
                {
                    "validFor": {"startDateTime": "2019-07-04T21:59:59Z"},
                    "duration": {"timePeriod": 30, "type": "day"},
                    "type": "activation",
                },
                {"name": "expirationFixExt", "type": "expirationType"},
                {
                    "validFor": {"endDateTime": "2028-07-03T21:59:59Z"},
                    "duration": {"timePeriod": 60, "type": "month"},
                    "type": "autoprolongation",
                },
                {"type": "termination"},
                {
                    "type": "paymentDueDate",
                    "characteristics": [
                        {"name": "unit", "value": "day"},
                        {"name": "amount", "value": "30"},
                    ],
                },
                {
                    "validFor": {
                        "startDateTime": "2019-07-03T22:00:00Z",
                        "endDateTime": "2021-07-03T21:59:59Z",
                    },
                    "duration": {"timePeriod": 24},
                    "type": "confidentialityClause",
                    "characteristics": [{"name": "penaltyAmount", "value": "1200000"}],
                },
                {
                    "type": "usageCommitment",
                    "characteristics": [
                        {"name": "voiceFee", "value": "50000"},
                        {"name": "voiceType", "value": "individual"},
                        {"name": "otherFee", "value": "200000"},
                        {"name": "otherType", "value": "extraServiceMonthlyFee"},
                        {"name": "dataFee", "value": "100000"},
                        {"name": "currency", "value": "HUF"},
                        {"name": "applicableTo", "value": "all"},
                    ],
                },
            ],
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
print(kafka_draft_response.text)
print()


# 4. KAFKA SAVE IN PROCESS


kafka_inprocess_body = {
    "header": {
        "masterId": SFA_CONTRACT_ID,
        "associationId": {},
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
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "inProcess",
            "type": "commercial",
            "subType": "frameAgreement",
            "characteristics": [
                {
                    "name": "isFrameAgreement",
                    "value": "true",
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
                    "role": "contractOwner",
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


print("4. KAFKA SAVE IN PROCESS")


kafka_inprocess_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_inprocess_body,
)

print(f"STATUS: {kafka_inprocess_response.status_code}")
print(kafka_inprocess_response.text)
print()


# 5. KAFKA SAVE SIGNED


kafka_signed_body = {
    "header": {
        "masterId": SFA_CONTRACT_ID,
        "associationId": {},
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
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "signed",
            "type": "commercial",
            "subType": "frameAgreement",
            "characteristics": [
                {"name": "isFrameAgreement", "value": "true"},
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
                    "role": "contractOwner",
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


print("5. KAFKA SAVE SIGNED")


kafka_signed_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_signed_body,
)

print(f"STATUS: {kafka_signed_response.status_code}")
print(kafka_signed_response.text)
print()


# 6. KAFKA SAVE ACTIVE


kafka_active_body = {
    "header": {
        "masterId": SFA_CONTRACT_ID,
        "associationId": {},
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
            "id": SFA_CONTRACT_ID,
            "name": AGREEMENT_NAME,
            "status": "active",
            "type": "commercial",
            "subType": "frameAgreement",
            "characteristics": [
                {"name": "isFrameAgreement", "value": "true"},
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
                    "role": "contractOwner",
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


print("6. KAFKA SAVE ACTIVE")


kafka_active_response = requests.post(
    f"{AGREEMENT_HOST}/kafka/agreement/v2/save",
    headers=AGREEMENT_HEADERS,
    json=kafka_active_body,
)

print(f"STATUS: {kafka_active_response.status_code}")
print(kafka_active_response.text)
print()

payload = {
    "agreementId": GENERATED_ID,
    "kafkaMethod": "CREATE",
}

response = requests.patch(PUBLISH_HOST, headers=PUBLISH_HEADERS, json=payload)

print("PUBLISH STATUS:", response.status_code)

print("FLOW FINISHED")
