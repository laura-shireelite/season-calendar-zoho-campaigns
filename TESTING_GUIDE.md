# Testing Guide - Zoho Gym Campaigns Skill

## Problem We Fixed

**Error 6606**: "Selected list/segment doesnot contain any contacts"

The issue was that the code was trying to use segment IDs (4913000010605024, 4913000010939004) directly as mailing list keys in the API, which doesn't work.

## The Solution

For **testing purposes**, we've simplified the code to:
1. Use the "Enrolled Athletes" mailing list (429 contacts) without segment filtering
2. Route campaigns to the correct `from_email` based on gym type
3. Once this works, we can add proper segment filtering

### Changes Made

**File: `zoho_campaigns_client.py`**
- Simplified `_get_list_details_for_gym()` to use the default mailing list with no segment filters
- Updated `from_email` routing: SE events use `hello@shireelite.com.au`, SCA events use `hello@scaallstars.com.au`
- Improved logging to show which list is being used

**File: `campaign_generator.py`**
- Added `target_gym` field to term-start campaigns (defaults to 'Shire Elite')

## Testing Steps

### Step 1: Run the Simple Test
```bash
cd /Users/lauragarrett/Documents/zoho-gym-campaigns
source config.txt
python3 test_campaign_simple.py
```

This creates 3 test campaigns:
- ✅ One for Shire Elite (using hello@shireelite.com.au)
- ✅ One for SCA Allstars (using hello@scaallstars.com.au)
- ✅ One generic campaign (using hello@shireelite.com.au)

**Expected outcome**: All 3 campaigns should create successfully to the "Enrolled Athletes" list

### Step 2: Check Zoho Campaigns
Log into your Zoho Campaigns account and verify the test campaigns appear as drafts in the "Email Campaigns" section.

### Step 3: Run the Full Skill
Once the test passes, run the main skill:
```bash
python3 main.py
```

This should:
1. Read events from your Google Sheet
2. Detect the next active term
3. Create 1 term overview + 5 reminder campaigns (6 total)
4. All campaigns should route to the "Enrolled Athletes" list

## API Format

The campaigns are now being created with this payload:
```json
{
    "campaignname": "Term 3 2026 - All Events",
    "subject": "📅 Term 3 2026 – Your Event Calendar",
    "from_email": "hello@shireelite.com.au",
    "resfmt": "json",
    "list_details": "{\"4913000005118553\": []}"
}
```

Where:
- `4913000005118553` = The "Enrolled Athletes" mailing list (429 contacts)
- `[]` = No segment filter (sends to all contacts in the list)

## Next Steps After Testing

Once we confirm campaigns are creating successfully, we can:

1. **Add proper segment routing** - Figure out how to filter by:
   - "Enrolled SE Athletes" for SE events
   - "Enrolled SCA Athletes" for SCA events
   - Never mix them

2. **Set up scheduling** - Configure the skill to run automatically on:
   - May 15 (start of Term 2)
   - Sept 30 (start of Term 3)
   - Jan 15 (start of Term 1)

3. **Add content templates** - Customize email bodies for different event types

## Troubleshooting

### Error 6606 still appears
- Verify "Enrolled Athletes" list has 429 contacts in Zoho UI
- Check that `ZOHO_DEFAULT_LIST_KEY=4913000005118553` in config.txt
- Verify `hello@shireelite.com.au` is verified as a sender in Zoho settings

### Error 6610 (Email not verified)
- Go to Zoho Campaigns > Settings > Email Addresses
- Verify both `hello@shireelite.com.au` and `hello@scaallstars.com.au`

### 401 Unauthorized
- Check that ZOHO_REFRESH_TOKEN is correct and not expired
- May need to re-authenticate in Zoho

## Questions?

The skill is designed to:
- ✅ Auto-detect which term to process (no manual selection needed)
- ✅ Route SE events to SE email, SCA events to SCA email (separate campaigns)
- ✅ Create 1 term overview + 1 reminder per event (3 days before)
- ✅ Schedule to run automatically without duplicates

All campaigns are created as **drafts** in Zoho, so you can review/edit them before sending.
