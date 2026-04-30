# Campaign Content Fix - Updated Implementation

## Problem Identified

The test campaign showed that campaigns were created successfully BUT **the CONTENT section was empty** with a "Create the content of your campaign" message.

This revealed that **Zoho Campaigns requires a two-step process**:
1. **Step 1:** Create the campaign with basic metadata (name, subject, recipients)
2. **Step 2:** Set the campaign content/body via a **separate API call**

## Solution Implemented

Updated `zoho_campaigns_client.py` to use a two-step process:

### Step 1: `_create_campaign_draft()`
- Creates the campaign with subject, sender, and recipients
- Returns the campaign ID

### Step 2: `_set_campaign_content()`
- Takes the campaign ID from step 1
- Calls `/updateCampaignContent` endpoint with the HTML body
- Tests multiple possible field names:
  - `content`
  - `htmlcontent`
  - `html`
  - `campaignid` / `campaignkey`

The main `create_campaign_draft()` method now orchestrates both steps automatically.

## Key Changes

**Before:** Campaign body was never sent to Zoho
```python
payload = {
    "campaignname": campaign_name,
    "subject": subject,
    "from_email": from_email,
    # ... body was not included
}
```

**After:** Two-step process with content setting
```python
# Step 1: Create campaign
campaign_id = self._create_campaign_draft(campaign_name, subject, target_gym)

# Step 2: Set content
if body:
    self._set_campaign_content(campaign_id, body)
```

## Testing Instructions

### 1. Run the verification test again
```bash
cd /Users/lauragarrett/Documents/zoho-gym-campaigns
source config.txt
python3 verify_fix.py
```

### 2. Check Zoho Campaigns
Look for: **"✅ VERIFY Fix - Test Campaign with Content"**

**Check if:**
- ✓ Subject appears: "✅ This subject should appear"
- ✓ CONTENT section has HTML (no longer shows "Create the content of your campaign")

### 3. If content still doesn't appear
The `/updateCampaignContent` endpoint might use a different field name. Try these alternatives in `zoho_campaigns_client.py` line 315-319:

**Option 1: Only use "content"**
```python
payload = {
    "campaignid": campaign_id,
    "campaignkey": campaign_id,
    "content": body,  # Try only this one
    "resfmt": "json",
}
```

**Option 2: Try "template" or "campaign_content"**
```python
payload = {
    "campaignid": campaign_id,
    "template": body,  # Or campaign_content
    "resfmt": "json",
}
```

**Option 3: Try GET method instead of POST**
Sometimes Zoho endpoints use different HTTP methods. We'd need to test a GET request.

## Running Full Campaign Generation

Once the two-step process works:

```bash
python3 test_campaign_simple.py
```

Watch for output like:
```
📤 Creating: Campaign Name
📝 Setting campaign content...
✅ Content set successfully
✅ Created: Campaign Name (ID: xxx)
```

## Expected Behavior After Fix

When you run `main.py`:
1. **Creates term overview campaign** with subject AND body content
2. **Creates reminder campaigns** with specific event templates
3. **All campaigns should have:**
   - Subject line (already working)
   - Email body content (now fixed!)
   - Proper recipient lists
   - Topic assigned (Important Info)

## Debugging Tips

If content is still empty after testing:

1. **Check if `/updateCampaignContent` is the right endpoint**
   - Zoho might use `/updateCampaignBody`, `/setCampaignContent`, etc.
   - Try searching Zoho API docs for "campaign content" endpoints

2. **Check if you need a different HTTP method**
   - Currently using POST, might need PUT or PATCH
   - The API response will tell us

3. **Check the campaign_id format**
   - Make sure we're using the correct ID format
   - Zoho response shows both `campaign_id` and `campaignKey` - might need the other

4. **Check HTML validation**
   - Zoho might be stripping invalid HTML
   - Try with simpler HTML: `<p>Test content</p>`

## Next Steps

1. Run `verify_fix.py` and report if content now appears
2. If yes: Run `python3 main.py` to create all campaigns for your term
3. If no: Try the alternative field names above and report which one works
4. Once working: Delete the test campaigns and set up scheduled runs for May 15, Sept 30, Jan 15

---

## Questions for Debugging

Please share:
- Does the test campaign now have HTML content visible?
- What's in the CONTENT section of the campaign?
- Any error messages in the terminal output?
- What endpoint URL would work for Zoho campaign content?

This will help us identify if we need to adjust the field name or endpoint!
