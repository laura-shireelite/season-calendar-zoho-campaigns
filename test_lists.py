#!/usr/bin/env python3
import os
import sys
import requests
from zoho_campaigns_client import ZohoCampaignsClient
import json

# Load config
os.environ['ZOHO_REFRESH_TOKEN'] = '1000.9060e30255ab37c3293841472c827a1f.07ccff166d35510f55e6619da05b38bd'

client = ZohoCampaignsClient(os.environ['ZOHO_REFRESH_TOKEN'])

# Try to fetch lists directly
print("\n" + "="*70)
print("FETCHING ZOHO MAILING LISTS (RAW RESPONSE)")
print("="*70 + "\n")

url = f"{client.BASE_URL}/getmailinglists"
headers = {
    "Authorization": f"Zoho-oauthtoken {client.access_token}",
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}\n")
    print("Response:")
    print(response.text)

    if response.status_code == 200:
        try:
            data = response.json()
            print("\nParsed JSON:")
            print(json.dumps(data, indent=2))
        except:
            print("(Could not parse as JSON)")
except Exception as e:
    print(f"Error: {e}")

print("\n")
