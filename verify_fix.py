#!/usr/bin/env python3
"""
Verification script to check if the campaigns have proper content after fixes.

This script:
1. Creates a single test campaign with full content
2. Reports the outcome
3. Helps verify the fix is working
"""
import os
import sys

sys.path.insert(0, '/Users/lauragarrett/Documents/zoho-gym-campaigns')

from zoho_campaigns_client import ZohoCampaignsClient

print("\n" + "="*70)
print("VERIFY: Testing Campaign Creation with Content Fix")
print("="*70)

# Load env vars
zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')
zoho_topic_id = os.getenv('ZOHO_TOPIC_ID')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing required environment variables")
    sys.exit(1)

print(f"\n🔧 Configuration:")
print(f"  List Key: {zoho_default_list_key[:20]}...")
print(f"  Topic ID: {zoho_topic_id}")

# Initialize client
print(f"\n🔌 Connecting to Zoho Campaigns...")
try:
    client = ZohoCampaignsClient(
        zoho_refresh_token,
        default_list_key=zoho_default_list_key,
        topic_id=zoho_topic_id
    )
    print("✅ Connected")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

# Create a test campaign with full content
print(f"\n📝 Creating test campaign with content...")
test_campaign = {
    'name': '✅ VERIFY Fix - Test Campaign with Content',
    'subject': '✅ This subject should appear',
    'body': '''<html><body>
    <h2>Campaign Content Test</h2>
    <p>If you can read this, the body fix is working!</p>
    <p>This HTML should appear in the campaign content area.</p>
    <p>Created: ''' + os.popen('date').read().strip() + '''</p>
    </body></html>''',
    'from_name': 'Shire Elite Gyms',
    'type': 'verification',
    'target_gym': 'Shire Elite'
}

result = client.create_campaign_draft(test_campaign)

if result:
    print("\n" + "="*70)
    print("✅ SUCCESS: Test campaign created")
    print("="*70)
    print("\n📋 Next steps:")
    print("   1. Log into Zoho Campaigns")
    print("   2. Find the draft campaign: '✅ VERIFY Fix - Test Campaign with Content'")
    print("   3. Check if:")
    print("      ✓ Subject is: '✅ This subject should appear'")
    print("      ✓ Body contains the HTML content (not empty)")
    print("   4. If BOTH are present, the fix is working! ✅")
    print("   5. If body is empty, the field name needs adjustment")
    print("\n   Run this to find the correct field name:")
    print("   $ python3 test_body_field.py")
else:
    print("\n" + "="*70)
    print("❌ FAILED: Test campaign could not be created")
    print("="*70)
    print("\n⚠️  Check:")
    print("   1. Zoho connection status")
    print("   2. Mailing list configuration")
    print("   3. Authentication token")

print()
