#!/usr/bin/env python3
"""
Test campaign creation WITH topicId parameter.

The API docs mention:
"topicId is mandatory for organizations or accounts that have enabled
the updated topic management version."

This test tries creating campaigns with topicId parameter.
"""
import os
import sys
import json
import requests
from datetime import datetime

zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing ZOHO_REFRESH_TOKEN or ZOHO_DEFAULT_LIST_KEY")
    sys.exit(1)

OAUTH_URL = "https://accounts.zoho.com.au/oauth/v2/token"
BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"
CLIENT_ID = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
CLIENT_SECRET = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"

print("\n" + "="*70)
print("CAMPAIGN CREATION TEST - With topicId parameter")
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
        print(f"❌ Failed to get token")
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

# Try different topicId values
test_cases = [
    {
        'name': 'Without topicId (original)',
        'topicId': None
    },
    {
        'name': 'With empty topicId',
        'topicId': ''
    },
    {
        'name': 'With default topicId (0)',
        'topicId': '0'
    },
    {
        'name': 'With default topicId (1)',
        'topicId': '1'
    },
]

successful = False

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'-'*70}")
    print(f"Test {i}: {test_case['name']}")
    print(f"{'-'*70}")

    campaign_name = f"🧪 Test {i} {timestamp}"

    payload = {
        "campaignname": campaign_name,
        "subject": f"[TEST] Test {i}",
        "from_email": "hello@shireelite.com.au",
        "resfmt": "json",
        "list_details": json.dumps({str(zoho_default_list_key): []}),
    }

    # Add topicId if specified
    if test_case['topicId'] is not None:
        payload['topicId'] = test_case['topicId']
        print(f"topicId: {test_case['topicId']}")
    else:
        print(f"topicId: (not sent)")

    try:
        url = f"{BASE_URL}/createCampaign"
        response = requests.post(url, data=payload, headers=headers, timeout=30)

        print(f"Status: {response.status_code}")

        try:
            data = response.json()

            if data.get('code') in [200, 201] or 'campaignKey' in data:
                print(f"✅ SUCCESS!")
                print(f"Response: {json.dumps(data, indent=2)}")
                successful = True
                break
            else:
                error_code = data.get('code', 'Unknown')
                error_msg = data.get('message', data.get('error', 'Unknown'))
                print(f"❌ Error {error_code}: {error_msg}")

        except:
            print(f"Response: {response.text[:300]}")

    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "="*70)
if successful:
    print("✅ Found working configuration!")
    print("   Update the main code with the successful parameters.")
else:
    print("❌ None of the topicId variations worked.")
    print("   Check Zoho's API documentation for other mandatory fields.")
print("="*70 + "\n")
