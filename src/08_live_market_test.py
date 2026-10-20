import json

import requests


# ==================================================
# AVNESTER PUBLIC RENTAL API
# ==================================================

API_URL = (
    "https://api.avnester.com/public/v1/search_properties"
)


# ==================================================
# TEST SEARCH
# ==================================================

def fetch_current_rentals():

    payload = {
        "city": "Bengaluru",
        "locality": "Whitefield",
        "propertyType": "apartment",
        "bedrooms": 2,
        "transactionType": "rent",
        "rentalStructure": "monthly",
        "limit": 10,
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# MAIN
# ==================================================

def main():

    print("==================================================")
    print("CURRENT RENTAL DATA TEST")
    print("==================================================")

    print("\nConnecting to AVnester...")

    try:

        data = fetch_current_rentals()

    except requests.exceptions.RequestException as error:

        print(
            "\nLIVE DATA CONNECTION FAILED"
        )

        print(
            f"\nError: {error}"
        )

        return


    print(
        "\nLIVE DATA CONNECTION SUCCESSFUL!"
    )


    print(
        "\n========== RESPONSE =========="
    )

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )[:6000]
    )


    print(
        "\n=================================================="
    )

    print(
        "CURRENT RENTAL DATA TEST COMPLETE"
    )

    print(
        "=================================================="
    )


if __name__ == "__main__":
    main()
