# Debug Notes - Error 6606 Investigation

## Issue
Error 6606 "Selected list/segment doesnot contain any contacts" when creating campaigns, even though "Enrolled Athletes" list shows 429 contacts in Zoho UI.

## Hypothesis
The Zoho API might require creating the campaign **without** the `list_details` parameter first, then adding recipients in a **separate API call** (similar to how the manual UI process works: Create → Add Recipients).

## What We Changed
Commented out the `list_details` parameter in the campaign creation to test if:
1. Campaign creation succeeds without list_details
2. We then need a separate endpoint to add recipients

## Next Steps to Test

### Test 1: Campaign Creation Without List Details
```bash
cd /Users/lauragarrett/Documents/zoho-gym-campaigns
source config.txt
python3 test_campaign_simple.py
```

**Expected outcome:**
- ✅ All 3 campaigns should create successfully as DRAFTS
- They will have no recipients assigned yet
- You'll see them in Zoho Campaigns as draft campaigns with empty recipient lists

**What this tells us:**
- If it works: The `list_details` parameter is the problem, not the API endpoint or credentials
- If it fails: There's a different issue preventing campaign creation

### Test 2: Check Campaign in Zoho UI
Once campaigns are created:
1. Log into Zoho Campaigns
2. Go to Campaigns > Email Campaigns
3. Look for "🧪 TEST" campaigns
4. Click one to open it
5. Go to "RECIPIENT" section
6. Manually select "Enrolled Athletes" list
7. Verify it saves successfully

This manual step will tell us if:
- The list is accessible via the UI (it is - 429 contacts)
- The list can be assigned to campaigns via the UI (should work)
- Something specific about the API format is wrong

### Test 3: Identify the Correct API Format

If campaigns create successfully but the list can't be assigned via the API, we need to investigate:

**Option A:** Use a different parameter name
- Maybe it's not `list_details` but `listdetails` or `list_key`?
- Check Zoho API docs for exact parameter names

**Option B:** Use a completely different endpoint
- Maybe there's a separate endpoint like:
  - `updateCampaignRecipient`
  - `addCampaignRecipient`  
  - `assignRecipients`
  - `updateRecipientList`

**Option C:** The parameter format is wrong
- Current format: `{"4913000005118553": []}`
- Maybe it should be: `[{"key": "4913000005118553", "filters": []}]`
- Or maybe: `["4913000005118553"]`
- Or maybe: `4913000005118553`

## API Documentation Resources

To find the correct endpoint/format:
1. Check Zoho's official API docs for `/createCampaign` endpoint
2. Look at the Zoho Campaigns API reference guide
3. Check if there's a `/addRecipients` or `/updateRecipients` endpoint
4. Look at the exact parameter names and formats required

## Key Information We Have

From screenshots and testing:
- ✅ List exists: "Enrolled Athletes" 
- ✅ List has contacts: 429 shown in UI
- ✅ Tokens work: Can authenticate to Zoho API
- ✅ Some campaigns may have been created successfully before (we saw evidence in history)
- ❌ Current API call format for list_details isn't working

## If Test 1 Passes

Then we need to:
1. Create a new method: `add_recipients_to_campaign(campaign_id, list_key)`
2. Call it after campaign creation
3. Figure out the correct endpoint/parameters

```python
# Example structure (to be filled in)
def add_recipients_to_campaign(self, campaign_id: str, list_key: str) -> bool:
    """Add a mailing list to an existing campaign."""
    url = f"{self.BASE_URL}/updateCampaignRecipients"  # or the correct endpoint
    payload = {
        "campaignid": campaign_id,
        "list_details": json.dumps({str(list_key): []})  # or correct format
    }
    response = requests.post(url, data=payload, headers=headers, timeout=30)
    return response.status_code == 200
```

Then in `create_campaign_draft`:
```python
# Create campaign
result = zoho_client.create_campaign_draft(campaign)

# If created, add recipients
if result and campaign_id:
    zoho_client.add_recipients_to_campaign(campaign_id, default_list_key)
```

## Bottom Line

Test whether campaigns can be created at all (without recipients). If yes, then the problem is specifically with how we're submitting the recipient/list information, and we can fix that in a second step.
