#!/usr/bin/env python3
"""
Debug script to see full API response when using content_url parameter.
"""
import os
import sys
import json
import requests
import base64

sys.path.insert(0, '/Users/lauragarrett/Documents/zoho-gym-campaigns')
from zoho_campaigns_client import ZohoCampaignsClient

zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')
zoho_topic_id = os.getenv('ZOHO_TOPIC_ID')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing environment variables")
    sys.exit(1)

print("\n" + "="*70)
print("DEBUG: Full API Response for content_url Parameter")
print("="*70)

# Initialize client
client = ZohoCampaignsClient(
    zoho_refresh_token,
    default_list_key=zoho_default_list_key,
    topic_id=zoho_topic_id
)

BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"

# Test 1: Simple HTML
print("\n🧪 Test 1: Simple HTML content")
simple_html = "<p>Simple test content</p>"
simple_encoded = base64.b64encode(simple_html.encode('utf-8')).decode('utf-8')
simple_url = f"data:text/html;base64,{simple_encoded}"

print(f"  Content: {simple_html}")
print(f"  Data URI length: {len(simple_url)}")

payload = {
    "campaignname": "🧪 Debug Test 1 - Simple HTML",
    "subject": "Test",
    "from_email": "hello@shireelite.com.au",
    "resfmt": "json",
    "list_details": json.dumps({str(zoho_default_list_key): []}),
    "topicId": zoho_topic_id,
    "content_url": simple_url,
}

headers = {
    "Authorization": f"Zoho-oauthtoken {client.access_token}",
}

response = requests.post(f"{BASE_URL}/createCampaign", data=payload, headers=headers, timeout=30)
print(f"  Status: {response.status_code}")
print(f"  Response: {response.text[:300]}")

try:
    data = response.json()
    print(f"  JSON: {json.dumps(data, indent=2)}")
except:
    pass

# Test 2: Without content_url (baseline)
print("\n🧪 Test 2: Without content_url (baseline)")
payload2 = {
    "campaignname": "🧪 Debug Test 2 - No Content",
    "subject": "Test",
    "from_email": "hello@shireelite.com.au",
    "resfmt": "json",
    "list_details": json.dumps({str(zoho_default_list_key): []}),
    "topicId": zoho_topic_id,
}

response2 = requests.post(f"{BASE_URL}/createCampaign", data=payload2, headers=headers, timeout=30)
print(f"  Status: {response2.status_code}")
print(f"  Response: {response2.text[:300]}")

try:
    data2 = response2.json()
    print(f"  JSON: {json.dumps(data2, indent=2)}")
except:
    pass

# Test 3: With a public URL instead of data URI
print("\n🧪 Test 3: With public URL (example.com)")
payload3 = {
    "campaignname": "🧪 Debug Test 3 - Public URL",
    "subject": "Test",
    "from_email": "hello@shireelite.com.au",
    "resfmt": "json",
    "list_details": json.dumps({str(zoho_default_list_key): []}),
    "topicId": zoho_topic_id,
    "content_url": "https://example.com",
}

response3 = requests.post(f"{BASE_URL}/createCampaign", data=payload3, headers=headers, timeout=30)
print(f"  Status: {response3.status_code}")
print(f"  Response: {response3.text[:300]}")

try:
    data3 = response3.json()
    print(f"  JSON: {json.dumps(data3, indent=2)}")
except:
    pass

print("\n" + "="*70)
print("Analysis:")
print("="*70)
print("""
If Test 2 (without content_url) succeeds:
  → Zoho doesn't support content_url parameter or rejects data: URIs
  → We need to host HTML on a real server

If Test 3 (with public URL) succeeds:
  → Zoho accepts content_url but needs a real HTTP(S) URL
  → We need to host campaign HTML on a web server

If Tests 1-3 all fail:
  → There might be a parameter validation issue
  → Check if there's a character limit or encoding problem
""")

print()
