#!/usr/bin/env python3
"""
Test creating a campaign with ZERO list/recipient parameters.

This tests whether /createCampaign endpoint requires recipients at all,
or if it's a two-step process (create empty, then add recipients).
"""
import os
import sys
import json
import requests
from datetime import datetime

zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')

if not zoho_refresh_token:
    print("❌ Missing ZOHO_REFRESH_TOKEN")
    sys.exit(1)

OAUTH_URL = "https://accounts.zoho.com.au/oauth/v2/token"
BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"
CLIENT_ID = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
CLIENT_SECRET = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"

print("\n" + "="*70)
print("MINIMAL CAMPAIGN TEST - No list/recipient parameters")
print("="*70)

# Get access token
print("\n🔄 Getting access token...")
try:
    token_response = requests.post(OAUTH_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": zoho_refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if token_response.status_code != 200:
        print(f"❌ Failed to get token: {token_response.status_code}")
        sys.exit(1)

    access_token = token_response.json().get('access_token')
    print(f"✅ Got access token")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
}

timestamp = datetime.now().strftime("%H%M%S")

# Test: Create campaign with ONLY required fields (no list)
print(f"\n{'-'*70}")
print("Creating campaign with MINIMAL parameters...")
print(f"{'-'*70}")

campaign_name = f"🧪 Minimal Test {timestamp}"

# Only mandatory fields - NO list/recipient parameters
payload = {
    "campaignname": campaign_name,
    "subject": "[TEST] Minimal campaign - no list parameter",
    "from_email": "hello@shireelite.com.au",
    "resfmt": "json",
}

print(f"\nPayload:")
for key, value in payload.items():
    print(f"  {key}: {value}")

try:
    url = f"{BASE_URL}/createCampaign"
    print(f"\nURL: {url}")

    response = requests.post(url, data=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}\n")

    try:
        data = response.json()
        print("Response:")
        print(json.dumps(data, indent=2))

        # Check if successful
        if data.get('code') in [200, 201]:
            print(f"\n✅ SUCCESS! Campaign created without list parameter!")
            print(f"   Campaign ID: {data.get('data', {}).get('campaignId', 'N/A')}")
            print(f"\n   This means we need a SECOND API call to add recipients.")
            print(f"   Look for endpoints like:")
            print(f"   - /addRecipients")
            print(f"   - /updateRecipients")
            print(f"   - /addCampaignRecipient")
        elif 'campaignId' in str(data):
            print(f"\n✅ SUCCESS! Found campaign ID in response")
            print(f"   This confirms the two-step process.")
        else:
            error_code = data.get('code', 'Unknown')
            error_msg = data.get('error', 'No error message')
            print(f"\n❌ Error {error_code}: {error_msg}")

            if error_code == 6606:
                print(f"\n   Still getting 6606 = endpoint requires a list")
            else:
                print(f"\n   Different error! This means we found the right endpoint")
                print(f"   but need to adjust something else.")

    except Exception as e:
        print(f"Could not parse JSON: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("Next step: Check results above to determine if two-step process is needed")
print("="*70 + "\n")
