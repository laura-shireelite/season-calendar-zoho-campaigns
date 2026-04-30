#!/usr/bin/env python3
"""
Setup Validation Script

Run this before executing the full skill to validate your configuration.
Checks that all credentials are set up correctly and can connect to services.
"""

import os
import sys
from datetime import datetime


def check_environment_variables():
    """Check that all required environment variables are set."""
    print("\n" + "="*70)
    print("1. CHECKING ENVIRONMENT VARIABLES")
    print("="*70)

    required = {
        'GOOGLE_SHEET_URL': 'Google Sheets URL',
        'GOOGLE_SERVICE_ACCOUNT_JSON': 'Google Service Account JSON path',
        'ZOHO_REFRESH_TOKEN': 'Zoho Refresh Token'
    }

    missing = []
    for var, name in required.items():
        value = os.getenv(var)
        if value:
            # Show first/last few chars for security, or filename for paths
            if var == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                display = value.split('/')[-1]  # Show just filename
            elif len(value) > 20:
                display = value[:10] + "..." + value[-10:]
            else:
                display = "*" * len(value)
            print(f"  ✅ {name}: {display}")
        else:
            print(f"  ❌ {name}: NOT SET")
            missing.append(var)

    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("\nSet them using:")
        print("  export GOOGLE_SHEET_URL='...'")
        print("  export GOOGLE_SERVICE_ACCOUNT_JSON='/path/to/file.json'")
        print("  export ZOHO_REFRESH_TOKEN='...'")
        print("\nOr edit config.txt and run: source config.txt")
        return False

    return True


def test_google_sheets():
    """Test Google Sheets API connection."""
    print("\n" + "="*70)
    print("2. TESTING GOOGLE SHEETS CONNECTION")
    print("="*70)

    try:
        from google_sheets_reader import GoogleSheetsReader

        sheet_url = os.getenv('GOOGLE_SHEET_URL')
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

        print(f"  Reading sheet: {sheet_url}")
        reader = GoogleSheetsReader(sheet_url, service_account_json)

        # Try to fetch events
        events = reader.fetch_events()
        print(f"  ✅ Successfully read {len(events)} events from sheet")

        # Validate format
        if reader.validate_sheet_format(events):
            print("  ✅ Sheet format is valid")
        else:
            print("  ⚠️  Sheet format validation failed")
            return False

        # Show sample events
        if events:
            print("\n  Sample events:")
            for event in events[:3]:
                print(f"    - {event.get('Date')}: {event.get('Event Name')}")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Failed to read sheet: {e}")
        return False


def test_zoho_connection():
    """Test Zoho Campaigns API connection."""
    print("\n" + "="*70)
    print("3. TESTING ZOHO CAMPAIGNS CONNECTION")
    print("="*70)

    try:
        from zoho_campaigns_client import ZohoCampaignsClient

        refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')

        print("  Connecting to Zoho Campaigns...")
        client = ZohoCampaignsClient(refresh_token)

        if client.test_connection():
            print("  ✅ Successfully connected to Zoho Campaigns")

            # Try to get audience lists
            lists = client.get_audience_lists()
            if lists:
                print(f"  ✅ Found {len(lists)} audience lists:")
                for name, list_id in list(lists.items())[:3]:
                    print(f"      - {name}: {list_id}")
            else:
                print("  ⚠️  No audience lists found (this is okay)")

            return True
        else:
            print("  ❌ Failed to connect to Zoho Campaigns")
            return False

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return False


def test_term_detection():
    """Test automatic term detection."""
    print("\n" + "="*70)
    print("4. TESTING AUTOMATIC TERM DETECTION")
    print("="*70)

    try:
        from google_sheets_reader import GoogleSheetsReader
        from main import TermDetector

        sheet_url = os.getenv('GOOGLE_SHEET_URL')
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

        print("  Reading events from sheet...")
        reader = GoogleSheetsReader(sheet_url, service_account_json)
        events = reader.fetch_events()

        print("  Testing term auto-detection...")
        detector = TermDetector(events)
        active_term = detector.get_active_term()

        if active_term:
            print(f"  ✅ Active term detected: {active_term['name']}")
            print(f"      Start date: {active_term['start_date'].strftime('%Y-%m-%d')}")

            # Get events for this term
            term_events = detector.get_term_events(active_term)
            print(f"      Events in term: {len(term_events)}")

            if term_events:
                print("      Sample events:")
                for event in term_events[:3]:
                    print(f"        - {event.get('Event Name')}")

            return True
        else:
            print("  ❌ Could not auto-detect active term")
            print("      Make sure your sheet has at least one 'Terms' type event")
            return False

    except Exception as e:
        print(f"  ❌ Term detection failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ZOHO GYM CAMPAIGNS - SETUP VALIDATION")
    print("="*70)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run tests in order
    tests = [
        ("Environment Variables", check_environment_variables),
        ("Google Sheets API", test_google_sheets),
        ("Zoho Campaigns API", test_zoho_connection),
        ("Term Auto-Detection", test_term_detection),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All checks passed! You're ready to run the skill.")
        print("\nNext step: python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix the issues above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
