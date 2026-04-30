#!/usr/bin/env python3
"""
Test campaign creation with content_url parameter (data URI approach).

This uses the content_url parameter discovered in the API docs to embed
HTML content directly during campaign creation.
"""
import os
import sys

sys.path.insert(0, '/Users/lauragarrett/Documents/zoho-gym-campaigns')

from zoho_campaigns_client import ZohoCampaignsClient

zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')
zoho_topic_id = os.getenv('ZOHO_TOPIC_ID')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing environment variables")
    sys.exit(1)

print("\n" + "="*70)
print("TEST: Campaign Creation with content_url (Data URI)")
print("="*70)

# Initialize client
print("\n🔌 Connecting to Zoho Campaigns...")
client = ZohoCampaignsClient(
    zoho_refresh_token,
    default_list_key=zoho_default_list_key,
    topic_id=zoho_topic_id
)
print("✅ Connected")

# Create test campaign WITH HTML content
print("\n📝 Creating test campaign with HTML content (data URI)...")
test_campaign = {
    'name': '✅ Content URL Test - Should Have Content',
    'subject': 'Test Subject with HTML Content',
    'body': '''<html><body style="font-family: Arial, sans-serif;">
    <h2>📧 Test Campaign Content</h2>
    <p>If you see this, the content_url parameter works!</p>
    <p><strong>This HTML was embedded as a data URI in the campaign creation.</strong></p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        Test timestamp: ''' + os.popen('date').read().strip() + '''
    </p>
    </body></html>''',
    'from_name': 'Shire Elite Gyms',
    'type': 'test',
    'target_gym': 'Shire Elite'
}

result = client.create_campaign_draft(test_campaign)

if result:
    print("\n" + "="*70)
    print("✅ SUCCESS: Campaign created with content_url parameter")
    print("="*70)
    print("\n📋 Next steps:")
    print("   1. Log into Zoho Campaigns")
    print("   2. Find: '✅ Content URL Test - Should Have Content'")
    print("   3. Check if CONTENT section now shows the HTML")
    print("   4. If yes, the content_url parameter works! 🎉")
    print("   5. If no, Zoho might not support data: URIs")
    print("\n   If it works:")
    print("   $ python3 main.py")
else:
    print("\n" + "="*70)
    print("❌ FAILED: Campaign could not be created")
    print("="*70)

print()
