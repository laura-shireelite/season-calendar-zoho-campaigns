#!/usr/bin/env python3
"""
Discover the correct Zoho API endpoint and field names for setting campaign content.

Tests multiple approaches to find what works.
"""
import os
import sys
import json
import requests

sys.path.insert(0, '/Users/lauragarrett/Documents/zoho-gym-campaigns')
from zoho_campaigns_client import ZohoCampaignsClient

zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')
zoho_topic_id = os.getenv('ZOHO_TOPIC_ID')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing environment variables")
    sys.exit(1)

print("\n" + "="*70)
print("DISCOVER: Campaign Content API Endpoint")
print("="*70)

# Initialize client
print("\n🔌 Connecting to Zoho Campaigns...")
client = ZohoCampaignsClient(
    zoho_refresh_token,
    default_list_key=zoho_default_list_key,
    topic_id=zoho_topic_id
)
print("✅ Connected")

# Create a test campaign first
print("\n📝 Creating test campaign...")
test_campaign = {
    'name': '🧪 Content Endpoint Discovery Test',
    'subject': 'Test Subject',
    'body': '<html><body><h2>Test Content</h2><p>Testing content endpoint discovery</p></body></html>',
    'from_name': 'Shire Elite Gyms',
    'type': 'test',
    'target_gym': 'Shire Elite'
}

campaign_id = client._create_campaign_draft(
    test_campaign['name'],
    test_campaign['subject'],
    test_campaign['target_gym']
)

if not campaign_id:
    print("❌ Failed to create campaign")
    sys.exit(1)

print(f"✅ Created campaign: {campaign_id}")
body = test_campaign['body']

# Test different endpoints and field combinations
test_cases = [
    {
        'name': 'updateCampaignContent with content field',
        'endpoint': '/updateCampaignContent',
        'method': 'POST',
        'payload': {
            'campaignid': campaign_id,
            'content': body,
            'resfmt': 'json',
        }
    },
    {
        'name': 'updateCampaignContent with htmlcontent field',
        'endpoint': '/updateCampaignContent',
        'method': 'POST',
        'payload': {
            'campaignid': campaign_id,
            'htmlcontent': body,
            'resfmt': 'json',
        }
    },
    {
        'name': 'updateCampaignContent with html field',
        'endpoint': '/updateCampaignContent',
        'method': 'POST',
        'payload': {
            'campaignid': campaign_id,
            'html': body,
            'resfmt': 'json',
        }
    },
    {
        'name': 'updateCampaign with content field',
        'endpoint': '/updateCampaign',
        'method': 'POST',
        'payload': {
            'campaignid': campaign_id,
            'content': body,
            'resfmt': 'json',
        }
    },
    {
        'name': 'editCampaign with html field',
        'endpoint': '/editCampaign',
        'method': 'POST',
        'payload': {
            'campaignid': campaign_id,
            'html': body,
            'resfmt': 'json',
        }
    },
]

print(f"\n{'='*70}")
print("Testing different endpoints and field names:")
print(f"{'='*70}\n")

BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"
headers = {
    "Authorization": f"Zoho-oauthtoken {client.access_token}",
}

for test in test_cases:
    name = test['name']
    endpoint = test['endpoint']
    method = test['method']
    payload = test['payload']

    print(f"Testing: {name}")
    print(f"  Endpoint: {endpoint}")
    print(f"  Method: {method}")

    try:
        url = f"{BASE_URL}{endpoint}"

        if method == 'POST':
            response = requests.post(url, data=payload, headers=headers, timeout=30)
        elif method == 'GET':
            response = requests.get(url, params=payload, headers=headers, timeout=30)

        print(f"  Status: {response.status_code}")

        # Try to parse response
        try:
            data = response.json()
            code = data.get('code', 'N/A')
            message = data.get('message', '')
            print(f"  Code: {code}")
            if message:
                print(f"  Message: {message}")

            # Check if it was successful
            if code in ['200', '201', 200, 201]:
                print(f"  ✅ MIGHT WORK!")
            elif 'error' in str(code).lower():
                print(f"  ❌ Error response")
            else:
                print(f"  ⚠️  Unknown response")

        except:
            print(f"  Could not parse JSON response")
            if response.text:
                print(f"  Response: {response.text[:100]}")

    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:60]}")

    print()

print("="*70)
print("Analysis:")
print("="*70)
print(f"""
The campaign ID {campaign_id} has been created and is ready for testing.

Check your Zoho account:
1. Log into Zoho Campaigns
2. Find campaign: '🧪 Content Endpoint Discovery Test'
3. Check CONTENT section - it should be empty

The above tests tried:
- Different endpoints (/updateCampaignContent, /updateCampaign, /editCampaign)
- Different field names (content, htmlcontent, html)

If any test shows "✅ MIGHT WORK!", that's the endpoint we need to use.

Once you identify which endpoint/field combination works:
1. Update zoho_campaigns_client.py _set_campaign_content() method
2. Re-run verify_fix.py
3. Confirm content now appears

If NONE of the tests work, the Zoho API might require:
- Base64 encoding the HTML
- A completely different approach (templates, imports, etc.)
- Or the content might need to be set during createCampaign, not after

Check Zoho Campaigns API documentation for: campaign content, campaign body, or campaign HTML.
""")
