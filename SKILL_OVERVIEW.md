# Zoho Gym Campaigns Skill - Complete Overview

## What This Skill Does

This skill automates email campaign creation in Zoho Campaigns based on your gym's term calendar stored in Google Sheets. It's designed to run at the start of each term to create professional email campaigns for your members.

**Every time the skill runs, it:**
1. ✅ Reads your term calendar from Google Sheets
2. ✅ Auto-detects which term to process (with smart mid-term logic)
3. ✅ Creates a single **Term Overview Campaign** listing all events for that term
4. ✅ Creates individual **Reminder Campaigns** scheduled 3 days before each event
5. ✅ Applies event-type-specific email templates (Cheer Clinics, Fees, Gym Closures, etc.)
6. ✅ Creates campaign drafts in Zoho Campaigns ready for you to customize and send

All campaigns are created as **drafts** in Zoho—you review them, customize if needed, then send.

---

## How It Works

### 1. Smart Automatic Term Detection

The skill automatically detects which term to process based on today's date:

**Scheduled Runs (at term start):**
- When scheduled to run on April 2 (Term 2 start) → Creates campaigns for Term 2
- When scheduled to run on July 10 (Term 3 start) → Creates campaigns for Term 3

**Manual Runs (anytime):**
- If you're within 7 days of a term start → Creates campaigns for that term
- If you're 7+ days into a term → Creates campaigns for the **next term** (assumes current term is done)

**Example:**
- Today is April 29 (27 days into Term 2)
- Running the skill now → Auto-detects Term 3 (starts July 10)
- Creates campaigns for Term 3 ✅

### 2. Google Sheets Integration

The skill reads your calendar directly from Google Sheets with your exact structure:

**Your sheet layout:**
- **Column A (SE):** Dates for Shire Elite Paddington location
- **Column B (SCA):** Dates for South Coast Athletics location
- **Column C (Event):** Event name
- **Column D (See more details →):** Event type

**Special handling:**
- When SE and SCA dates match: Creates single event marked "Both"
- When dates differ: Creates separate events for each location
- When one column has "—": Creates event for that location only
- Terms events (marked "Terms →"): Used for term boundary detection, not included in reminders

### 3. Event Processing

**For each event, the skill:**
1. Extracts the event details (date, name, type, location)
2. Checks the event type (Cheer Clinics, Fees, Gym Closures, etc.)
3. Selects the appropriate email template
4. Creates a reminder campaign scheduled for 3 days before the event
5. Uses proper gym name and branding in the email

**Events are processed correctly whether:**
- Single-day events: "Fri 15 April"
- Date ranges within month: "Thu 15–Fri 16 Jan"
- Date ranges across months: "Tue 29 Sep–Thu 1 Oct"
- With or without day of week
- With or without year (auto-inferred based on current date)

### 4. Campaign Drafts in Zoho

All campaigns are created as drafts with proper formatting:

**Term Overview Campaign:**
- Subject: "📅 Term 2 – Your Event Calendar"
- Contains table of all events with dates, names, locations
- Call-to-action link to view full calendar
- Summary of what to expect (detailed reminders, easy registration, etc.)

**Reminder Campaigns (one per event):**
- Subject and body tailored to event type
- Created as drafts scheduled for 3 days before event
- Ready for you to set final send date and send to your contact list

**Next Steps After Skill Runs:**
1. Log into Zoho Campaigns
2. Review your campaign drafts
3. Customize templates/content as needed
4. Set send dates and audience
5. Send to your members

---

## Setup & Configuration

### Requirements
- Python 3.7+
- Google Sheets API service account (JSON file)
- Zoho Campaigns refresh token
- Required Python packages: `requests`, `cryptography`

### Files Provided
- `main.py` - Main script with term detection logic
- `google_sheets_reader.py` - Google Sheets API integration
- `zoho_campaigns_client.py` - Zoho Campaigns API integration
- `campaign_generator.py` - Email campaign generator
- `templates.py` - Event-type-specific email templates
- `test_setup.py` - Validates configuration
- `test_fixes.py` - Tests date parsing and term detection
- `test_smart_scheduling.py` - Tests scheduling logic
- `config.txt` - Runtime configuration (you fill this in)
- `requirements.txt` - Python dependencies

### Initial Setup

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Edit config.txt with:
#    - Your Google Sheet URL
#    - Path to service account JSON
#    - Zoho refresh token
source config.txt

# 3. Test configuration
python3 test_setup.py

