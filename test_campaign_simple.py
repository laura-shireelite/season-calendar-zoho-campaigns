#!/usr/bin/env python3
"""
Simple test to verify campaign creation with the fixed list routing.

This test creates a few test campaigns to verify the API is working correctly.
"""
import os
import sys
from datetime import datetime, timedelta
from zoho_campaigns_client import ZohoCampaignsClient

# Load environment variables
zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
zoho_se_list_key = os.getenv('ZOHO_SE_LIST_KEY')
zoho_sca_list_key = os.getenv('ZOHO_SCA_LIST_KEY')
zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')
zoho_topic_id = os.getenv('ZOHO_TOPIC_ID')

if not all([zoho_refresh_token, zoho_default_list_key]):
    print("❌ Missing required environment variables:")
    print("   ZOHO_REFRESH_TOKEN")
    print("   ZOHO_DEFAULT_LIST_KEY")
    sys.exit(1)

print("\n" + "="*70)
print("ZOHO CAMPAIGNS TEST - Simple Campaign Creation")
print("="*70)
print(f"\n✓ Config loaded:")
print(f"  Default List Key: {zoho_default_list_key}")
if zoho_topic_id:
    print(f"  Topic ID: {zoho_topic_id}")
if zoho_se_list_key:
    print(f"  SE Segment ID: {zoho_se_list_key}")
if zoho_sca_list_key:
    print(f"  SCA Segment ID: {zoho_sca_list_key}")

# Initialize client
print("\n🔌 Connecting to Zoho Campaigns...")
try:
    client = ZohoCampaignsClient(
        zoho_refresh_token,
        se_list_key=zoho_se_list_key,
        sca_list_key=zoho_sca_list_key,
        default_list_key=zoho_default_list_key,
        topic_id=zoho_topic_id
    )
    print("✅ Connected to Zoho Campaigns")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

# Test 1: Simple campaign for Shire Elite
print("\n" + "-"*70)
print("Test 1: Shire Elite Campaign")
print("-"*70)

se_campaign = {
    'name': f'🧪 TEST SE Campaign {datetime.now().strftime("%H%M%S")}',
    'subject': '[TEST] Shire Elite - Test Campaign',
    'body': '<html><body><p>This is a test campaign for Shire Elite gym.</p></body></html>',
    'type': 'test',
    'target_gym': 'Shire Elite'
}

result = client.create_campaign_draft(se_campaign)
if result:
    print("✅ Test 1 PASSED - SE campaign created successfully")
else:
    print("❌ Test 1 FAILED - Could not create SE campaign")

# Test 2: Simple campaign for SCA Allstars
print("\n" + "-"*70)
print("Test 2: SCA Allstars Campaign")
print("-"*70)

sca_campaign = {
    'name': f'🧪 TEST SCA Campaign {datetime.now().strftime("%H%M%S")}',
    'subject': '[TEST] SCA Allstars - Test Campaign',
    'body': '<html><body><p>This is a test campaign for SCA Allstars gym.</p></body></html>',
    'type': 'test',
    'target_gym': 'SCA Allstars'
}

result = client.create_campaign_draft(sca_campaign)
if result:
    print("✅ Test 2 PASSED - SCA campaign created successfully")
else:
    print("❌ Test 2 FAILED - Could not create SCA campaign")

# Test 3: Campaign with generic gym
print("\n" + "-"*70)
print("Test 3: Generic Campaign (All)")
print("-"*70)

all_campaign = {
    'name': f'🧪 TEST All Campaign {datetime.now().strftime("%H%M%S")}',
    'subject': '[TEST] All - Test Campaign',
    'body': '<html><body><p>This is a test campaign for all gyms.</p></body></html>',
    'type': 'test',
    'target_gym': 'All'
}

result = client.create_campaign_draft(all_campaign)
if result:
    print("✅ Test 3 PASSED - All campaign created successfully")
else:
    print("❌ Test 3 FAILED - Could not create All campaign")

print("\n" + "="*70)
print("Test Summary")
print("="*70)
print("\nIf all 3 tests passed, the API is working correctly!")
print("Check your Zoho Campaigns account for the test campaigns.")
print("\n✅ Next step: Run main.py to test full skill workflow\n")
