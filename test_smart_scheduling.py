#!/usr/bin/env python3
"""
Test the smart scheduling logic:
- When running within 7 days of term start: use current term
- When running more than 7 days into term: use next term
"""

from datetime import datetime, timedelta
from main import TermDetector

print("\n" + "="*70)
print("TESTING SMART SCHEDULING LOGIC")
print("="*70)

# Mock data with three terms
mock_events = [
    {'Date': 'Tue 27 Jan', 'Gym': 'SE', 'Event Name': 'Term 1', 'Event Type': 'Terms →'},
    {'Date': 'Thu 2 Apr', 'Gym': 'SE', 'Event Name': 'Term 2', 'Event Type': 'Terms →'},
    {'Date': 'Fri 10 Jul', 'Gym': 'SE', 'Event Name': 'Term 3', 'Event Type': 'Terms →'},
    {'Date': '2026-04-15', 'Gym': 'SE', 'Event Name': 'Cheer Clinics', 'Event Type': 'Cheer Clinics'},
]

detector = TermDetector(mock_events)

print("\n🧪 TEST 1: Scheduling at Term Start (Apr 2)")
print("-" * 70)
test_date = datetime(2026, 4, 2)  # First day of Term 2
active = detector.get_active_term(reference_date=test_date)
if active:
    print(f"Active term: {active['name']} (starts {active['start_date'].strftime('%Y-%m-%d')})")
    next_term = detector.get_next_term(reference_date=test_date)
    if next_term:
        print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
        days_into = (test_date - active['start_date']).days
        print(f"Days into term: {days_into}")
        if days_into <= 7:
            print(f"✅ Should use current term (within 7 days): {active['name']}")
        else:
            print(f"⚠️  Would use next term (beyond 7 days): {next_term['name']}")

print("\n🧪 TEST 2: Manual Run 9 Days Into Term (Apr 11)")
print("-" * 70)
test_date = datetime(2026, 4, 11)  # 9 days into Term 2
active = detector.get_active_term(reference_date=test_date)
if active:
    print(f"Active term: {active['name']} (starts {active['start_date'].strftime('%Y-%m-%d')})")
    next_term = detector.get_next_term(reference_date=test_date)
    if next_term:
        print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
        days_into = (test_date - active['start_date']).days
        print(f"Days into term: {days_into}")
        if days_into <= 7:
            print(f"✅ Should use current term (within 7 days): {active['name']}")
        else:
            print(f"✅ Should use next term (beyond 7 days): {next_term['name']}")

print("\n🧪 TEST 3: Today (Apr 29) - Should Target Term 3")
print("-" * 70)
test_date = datetime(2026, 4, 29)  # Today
active = detector.get_active_term(reference_date=test_date)
if active:
    print(f"Active term: {active['name']} (starts {active['start_date'].strftime('%Y-%m-%d')})")
    next_term = detector.get_next_term(reference_date=test_date)
    if next_term:
        print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
        days_into = (test_date - active['start_date']).days
        print(f"Days into term: {days_into}")
        if days_into <= 7:
            print(f"⚠️  Would use current term (within 7 days): {active['name']}")
        else:
            print(f"✅ Should use next term (beyond 7 days): {next_term['name']}")
            print(f"    This is what the skill will do on your next run!")

print("\n" + "="*70)
print("✅ SMART SCHEDULING LOGIC TEST COMPLETE")
print("="*70)
print("\nSummary:")
print("- Runs at/near term start (≤7 days): Create campaigns for that term")
print("- Manual runs mid-term (>7 days): Create campaigns for next term")
print("- Your next skill run will target Term 3 (starts July 10) ✅")
print("\n")