# 4. Once validated, run the skill
python3 main.py
```

---

## Smart Scheduling Examples

### Example 1: Scheduled Run at Term Start
**Setup:** Schedule skill to run April 2 at 8:00 AM (Term 2 start)

| Date | Term Started | Days Into | Action |
|------|-------------|-----------|--------|
| Apr 2, 8am | Term 2 | 0 | ✅ Creates campaigns for Term 2 |
| Apr 10, manual | Term 2 | 8 | ✅ Creates campaigns for Term 3 |
| May 1, manual | Term 2 | 29 | ✅ Creates campaigns for Term 3 |

### Example 2: Always Schedule at Term Start
Best practice: Schedule the skill to run automatically at the start of each term.

```
Recurring Schedule:
- April 2 @ 8am → Term 2 campaigns
- July 10 @ 8am → Term 3 campaigns
- October 15 @ 8am → Term 4 campaigns (when added to sheet)
```

With this setup, the skill always creates the right campaigns at the right time.

### Example 3: Manual Pre-Creation
If you want to create campaigns early:
- Run manually 1-2 days before term start (within 7-day window)
- Skill creates campaigns for that upcoming term
- You have them ready to review and customize in advance

---

## Date Format Support

The skill handles all these date formats automatically:

| Format | Examples |
|--------|----------|
| ISO format | 2026-04-02, 2026-07-10 |
| European | 02/04/2026, 02-04-2026 |
| US format | 04/02/2026 |
| Short with day | Tue 27 Jan, Thu 2 Apr |
| Short without day | 27 Jan, 2 Apr |
| Date ranges | "Thu 15–Fri 16 Jan" or "Tue 29 Sep–Thu 1 Oct" |

### Year Inference
- Dates within 6 months past: current year
- Dates more than 6 months past: next year
- Dates in future: current year
- Day of week automatically parsed if included

---

## Event Type Templates

The skill includes specialized email templates for each event type:

| Event Type | Template |
|-----------|----------|
| Events | General events |
| Terms | Term start/end notifications |
| Gym Closures | Closure announcements |
| Catch Ups | Social/catch-up events |
| Fees | Payment/fee reminders |
| Cheer Clinics | Cheer-specific training |
| Other | Fallback for custom types |

Each template:
- Has event-appropriate subject lines
- Uses consistent branding (gym name, colors)
- Includes event details, date, location, call-to-action
- Is professionally formatted for email clients

---

## Testing

### Test Files
1. **test_setup.py** - Validates environment, credentials, Google Sheets, Zoho connection
2. **test_fixes.py** - Tests date parsing, terms detection, active term detection
3. **test_smart_scheduling.py** - Tests scheduling logic at different points in term cycle

### Run Tests
```bash
cd zoho-gym-campaigns

# Full setup validation
python3 test_setup.py

# Date and term detection tests
python3 test_fixes.py

# Smart scheduling logic tests
python3 test_smart_scheduling.py
```

---

## Troubleshooting

### "No term events found"
**Cause:** Sheet doesn't have any events marked with "Terms" in the Event Type column
**Fix:** Add Term Start events to your sheet with Event Type = "Terms" or "Terms →"

### "Could not parse date"
**Cause:** Date format not recognized
**Fix:** Use one of the supported formats listed above

### "Column structure warning"
**Cause:** Column names don't match expected names
**Fix:** This is just a warning. The skill reads your actual columns (SE, SCA, Event, See more details →) correctly

### "Missing required environment variables"
**Cause:** config.txt not loaded or missing settings
**Fix:** Run `source config.txt` before running the skill

### "Zoho authentication failed"
**Cause:** Refresh token invalid or expired
**Fix:** Generate a new Zoho refresh token following the OAuth flow

---

## Your Sheet Structure (Shire Elite)

The skill is configured for your exact sheet layout:

```
Row 1: "2026 FULL TIMELINE" (title, skipped)

Row 2: SE | SCA | Event | See more details →
       (headers)

Row 3+: Data rows
  - SE date (or "—" if SCA only)
  - SCA date (or "—" if SE only)
  - Event name
  - Event type / category

Examples:
  Tue 27 Jan | — | Summer Swim | Events
  — | Thu 2 Apr | Training Camp | Cheer Clinics
  15 Apr | 15 Apr | Club Fee | Fees (marked as "Both")
  Thu 20–Fri 21 May | — | Championships | Events
```

---

## Customization

### Change Reminder Timing
Edit `campaign_generator.py` line 131:
```python
reminder_date = event_date - timedelta(days=3)  # Change 3 to desired days
```

### Change Gym Name in Emails
Edit `campaign_generator.py` line 226:
```python
return "Shire Elite Gyms"  # Change to your preferred name
```

### Change Email Templates
Edit `templates.py` to customize subject lines, HTML formatting, call-to-action text

### Change Term Detection Threshold
Edit `main.py` line 271:
```python
if days_into_term > 7:  # Change 7 to desired threshold
```

---

## Next Steps

1. ✅ **Setup Complete** - All files configured and tested
2. 📅 **Set Schedule** - Schedule skill to run at term start times
3. 🧪 **First Run** - Run `python3 main.py` to create initial campaigns
4. 📧 **Review & Customize** - Log into Zoho, review drafts, customize templates
5. 📨 **Send Campaigns** - Set audience and send dates in Zoho

---

## Support

**If something isn't working:**
1. Run `python3 test_setup.py` to validate configuration
2. Check that your sheet has at least one "Terms" event
3. Verify Google service account JSON and Zoho tokens
4. Run `python3 test_fixes.py` to test date parsing
5. Check that environment variables are loaded: `echo $GOOGLE_SHEET_URL`

Your skill is now ready to automate your gym's email campaigns! 🚀
