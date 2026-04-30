---
name: zoho-gym-campaigns
description: |
  Create Zoho Campaigns email marketing drafts automatically for your gym's term calendar. This skill reads your key calendar dates from a Google Sheet and creates two types of campaign drafts in Zoho Campaigns:
  
  1. **Term-start campaigns**: A single "Term X YYYY - All Events" campaign listing all upcoming events for the term
  2. **Reminder campaigns**: Individual campaigns scheduled to be created 3 days before each event
  
  Templates are customized by event type (promotions, class launches, member events, etc.). The skill can be scheduled to run on a set calendar (e.g., at the start of each gym term) or triggered manually.
  
  Use this skill when you want to automate campaign creation for recurring gym events, ensure consistent messaging across your term calendar, or save time creating multiple related campaigns at once.
---

# Zoho Gym Campaigns Skill

## What This Skill Does

This skill bridges your gym's calendar planning (stored in Google Sheets) with your email marketing platform (Zoho Campaigns). It automates the creation of campaign **drafts** — not sent emails, just drafts ready for you to review and tweak in Zoho before sending.

### Workflow

1. **At term start**: Creates a single campaign draft titled "Term X YYYY - All Events" that gives members an overview of everything coming up
2. **Throughout the term**: Creates reminder campaign drafts 3 days before each event
3. **Customization**: Different event types (promotions, classes, member events, etc.) get different email templates

---

## Setup & Configuration

Before the skill can run, you need to:

### 1. Google Sheets Setup
- Your calendar spreadsheet with columns: **Date**, **Gym** (SE/SCA/Both), **Event Name**, **Event Type**, and a reference to detailed info tabs
- Make the sheet shareable (link access is fine)
- The skill will read this sheet to pull upcoming events

### 2. Zoho Campaigns Connection
- **Create a Zoho API token**: Go to Zoho Campaigns → Settings → API Keys, generate a token with campaign draft creation permissions
- **Provide the token**: When running the skill, you'll paste this token so it can create drafts in your account
- **Identify your audience list**: Zoho Campaigns will ask which email list(s) to target for each campaign (you can set this per campaign or use a default)

### 3. Calendar Planning
- Decide which term you want campaigns for (e.g., "Term 2 2026")
- Ensure all key events for that term are listed in your Google Sheet with:
  - Event dates
  - Event names
  - Event types (this determines the email template used)
  - Which gym(s) it applies to

---

## How to Run the Skill

### Option A: Manual (On-Demand)
Ask Claude: *"Create Zoho campaign drafts for Term 2 2026"*

The skill will:
- Read your calendar sheet
- Create the term-start campaign
- Calculate 3-days-before dates for each event
- Create reminder campaign drafts
- Show you a summary of what was created

### Option B: Scheduled
Set up a scheduled task to run the skill automatically at the start of each term. The skill can be configured to run on specific dates.

---

## Campaign Naming & Structure

All campaigns follow human-readable naming:
- **Term-start**: `"Term 2 2026 - All Events"`
- **Reminders**: `"[Event Name] - 3 Day Reminder"`

Example:
- "Yoga Challenge - 3 Day Reminder"
- "New Member Special - 3 Day Reminder"

---

## Email Templates by Event Type

The skill automatically selects email templates based on your event type. You'll configure these templates during setup:

### Template Categories
The skill uses these email templates based on your event types:

- **Events** (social events, competitions, workshops) — exciting, engaging tone; encourages attendance
- **Terms** (new term start, term information) — informational, clear structure of term schedule and important dates
- **Gym Closures** (facility closures, holiday breaks) — important notification style; clear about dates and impact
- **Catch Ups** (team meetings, check-ins) — professional, friendly; clear timing and purpose
- **Fees** (payment announcements, fee reminders) — clear, direct; includes amounts and due dates
- **Cheer Clinics** (cheerleading events, clinics) — energetic, exciting; highlights skills and experience levels
- **Other important dates** (flexible catchall) — professional informational tone; adaptable to context

Each template includes:
- **Subject line**: Dynamic (includes event name & date)
- **Email body**: Pre-written copy tailored to the event type, with event details filled in
- **Call-to-action**: Varies by type ("Sign up", "Mark your calendar", "Pay by X date", "Learn more", etc.)

