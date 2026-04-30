#!/usr/bin/env python3
"""
Test script to verify which field name Zoho Campaigns API accepts for email body.

Since the campaigns are being created but empty, the issue is likely one of:
1. Field name is wrong (should be "body", "htmlbody", "html", "content", etc.)
2. The body needs to be set via a separate API call after campaign creation
3. The body needs special formatting

This script tests different possible field names.
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
print("TEST: Zoho Campaigns Body Field Name")
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
        print(f"❌ Failed to get token: {token_response.text}")
        sys.exit(1)

    access_token = token_response.json().get('access_token')
    print(f"✅ Got access token")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
}

# Get mailing lists
print("\n📋 Fetching mailing lists...")
try:
    url = f"{BASE_URL}/getmailinglists"
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200 or data.get('code') == '200':
            lists = data.get('data', {})
            if lists:
                # Use the first available list
                list_key = list(lists.keys())[0]
                print(f"✅ Using list: {list_key}")
            else:
                print("❌ No mailing lists found")
                sys.exit(1)
        else:
            print(f"❌ API Error: {data}")
            sys.exit(1)
    else:
        print(f"❌ Failed to get lists: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test different body field names
body_content = "<html><body><h2>Test Campaign</h2><p>This is test content to verify the body field name.</p></body></html>"

field_names_to_test = [
    "body",
    "htmlbody",
    "html",
    "content",
    "emailbody",
    "message"
]

print(f"\n{'='*70}")
print("Testing different body field names:")
print(f"{'='*70}\n")

for field_name in field_names_to_test:
    print(f"Testing: {field_name}")

    payload = {
        "campaignname": f"🧪 Body Field Test - {field_name}",
        "subject": f"Test - {field_name}",
        "from_email": "hello@shireelite.com.au",
        "resfmt": "json",
        "list_details": json.dumps({str(list_key): []}),
        field_name: body_content,  # Test this field name
    }

    try:
        url = f"{BASE_URL}/createCampaign"
        response = requests.post(url, data=payload, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                code = str(response_data.get('code', ''))
                has_campaign_key = 'campaignKey' in response_data or 'campaign_id' in response_data

                if code in ['200', '201'] or has_campaign_key:
                    print(f"  ✅ Campaign created - might work with '{field_name}'")
                else:
                    print(f"  ❌ API returned code: {code}")
            except:
                print(f"  ✅ Campaign might have been created")
        else:
            print(f"  ❌ Status: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Error: {str(e)[:60]}")

    print()

print("="*70)
print("Next steps:")
print("1. Check your Zoho Campaigns account for the test campaigns")
print("2. Identify which field name resulted in campaigns WITH content")
print("3. Update zoho_campaigns_client.py to use the correct field name")
print("="*70 + "\n")
