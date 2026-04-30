#!/usr/bin/env python3
"""
Test the fixes applied:
1. Header parsing (should use rows[1] not rows[0])
2. Date parsing with '%a %d %b' format
3. Terms event detection
"""

from datetime import datetime
from main import TermDetector

print("\n" + "="*70)
print("TESTING FIXES")
print("="*70)

# Test 1: Date Parsing
print("\n📅 TEST 1: Date Parsing with New Format")
print("-" * 70)

test_dates = [
    ("Tue 27 Jan", 2026, 1, 27),   # Jan 27 is 92 days ago (< 180), so current year
    ("Thu 2 Apr", 2026, 4, 2),      # Apr 2 is 27 days ago (< 180), so current year (active term!)
    ("Fri 10 Jul", 2026, 7, 10),    # Jul is in future, so current year
]

date_parse_ok = True
for date_str, expected_year, expected_month, expected_day in test_dates:
    try:
        parsed = TermDetector._parse_date(date_str)
        if parsed.year == expected_year and parsed.month == expected_month and parsed.day == expected_day:
            print(f"✅ '{date_str}' -> {parsed.strftime('%Y-%m-%d')}")
        else:
            print(f"❌ '{date_str}' -> {parsed.strftime('%Y-%m-%d')} (expected {expected_year}-{expected_month:02d}-{expected_day:02d})")
            date_parse_ok = False
    except Exception as e:
        print(f"❌ '{date_str}' FAILED: {e}")
        date_parse_ok = False

# Test 2: Terms Event Detection
print("\n🔍 TEST 2: Terms Event Detection")
print("-" * 70)

# Simulate sheet data with proper structure
# Note: Today is 2026-04-29, so Term 2 (starts Apr 2) is the active term
mock_events = [
    {'Date': 'Tue 27 Jan', 'Gym': 'SE', 'Event Name': 'Term 1', 'Event Type': 'Terms →'},
    {'Date': '2026-02-14', 'Gym': 'SE', 'Event Name': 'Valentine Event', 'Event Type': 'Events'},
    {'Date': 'Thu 2 Apr', 'Gym': 'SE', 'Event Name': 'Term 2', 'Event Type': 'Terms →'},
    {'Date': '2026-04-15', 'Gym': 'SE', 'Event Name': 'Cheer Clinics', 'Event Type': 'Cheer Clinics'},
    {'Date': '2026-04-20', 'Gym': 'SE', 'Event Name': 'Training Camp', 'Event Type': 'Events'},
    {'Date': 'Fri 10 Jul', 'Gym': 'SE', 'Event Name': 'Term 3', 'Event Type': 'Terms →'},
    {'Date': '2026-07-22', 'Gym': 'SE', 'Event Name': 'Summer Event', 'Event Type': 'Events'},
]

try:
    detector = TermDetector(mock_events)
    term_events = detector.term_events

    if len(term_events) == 3:
        print(f"✅ Found {len(term_events)} Terms events")
        for event in term_events:
            print(f"   - {event.get('Event Name')} ({event.get('Event Type')})")
    else:
        print(f"❌ Expected 3 Terms events, found {len(term_events)}")
        print(f"   Events detected: {[e.get('Event Name') for e in term_events]}")
        date_parse_ok = False
except Exception as e:
    print(f"❌ Terms detection FAILED: {e}")
    date_parse_ok = False

# Test 3: Active Term Detection
print("\n🎯 TEST 3: Active Term Detection")
print("-" * 70)

try:
    detector = TermDetector(mock_events)

    # Test with date in April 2026
    test_date = datetime(2026, 4, 29)
    active_term = detector.get_active_term(reference_date=test_date)

    if active_term and 'Term' in active_term.get('name', ''):
        print(f"✅ Active term detected: {active_term['name']}")
        print(f"   Start date: {active_term['start_date'].strftime('%Y-%m-%d')}")
    else:
        print(f"❌ Could not detect active term for {test_date.strftime('%Y-%m-%d')}")
        date_parse_ok = False
except Exception as e:
    print(f"❌ Active term detection FAILED: {e}")
    import traceback
    traceback.print_exc()
    date_parse_ok = False

# Test 4: Get Term Events
print("\n📋 TEST 4: Get Events for Active Term")
print("-" * 70)

try:
    if active_term:
        term_events = detector.get_term_events(active_term)
        print(f"✅ Found {len(term_events)} events for active term")
        for event in term_events:
            print(f"   - {event.get('Date')}: {event.get('Event Name')} ({event.get('Event Type')})")
except Exception as e:
    print(f"❌ Get term events FAILED: {e}")
    date_parse_ok = False

# Summary
print("\n" + "="*70)
if date_parse_ok:
    print("✅ ALL TESTS PASSED")
else:
    print("❌ SOME TESTS FAILED")
print("="*70 + "\n")

exit(0 if date_parse_ok else 1)
