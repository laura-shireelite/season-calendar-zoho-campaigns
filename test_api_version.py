#!/usr/bin/env python3
"""
Test different Zoho API versions to see which one accepts campaign creation.

The error response shows /api/v2 but we're using /api/v1.1.
Let's test multiple API versions to find which one works.
"""
import os
import sys
import json
import requests
from datetime import datetime

# Load environment variables
zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing ZOHO_REFRESH_TOKEN or ZOHO_DEFAULT_LIST_KEY")
    sys.exit(1)

OAUTH_URL = "https://accounts.zoho.com.au/oauth/v2/token"
CLIENT_ID = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
CLIENT_SECRET = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"

print("\n" + "="*70)
print("ZOHO API VERSION TEST")
print("="*70)

# Step 1: Get access token
print("\n🔄 Refreshing access token...")
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

# Step 2: Test different API versions
api_versions = [
    "v1.1",
    "v2",
    "v2.1",
    "v3",
]

timestamp = datetime.now().strftime("%H%M%S")

for version in api_versions:
    print(f"\n{'-'*70}")
    print(f"Testing API version: {version}")
    print(f"{'-'*70}")

    base_url = f"https://campaigns.zoho.com.au/api/{version}"
    url = f"{base_url}/createCampaign"

    campaign_name = f"🧪 API v{version} Test {timestamp}"

    payload = {
        "campaignname": campaign_name,
        "subject": f"[TEST] API {version}",
        "from_email": "hello@shireelite.com.au",
        "resfmt": "json",
        "list_details": json.dumps({str(zoho_default_list_key): []}),
    }

    try:
        print(f"URL: {url}")
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")

        try:
            data = response.json()

            # Check for success
            if data.get('code') in [200, 201] or 'campaignId' in str(data):
                print(f"✅ SUCCESS with API {version}!")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                error_code = data.get('code', 'Unknown')
                error_msg = data.get('error', 'Unknown error')
                print(f"❌ Error {error_code}: {error_msg}")
                if 'uri' in data:
                    print(f"   API redirected to: {data['uri']}")

        except:
            print(f"Response: {response.text[:300]}")

    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("Test complete - check results above")
print("="*70 + "\n")
