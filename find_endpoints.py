#!/usr/bin/env python3
"""
Guide to finding the correct Zoho Campaigns API endpoints.

Run this if test_minimal_campaign.py shows campaigns CAN be created
without list parameters - then we just need to find the second endpoint.
"""

print("""
╔════════════════════════════════════════════════════════════════════════╗
║       FINDING THE CORRECT ZOHO CAMPAIGNS API ENDPOINTS                 ║
╚════════════════════════════════════════════════════════════════════════╝

If test_minimal_campaign.py succeeded, then we know:
✅ /createCampaign exists and works (doesn't need list at creation)
❌ /createCampaign returns campaign ID
🔄 We need a SECOND endpoint to add recipients

NEXT STEPS TO FIND THE SECOND ENDPOINT:
════════════════════════════════════════════════════════════════════════

1. CHECK ZOHO'S API DOCUMENTATION
   Search for:
   - "Zoho Campaigns API create campaign with recipients"
   - "Zoho Campaigns API v1.1 add recipients"
   - "Zoho Campaigns API update campaign recipients"
   - Look for endpoints like:
     * /addRecipients
     * /addCampaignRecipient
     * /updateCampaignRecipient
     * /setCampaignRecipient

2. COMMON ZOHO API PATTERNS
   Based on Zoho's standard REST API design, try these URLs:

   Pattern A - Add Recipients:
   └─ https://campaigns.zoho.com.au/api/v1.1/addRecipients
      Parameters: campaignid={id}, listkey={key}

   Pattern B - Update Recipients:
   └─ https://campaigns.zoho.com.au/api/v1.1/updateRecipient
      Parameters: campaignid={id}, listkey={key}

   Pattern C - Nested endpoint:
   └─ https://campaigns.zoho.com.au/api/v1.1/campaigns/{campaignid}/addrecipient
      Parameters: listkey={key}

   Pattern D - Campaign settings:
   └─ https://campaigns.zoho.com.au/api/v1.1/updateCampaignSettings
      Parameters: campaignid={id}, listdetails={json}

3. LOOK AT WHAT THE UI DOES
   When you manually create campaigns in Zoho:
   1. POST to /createCampaign → returns campaign ID
   2. Redirect to edit page: /campaigns/{id}/edit or similar
   3. POST to add recipients with campaign ID + list key

   The API probably follows the same steps.

4. TEST THE ENDPOINTS
   Once you have a campaign ID from createCampaign, try:

   ```bash
   curl -X POST https://campaigns.zoho.com.au/api/v1.1/addRecipients \\
     -H "Authorization: Zoho-oauthtoken {token}" \\
     -d "campaignid=CAMPAIGN_ID_HERE" \\
     -d "listkey=4913000005118553"
   ```

   Or with the Python client:
   ```python
   payload = {
       "campaignid": campaign_id,
       "listkey": "4913000005118553"
   }
   response = requests.post(
       "https://campaigns.zoho.com.au/api/v1.1/addRecipients",
       data=payload,
       headers=headers
   )
   ```

5. KEY INFORMATION FROM EARLIER FINDINGS
   ✓ API responds with /api/v2/createCampaign (might need v2 endpoints)
   ✓ listkey parameter works for list management
   ✓ Segments have separate IDs (4913000010605024, 4913000010939004)
   ✓ The "Enrolled Athletes" list (4913000005118553) has 429 contacts

═══════════════════════════════════════════════════════════════════════════

IF YOU FIND THE CORRECT ENDPOINT:
════════════════════════════════════════════════════════════════════════════

Send the endpoint URL + parameters to update the code:

```python
# After campaign creation succeeds, add recipients in a second call:
def add_recipients_to_campaign(self, campaign_id, list_key):
    url = f"{self.BASE_URL}/[CORRECT_ENDPOINT_HERE]"
    payload = {
        "campaignid": campaign_id,
        "listkey": list_key,
        # Add any other required parameters
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.status_code == 200
```

═══════════════════════════════════════════════════════════════════════════

EXPECTED SUCCESS RESPONSE:
```json
{
  "code": 200,
  "message": "Recipient added successfully"
}
```

═══════════════════════════════════════════════════════════════════════════
""")
