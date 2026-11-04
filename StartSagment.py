from datetime import datetime, timezone, timedelta
import uuid
import requests
from config import (
    AGREEMENT_BASE_HEADERS,
    AGREEMENT_HOST,
    CREATED_BY,
    MONOGRAM,
    PUBLISH_HEADERS,
    PUBLISH_HOST,
    TENANT_ID,
)

# MANUAL INPUT
agreementId = "AA-26-1103-1000001567"

# GENERATED VALUES
now = datetime.now(timezone.utc)
current_timestamp = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
current_date = now.strftime("%Y-%m-%d %H:%M:%S")
compact_date = now.strftime("%Y%m%d%H%M%S")

current_unix_ms = int(now.timestamp() * 1000)

AGREEMENT_NAME = f"Egyedi szolgáltatási szerződés"


def new_guid():
    return str(uuid.uuid4())


AGREEMENT_HEADERS = {
    **AGREEMENT_BASE_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

# --- 0. GET EXISTING AGREEMENT & STRICT VALIDATION ---

print(f"0. GET EXISTING AGREEMENT (ID: {agreementId})")

get_headers = {
    **AGREEMENT_HEADERS,
    "X-Request-Id": new_guid(),
    "X-Request-Tracking-Id": new_guid(),
    "X-Request-Session-Id": new_guid(),
}

get_response = requests.get(
    f"{AGREEMENT_HOST}/agreements/internal/v2/agreements/{agreementId}",
    headers=get_headers,
)

print(f"GET Agreement STATUS: {get_response.status_code}")
get_response.raise_for_status()

current_response_json = get_response.json()

if isinstance(current_response_json, list):
    current_response_json = current_response_json[0]

current_status = current_response_json.get("status")
print(f"Current Agreement Status: {current_status}")
print()

agreement_id_to_use = current_response_json.get("id")
if not agreement_id_to_use:
    raise ValueError(f"HIBA: A lekérdezett Agreement válaszból hiányzik az 'id' mező!")

# --- VALIDÁCIÓ ---

customer_party = next(
    (party for party in current_response_json.get("relatedParties", []) if party.get("role") in ("contractOwner", "owner")),
    None
)
if not customer_party or not customer_party.get("id"):
    raise ValueError(f"HIBA: A DPS által létrehozott Agreement ({agreementId}) érvénytelen vagy hiányos! Nem található 'contractOwner' vagy 'owner' szerepkörű ügyfél ID a relatedParties-ban.")
customer_id = customer_party.get("id")

opportunity_entity = next(
    (entity for entity in current_response_json.get("relatedEntities", []) if entity.get("entityType") == "Opportunity"),
    None
)
if not opportunity_entity:
    raise ValueError(f"HIBA: A DPS által létrehozott Agreement ({agreementId})-ből hiányzik az 'Opportunity' típusú relatedEntity!")

opportunity_id = opportunity_entity.get("relatedEntityId")
opportunity_business_id = opportunity_entity.get("relatedEntityBusinessId")

if not opportunity_id or not opportunity_business_id:
    raise ValueError(f"HIBA: Az Opportunity azonosítók (relatedEntityId vagy relatedEntityBusinessId) hiányoznak az Agreement-ből!")


# --- 1. & 2. & 3. FOLYAMAT INDÍTÁSA A STÁTUSZTÓL FÜGGŐEN ---

if current_status == "inProcess":
    print("3. AGREEMENT UPDATE (INPROCESS -> SIGNED)")
    
    # Ha inProcess a státusz, bekerül az agreementAuthorizations rész is a kérésbe
    current_response_json["agreementAuthorizations"] = [
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
    ]
    
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
    agreement_signed_response.raise_for_status()
    current_response_json = agreement_signed_response.json()
    print()
elif current_status == "signed":
    print("Az agreement már 'signed' státuszban van, a frissítés kihagyva.\n")
else:
    raise ValueError(f"HIBA: Ismeretlen vagy nem támogatott agreement státusz: '{current_status}'. Csak 'inProcess' vagy 'signed' várt.")


# --- 4. KAFKA SAVE ACTIVE ---

print("5. KAFKA SAVE ACTIVE")

kafka_active_body = {
    "header": {
        "masterId": agreement_id_to_use,
        "associationId": agreement_id_to_use,
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
            "id": agreement_id_to_use,
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
print(agreement_active_response.text)
agreement_active_response.raise_for_status()
print()

# --- 5. PUBLISH ---

payload = {
    "agreementId": agreement_id_to_use,
    "method": "CREATE",
}

response = requests.post(PUBLISH_HOST, headers=PUBLISH_HEADERS, json=payload)
print("PUBLISH STATUS:", response.status_code)