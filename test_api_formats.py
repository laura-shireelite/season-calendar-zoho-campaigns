#!/usr/bin/env python3
"""
Test different API parameter formats to find what works with Zoho Campaigns.

The goal is to figure out the correct format for specifying the mailing list
when creating a campaign via the API.
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

BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"
OAUTH_URL = "https://accounts.zoho.com.au/oauth/v2/token"
CLIENT_ID = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
CLIENT_SECRET = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"

print("\n" + "="*70)
print("ZOHO API FORMAT TEST - Finding the correct list parameter format")
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
        print(token_response.text)
        sys.exit(1)

    access_token = token_response.json().get('access_token')
    print(f"✅ Got access token")
except Exception as e:
    print(f"❌ Error getting token: {e}")
    sys.exit(1)

# Step 2: Test different parameter formats
headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
}

timestamp = datetime.now().strftime("%H%M%S")
test_cases = [
    {
        'name': 'Format 1: JSON with array',
        'list_details': json.dumps({str(zoho_default_list_key): []})
    },
    {
        'name': 'Format 2: Plain string (list key only)',
        'list_details': str(zoho_default_list_key)
    },
    {
        'name': 'Format 3: JSON array of keys',
        'list_details': json.dumps([str(zoho_default_list_key)])
    },
    {
        'name': 'Format 4: Simple list parameter (no list_details)',
        'list': str(zoho_default_list_key)
    },
]

successful_formats = []

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'-'*70}")
    print(f"Test {i}: {test_case['name']}")
    print(f"{'-'*70}")

    campaign_name = f"🧪 Test Format {i} {timestamp}"

    # Build payload
    payload = {
        "campaignname": campaign_name,
        "subject": f"[TEST] Format {i}",
        "from_email": "hello@shireelite.com.au",
        "resfmt": "json",
    }

    # Add the test parameter
    for key, value in test_case.items():
        if key != 'name':
            payload[key] = value
            print(f"Parameter: {key}={value}")

    # Make API call
    try:
        response = requests.post(
            f"{BASE_URL}/createCampaign",
            data=payload,
            headers=headers,
            timeout=30
        )

        print(f"Status: {response.status_code}")

        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            if data.get('code') in [200, 201] or 'campaignId' in str(data):
                print(f"✅ SUCCESS - Format {i} works!")
                successful_formats.append({
                    'test': i,
                    'name': test_case['name'],
                    'format': payload
                })
            else:
                error_code = data.get('code', 'Unknown')
                error_msg = data.get('error', 'Unknown error')
                print(f"❌ Error {error_code}: {error_msg}")
        except:
            print(f"Response text: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Exception: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if successful_formats:
    print(f"\n✅ Found {len(successful_formats)} working format(s):\n")
    for result in successful_formats:
        print(f"Test {result['test']}: {result['name']}")
        print(f"  Payload keys: {list(result['format'].keys())}")
else:
    print("\n❌ No working formats found yet.")
    print("\nNext steps:")
    print("1. Check Zoho API documentation for correct parameter names")
    print("2. Try different endpoint versions (v2 instead of v1.1?)")
    print("3. Verify the list key is correct: " + zoho_default_list_key)

print("\n")
