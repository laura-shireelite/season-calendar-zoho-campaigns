#!/usr/bin/env python3
"""
Call getmailinglists API to get the ACTUAL list keys from Zoho.

The createCampaign API documentation says:
"You can get list key and segment ID from getmailinglists API"

So let's do that - find out what the real list key is.
"""
import os
import sys
import json
import requests

zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')

if not zoho_refresh_token:
    print("❌ Missing ZOHO_REFRESH_TOKEN")
    sys.exit(1)

OAUTH_URL = "https://accounts.zoho.com.au/oauth/v2/token"
BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"
CLIENT_ID = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
CLIENT_SECRET = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"

print("\n" + "="*70)
print("GET MAILING LISTS - Discover actual list keys from Zoho")
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

# Call getmailinglists
print(f"\n📋 Calling getmailinglists API...")
print(f"{'-'*70}")

try:
    url = f"{BASE_URL}/getmailinglists"
    print(f"URL: {url}\n")

    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}\n")

    try:
        data = response.json()
        print("Response:")
        print(json.dumps(data, indent=2))

        if response.status_code == 200:
            if data.get('code') == 200:
                lists = data.get('data', {})

                if lists:
                    print(f"\n✅ SUCCESS! Found {len(lists)} mailing list(s):\n")

                    for list_key, list_info in lists.items():
                        print(f"   List Key: {list_key}")
                        print(f"   Name: {list_info.get('listname', 'N/A')}")
                        print(f"   Total Contacts: {list_info.get('totalcontacts', 'N/A')}")
                        print(f"   Active Contacts: {list_info.get('activecontacts', 'N/A')}")
                        print(f"   Inactive Contacts: {list_info.get('inactivecontacts', 'N/A')}")
                        print()

                    print("="*70)
                    print("USE ONE OF THESE LIST KEYS FOR CAMPAIGN CREATION")
                    print("="*70)
                else:
                    print("\n⚠️  No lists found in response (empty data)")
            else:
                error_code = data.get('code', 'Unknown')
                error_msg = data.get('error', 'Unknown error')
                print(f"\n❌ API Error {error_code}: {error_msg}")
        else:
            print(f"\n❌ HTTP Error {response.status_code}")

    except Exception as e:
        print(f"Could not parse response: {e}")
        print(f"Raw response: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")

print("\n")
