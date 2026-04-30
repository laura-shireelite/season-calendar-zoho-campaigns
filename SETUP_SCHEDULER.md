# One-Time Setup: Automatic Scheduling

After your first manual run, set up **one scheduler** and it runs automatically forever.

---

## Option 1: Mac/Linux - Cron (Easiest)

### Setup (One time)
```bash
crontab -e
```

Add these three lines:
```
0 8 15 5 * /path/to/zoho-gym-campaigns/run.sh >> /path/to/zoho-gym-campaigns/logs.txt 2>&1
0 8 30 9 * /path/to/zoho-gym-campaigns/run.sh >> /path/to/zoho-gym-campaigns/logs.txt 2>&1
0 8 15 1 * /path/to/zoho-gym-campaigns/run.sh >> /path/to/zoho-gym-campaigns/logs.txt 2>&1
```

Replace `/path/to/zoho-gym-campaigns` with actual path (e.g., `/Users/laura/Projects/zoho-gym-campaigns`)

### What This Does
- May 15 @ 8am → Creates Term 3 campaigns
- Sept 30 @ 8am → Creates Term 4 campaigns  
- Jan 15 @ 8am → Creates Term 1 campaigns

### That's It!
Every year, at those exact times, it runs automatically. No manual intervention needed.

---

## Option 2: Mac - LaunchAgent (GUI Method)

Create file: `~/Library/LaunchAgents/com.shireelite.zoho-campaigns.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.shireelite.zoho-campaigns</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/zoho-gym-campaigns/run.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <!-- May 15 @ 8am -->
        <dict>
            <key>Month</key>
            <integer>5</integer>
            <key>Day</key>
            <integer>15</integer>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- Sept 30 @ 8am -->
        <dict>
            <key>Month</key>
            <integer>9</integer>
            <key>Day</key>
            <integer>30</integer>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- Jan 15 @ 8am -->
        <dict>
            <key>Month</key>
            <integer>1</integer>
            <key>Day</key>
            <integer>15</integer>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>StandardOutPath</key>
    <string>/path/to/zoho-gym-campaigns/logs.txt</string>
    <key>StandardErrorPath</key>
    <string>/path/to/zoho-gym-campaigns/errors.txt</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.shireelite.zoho-campaigns.plist
```

---

## Option 3: Windows - Task Scheduler

### Create Task
1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Zoho Gym Campaigns"
4. Trigger: Set to run on May 15, Sept 30, Jan 15 @ 8am
5. Action: Start a program
   - Program: `python.exe` or `python3.exe`
   - Arguments: `C:\path\to\run.sh` (or create .bat file)

### Or use PowerShell
```powershell
# Run as Administrator
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\path\to\main.py"
$trigger = New-ScheduledTaskTrigger -At "08:00AM" -On "05/15/2026" -RepetitionInterval (New-TimeSpan -Days 365*3) -RepetitionDuration (New-TimeSpan -Days 9999)
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ZohoGymCampaigns"
```

---

## After Setup

| When | What You Do |
|------|------------|
| May 15, 8am | ✅ Nothing! Skill runs automatically |
| Check Zoho | ✅ See Term 3 campaigns created |
| Customize | ✅ Edit templates, set send dates |
| Send | ✅ Send to your audience |
| Sept 30, 8am | ✅ Nothing! Skill runs automatically |
| Check Zoho | ✅ See Term 4 campaigns created |
| ... | ... |

**That's it.** Once scheduled, it runs forever. No manual runs ever needed.

---

## Monitoring

Cron version logs to: `/path/to/zoho-gym-campaigns/logs.txt`

Check if it ran:
```bash
tail -f /path/to/zoho-gym-campaigns/logs.txt
```

---

## Summary

- **First time:** Run manually: `python3 main.py`
- **Review:** Look at drafts in Zoho
- **One-time setup:** Add 3 lines to crontab (takes 1 minute)
- **Forever after:** Skill runs automatically, no manual intervention needed

**Choose cron (Option 1) - it's the simplest!** 🚀
