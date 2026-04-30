"""
Campaign Generator Module

Builds campaign content for Zoho Campaigns including subject lines,
email bodies, and metadata. Handles both term-start overviews and
individual reminder campaigns.

With GitHub Pages hosting: Saves HTML files to docs/campaigns/ and
returns public URLs for content_url parameter in Zoho API.
"""

import os
import unicodedata
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote
from brand_templates import ShireEliteTemplate


# GitHub Pages configuration
# Update these for your GitHub setup
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'your-username')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'zoho-gym-campaigns')
GITHUB_PAGES_BASE_URL = f"https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}/campaigns"

# Local file paths
CAMPAIGNS_DIR = os.path.join(os.path.dirname(__file__), 'docs', 'campaigns')


def ensure_campaigns_dir():
    """Create docs/campaigns directory if it doesn't exist."""
    os.makedirs(CAMPAIGNS_DIR, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for use in URLs.

    Replaces non-ASCII characters with ASCII equivalents:
    - En-dash (–) → hyphen (-)
    - Em-dash (—) → hyphen (-)
    - Accented characters → unaccented equivalents
    - Other non-ASCII → removed

    Args:
        filename: Original filename string (typically pre-processed: lowercased, spaces→hyphens)

    Returns:
        URL-safe filename with only ASCII characters
    """
    # Step 1: Replace smart quotes and dashes with ASCII equivalents BEFORE normalization
    result = filename
    result = result.replace('–', '-')      # en-dash
    result = result.replace('—', '-')      # em-dash
    result = result.replace('−', '-')      # minus sign
    result = result.replace(''', "'")      # left single quote
    result = result.replace(''', "'")      # right single quote
    result = result.replace('"', '"')      # left double quote
    result = result.replace('"', '"')      # right double quote

    # Step 2: Normalize to NFD (decomposed form) to separate accents from base characters
    normalized = unicodedata.normalize('NFD', result)

    # Step 3: Remove combining characters (accents/diacritics)
    ascii_only = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'  # Mn = Mark, Nonspacing (accents)
    )

    # Step 4: Keep only ASCII alphanumeric, hyphens, underscores, and dots
    safe = ''
    for char in ascii_only:
        if ord(char) < 128 and (char.isalnum() or char in '-_.'):
            safe += char
        # Skip any remaining non-ASCII characters

    # Step 5: Clean up any doubled hyphens that might have resulted
    while '--' in safe:
        safe = safe.replace('--', '-')

    return safe


class CampaignGenerator:
    """Generates campaign content for a gym term."""

    def __init__(self, term_name: str, events: List[Dict], base_url: Optional[str] = None):
        """
        Initialize the generator.

        Args:
            term_name: Name of the term (e.g., "Term 2 2026")
            events: List of event dictionaries for this term (sorted by date)
            base_url: Optional override for GitHub Pages base URL (defaults to env var)
        """
        self.term_name = term_name
        self.events = events
        self.base_url = base_url or GITHUB_PAGES_BASE_URL
        ensure_campaigns_dir()

    def _save_html_and_get_url(self, html_content: str, filename: str) -> str:
        """
        Save HTML content to file and return the GitHub Pages URL.

        Args:
            html_content: HTML string to save
            filename: Filename (without path) to save as

        Returns:
            Public GitHub Pages URL
        """
        file_path = os.path.join(CAMPAIGNS_DIR, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Return the public URL with proper URL encoding
            # quote() keeps ASCII alphanumeric and certain safe chars, encodes the rest
            encoded_filename = quote(filename, safe='')
            url = f"{self.base_url}/{encoded_filename}"
            print(f"    💾 Saved HTML: {filename}")
            print(f"    🌐 Public URL: {url}")
            return url
        except Exception as e:
            print(f"    ❌ Failed to save HTML file: {e}")
            raise

    def create_term_start_campaign(self) -> Dict:
        """
        Create the term-start campaign listing all events (excluding holiday clinics).

        Returns:
            Campaign dict ready for Zoho API with content_url pointing to hosted HTML
        """
        if not self.events:
            return {}

        campaign_name = f"{self.term_name} - What's Coming Up"

        # Exclude holiday clinic events from the overview
        # (they get their own grouped campaign)
        non_clinic_events = [
            e for e in self.events
            if not self._is_holiday_clinic(e.get('Event Name', ''))
        ]

        # Build the event list for the email body
        if non_clinic_events:
            events_html = "<ul>"
            for event in non_clinic_events:
                events_html += f"<li>{event.get('Event Name', '')}</li>"
            events_html += "</ul>"
        else:
            events_html = "<p>Check back soon for event details!</p>"

        # Get term dates
        term_start = self.events[0].get('Date', 'TBA') if self.events else 'TBA'
        term_end = "TBA"
        for event in self.events:
            if 'end' in event.get('Event Name', '').lower() and 'terms' in event.get('Event Type', '').lower():
                term_end = event.get('Date', 'TBA')

        # Build email body content
        subject = f"📅 {self.term_name} – What's Coming Up"

        main_content = f"""<p><strong>Term Runs:</strong> {term_start} to {term_end}</p>
<p><strong>Upcoming events:</strong></p>
{events_html}
<p>You'll receive reminders 3 days before each event. Holiday clinics will be announced separately!</p>
<p>Thanks!<br>Your Gym Team</p>"""

        # Render using brand template
        html_body = ShireEliteTemplate.render(
            event_title=f"📅 {self.term_name}",
            main_content=main_content,
            button_text="Athletes Page",
            button_url="https://www.shireelite.com.au/athletes",
            logo_url="https://campaigns.zoho.com.au/campaigns/org7001313022/imagebannerAction.do?imgName=Campaigns_email_header_logo.png&folderId=127892000000155021"
        )

        # Save HTML and get public URL
        safe_term_name = sanitize_filename(self.term_name.lower().replace(' ', '-'))
        filename = f"term-overview-{safe_term_name}.html"
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'term_overview',
            'target_gym': 'Shire Elite'
        }

    def create_reminder_campaigns(self) -> List[Dict]:
        """
        Create reminder campaigns for 3 days before each event.

        Handles:
        - Regular events (individual reminders)
        - Gym closures (individual reminders)
        - Holiday clinics (grouped by holiday period)

        Returns:
            List of campaign dicts ready for Zoho API
        """
        campaigns = []
        processed_events = set()  # Track which events we've processed
        holiday_clinic_groups = {}  # Group clinics by holiday period

        print(f"    📊 Processing {len(self.events)} events for reminders...")

        # First pass: group holiday clinics by holiday period
        for event in self.events:
            event_name = event.get('Event Name', '')
            if self._is_holiday_clinic(event_name):
                holiday_period = self._extract_holiday_period(event_name)
                if holiday_period not in holiday_clinic_groups:
                    holiday_clinic_groups[holiday_period] = []
                holiday_clinic_groups[holiday_period].append(event)

        # Second pass: create campaigns
        for idx, event in enumerate(self.events):
            event_name = event.get('Event Name', '')
            event_type = event.get('Event Type', '').strip().lower()
            event_date_str = event.get('Date', '')
            event_id = f"{event_name}_{event_date_str}"  # Unique identifier

            # Skip if already processed (as part of a group)
            if event_id in processed_events:
                continue

            # Skip term events (they don't get reminders)
            if 'terms' in event_type:
                print(f"    ⏭️  Event {idx+1}: Skipping '{event_name}' (term event)")
                continue

            try:
                event_date = self._parse_date(event_date_str)
            except ValueError as e:
                print(f"    ❌ Event {idx+1}: Skipping '{event_name}' (invalid date '{event_date_str}')")
                continue

            # Calculate reminder date (3 days before)
            reminder_date = event_date - timedelta(days=3)

            # Handle holiday clinics as a group
            if self._is_holiday_clinic(event_name):
                holiday_period = self._extract_holiday_period(event_name)
                if holiday_period in holiday_clinic_groups:
                    # Create one campaign for all clinics in this period
                    campaign = self._build_holiday_clinic_campaign(
                        holiday_period,
                        holiday_clinic_groups[holiday_period],
                        reminder_date
                    )
                    if campaign:
                        campaigns.append(campaign)
                        for clinic_event in holiday_clinic_groups[holiday_period]:
                            processed_events.add(f"{clinic_event.get('Event Name', '')}{clinic_event.get('Date', '')}")
                        print(f"    ✅ Grouped: '{holiday_period}' clinics → reminder on {reminder_date.strftime('%Y-%m-%d')}")
                    # Remove from dict so we don't process it again
                    del holiday_clinic_groups[holiday_period]
            else:
                # Regular event or gym closure
                campaign = self._build_reminder_campaign(event, reminder_date)
                if campaign:
                    campaigns.append(campaign)
                    processed_events.add(event_id)
                    print(f"    ✅ Event {idx+1}: '{event_name}' → reminder on {reminder_date.strftime('%Y-%m-%d')}")

        print(f"    📋 Created {len(campaigns)} reminder campaigns from {len(self.events)} events")
        return campaigns

    def _is_holiday_clinic(self, event_name: str) -> bool:
        """Check if an event is a holiday clinic (e.g., 'Cheer Clinics – Winter Hols Wk 2')."""
        lower_name = event_name.lower()
        return 'cheer clinics' in lower_name and ('hols' in lower_name or 'holidays' in lower_name)

    def _extract_holiday_period(self, event_name: str) -> str:
        """Extract the holiday period name from an event (e.g., 'Winter Hols' from 'Cheer Clinics – Winter Hols Wk 2')."""
        # Find the holiday period between dashes
        import re
        match = re.search(r'–\s*(.+?)\s+Wk', event_name)
        if match:
            return match.group(1).strip()
        return event_name

    def _build_reminder_campaign(self, event: Dict, reminder_date: datetime) -> Dict:
        """Build a single reminder campaign."""
        event_name = event.get('Event Name', '')
        event_type = event.get('Event Type', '')
        event_date_str = event.get('Date', '')
        gym = event.get('Gym', 'All')

        # Campaign name
        campaign_name = f"{event_name} - 3 Day Reminder"

        # Build email content based on event type
        subject = f"⏰ {event_name} – 3 Day Reminder"
        main_content = self._build_event_content(event_type, event_name, event_date_str, event)

        # Render using brand template
        html_body = ShireEliteTemplate.render(
            event_title=event_name,
            main_content=main_content,
            button_text="Event Details",
            button_url="https://www.shireelite.com.au/athletes",
            logo_url="https://campaigns.zoho.com.au/campaigns/org7001313022/imagebannerAction.do?imgName=Campaigns_email_header_logo.png&folderId=127892000000155021"
        )

        # Save HTML and get public URL
        safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
        filename = f"reminder-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': event_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': gym
        }

    def _build_holiday_clinic_campaign(self, holiday_period: str, clinic_events: List[Dict], reminder_date: datetime) -> Dict:
        """Build a campaign for grouped holiday clinics (e.g., all Winter Hols clinics together)."""
        # Combine dates from all clinic events (for email body)
        clinic_dates = [e.get('Date', '') for e in clinic_events]
        combined_dates = " / ".join(clinic_dates)

        # Simplified campaign name (for Zoho API - no special characters)
        campaign_name = f"Holiday Clinics - {holiday_period}"

        # Build email content for holiday clinics
        subject = f"🎉 Cheer Clinics – {holiday_period}"
        main_content = f"""<p>Join us for exciting cheer clinics during the {holiday_period} holiday break!</p>
<p><strong>📅 Dates:</strong> {combined_dates}</p>
<p>Perfect opportunity to improve your skills, meet other cheerleaders, and have fun!</p>
<p>Limited spots available – register early to secure your place.</p>"""

        # Render using brand template
        html_body = ShireEliteTemplate.render(
            event_title=f"Cheer Clinics – {holiday_period}",
            main_content=main_content,
            button_text="Register Now",
            button_url="https://www.shireelite.com.au/athletes",
            logo_url="https://campaigns.zoho.com.au/campaigns/org7001313022/imagebannerAction.do?imgName=Campaigns_email_header_logo.png&folderId=127892000000155021"
        )

        # Save HTML and get public URL
        safe_period = sanitize_filename(holiday_period.lower().replace(' ', '-'))
        filename = f"reminder-holiday-clinics-{safe_period}-{reminder_date.strftime('%Y%m%d')}.html"
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': f"{campaign_name} - 3 Day Reminder",
            'subject': subject,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': campaign_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': 'All'
        }

    def _build_event_content(self, event_type: str, event_name: str, event_date_str: str, event: Dict) -> str:
        """
        Build HTML content for an event based on its type.

        Args:
            event_type: Type of event (e.g., 'Events', 'Gym Closures', 'Terms')
            event_name: Name of the event
            event_date_str: Date string for the event
            event: Full event dict for additional context

        Returns:
            HTML string with event content
        """
        event_type_lower = event_type.strip().lower()

        if 'gym closure' in event_type_lower:
            return f"""<p>Please note: Our gym will be closed for maintenance.</p>
<p><strong>📅 Closure Period:</strong> {event_date_str}</p>
<p>We apologize for any inconvenience. We'll be back to our normal schedule shortly!</p>
<p>If you have any questions, please don't hesitate to contact us.</p>"""

        elif 'fee' in event_type_lower or 'payment' in event_type_lower:
            return f"""<p>Please remember to submit your payment for the upcoming term.</p>
<p><strong>📅 Due Date:</strong> {event_date_str}</p>
<p>Payment details are available in your account. Thank you!</p>"""

        elif 'important' in event_type_lower:
            return f"""<p><strong>⚠️ Important Update:</strong> {event_name}</p>
<p><strong>📅 Date:</strong> {event_date_str}</p>
<p>Please take a moment to read this important information.</p>"""

        else:
            # Default for regular events and other types
            return f"""<p>You're invited to an exciting event!</p>
<p><strong>📅 Date:</strong> {event_date_str}</p>
<p>Join us for this amazing opportunity! Whether you're competing or cheering, this promises to be an unforgettable event!</p>
<p>Get ready to shine! 🌟</p>"""

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse date string from sheet."""
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

        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d/%m/%y',
            '%m/%d/%Y',
            '%d-%m-%Y',
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

    @staticmethod
    def _get_gym_from_name() -> str:
        """Get the gym name for 'from' field. Can be customized."""
        return "Shire Elite Gyms"

    def get_campaign_summary(self) -> Dict:
        """Get a summary of what campaigns will be created."""
        term_campaign = self.create_term_start_campaign()
        reminders = self.create_reminder_campaigns()

        return {
            'term_campaign': term_campaign.get('name', ''),
            'reminder_count': len(reminders),
            'event_count': len(self.events),
            'reminders': [r.get('name', '') for r in reminders]
        }
