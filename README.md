# Zoho Gym Campaigns Skill

**Automate email campaign creation in Zoho Campaigns based on your gym's term calendar.**

## Status: ✅ READY TO USE

All components tested and verified. The skill is fully functional and ready to create your first campaigns.

---

## Quick Start

### 1. Install Dependencies
```bash
cd zoho-gym-campaigns
pip3 install -r requirements.txt
```

### 2. Configure
```bash
# Edit config.txt with your settings:
# - GOOGLE_SHEET_URL: Your gym's calendar sheet URL
# - GOOGLE_SERVICE_ACCOUNT_JSON: Path to service account JSON
# - ZOHO_REFRESH_TOKEN: Your Zoho refresh token

source config.txt
```

### 3. Test
```bash
python3 test_setup.py          # Validates configuration
python3 test_fixes.py          # Tests date parsing & term detection
python3 test_smart_scheduling.py # Tests scheduling logic
```

### 4. Run
```bash
python3 main.py
```

The skill will:
- Auto-detect which term to process
- Read all events from your Google Sheet
- Create term overview campaign + reminder campaigns in Zoho
- Show summary of what was created

Then log into Zoho Campaigns to review and customize your campaign drafts!

---

## What's Included

### Core Modules
- **main.py** - Term detection and orchestration
- **google_sheets_reader.py** - Google Sheets API integration  
- **zoho_campaigns_client.py** - Zoho Campaigns API integration
- **campaign_generator.py** - Email campaign content generation
- **templates.py** - Event-type-specific email templates

### Configuration
- **config.txt** - Runtime environment variables
- **requirements.txt** - Python dependencies

### Testing & Documentation
- **test_setup.py** - Configuration validation
- **test_fixes.py** - Core functionality tests
- **test_smart_scheduling.py** - Scheduling logic tests
- **SKILL_OVERVIEW.md** - Complete feature documentation
- **FIXES_APPLIED.md** - Technical improvements and results
- **README.md** - Quick start guide (this file)

---

## Key Features

✅ **Smart Automatic Term Detection**
- Runs at term start? Creates campaigns for that term
- Runs mid-term? Automatically targets next term
- Always gets the right term without manual selection

✅ **Supports Your Sheet Structure**
- Reads SE/SCA date columns correctly
- Handles merged cells and "—" indicators
- Works with your exact column names

✅ **Flexible Date Formats**
- Parses any date format: "Tue 27 Jan", "2026-04-02", etc.
- Handles date ranges: "Thu 15–Fri 16 Jan", "Tue 29 Sep–Thu 1 Oct"
- Auto-infers year for dates without year specified

✅ **Professional Email Campaigns**
- Event-type-specific templates (Cheer Clinics, Fees, etc.)
- One term overview + individual reminders 3 days before each event
- All created as drafts in Zoho for your review and customization

---

## How It Works

When you run `python3 main.py`, the skill:

1. **Reads your calendar** from Google Sheets
2. **Auto-detects the term** to process:
   - At/near term start (≤7 days) → creates for that term
   - Mid-term (>7 days) → creates for next term
3. **Gets all events** for the detected term
4. **Creates campaigns in Zoho**:
   - 1 Term Overview campaign listing all events
   - 1 Reminder campaign per event (3 days before)
5. **Shows summary** of what was created

All campaigns are created as **drafts**. You review them in Zoho, customize if needed, then send!

---

## Quick Command Reference

```bash
# Setup
source config.txt                    # Load environment variables

# Testing
python3 test_setup.py               # Validate configuration
python3 test_fixes.py               # Test date parsing and term detection
python3 test_smart_scheduling.py    # Test scheduling logic

# Run
python3 main.py                     # Create campaigns for upcoming term

# Troubleshooting
find . -name "*.pyc" -delete        # Clear Python cache
rm -rf __pycache__                  # Remove cache directories
echo $GOOGLE_SHEET_URL              # Verify environment variables
```

---

## Next Steps

1. ✅ **Setup** - Skill is ready to use
2. 📝 **Configure** - Edit config.txt with your settings
3. 🧪 **Test** - Run test_setup.py to validate
4. ⏰ **Schedule** - Set up recurring runs (optional)
5. 🚀 **First Run** - Run python3 main.py
6. 📧 **Review** - Log into Zoho Campaigns to customize
7. 📨 **Send** - Set audience and send dates in Zoho

---

## Need Help?

- **SKILL_OVERVIEW.md** - Complete documentation with examples
- **FIXES_APPLIED.md** - Technical details and test results
- Check that your Google Sheet has at least one "Terms" event
- Verify environment variables: `source config.txt` then `echo $GOOGLE_SHEET_URL`
- Run `python3 test_setup.py` to diagnose any issues

---

**Your skill is ready! 🚀**
