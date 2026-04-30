#!/usr/bin/env python3
"""
Test campaign creation with the updated segment routing.
"""
import os
import sys
from zoho_campaigns_client import ZohoCampaignsClient

# Load config from environment
zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_se_list_key = os.getenv('ZOHO_SE_LIST_KEY')
zoho_sca_list_key = os.getenv('ZOHO_SCA_LIST_KEY')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing required config:")
    print("   ZOHO_REFRESH_TOKEN, ZOHO_DEFAULT_LIST_KEY")
    sys.exit(1)

print("\n" + "="*70)
print("TEST: Campaign Creation with Segment Routing")
print("="*70)

# Initialize client
try:
    client = ZohoCampaignsClient(
        zoho_refresh_token,
        se_list_key=zoho_se_list_key,
        sca_list_key=zoho_sca_list_key,
        default_list_key=zoho_default_list_key
    )
    print("\n✅ Connected to Zoho Campaigns")
except Exception as e:
    print(f"\n❌ Failed to connect: {e}")
    sys.exit(1)

# Test 1: SE campaign (should target SE segment)
print("\n" + "-"*70)
print("Test 1: SE Event Campaign")
print("-"*70)
se_campaign = {
    'name': '🧪 TEST: Shire Elite Event',
    'subject': '[TEST] Shire Elite Upcoming Event',
    'body': '<p>This is a test campaign for Shire Elite.</p>',
    'from_email': 'hello@shireelite.com.au',
    'type': 'regular',
    'target_gym': 'Shire Elite'
}
result = client.create_campaign_draft(se_campaign)
print(f"Result: {'✅ Success' if result else '❌ Failed'}")

# Test 2: SCA campaign (should target SCA segment)
print("\n" + "-"*70)
print("Test 2: SCA Event Campaign")
print("-"*70)
sca_campaign = {
    'name': '🧪 TEST: SCA Allstars Event',
    'subject': '[TEST] SCA Allstars Upcoming Event',
    'body': '<p>This is a test campaign for SCA Allstars.</p>',
    'from_email': 'hello@scaallstars.com.au',
    'type': 'regular',
    'target_gym': 'SCA Allstars'
}
result = client.create_campaign_draft(sca_campaign)
print(f"Result: {'✅ Success' if result else '❌ Failed'}")

# Test 3: Default campaign (no specific gym)
print("\n" + "-"*70)
print("Test 3: Default Campaign (no segment)")
print("-"*70)
default_campaign = {
    'name': '🧪 TEST: Default Event',
    'subject': '[TEST] Default Upcoming Event',
    'body': '<p>This is a test campaign with no segment filter.</p>',
    'from_email': 'hello@shireelite.com.au',
    'type': 'regular',
    'target_gym': 'All'
}
result = client.create_campaign_draft(default_campaign)
print(f"Result: {'✅ Success' if result else '❌ Failed'}")

print("\n" + "="*70)
print("Test Complete")
print("="*70 + "\n")
