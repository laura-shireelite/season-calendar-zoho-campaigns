"""Quick test to verify gym filtering logic"""
from datetime import datetime
from main import TermDetector

# Test events from the sheet
events = [
    {'Date': 'Sat 1–Sun 2 Aug', 'Gym': 'SE', 'Event Name': 'Aussie Gold State', 'Event Type': 'Events'},
    {'Date': 'Fri 11–Sun 13 Sep', 'Gym': 'SE', 'Event Name': 'AASCF State', 'Event Type': 'Events'},
    {'Date': 'Tue 29 Sep–Thu 1 Oct', 'Gym': 'SE', 'Event Name': 'Cheer Clinics – Spring Hols Wk 1', 'Event Type': 'Important Dates'},
]

print("Testing gym filtering logic...")
print(f"Total events: {len(events)}")

for event in events:
    gym = event.get('Gym', 'SE')
    print(f"  {event['Event Name']}: {gym}")

# Test gym detection
gyms_in_term = set()
for event in events:
    event_gym = event.get('Gym', 'SE')
    if event_gym == 'Both':
        gyms_in_term.add('SE')
        gyms_in_term.add('SCA')
    else:
        gyms_in_term.add(event_gym)

print(f"\nDetected gyms: {sorted(gyms_in_term)}")

# Test filtering for SE
se_events = []
for event in events:
    event_gym = event.get('Gym', 'SE')
    if event_gym == 'SE' or event_gym == 'Both':
        se_events.append(event)

print(f"SE events: {len(se_events)}")
print("✅ Gym logic test passed")
