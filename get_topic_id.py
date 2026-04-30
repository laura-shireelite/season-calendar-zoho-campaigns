#!/usr/bin/env python3
"""
Fetch all topics from Zoho Campaigns to find the topic ID for "Important Info".

Per Zoho API docs: GET /api/v1.1/topics
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
print("GET TOPICS - Find topicId for 'Important Info'")
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

# Call /topics endpoint
print(f"\n📋 Calling /topics endpoint...")
print(f"{'-'*70}")

try:
    url = f"{BASE_URL}/topics"
    print(f"URL: {url}\n")

    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}\n")

    try:
        data = response.json()

        if data.get('code') == '200' or data.get('code') == 200:
            topic_details = data.get('topicDetails', [])

            if topic_details:
                print(f"✅ Found {len(topic_details)} topic(s):\n")

                important_info_topic = None

                for topic in topic_details:
                    topic_name = topic.get('topicName', 'N/A')
                    topic_id = topic.get('topicId', 'N/A')
                    print(f"   Topic Name: {topic_name}")
                    print(f"   Topic ID: {topic_id}")
                    print()

                    if 'important' in topic_name.lower():
                        important_info_topic = topic_id

                if important_info_topic:
                    print("="*70)
                    print(f"✅ FOUND 'Important Info' Topic!")
                    print(f"   Topic ID: {important_info_topic}")
                    print("="*70)
                    print(f"\nUpdate config.txt with:")
                    print(f'   export ZOHO_TOPIC_ID="{important_info_topic}"')
                else:
                    print("⚠️  Could not find 'Important Info' topic")
                    print("   Use one of the topic IDs above")

            else:
                print("⚠️  No topics found")

        else:
            error_code = data.get('code', 'Unknown')
            error_msg = data.get('message', 'Unknown error')
            print(f"❌ Error {error_code}: {error_msg}")

    except Exception as e:
        print(f"Could not parse response: {e}")
        print(f"Raw response: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")

print("\n")
