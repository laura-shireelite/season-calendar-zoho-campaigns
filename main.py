#!/usr/bin/env python3
"""
Zoho Gym Campaigns Skill - Main Entry Point

This skill automates email campaign creation in Zoho Campaigns based on your gym's
term calendar stored in Google Sheets. When scheduled to run at the start of each term,
it automatically detects which term is active and creates:

1. A single "Term X YYYY - All Events" campaign listing all upcoming events
2. Individual reminder campaigns scheduled 3 days before each event

Event types are matched to custom email templates for consistent messaging.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Import local modules
from google_sheets_reader import GoogleSheetsReader
from zoho_campaigns_client import ZohoCampaignsClient
from campaign_generator import CampaignGenerator


class TermDetector:
    """Automatically detects which term should be processed based on current date."""

    def __init__(self, events: List[Dict]):
        """
        Initialize with all events from the sheet.

        Args:
            events: List of event dictionaries from Google Sheet
        """
        self.events = events
        self.term_events = self._extract_term_events()

    def _extract_term_events(self) -> List[Dict]:
        """Extract all events with type 'Terms' to identify term boundaries."""
        return [e for e in self.events 
                if 'terms' in e.get('Event Type', '').strip().lower()
                and 'end' not in e.get('Event Name', '').strip().lower()]

    def get_active_term(self, reference_date: Optional[datetime] = None) -> Optional[Dict]:
        """
        Detect which term should be processed.

        The active term is the one whose start date is closest to (but not after)
        the reference date. This handles both scheduled runs at term start and
        manual runs during a term.

        Args:
            reference_date: Date to use for detection (defaults to today)

        Returns:
            Dict with term info including name and start date, or None if no term found
        """
        if reference_date is None:
            reference_date = datetime.now()

        if not self.term_events:
            print("❌ No term events found in sheet. Cannot auto-detect term.")
            return None

        # Find the term event with the closest (not-after) date
        matching_terms = []
        for term_event in self.term_events:
            try:
                term_date = self._parse_date(term_event.get('Date', ''))
                # Include terms that start on or before the reference date
                if term_date <= reference_date:
                    matching_terms.append({
                        'name': term_event.get('Event Name', 'Unknown Term'),
                        'start_date': term_date,
                        'event': term_event
                    })
            except ValueError:
                print(f"⚠️  Skipping term event with invalid date: {term_event.get('Date')}")

        if not matching_terms:
            print("❌ No term starting on or before today found in sheet.")
            return None

        # Return the most recent one (closest to today)
        active_term = max(matching_terms, key=lambda t: t['start_date'])
        return active_term

    def get_next_term(self, reference_date: Optional[datetime] = None) -> Optional[Dict]:
        """
        Get the next upcoming term after the reference date.

        Useful for manual runs during a term when you want to pre-create campaigns
        for the next term.

        Args:
            reference_date: Date to use for detection (defaults to today)

        Returns:
            Dict with term info, or None if no future term exists
        """
        if reference_date is None:
            reference_date = datetime.now()

        if not self.term_events:
            return None

        # Find all terms that start after the reference date
        future_terms = []
        for term_event in self.term_events:
            try:
                term_date = self._parse_date(term_event.get('Date', ''))
                if term_date > reference_date:
                    future_terms.append({
                        'name': term_event.get('Event Name', 'Unknown Term'),
                        'start_date': term_date,
                        'event': term_event
                    })
            except ValueError:
                continue

        if not future_terms:
            return None

        # Return the closest one (soonest to arrive)
        return min(future_terms, key=lambda t: t['start_date'])

    def get_term_events(self, term_info: Dict) -> List[Dict]:
        """
        Get all events for a specific term.

        Events belong to a term from its start date until the next term starts.

        Args:
            term_info: Term info dict from get_next_term() or get_active_term()

        Returns:
            List of event dicts for this term, sorted by date
        """
        if not term_info:
            return []

        term_start = term_info['start_date']

        # Find when the NEXT term starts (the one after this term, not just any other term)
        future_terms = [
            self._parse_date(t.get('Date', ''))
            for t in self.term_events
            if self._parse_date(t.get('Date', '')) > term_start
        ]

        if future_terms:
            next_term_date = min(future_terms)
        else:
            # No future term, use far future date
            next_term_date = datetime(2099, 12, 31)

        # Include all non-term events within this term's date range
        term_events = [
            e for e in self.events
            if (term_start <= self._parse_date(e.get('Date', '')) < next_term_date
                and 'terms' not in e.get('Event Type', '').strip().lower())
        ]

        # Sort by date
        term_events.sort(key=lambda e: self._parse_date(e.get('Date', '')))

        return term_events

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse various date formats from the sheet."""
        if not date_str:
            raise ValueError("Empty date string")

        # Handle date ranges like "Thu 15–Fri 16 Jan" or "Tue 29 Sep–Thu 1 Oct" by extracting the start date
        import re
        if '–' in date_str or '-' in date_str:
            # Extract the first date from ranges like:
            # - "15–16 Jan" (single month)
            # - "Thu 15–Fri 16 Jan" (single month with days)
            # - "Tue 29 Sep–Thu 1 Oct" (two different months)
            # Pattern: optional(StartDay) StartNum optional(StartMonth) – optional(EndDay) EndNum EndMonth
            match = re.search(r'(\w+\s+)?(\d+)(?:\s+(\w+))?(?:–|-)(?:\w+\s+)?(\d+)\s+(\w+)', date_str)
            if match:
                # Reconstruct as "Day DD Mon" (with month) or "DD Mon"
                start_day = match.group(1).strip() if match.group(1) else ""
                start_date = match.group(2)
                # Use the first month if it exists (for ranges like "29 Sep–1 Oct"), else use the end month
                month = match.group(3) if match.group(3) else match.group(5)
                if start_day:
                    date_str = f"{start_day} {start_date} {month}"
                else:
                    date_str = f"{start_date} {month}"

        # Try common formats
        formats = [
            '%Y-%m-%d',      # 2026-06-03
            '%d/%m/%Y',      # 03/06/2026
            '%d/%m/%y',      # 03/06/26
            '%m/%d/%Y',      # 06/03/2026
            '%d-%m-%Y',      # 03-06-2026
            '%a %d %b',      # Tue 27 Jan (day abbr, date, month abbr - no year)
            '%d %b',         # 27 Jan (date, month abbr - no year)
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                # For dates without year (like "Tue 27 Jan"), infer the year
                if parsed.year == 1900:  # strptime defaults to 1900 when year not specified
                    today = datetime.now()
                    parsed = parsed.replace(year=today.year)
                    # If the date is more than 6 months in the past, assume it's next year
                    days_in_past = (today - parsed).days
                    if days_in_past > 180:  # More than 6 months in the past
                        parsed = parsed.replace(year=today.year + 1)
                return parsed
            except ValueError:
                continue

        raise ValueError(f"Could not parse date: {date_str}")


def main():
    """Main skill execution flow."""
    print("\n" + "="*70)
    print("ZOHO GYM CAMPAIGNS SKILL")
    print("="*70)

    # Step 1: Load configuration
    print("\n📋 Loading configuration...")
    google_sheet_url = os.getenv('GOOGLE_SHEET_URL')
    google_service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
    zoho_se_list_key = os.getenv('ZOHO_SE_LIST_KEY')
    zoho_sca_list_key = os.getenv('ZOHO_SCA_LIST_KEY')

    if not all([google_sheet_url, google_service_account_json, zoho_refresh_token]):
        print("❌ Missing required environment variables:")
        print("   - GOOGLE_SHEET_URL")
        print("   - GOOGLE_SERVICE_ACCOUNT_JSON")
        print("   - ZOHO_REFRESH_TOKEN")
        sys.exit(1)

    if not zoho_se_list_key or not zoho_sca_list_key:
        print("⚠️  Warning: Zoho list keys not configured")
        print("   - ZOHO_SE_LIST_KEY")
        print("   - ZOHO_SCA_LIST_KEY")
        print("   Campaign creation may fail without valid list keys")

    # Step 2: Read events from Google Sheet
    print("\n📊 Reading calendar from Google Sheet...")
    try:
        sheets_reader = GoogleSheetsReader(google_sheet_url, google_service_account_json)
        all_events = sheets_reader.fetch_events()
        print(f"✅ Loaded {len(all_events)} events from sheet")
    except Exception as e:
        print(f"❌ Failed to read Google Sheet: {e}")
        sys.exit(1)

    # Step 3: Auto-detect next upcoming term
    print("\n🔍 Finding next upcoming term...")
    detector = TermDetector(all_events)
    today = datetime.now()
    next_term = detector.get_next_term(reference_date=today)

    if not next_term:
        print("❌ Could not find next upcoming term")
        print("   (Make sure your sheet has future 'Terms' events)")
        sys.exit(1)

    term_name = next_term['name']
    term_start = next_term['start_date']
    days_until = (term_start - today).days

    print(f"✅ Will create campaigns for: {term_name}")
    print(f"   (Starts {term_start.strftime('%Y-%m-%d')} — {days_until} days away)")

    # Step 4: Get all events for this term
    print("\n📅 Fetching events for this term...")
    term_events = detector.get_term_events(next_term)

    if not term_events:
        print("⚠️  No events found for this term")
        print("✅ Skill completed with no campaigns to create")
        return

    print(f"✅ Found {len(term_events)} events for {term_name}")

    # Show breakdown of event types
    term_count = sum(1 for e in term_events if 'terms' in e.get('Event Type', '').lower())
    reminder_count = len(term_events) - term_count

    print(f"   Total events: {len(term_events)}")
    print(f"   - Term events (no reminders): {term_count}")
    print(f"   - Events with reminders: {reminder_count}")

    print(f"\n📋 Event breakdown:")
    for event in term_events:
        event_type = event.get('Event Type', '')
        skip_marker = "⏭️" if 'terms' in event_type.lower() else "✅"
        print(f"   {skip_marker} {event.get('Date')}: {event.get('Event Name')} ({event_type})")

    # Step 5: Initialize Zoho client
    print("\n🔌 Connecting to Zoho Campaigns...")
    try:
        zoho_default_list_key = os.getenv('ZOHO_DEFAULT_LIST_KEY')
        zoho_topic_id = os.getenv('ZOHO_TOPIC_ID')

        zoho_client = ZohoCampaignsClient(
            zoho_refresh_token,
            se_list_key=zoho_se_list_key,
            sca_list_key=zoho_sca_list_key,
            default_list_key=zoho_default_list_key,
            topic_id=zoho_topic_id
        )
        print("✅ Connected to Zoho Campaigns")
    except Exception as e:
        print(f"❌ Failed to connect to Zoho: {e}")
        sys.exit(1)

    # Step 6: Generate and create campaigns - gym-specific
    print("\n✍️  Creating campaigns...")

    try:
        # Track all campaigns for scheduling
        campaigns_to_schedule = []

        # Determine which gyms have events in this term
        gyms_in_term = set()
        for event in term_events:
            event_gym = event.get('Gym', 'SE')
            if event_gym == 'Both':
                gyms_in_term.add('SE')
                gyms_in_term.add('SCA')
            else:
                gyms_in_term.add(event_gym)

        print(f"   📍 Events for gyms: {', '.join(sorted(gyms_in_term))}")

        total_reminder_count = 0

        # Create campaigns for each gym
        for gym in sorted(gyms_in_term):
            print(f"\n   🏢 Creating {gym} campaigns...")

            # Filter events for this gym
            gym_events = []
            for event in term_events:
                event_gym = event.get('Gym', 'SE')
                if event_gym == gym or event_gym == 'Both':
                    gym_events.append(event)

            if not gym_events:
                continue

            # Create generator for this gym
            generator = CampaignGenerator(term_name, gym_events, gym=gym)

            # Create term-start campaign
            term_campaign = generator.create_term_start_campaign()
            campaign_id = zoho_client.create_campaign_draft(term_campaign)
            if campaign_id:
                print(f"      ✅ Created term campaign: {term_campaign['name']}")
                # Schedule for day before term starts
                schedule_date = term_start - timedelta(days=1)
                campaigns_to_schedule.append({
                    'id': campaign_id,
                    'name': term_campaign['name'],
                    'send_date': schedule_date
                })

            # Create reminder campaigns
            reminder_campaigns = generator.create_reminder_campaigns()
            created_count = 0
            for reminder in reminder_campaigns:
                campaign_id = zoho_client.create_campaign_draft(reminder)
                if campaign_id:
                    created_count += 1
                    # Extract reminder date from campaign dict
                    reminder_date_str = reminder.get('reminder_date', '')
                    if reminder_date_str:
                        try:
                            schedule_date = datetime.strptime(reminder_date_str, '%Y-%m-%d')
                            campaigns_to_schedule.append({
                                'id': campaign_id,
                                'name': reminder['name'],
                                'send_date': schedule_date
                            })
                        except ValueError:
                            pass

            total_reminder_count += created_count
            print(f"      ✅ Created {created_count}/{len(reminder_campaigns)} {gym} reminder campaigns")

        # Step 7: Schedule all campaigns
        print("\n📅 Scheduling campaigns...")
        scheduled_count = 0
        for campaign in campaigns_to_schedule:
            if zoho_client.schedule_campaign(campaign['id'], campaign['send_date']):
                scheduled_count += 1

        print(f"✅ Scheduled {scheduled_count}/{len(campaigns_to_schedule)} campaigns")

    except Exception as e:
        print(f"❌ Failed to create campaigns: {e}")
        sys.exit(1)

    # Step 8: Summary
    print("\n" + "="*70)
    print("✅ SKILL COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"\nCreated campaigns for: {term_name}")
    print(f"Gyms: {', '.join(sorted(gyms_in_term))}")
    print(f"Total campaigns: {len(campaigns_to_schedule)} ({len(gyms_in_term)} term overview + {total_reminder_count} reminders)")
    print(f"✅ All campaigns have been scheduled for automatic sending!")
    print("\n📌 Next steps (optional):")
    print("   If you want gym logos to display in emails:")
    print("   1. Log into Zoho Campaigns")
    print("   2. For EACH campaign draft:")
    print("      • Open the campaign")
    print("      • Click 'Create Content'")
    print("      • Copy and paste the appropriate master template HTML:")
    print("        - Shire Elite: master_template.html")
    print("        - SCA Allstars: master_template_sca.html")
    print("      • (The gym logo will display automatically)")
    print("\n   Otherwise, campaigns will send with content from the auto-generated HTML.")
    print("\n")


if __name__ == "__main__":
    main()
