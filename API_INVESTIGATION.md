# Zoho Campaigns API Investigation

## The Core Problem
Error 6606 "Selected list/segment doesnot contain any contacts" when creating campaigns, even though:
- ✅ The list "Enrolled Athletes" has 429 contacts (verified in UI)
- ✅ Authentication works (token refreshes successfully)
- ✅ The API endpoint is reachable

## Key Observations

1. **Error persists with AND without list_details parameter**
   - When we include it: Error 6606
   - When we don't include it: Error 6606 (still!)
   - This suggests either:
     - The endpoint ALWAYS requires a list (and returns 6606 if missing)
     - The API has default behavior that tries to use a list
     - Something else entirely

2. **API version mismatch**
   - We're calling: `https://campaigns.zoho.com.au/api/v1.1/createCampaign`
   - Error response shows: `/api/v2/createCampaign`
   - Zoho might have deprecated v1.1 or redirects to v2
   - **Solution**: Try using v2 endpoint directly

3. **Previous successful runs existed**
   - Terminal history showed campaigns WERE created successfully before
   - Something changed (possibly email verification or list structure)

## Parameter Format Variations to Test

### Current attempt (Format 1):
```
list_details: json.dumps({"4913000005118553": []})
Result: {"list_details": "{\"4913000005118553\": []}"}
```

### Alternative Format 2 (now trying):
```
list_details: "4913000005118553"
Result: {"list_details": "4913000005118553"}
```

### Alternative Format 3:
```
list_details: json.dumps(["4913000005118553"])
Result: {"list_details": "[\"4913000005118553\"]"}
```

### Alternative Format 4:
```
"list": "4913000005118553"  # Different parameter name
Result: {"list": "4913000005118553"}
```

## API Endpoint Variations to Try

### Current (v1.1):
```
https://campaigns.zoho.com.au/api/v1.1/createCampaign
```

### Variant 1 (v2.1):
```
https://campaigns.zoho.com.au/api/v2.1/createCampaign
```

### Variant 2 (v2):
```
https://campaigns.zoho.com.au/api/v2/createCampaign
```

### Variant 3 (v3):
```
https://campaigns.zoho.com.au/api/v3/createCampaign
```

## Hypothesis: Two-Step Process Required

Looking at the manual UI flow:
1. Create campaign (name only)
2. Save
3. Go to Recipients section
4. Add list/segments

The API might work the same way:
1. Create campaign without list → returns campaign ID
2. Use separate endpoint to add recipients: `/updateCampaignRecipients` or `/addRecipients`

## Test Cases to Run

```bash
# Test different parameter formats
python3 test_api_formats.py

# Once a format works, update the code and test full skill
python3 test_campaign_simple.py

# Then run full skill
python3 main.py
```

## If No Format Works

Check these resources:
1. **Zoho's official API documentation**: Search for "Zoho Campaigns API v1.1 createCampaign" or "v2"
2. **API Reference for list_details parameter**: Look for exact syntax and accepted values
3. **Segment vs List**: Verify segment IDs (4913000010605024, 4913000010939004) vs list keys
4. **Contact filtering**: Check if API requires contacts to be accessible via specific filter criteria

## Success Indicators

A successful API call will return:
```json
{
  "code": 200,
  "data": {
    "campaignId": "4913000001234567",
    ...
  }
}
```

Or similar with code 201 or `campaignId` present somewhere in response.

## Current Code State

- ✅ Tokens work (refresh succeeds)
- ✅ Endpoint is reachable (getting responses)
- ❌ Parameter format unknown
- ❌ List accessibility unknown

Next blocker: Find correct parameter format for list/recipients in createCampaign endpoint.