### Customizing Templates
After the skill creates your first batch of campaigns, you can:
- Edit the templates in Zoho
- Ask the skill to adjust templates for specific event types
- Fine-tune subject lines, tone, or calls-to-action
- Test different approaches and iterate

---

## What the Skill Creates in Zoho Campaigns

### Campaign Draft Fields (attempted)
The skill will populate as many of these as Zoho Campaigns' API allows:

- ✅ **Campaign name** (human-readable, formatted per above)
- ✅ **Subject line** (template-based, includes event details)
- ✅ **Email body** (template-based HTML, personalized with event info)
- ✅ **From name** (e.g., "[Your Gym Name]")
- ✅ **Target audience/list** (specified per campaign or default list)
- ⚠️ **Send schedule** (may require manual setup in Zoho — skill will note the intended send date in draft)

**Note**: If the API can't set certain fields (like exact send time), you can manually adjust in Zoho before sending. The skill's job is to handle the content creation and basic setup.

---

## Example Workflow

**Your Google Sheet has**:
- June 3: Term 2 starts (Terms) — both gyms
- June 10: Cheer Clinic - Level 1 (Cheer Clinics) — both gyms
- June 15: Membership fees due (Fees) — both gyms
- June 20: Mid-term check-in (Catch Ups) — both gyms
- June 30: Special Event - Showcase (Events) — SE gym only
- July 4-5: Gym Closure (Gym Closures) — both gyms

**The skill will create**:

1. **At term start** (June 1):
   - Campaign draft: "Term 2 2026 - All Events"
   - Body lists all six events with dates, locations, and descriptions

2. **Three days before each event**:
   - June 7: "Term 2 starts - 3 Day Reminder" (Terms template)
   - June 7: "Cheer Clinic - Level 1 - 3 Day Reminder" (Cheer Clinics template)
   - June 12: "Membership fees due - 3 Day Reminder" (Fees template)
   - June 17: "Mid-term check-in - 3 Day Reminder" (Catch Ups template)
   - June 27: "Special Event - Showcase - 3 Day Reminder" (Events template, SE gym only)
   - July 1: "Gym Closure - 3 Day Reminder" (Gym Closures template)

Each uses the right template for its type, auto-fills the event date/name, and targets the correct gym(s).

---

## Limitations & Notes

- **Drafts only**: The skill creates unsent drafts. You review in Zoho before sending.
- **3-day reminder timing**: Reminders are scheduled for 3 days before events. Event types may adjust this (you can customize during iteration).
- **Google Sheet format**: Your sheet must be consistently formatted. If columns shift or data is missing, the skill will flag it.
- **Zoho API limits**: Zoho Campaigns has rate limits on API calls. Creating many campaigns in quick succession may hit limits (the skill handles throttling).
- **Event type must exist**: The skill needs your event types to match configured templates. Unknown event types will get a default template.

---

## Iterating on the Skill

This skill is designed to be **refined with use**. After your first run:

1. **Review the drafts** in Zoho — do they look good? Are templates right?
2. **Give feedback**: "The subject lines are too long" or "I want the reminders to be 5 days before, not 7" or "Add a discount code to all promotion templates"
3. **Refine templates**: Edit email templates in Zoho, or ask the skill to update them
4. **Adjust timing**: Change reminder timing per event type
5. **Rerun**: The skill creates the next batch with improvements

You can iterate as many times as you want until the campaigns are *exactly* how you want them.

---

## Troubleshooting

**"Skill can't access my Google Sheet"**
- Ensure the sheet is shared (anyone with the link can view)
- Check that you provided the correct sheet URL
- Verify the tab name matches (e.g., "Term 2 2026" vs "term-2-2026")

**"Zoho token is invalid"**
- Regenerate your API token in Zoho Campaigns
- Ensure the token has "Draft Creation" permissions
- Paste the new token when prompted

**"Some campaigns weren't created"**
- Check Zoho API logs for throttling or errors
- Verify event type names match your configured templates
- Check for missing data (blank dates, event names, etc.) in the sheet

**"I want to change X about the campaigns"**
- Let me know what needs adjusting, and we'll iterate on the skill together
- Common tweaks: template wording, timing, event type names, audience targeting

---

## Support & Iteration

This is a living skill — **tell me what works, what doesn't, and what you want to improve**, and I'll refine it. Nothing is locked in. We'll iterate together until it's perfect for your gym's workflow.
