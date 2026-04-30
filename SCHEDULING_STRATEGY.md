# Scheduling Strategy: Next-Term-Only Approach

## The Strategy

**Always target the next upcoming term, run at fixed mid-to-late term dates.**

This is the simplest, most reliable approach:
- ✅ No duplicates (runs exactly once per term)
- ✅ No manual runs ever
- ✅ Simple logic (find next term, create campaigns)
- ✅ Predictable timing
- ✅ Time to review campaigns before term starts

---

## How It Works

**The skill always does this:**
1. Find the next upcoming term (after today)
2. Get all events for that term
3. Create campaigns for those events
4. Done!

**Example:**
- Today: April 29, 2026 (in Term 2)
- Next term: Term 3 (starts July 10)
- Skill creates: Term 3 campaigns
- Notice time: 72 days to review and customize before Term 3

---

## Recommended Schedule

Run the skill at these **fixed, safe dates** (mid-to-late in each current term):

### For Your Gym's Schedule

| Run Date | Current Term | Targets | Notice Time |
|----------|-------------|---------|------------|
| **May 15, 2026** | Term 2 (Apr 2 - Jul 9) | Term 3 (Jul 10) | 56 days ✅ |
| **September 30, 2026** | Term 3 (Jul 10 - Oct 14) | Term 4 (Oct 15) | 15 days ✅ |
| **January 15, 2027** | Term 4 (Oct 15 - Jan 24) | Term 1 (Jan 25) | 10 days ✅ |

---

## Setting Up the Schedule

### Option 1: Cron (Linux/Mac)
```bash
# Edit your crontab
crontab -e

# Add these lines:
0 8 15 5 * /path/to/zoho-gym-campaigns/run.sh   # May 15 @ 8am
0 8 30 9 * /path/to/zoho-gym-campaigns/run.sh   # Sept 30 @ 8am
0 8 15 1 * /path/to/zoho-gym-campaigns/run.sh   # Jan 15 @ 8am
```

Create `run.sh`:
```bash
#!/bin/bash
cd /path/to/zoho-gym-campaigns
source config.txt
python3 main.py
```

### Option 2: Cowork Scheduled Tasks
```bash
# Use the Cowork schedule skill to set up recurring tasks
# Schedule for: May 15, Sept 30, Jan 15 at 8:00 AM
```

### Option 3: System Scheduler (Windows)
Use Task Scheduler to run `python3 main.py` at the fixed dates above.

---

## Why This Works Better

### Old Approach (Complex)
- Try to detect current vs mid-term
- Use 7-day threshold logic
- Could still run multiple times
- Risk of duplicates if run manually

### New Approach (Simple) ✅
```
Run at May 15? → Creates for Term 3
Run at Sept 30? → Creates for Term 4
Run at Jan 15? → Creates for Term 1

Never run manually. Always targets next term. No duplicates.
```

---

## Examples

### Scenario 1: First Run (May 15, 2026)
```
Today: May 15, 2026
Current Term: Term 2 (started Apr 2)
Next Term: Term 3 (starts Jul 10)
Campaigns Created: Term 3
Notice: 56 days before Term 3 starts
Action: Review & customize in Zoho, then send
```

### Scenario 2: Second Run (Sept 30, 2026)
```
Today: Sept 30, 2026
Current Term: Term 3 (started Jul 10)
Next Term: Term 4 (starts Oct 15)
Campaigns Created: Term 4
Notice: 15 days before Term 4 starts
Action: Review & customize in Zoho, then send
```

### Scenario 3: Third Run (Jan 15, 2027)
```
Today: Jan 15, 2027
Current Term: Term 4 (started Oct 15)
Next Term: Term 1 (starts Jan 25)
Campaigns Created: Term 1
Notice: 10 days before Term 1 starts
Action: Review & customize in Zoho, then send
```

---

## Safe Scheduling Rules

✅ **DO:**
- Run at the same time every term (predictable)
- Run mid-to-late in current term (gives advance notice)
- Let the scheduler run it automatically (no manual runs)
- Add new term dates to your sheet before scheduled run date

❌ **DON'T:**
- Run manually (defeats the purpose)
- Run at term start or early in term (schedules create next term)
- Change the schedule dates mid-year
- Run multiple times per term (creates duplicates)

---

## Updating Your Schedule

As new terms are added to your sheet:

1. Add the term to your Google Sheet (e.g., Term 5 starting Jan 20, 2027)
2. Next scheduled run will automatically include it
3. No code changes needed!

Example: If you add "Term 5" to your sheet with date "Tue 25 Jan 2027":
- May 15 run → targets Term 3 ✓
- Sept 30 run → targets Term 4 ✓
- Jan 15 run → targets Term 5 ✓

---

## Key Differences from Manual Runs

| Aspect | Scheduled | Manual |
|--------|-----------|--------|
| Duplicates | ❌ None | ⚠️ Possible |
| Complexity | ✅ Simple | ❌ Complex |
| Reliability | ✅ Automatic | ❌ Depends on you |
| Predictability | ✅ Fixed dates | ❌ Random |
| Risk | ✅ Low | ❌ High |

---

## Troubleshooting

### "No upcoming term found"
**Cause:** Next term not added to sheet yet
**Fix:** Add the upcoming term to your Google Sheet with Event Type = "Terms"

### "Creates wrong term"
**Cause:** Schedule date is wrong or changed
**Fix:** Verify scheduled dates match your term calendar

### "Ran multiple times in one day"
**Cause:** Scheduler misconfigured
**Fix:** Check cron/task scheduler settings, ensure exactly one run per date

---

## Summary

This strategy is:
- **Simple:** Find next term, create campaigns, done
- **Safe:** No duplicates, no manual errors
- **Reliable:** Runs automatically at fixed times
- **Scalable:** Works with any number of future terms

**Set it and forget it.** 🚀
