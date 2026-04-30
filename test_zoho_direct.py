#!/usr/bin/env python3
"""Test Zoho API directly without Google Sheets dependency."""

import sys
sys.path.insert(0, '/sessions/bold-kind-carson/mnt/zoho-gym-campaigns')

from zoho_campaigns_client import ZohoCampaignsClient

# Load config
import os
refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')

if not refresh_token:
    print("❌ ZOHO_REFRESH_TOKEN not set")
    sys.exit(1)

print("\n" + "="*70)
print("TESTING ZOHO CAMPAIGNS API - Direct Campaign Creation")
print("="*70)

# Initialize client
try:
    client = ZohoCampaignsClient(refresh_token)
    print(f"✅ Zoho client initialized")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

# Test campaign (minimal content to avoid 1001 error)
test_campaign = {
    'name': 'Test Campaign - With fromemail',
    'subject': '📅 Test Subject',
    'body': '<html><body><h2>Test Campaign</h2><p>This is a test.</p></body></html>',
    'from_name': 'Shire Elite Gyms',
}

print(f"\n📤 Attempting to create test campaign...")
print(f"   Campaign: {test_campaign['name']}")
print(f"   Subject: {test_campaign['subject']}")

success = client.create_campaign_draft(test_campaign)

if success:
    print("\n✅ SUCCESS - Campaign created!")
    print("   The fromemail field fix appears to be working.")
else:
    print("\n❌ FAILED - Campaign was not created.")
    print("   Check error messages above for details.")
