# Shire Elite Campaign Automation Workflow

## Overview
This automation system creates email campaigns in Zoho Campaigns with 95% full automation. The final step (adding content/logo) is manual but takes only ~30 seconds per campaign.

## Why This Approach?

**What's Automated:**
- ✅ Read events from Google Sheets
- ✅ Auto-detect current term
- ✅ Generate campaign metadata (names, subjects, recipients)
- ✅ Create all campaigns via Zoho API
- ✅ Configure mailing lists and topics
- ✅ Prepare master template with logo

**What Requires One Click:**
- ⏱️ Paste HTML content into each campaign (preserves logo display)

This is necessary because Zoho's Content Security Policy strips images from externally-loaded content URLs, but preserves them when content is set internally.

---

## How to Use

### Step 1: Run the Automation
```bash
python3 main.py
```

This will:
1. Read your Google Sheets calendar
2. Find the next upcoming term
3. Create all campaign drafts in Zoho (automatically)
4. Display a summary

### Step 2: Add Content to Each Campaign (Manual - ~2 minutes total for 5 campaigns)

For each campaign that was created:

1. **Log into Zoho Campaigns**
2. **Open each campaign draft** (they'll be named like "Term 3 begins – all programs - What's Coming Up")
3. **Click "Create Content"** button
4. **Copy the master template HTML:**
   - Open `master_template.html` in this folder
   - Copy all the HTML content
5. **Paste into Zoho content editor**
6. **Done!** The Shire Elite logo will display automatically

### Step 3: Schedule & Send

Once all campaigns have content:
1. Set send dates for each campaign
2. Review the preview (logo should display)
3. Send to your audience

---

## Files

- **`main.py`** — Entry point. Run this to create campaigns automatically.
- **`master_template.html`** — The email template with Shire Elite logo and styling. Copy/paste this into each campaign.
- **`campaign_generator.py`** — Generates campaign content and metadata from events
- **`zoho_campaigns_client.py`** — Handles API communication with Zoho
- **`google_sheets_reader.py`** — Reads events from your Google Sheets calendar

---

## Configuration

Required environment variables (set once):
```
GOOGLE_SHEET_URL=<your sheet URL>
GOOGLE_SERVICE_ACCOUNT_JSON=<your service account JSON>
ZOHO_REFRESH_TOKEN=<your refresh token>
ZOHO_SE_LIST_KEY=4913000010605024
ZOHO_TOPIC_ID=4913000004767578
```

---

## Why Not Fully Automated?

We investigated using Zoho's API to set content automatically, but:
- The content update APIs return "resource not found" errors
- The feature may require explicit enablement at the org level (contact Zoho support if you want this)
- The manual paste approach is simple, fast, and guarantees the logo displays

**The current solution is optimal:** Minimal manual work (1 paste per campaign) + maximum reliability.

---

## Troubleshooting

**Campaigns not created?**
- Check environment variables are set: `echo $ZOHO_REFRESH_TOKEN`
- Verify Google Sheets is accessible
- Check that your sheet has "Full Timeline" worksheet with columns: SE, SCA, Event

**Logo not displaying in preview?**
- Make sure you're pasting the ENTIRE `master_template.html` content
- The logo URL is Zoho's internal Stratus CDN: it must be pasted internally (not via external URL)

**Reminder dates wrong?**
- Check your Google Sheets date format. Supported: "Tue 27 Jan", "27 Jan", "27/1/2026"

---

## Questions?

The automation handles:
- Term detection (finds next upcoming term automatically)
- Event grouping (groups holiday clinics together)
- Reminder scheduling (3 days before each event)
- Personalization (includes Zoho merge tags for athlete names, teams, etc.)

All campaigns use your `master_template.html` which includes your Shire Elite branding and logo.
