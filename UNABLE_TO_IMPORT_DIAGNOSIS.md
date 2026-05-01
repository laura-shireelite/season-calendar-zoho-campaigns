# Zoho UNABLE_TO_IMPORT Error - Root Cause Analysis & Fix

## Problem Summary
One campaign was consistently failing with `UNABLE_TO_IMPORT` error in Zoho:
- **Campaign**: "Term 3 ends - Recreational programs and Gym Closure - 3 Day Reminder"
- **Error**: Zoho returned UNABLE_TO_IMPORT but provided no error details
- **Status**: File created, pushed to GitHub, URL accessible, HTML valid
- **File Example**: `reminder-term-3-ends-recreational-programs-and-gym-closure--20260922.html`

## Root Cause Discovered

### Issue 1: Gym Closure Event Names Include Holiday Suffixes
The Google Sheet contains gym closure events with full holiday period information in the name:
- **Original name**: "Gym Closure - Wk2 Spring School Hols"
- **Expected**: Just "Gym Closure"

When combined with term end events, this created very long campaign names:
- **Before fix**: "Term 3 ends - Recreational programs and Gym Closure - Wk2 Spring School Hols"
- **Length**: 76 characters (exceeds practical limits)

### Issue 2: URL Truncation Created Filename Mismatch
When the campaign name was too long:
1. Full filename would be 95 characters
2. Full URL would be 171 characters (exceeds 150 char limit)
3. Truncation function would aggressive shorten it
4. Result: `reminder-term-3-ends-recreational-programs-and-gym-closure--20260922.html` (double hyphen)
5. HTML h1 still contained the full "Wk2 Spring School Hols" part

**Result of mismatch**:
- Filename: `reminder-term-3-ends-recreational-programs-and-gym-closure--20260922.html` (truncated)
- H1 in HTML: `"Term 3 ends - Recreational programs and Gym Closure - Wk2 Spring School Hols"` (full)
- Zoho likely rejected due to content mismatch or URL formatting issue

### Issue 3: Double Hyphen in URL
The truncation process left a double hyphen (`--`) in the filename:
- After rstrip('-'): `reminder-term-3-ends-recreational-programs-and-gym-closure-`
- After adding '-': `reminder-term-3-ends-recreational-programs-and-gym-closure--20260922.html`

The double hyphen might have triggered validation issues in Zoho's URL parser.

## Solution Implemented

### Fix: Strip Holiday Suffixes from Gym Closure Names
In `_build_term_end_closure_campaign()`, added regex to remove holiday period information:

```python
closure_base = re.sub(r'\s*-\s*(wk\d+|week\d+|spring|winter|summer|autumn|fall|hols|holidays|school\s+hols).*', 
                      '', closure_base, flags=re.IGNORECASE)
```

### Impact of Fix
- Campaign name: 76 → 51 characters (25 char reduction)
- URL length: 171 → 148 characters (fits within 150 limit)
- Filename: No truncation needed
- Double hyphen: Eliminated
- H1 and filename: Now in sync

### Example
**Before**:
```
Campaign name: "Term 3 ends - Recreational programs and Gym Closure - Wk2 Spring School Hols"
Filename: reminder-term-3-ends-recreational-programs-and-gym-closure--20260922.html (truncated)
H1: "Term 3 ends - Recreational programs and Gym Closure - Wk2 Spring School Hols" (full)
URL length: 171 (exceeds limit)
```

**After**:
```
Campaign name: "Term 3 ends - Recreational programs and Gym Closure"
Filename: reminder-term-3-ends-recreational-programs-and-gym-closure-20260922.html (no truncation)
H1: "Term 3 ends - Recreational programs and Gym Closure" (matches filename)
URL length: 148 (within limit)
```

## Testing

To verify the fix resolves the issue:

1. Run the skill: `bash RUN_TEST.sh`
2. Check that "Term 3 ends - Recreational programs and Gym Closure - 3 Day Reminder" campaign is created
3. Verify all campaigns import successfully in Zoho
4. Check that no double-hyphen filenames are created

## Related Files Modified
- `campaign_generator.py`: Added holiday suffix stripping in `_build_term_end_closure_campaign()`
- `campaign_generator.py`: Improved truncation logic with additional safety check

## Note on Other Holiday Events
The fix only affects **combined Term+Closure campaigns**. Holiday clinic grouping (e.g., "Holiday Clinics - Spring Hols") continues to work as intended since those are handled separately.
