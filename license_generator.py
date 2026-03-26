import os
import requests

LICENSE_SERVER_URL = "https://web-production-0746.up.railway.app"
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "").strip()


def create_license(status="PRO", max_activations=2):
    if not ADMIN_SECRET:
        raise RuntimeError("ADMIN_SECRET saknas i miljövariablerna")

    response = requests.post(
        f"{LICENSE_SERVER_URL}/create-license",
        headers={"X-Admin-Secret": ADMIN_SECRET},
        json={
            "status": status,
            "max_activations": max_activations
        },
        timeout=10
    )

    data = response.json()

    if response.status_code != 200 or not data.get("success"):
        raise RuntimeError(f"Kunde inte skapa licens: {data}")

    return data


if __name__ == "__main__":
    result = create_license(status="PRO", max_activations=2)
    print("Ny licens skapad:")
    print("Nyckel:", result["license_key"])
    print("Status:", result["status"])
    print("Max aktiveringar:", result["max_activations"])