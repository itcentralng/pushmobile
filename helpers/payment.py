import requests
import json
import os


def generate_ussd_code(name, amount, code="737"):

    url = "https://api.paystack.co/charge"
    headers = {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": f"{name.lower()}@pushmobile.ng",
        "amount": f"{amount*100}",
        "ussd": {
            "type": code
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.json())
    return response.json()
