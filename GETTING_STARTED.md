# Getting Started with Zoho Gym Campaigns

This guide walks you through setting up the skill step-by-step.

## What You've Got

Your skill directory contains:

```
zoho-gym-campaigns/
├── main.py                    # ← The entry point (what runs)
├── google_sheets_reader.py    # Reads your calendar
├── zoho_campaigns_client.py   # Connects to Zoho
├── campaign_generator.py      # Builds emails
├── templates.py               # Email designs
├── test_setup.py             # Test your configuration
├── config.example.txt        # Template for your credentials
├── requirements.txt          # Python dependencies
├── README.md                 # Full documentation
├── SKILL.md                  # Detailed spec
└── GETTING_STARTED.md        # This file
```

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs the `requests` library which the skill uses to talk to Google and Zoho.

## Step 2: Gather Your Credentials

You need three pieces of information:

### a) Google API Key

1. Go to **Google Cloud Console**: https://console.cloud.google.com
2. Select or create a project
3. Enable the **Google Sheets API**:
   - Click "APIs & Services" → "Library"
   - Search for "Google Sheets"
   - Click "Enable"
4. Create an API Key:
   - Click "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the key (looks like: `AIzaSyD...`)

### b) Google Sheet URL

1. Open your gym's calendar spreadsheet in Google Sheets
2. Copy the URL from the address bar
   - Full URL: `https://docs.google.com/spreadsheets/d/1abc123xyz.../edit`

### c) Zoho Campaigns Refresh Token

1. Go to **Zoho Campaigns**: https://campaigns.zoho.com.au
2. Click **Settings** → **API Keys**
3. Click "Generate Grant Code"
4. You'll get a grant code (looks like: `1000.47a...`)
5. Run the included token exchange script:

```bash
python get_zoho_tokens.py
```

When prompted, paste your grant code. The script will give you your **refresh token** (the long-lived credential).

Save this refresh token - you'll use it.

## Step 3: Create Your Configuration

Copy the example config and fill in your credentials:

```bash
cp config.example.txt config.txt
```

Edit `config.txt`:

```bash
export GOOGLE_SHEET_URL="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
export ZOHO_REFRESH_TOKEN="YOUR_REFRESH_TOKEN_HERE"
```

Save the file.

## Step 4: Test Your Setup

Load your configuration:

```bash
source config.txt
```

Run the validation script:

```bash
python test_setup.py
```

This will check:
- ✅ Environment variables are set
- ✅ Can read your Google Sheet
- ✅ Can connect to Zoho Campaigns
- ✅ Can auto-detect your term

If all tests pass, you're ready! If not, it will tell you what's wrong.

## Step 5: Run a Test

Create your first campaigns:

```bash
source config.txt
python main.py
```

Watch the output. It will:
1. Read your calendar
2. Auto-detect the current term
3. Show you what campaigns it's about to create
4. Create the drafts in Zoho

Go to Zoho Campaigns and check your draft campaigns. Do they look good? If yes, move to Step 6.

## Step 6: Schedule It

You want this skill to run automatically at the start of each term. Here's how:

### Option A: Cowork Scheduled Tasks (Recommended)

If you're using Cowork:

1. In Cowork, go to **Scheduled Tasks**
2. Click **Create New Scheduled Task**
3. Name: "Zoho Gym Campaigns - Term 2 2026"
4. Schedule: "Once at specific time"
5. Date/Time: June 1, 2026 at 8:00 AM (or whenever your term starts)
6. Command: `python /path/to/zoho-gym-campaigns/main.py`
7. Save

The skill will run automatically on that date, detect the term, and create campaigns.

**Repeat for each term:**
- Term 3: September 1, 2026
- Term 4: December 1, 2026
- etc.

### Option B: Mac/Linux Cron

Add to your crontab (`crontab -e`):

```bash
# Term 2 start - June 1st at 8am
0 8 1 6 * source ~/.config/zoho-gym/config.txt && cd ~/.config/zoho-gym && python main.py

# Term 3 start - September 1st at 8am
0 8 1 9 * source ~/.config/zoho-gym/config.txt && cd ~/.config/zoho-gym && python main.py
```

### Option C: Windows Task Scheduler

1. Press `Win+R`, type `taskschd.msc`
2. Right-click "Task Scheduler Library" → "Create Basic Task"
3. Name: "Zoho Gym Campaigns"
4. Trigger: Set date to term start
5. Action: "Start a program"
6. Program: `python.exe`
7. Arguments: `C:\path\to\main.py`
8. Save

## Step 7: What Happens When It Runs

On the scheduled date, the skill:

1. **Reads your sheet** → Gets all 2026 events
2. **Detects the term** → Finds "June 3: Term 2 Starts"
3. **Gets events for that term** → All events from June 3 until Sept 2
4. **Creates "Term 2 2026 - All Events"** campaign listing everything
5. **Creates reminder campaigns** → One for each event, 3 days before
6. **All as drafts** → You review in Zoho before sending

Total time: ~30 seconds.

## Troubleshooting

### "Import error: requests"
```bash
pip install requests
```

### "Invalid Google API key"
- Check the key in config.txt matches exactly
- Make sure Google Sheets API is enabled in Google Cloud Console
- Create a new key if unsure

### "Invalid Zoho refresh token"
- Run `python get_zoho_tokens.py` again with a fresh grant code
- Refresh tokens expire after 6 months if unused
- Regenerate in Zoho Settings → API Keys

### "No term detected"
- Your sheet must have at least one event with Event Type = "Terms"
- That event's date must be on or before today
- Check date format (YYYY-MM-DD or DD/MM/YYYY)

### "Can read sheet but campaigns not created"
- Check Zoho rate limits (max 5 requests/second)
- Verify event types match templates (Events, Terms, Gym Closures, etc.)
- Check Zoho Campaigns → Campaign Drafts to see if they were created

## Next: Customize

Once you've run it once and reviewed the campaigns:

1. **Edit email templates** in `templates.py` if you want different wording
2. **Change reminder timing** if you want 2 days or 5 days instead of 3
3. **Adjust gym name** in `campaign_generator.py` (line ~180)
4. **Modify HTML styling** in templates for your brand colors

Then re-run to create new campaigns with your customizations.

## Questions?

See **README.md** for detailed documentation.

Refer to **SKILL.md** for the complete feature specification.

Good luck! 🎉
