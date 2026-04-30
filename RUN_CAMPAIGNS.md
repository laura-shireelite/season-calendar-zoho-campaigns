# How to Run the Zoho Campaigns Skill

## Quick Start (Recommended)

Open your terminal and run this in your project folder:

```bash
# Navigate to the project
cd ~/Documents/zoho-gym-campaigns

# Load configuration and run
source config.txt && python3 main.py
```

## Step-by-Step Instructions

### 1. Open Terminal
- **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
- **Windows**: Press `Win + R`, type "cmd", press Enter

### 2. Navigate to Your Project Folder
```bash
cd ~/Documents/zoho-gym-campaigns
```

If you get "No such file or directory", check that the path is correct.

### 3. Run the Script

**Option A: Full Automated Run** (reads Google Sheets + creates campaigns)
```bash
source config.txt && python3 main.py
```

**Option B: Test Run** (uses local test data, no Google Sheets needed)
```bash
source config.txt && python3 << 'EOF'
import os, sys
# Load config
config = {}
with open('config.txt', 'r') as f:
    for line in f:
        if line.startswith('export '):
            parts = line.replace('export ', '').split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().strip('"\'')
                os.environ[key] = value

from zoho_campaigns_client import ZohoCampaignsClient
from campaign_generator import CampaignGenerator

test_events = [
    {'Event Name': 'Term 3 Begins', 'Date': 'Mon 1 Sep', 'Event Type': 'Terms', 'Gym': 'All'},
    {'Event Name': 'Spring Comp', 'Date': 'Sat 6 Sep', 'Event Type': 'Events', 'Gym': 'Shire Elite'},
    {'Event Name': 'Gym Closure – Maintenance', 'Date': 'Mon 8–Wed 10 Sep', 'Event Type': 'Gym Closures', 'Gym': 'All'},
    {'Event Name': 'Cheer Clinics – Spring Hols Wk 1', 'Date': 'Mon 22–Fri 26 Sep', 'Event Type': 'Cheer Clinics', 'Gym': 'All'},
    {'Event Name': 'Cheer Clinics – Spring Hols Wk 2', 'Date': 'Mon 29 Sep–Fri 3 Oct', 'Event Type': 'Cheer Clinics', 'Gym': 'All'},
]

print("\n" + "="*70)
print("CREATING TEST CAMPAIGNS WITH PROFESSIONAL STYLING")
print("="*70)

try:
    zoho_token = os.getenv('ZOHO_REFRESH_TOKEN')
    zoho_client = ZohoCampaignsClient(zoho_token, default_list_key=os.getenv('ZOHO_DEFAULT_LIST_KEY'), topic_id=os.getenv('ZOHO_TOPIC_ID'))
    generator = CampaignGenerator("Term 3 2026", test_events)
    
    print("\n📅 Creating Term Overview Campaign...")
    term_campaign = generator.create_term_start_campaign()
    if term_campaign:
        zoho_client.create_campaign_draft(term_campaign)
        print(f"✅ Created: {term_campaign['name']}")
    
    print("\n⏰ Creating Reminder Campaigns...")
    reminders = generator.create_reminder_campaigns()
    for reminder in reminders:
        zoho_client.create_campaign_draft(reminder)
        print(f"✅ Created: {reminder['name']}")
    
    print("\n" + "="*70)
    print(f"✅ SUCCESS: Created {1 + len(reminders)} campaigns with professional styling!")
    print("="*70)
    print("\n📧 Check Zoho Campaigns to see your new drafts with:")
    print("   • Gradient headers with brand colors")
    print("   • Responsive mobile design")
    print("   • Styled CTA buttons")
    print("   • Professional footer")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF
```

## What You'll See

When the script runs, you'll see:

```
======================================================================
ZOHO GYM CAMPAIGNS SKILL
======================================================================

📋 Loading configuration...
✅ Configuration loaded

📊 Reading calendar from Google Sheet...
✅ Loaded X events from sheet

🔍 Finding next upcoming term...
✅ Will create campaigns for: Term 3 2026

📅 Fetching events for this term...
✅ Found 15 events for Term 3 2026

🔌 Connecting to Zoho Campaigns...
✅ Connected to Zoho Campaigns

✍️  Creating campaigns...
   📅 Term 3 2026 - What's Coming Up
      ✅ Created term campaign

   ⏰ Spring Comp - 3 Day Reminder
      ✅ Created reminder
   
   [more campaigns...]

======================================================================
✅ SKILL COMPLETED SUCCESSFULLY
======================================================================
```

## Troubleshooting

### Error: "No such file or directory"
- Make sure you're in the correct folder: `cd ~/Documents/zoho-gym-campaigns`
- Check the path with: `pwd`

### Error: "python3: command not found"
- Install Python 3: https://www.python.org/downloads/
- Or try `python main.py` instead of `python3 main.py`

### Error: "Permission denied"
- Make sure config.txt is readable: `chmod 644 config.txt`

### Error: "Failed to read Google Sheet"
- Check GOOGLE_SHEET_URL in config.txt
- Check GOOGLE_SERVICE_ACCOUNT_JSON file exists
- Make sure calendar-campaigns-automation.json is in the project folder

### Error: "Failed to refresh token"
- Check ZOHO_REFRESH_TOKEN in config.txt is correct
- Token may have expired; regenerate from Zoho

## Next Steps

1. **Run the script** using one of the commands above
2. **Log into Zoho Campaigns** (zoho.com.au)
3. **Check your Drafts** - you should see new campaigns with professional styling
4. **Preview the emails** - click into each campaign to see the responsive design
5. **Edit and customize** - adjust content, colors, buttons as needed
6. **Set up scheduling** - use `python3 schedule.py` to automate on a schedule (coming soon)

## Files Created

When you run the script, it automatically:
- Reads events from your Google Sheet
- Generates HTML emails with professional styling
- Uploads them to GitHub Pages
- Creates draft campaigns in Zoho
- Saves everything to `docs/campaigns/` folder

---

**Questions?** Check the README.md or DEBUG_NOTES.md files for more details.
