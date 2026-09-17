import uuid
import requests
from config import AGREEMENT_HOST, AGREEMENT_BASE_HEADERS


def terminate_agreements_by_mtid(mt_id: str):
    correlation_id = f"corr-{uuid.uuid4()}"

    headers = {
        **AGREEMENT_BASE_HEADERS,
        "x-channel-id": "B2B",
        "brand": "MT",
        "x-m2m-user-id": "m2mUserId123",
        "x-context-id": f"context-{uuid.uuid4()}",
        "x-correlation-id": correlation_id,
        "x-request-id": correlation_id,
        "x-request-session-id": correlation_id,
        "x-request-tracking-id": correlation_id,
    }

    base_url = f"{AGREEMENT_HOST}/agreements/internal/v2/agreements"

    query_params = (
        "query=and("
        "or(eq(type,frameContract),and(eq(type,commercial),eq(subType,frameAgreement))),"
        f"contains(relatedParties,and(eq(id,{mt_id}),eq(entityReferredType,Customer))),"
        "in(status,active,rejected,inProtectionPeriod)"
        ")&page=0&size=100&fields=id,status"
    )

    search_url = f"{base_url}?{query_params}"

    print(f"=== 1. Megállapodások lekérése az alábbi MTID-hoz: {mt_id} ===")
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        agreements = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Hiba a keresési hívás során: {e}")
        return

    # Kiszűrjük azokat, ahol status == "active"
    active_agreements = [
        item for item in agreements if item.get("status") == "active"
    ]

    if not active_agreements:
        print("Nem található 'active' státuszú megállapodás ehhez az MTID-hoz.")
        return

    print(
        f"\n=== 2. Megtalált active FA-k lezárása ({len(active_agreements)} db) ==="
    )

    for item in active_agreements:
        agreement_id = item["id"]
        print(f"\n------------------------------------------------")
        print(f"Feldolgozás alatt: {agreement_id}")

        item_url = f"{base_url}/{agreement_id}"

        # 2.1 GET hívás
        try:
            print("  -> GET adatok lekérése...")
            get_res = requests.get(item_url, headers=headers)
            get_res.raise_for_status()
            agreement_data = get_res.json()
        except requests.exceptions.RequestException as e:
            print(f"  -> Hiba a GET során ({agreement_id}): {e}")
            continue

        # 2.2 'status' mező átírása 'terminated'-re
        agreement_data["status"] = "terminated"

        # 2.3 PATCH hívás a módosított adatokkal
        try:
            print("  -> PATCH küldése (status -> terminated)...")
            patch_url = f"{item_url}?fields=status"
            patch_res = requests.patch(
                patch_url, headers=headers, json=agreement_data
            )
            patch_res.raise_for_status()
            print(f"  -> Sikeresen lezárva: {agreement_id}")
        except requests.exceptions.RequestException as e:
            print(f"  -> Hiba a PATCH során ({agreement_id}): {e}")

    print("\n=== Kész! Minden 'active' FA lezárásra került. ===")


if __name__ == "__main__":
    # Add meg az MTID-t amit fel szeretnél dolgozni
    TARGET_MTID = "814063238"
    terminate_agreements_by_mtid(TARGET_MTID)