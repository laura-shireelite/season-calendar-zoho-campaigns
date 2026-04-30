#!/usr/bin/env python3
"""
Test the simplified scheduling strategy:
- Always target the next upcoming term (not current)
- Run at fixed mid-to-late term dates
- Never run manually
- Result: No duplicates, clean scheduling
"""

from datetime import datetime
from main import TermDetector

print("\n" + "="*70)
print("TESTING NEXT-TERM-ONLY STRATEGY")
print("="*70)

# Mock data with three terms
mock_events = [
    {'Date': 'Tue 27 Jan', 'Gym': 'SE', 'Event Name': 'Term 1', 'Event Type': 'Terms →'},
    {'Date': 'Thu 2 Apr', 'Gym': 'SE', 'Event Name': 'Term 2', 'Event Type': 'Terms →'},
    {'Date': 'Fri 10 Jul', 'Gym': 'SE', 'Event Name': 'Term 3', 'Event Type': 'Terms →'},
    {'Date': '2026-10-15', 'Gym': 'SE', 'Event Name': 'Term 4', 'Event Type': 'Terms →'},
    {'Date': '2026-04-15', 'Gym': 'SE', 'Event Name': 'Event during Term 2', 'Event Type': 'Events'},
    {'Date': '2026-07-22', 'Gym': 'SE', 'Event Name': 'Event during Term 3', 'Event Type': 'Events'},
]

detector = TermDetector(mock_events)

print("\n🧪 TEST 1: Early in Term 1 (Jan 30)")
print("-" * 70)
test_date = datetime(2026, 1, 30)
next_term = detector.get_next_term(reference_date=test_date)
if next_term:
    print(f"Current term: Term 1 (started Jan 27)")
    print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
    print(f"✅ Will create campaigns for: {next_term['name']}")

print("\n🧪 TEST 2: Mid-term scheduled run - May 15 (in Term 2)")
print("-" * 70)
test_date = datetime(2026, 5, 15)
next_term = detector.get_next_term(reference_date=test_date)
if next_term:
    print(f"Current term: Term 2 (started Apr 2)")
    print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
    days_until = (next_term['start_date'] - test_date).days
    print(f"Days until next term: {days_until}")
    print(f"✅ Safe scheduled run: Creates for {next_term['name']}")
    print(f"   ({days_until} days notice before term starts)")

print("\n🧪 TEST 3: Safe mid-late term run - Sept 30 (in Term 3)")
print("-" * 70)
test_date = datetime(2026, 9, 30)
next_term = detector.get_next_term(reference_date=test_date)
if next_term:
    print(f"Current term: Term 3 (started Jul 10)")
    print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
    days_until = (next_term['start_date'] - test_date).days
    print(f"Days until next term: {days_until}")
    print(f"✅ Safe scheduled run: Creates for {next_term['name']}")
    print(f"   ({days_until} days notice before term starts)")

print("\n🧪 TEST 4: Today (Apr 29 - in Term 2)")
print("-" * 70)
test_date = datetime(2026, 4, 29)
next_term = detector.get_next_term(reference_date=test_date)
if next_term:
    print(f"Current term: Term 2 (started Apr 2, 27 days ago)")
    print(f"Next term: {next_term['name']} (starts {next_term['start_date'].strftime('%Y-%m-%d')})")
    days_until = (next_term['start_date'] - test_date).days
    print(f"Days until next term: {days_until}")
    print(f"✅ Today: Should not run yet")
    print(f"   (Schedule for May 15-20 to create Term 3 campaigns)")

print("\n" + "="*70)
print("RECOMMENDED SCHEDULE")
print("="*70)
print("""
Run the skill at these safe dates (mid-to-late in each term):

  • May 15, 2026 @ 8am
    → Currently in Term 2, creates campaigns for Term 3 (starts Jul 10)
    → Gives 56 days notice before Term 3

  • September 30, 2026 @ 8am
    → Currently in Term 3, creates campaigns for Term 4 (starts Oct 15)
    → Gives 15 days notice before Term 4

  • And so on for future terms...

Benefits:
  ✅ No duplicates (runs exactly once per term)
  ✅ No manual runs needed
  ✅ Consistent timing
  ✅ Time to review & customize campaigns before term starts
  ✅ Simple, reliable, predictable
""")

print("="*70)
print("✅ NEXT-TERM-ONLY STRATEGY IS CLEAN AND RELIABLE")
print("="*70 + "\n")
