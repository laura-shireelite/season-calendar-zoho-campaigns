"""
Campaign Generator Module

Builds campaign content for Zoho Campaigns including subject lines,
email bodies, and metadata. Handles both term-start overviews and
individual reminder campaigns.

Uses master template approach: Fetches the template HTML from Zoho,
replaces placeholders, and uses the modified template for all campaigns.
"""

import os
import unicodedata
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote
from git_helper import push_to_github


# Zoho Campaigns API configuration
ZOHO_ORG_ID = os.getenv('ZOHO_ORG_ID', '7001313022')
ZOHO_REFRESH_TOKEN = os.getenv('ZOHO_REFRESH_TOKEN')
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
ZOHO_API_BASE = "https://campaigns.zoho.com.au/api/v1"

# Master template ID with logo already embedded
MASTER_TEMPLATE_ID = "4913000011840304"

# Local file paths (for backup, if needed)
CAMPAIGNS_DIR = os.path.join(os.path.dirname(__file__), 'docs', 'campaigns')


def get_zoho_access_token() -> str:
    """
    Get a fresh Zoho API access token using the refresh token.

    Returns:
        Access token string

    Raises:
        Exception if token retrieval fails
    """
    if not all([ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET]):
        raise ValueError("Missing Zoho API credentials in environment variables")

    url = "https://accounts.zoho.com.au/oauth/v2/token"
    params = {
        'refresh_token': ZOHO_REFRESH_TOKEN,
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']


def fetch_master_template_html(gym: str = 'SE') -> str:
    """
    Load the master template HTML from the local file.

    The master template is stored locally and contains gym branding
    with styling and placeholders for dynamic content.

    Args:
        gym: Gym name ('SE' for Shire Elite, 'SCA' for SCA Allstars)

    Returns:
        HTML string of the master template

    Raises:
        Exception if template file is not found
    """
    if gym == 'SCA':
        template_path = os.path.join(os.path.dirname(__file__), 'master_template_sca.html')
    else:
        template_path = os.path.join(os.path.dirname(__file__), 'master_template.html')

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Master template not found at {template_path}")

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html
    except Exception as e:
        print(f"❌ Failed to load master template: {e}")
        raise


def replace_template_placeholders(html: str, heading: str, body: str) -> str:
    """
    Replace placeholders in the master template HTML.

    Args:
        html: Master template HTML
        heading: Text to replace "HEADING CONTENT"
        body: HTML to replace "BODY CONTENT"

    Returns:
        Modified HTML with placeholders replaced
    """
    # Replace HEADING CONTENT placeholder
    modified_html = html.replace('HEADING CONTENT', heading)

    # Replace BODY CONTENT placeholder
    modified_html = modified_html.replace('BODY CONTENT', body)

    return modified_html


def ensure_campaigns_dir():
    """Create docs/campaigns directory if it doesn't exist."""
    os.makedirs(CAMPAIGNS_DIR, exist_ok=True)


def truncate_filename_for_url(filename: str, max_url_length: int = 200) -> str:
    """
    Truncate filename to keep the final URL under a character limit.

    Zoho Campaigns has a URL length limit for content_url parameter.
    This function ensures the full URL stays under the limit by shortening
    the filename while preserving the date suffix.

    Args:
        filename: Original filename (e.g., "reminder-term-3-ends-competitive-programs-20260929.html")
        max_url_length: Maximum URL length (default 200 characters)

    Returns:
        Shortened filename
    """
    base_url = "https://laura-shireelite.github.io/season-calendar-zoho-campaigns/campaigns/"
    full_url = f"{base_url}{filename}"

    if len(full_url) <= max_url_length:
        return filename  # Already short enough

    # CRITICAL: Preserve the date and .html extension
    # Format: reminder-XXX-YYYYMMDD.html (last 17 chars: -YYYYMMDD.html = 13 chars + "reminder")
    # Find the last hyphen followed by 8 digits and .html
    import re
    match = re.search(r'-(\d{8})\.html$', filename)

    if not match:
        # Fallback if date format not found - just truncate from the beginning
        return filename[:max_url_length - len(base_url)]

    # Extract the preserved suffix: -YYYYMMDD.html
    date_suffix = filename[match.start():]  # e.g., "-20260929.html"
    name_part = filename[:match.start()]     # Everything before the date

    # Calculate how much space we have for the name
    available_space = max_url_length - len(base_url) - len(date_suffix) - 2  # -2 for safety

    if available_space < 20:
        # If we don't have enough space, use minimal name
        truncated_name = "reminder-event"
    else:
        # Truncate name to fit
        if len(name_part) > available_space:
            truncated_name = name_part[:available_space]
            # Remove trailing hyphens to avoid double-hyphens before date
            truncated_name = truncated_name.rstrip('-')
        else:
            truncated_name = name_part

    # Ensure exactly one hyphen before date (don't add if already ends with hyphen)
    if not truncated_name.endswith('-'):
        truncated_name += '-'

    truncated_filename = f"{truncated_name}{date_suffix}"

    # Verify we're not over the limit
    final_url = f"{base_url}{truncated_filename}"
    if len(final_url) > max_url_length:
        # If still over, be more aggressive
        overage = len(final_url) - max_url_length
        truncated_name = truncated_name.rstrip('-')[:len(truncated_name) - overage - 1]
        truncated_name = truncated_name.rstrip('-')
        if not truncated_name.endswith('-'):
            truncated_name += '-'
        truncated_filename = f"{truncated_name}{date_suffix}"

    return truncated_filename


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
    """Generates campaign content for a gym term using master template approach."""

    def __init__(self, term_name: str, events: List[Dict], gym: str = 'SE', use_master_template: bool = True, all_events: Optional[List[Dict]] = None):
        """
        Initialize the generator.

        Args:
            term_name: Name of the term (e.g., "Term 2 2026")
            events: List of event dictionaries for this term (sorted by date)
            gym: Gym name ('SE' for Shire Elite, 'SCA' for SCA Allstars)
            use_master_template: If True, use master template (recommended).
                                If False, fall back to GitHub Pages HTML generation.
            all_events: List of ALL events (for finding next term dates). If None, uses just current term events.
        """
        self.term_name = term_name
        self.events = events
        self.all_events = all_events if all_events else events  # Use all_events for lookups, fallback to just term events
        self.gym = gym
        self.use_master_template = use_master_template
        self.master_template_html = None
        self.base_url = "https://laura-shireelite.github.io/season-calendar-zoho-campaigns/campaigns"

        ensure_campaigns_dir()

        # Fetch master template once if using the master template approach
        if self.use_master_template:
            try:
                self.master_template_html = fetch_master_template_html(gym=gym)
                template_file = 'master_template_sca.html' if gym == 'SCA' else 'master_template.html'
                gym_display = 'SCA Allstars (pink)' if gym == 'SCA' else 'Shire Elite (yellow)'
                print(f"✅ Master template loaded for {gym_display} ({template_file})")
            except Exception as e:
                print(f"⚠️  Could not load master template: {e}")
                print("   Falling back to GitHub Pages approach")
                self.use_master_template = False

    def _load_generic_template(self, category: str) -> str:
        """
        Load a generic category template for the current gym.

        Generic templates are stored in /docs/templates/TEMPLATE-{GYM}-{CATEGORY}.html

        Args:
            category: Category name (FEES, CHEER_CLINICS, GYM_CLOSURE, CATCHUP, OTHER_IMPORTANT_DATES)

        Returns:
            Template HTML content as string, or raises FileNotFoundError if not found
        """
        # Map category to template name
        category_map = {
            'FEES': 'FEES',
            'CHEER_CLINICS': 'CHEER-CLINICS',
            'GYM_CLOSURE': 'GYM-CLOSURE',
            'CATCHUP': 'CATCHUP',
            'OTHER_IMPORTANT_DATES': 'OTHER-IMPORTANT-DATES',
        }

        if category not in category_map:
            raise ValueError(f"Unknown category: {category}")

        template_name = category_map[category]
        template_path = os.path.join(
            os.path.dirname(__file__),
            'docs', 'templates',
            f'TEMPLATE-{self.gym}-{template_name}.html'
        )

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Generic template not found: {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Failed to load generic template: {e}")
            raise

    def _save_html_and_get_url(self, html_content: str, filename: str) -> str:
        """
        Save HTML content to file, push to GitHub, and return the GitHub Pages URL.

        Args:
            html_content: HTML string to save
            filename: Filename (without path) to save as

        Returns:
            Public GitHub Pages URL
        """
        file_path = os.path.join(CAMPAIGNS_DIR, filename)

        try:
            # Save file locally
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"    💾 Saved HTML: {filename}")

            # Push to GitHub immediately
            push_to_github(file_path, commit_message=f"Campaign: {filename}")

            # Return the public URL with proper URL encoding
            # quote() keeps ASCII alphanumeric and certain safe chars, encodes the rest
            encoded_filename = quote(filename, safe='')
            url = f"{self.base_url}/{encoded_filename}"
            print(f"    🌐 Public URL: {url}")
            return url
        except Exception as e:
            print(f"    ❌ Failed to save HTML file: {e}")
            raise

    def create_term_start_campaign(self) -> Dict:
        """
        Create the term-start campaign listing all events (excluding holiday clinics).

        Returns:
            Campaign dict ready for Zoho API
        """
        if not self.events:
            return {}

        campaign_name = f"{self.gym} {self.term_name} - What's Coming Up"

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

        heading = f"📅 {self.term_name}"

        body_content = f"""<p><strong>Term Runs:</strong> {term_start} to {term_end}</p>
<p><strong>Upcoming events:</strong></p>
{events_html}
<p>You'll receive reminders 3 days before each event. Holiday clinics will be announced separately!</p>
<p>Thanks!<br>Your Gym Team</p>"""

        # Use master template if available
        if self.use_master_template and self.master_template_html:
            html_body = replace_template_placeholders(
                self.master_template_html,
                heading=heading,
                body=body_content
            )
            # Save to GitHub Pages so Zoho can access it
            safe_term_name = sanitize_filename(self.term_name.lower().replace(' ', '-'))
            filename = f"term-overview-{self.gym.lower()}-{safe_term_name}.html"
            content_url = self._save_html_and_get_url(html_body, filename)
        else:
            # Fallback to GitHub approach
            from brand_templates import ShireEliteTemplate
            html_body = ShireEliteTemplate.render(
                event_title=heading,
                main_content=body_content,
                button_text="Athletes Page",
                button_url="https://www.shireelite.com.au/athletes",
                logo_url="https://laura-shireelite.github.io/season-calendar-zoho-campaigns/images/shire-elite-logo-email.png"
            )
            safe_term_name = sanitize_filename(self.term_name.lower().replace(' ', '-'))
            filename = f"term-overview-{self.gym.lower()}-{safe_term_name}.html"
            content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'term_overview',
            'target_gym': self.gym
        }

    # ============================================================================
    # CATEGORY DETECTION METHODS
    # ============================================================================

    def _detect_event_category(self, event: Dict) -> str:
        """
        Detect the category of an event.

        Returns one of:
        - 'TERM_BEGIN': Term begins events
        - 'TERM_END': Term ends events
        - 'FEES': Important Dates > Fees
        - 'CHEER_CLINICS': Cheer Clinics (all are holiday/school-break related)
        - 'OTHER_IMPORTANT_DATES': Important Dates > Other
        - 'GYM_CLOSURE': Gym Closure events (non-school-holiday)
        - 'CATCHUP': Catch-Up sessions
        - 'EVENTS': Regular events (to skip)
        - 'UNKNOWN': Could not determine
        """
        event_name = event.get('Event Name', '').lower()
        event_type = event.get('Event Type', '').strip().lower()

        # Check for TERM events first
        if 'terms' in event_type:
            if 'begin' in event_name and 'end' not in event_name:
                return 'TERM_BEGIN'
            elif 'end' in event_name:
                return 'TERM_END'

        # Check for IMPORTANT DATES subcategories
        if 'important' in event_type or 'important dates' in event_type:
            if self._is_fees_event(event):
                return 'FEES'
            elif self._is_cheer_clinic(event.get('Event Name', '')):
                return 'CHEER_CLINICS'
            else:
                return 'OTHER_IMPORTANT_DATES'

        # Check for GYM CLOSURES
        if 'gym' in event_type or 'closure' in event_type:
            if self._is_catchup_event(event.get('Event Name', '')):
                return 'CATCHUP'
            elif self._is_school_holiday_closure(event.get('Event Name', '')):
                return 'SKIP'  # Skip school holiday closures
            else:
                return 'GYM_CLOSURE'

        # Check for regular EVENTS (to skip)
        if 'events' in event_type:
            return 'EVENTS'

        return 'UNKNOWN'

    def _is_fees_event(self, event: Dict) -> bool:
        """Check if an Important Dates event is about fees."""
        event_name = event.get('Event Name', '').lower()
        return any(keyword in event_name for keyword in ['fee', 'payment', 'cost', 'invoice', 'registration'])

    def _is_cheer_clinic(self, event_name: str) -> bool:
        """Check if an event is a cheer clinic (all are holiday/school-break related)."""
        return 'cheer clinic' in event_name.lower()

    def _is_school_holiday_closure(self, event_name: str) -> bool:
        """Check if a gym closure is due to school holidays."""
        lower_name = event_name.lower()
        return any(keyword in lower_name for keyword in ['school hol', 'school holidays', 'public holiday'])

    def _is_catchup_event(self, event_name: str) -> bool:
        """Check if an event is a catch-up session."""
        lower_name = event_name.lower()
        return 'catch-up' in lower_name or 'catch up' in lower_name

    # ============================================================================
    # NEW CAMPAIGN BUILDER METHODS FOR EACH CATEGORY
    # ============================================================================

    def _build_fees_campaign(self, event: Dict, reminder_date: datetime) -> Dict:
        """Build a campaign for a fees/payment event using generic FEES template."""
        event_name = event.get('Event Name', '')
        event_date_str = event.get('Date', '')

        event_name_clean = event_name.replace('–', '-').replace('—', '-')
        campaign_name = f"{self.gym} {event_name_clean} - 3 Day Reminder"
        subject = f"💳 {event_name} - 3 Day Reminder"

        # Build specific body content for this event (no <p> tags - template provides them)
        body_content = f"<strong>📅 Due Date:</strong> {event_date_str}"

        # Load generic FEES template and replace placeholders
        try:
            generic_template = self._load_generic_template('FEES')
            html_body = replace_template_placeholders(
                generic_template,
                heading=event_name,
                body=body_content
            )
        except FileNotFoundError:
            # Fallback to master template if generic template not found
            if self.use_master_template and self.master_template_html:
                html_body = replace_template_placeholders(
                    self.master_template_html,
                    heading=event_name,
                    body=body_content
                )
            else:
                raise

        safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
        filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
        filename = truncate_filename_for_url(filename)
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': event_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym,
            'category': 'FEES'
        }

    def _build_other_important_dates_campaign(self, event: Dict, reminder_date: datetime) -> Dict:
        """Build a campaign for other important dates using generic OTHER-IMPORTANT-DATES template."""
        event_name = event.get('Event Name', '')
        event_date_str = event.get('Date', '')

        event_name_clean = event_name.replace('–', '-').replace('—', '-')
        campaign_name = f"{self.gym} {event_name_clean} - 3 Day Reminder"
        subject = f"⚠️ {event_name} - 3 Day Reminder"

        # Build specific body content for this event (no <p> tags - template provides them)
        body_content = f"<strong>📅 Date:</strong> {event_date_str}"

        # Load generic OTHER-IMPORTANT-DATES template and replace placeholders
        try:
            generic_template = self._load_generic_template('OTHER_IMPORTANT_DATES')
            html_body = replace_template_placeholders(
                generic_template,
                heading=event_name,
                body=body_content
            )
        except FileNotFoundError:
            # Fallback to master template if generic template not found
            if self.use_master_template and self.master_template_html:
                html_body = replace_template_placeholders(
                    self.master_template_html,
                    heading=event_name,
                    body=body_content
                )
            else:
                raise

        safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
        filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
        filename = truncate_filename_for_url(filename)
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': event_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym,
            'category': 'OTHER_IMPORTANT_DATES'
        }

    def _build_gym_closure_campaign(self, event: Dict, reminder_date: datetime) -> Dict:
        """Build a campaign for a gym closure event using generic GYM-CLOSURE template."""
        event_name = event.get('Event Name', '')
        event_date_str = event.get('Date', '')

        event_name_clean = event_name.replace('–', '-').replace('—', '-')
        campaign_name = f"{self.gym} {event_name_clean} - 3 Day Reminder"
        subject = f"🔒 {event_name} - 3 Day Reminder"

        # Build specific body content for this event (no <p> tags - template provides them)
        body_content = f"<strong>📅 Closure Period:</strong> {event_date_str}"

        # Load generic GYM-CLOSURE template and replace placeholders
        try:
            generic_template = self._load_generic_template('GYM_CLOSURE')
            html_body = replace_template_placeholders(
                generic_template,
                heading=event_name,
                body=body_content
            )
        except FileNotFoundError:
            # Fallback to master template if generic template not found
            if self.use_master_template and self.master_template_html:
                html_body = replace_template_placeholders(
                    self.master_template_html,
                    heading=event_name,
                    body=body_content
                )
            else:
                raise

        safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
        filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
        filename = truncate_filename_for_url(filename)
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': event_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym,
            'category': 'GYM_CLOSURE'
        }

    def _build_catchup_campaign(self, event: Dict, reminder_date: datetime) -> Dict:
        """Build a campaign for a catch-up session using generic CATCHUP template."""
        event_name = event.get('Event Name', '')
        event_date_str = event.get('Date', '')

        event_name_clean = event_name.replace('–', '-').replace('—', '-')
        campaign_name = f"{self.gym} {event_name_clean} - 3 Day Reminder"
        subject = f"⚡ {event_name} - 3 Day Reminder"

        # Build specific body content for this event (no <p> tags - template provides them)
        body_content = f"<strong>📅 Date:</strong> {event_date_str}"

        # Load generic CATCHUP template and replace placeholders
        try:
            generic_template = self._load_generic_template('CATCHUP')
            html_body = replace_template_placeholders(
                generic_template,
                heading=event_name,
                body=body_content
            )
        except FileNotFoundError:
            # Fallback to master template if generic template not found
            if self.use_master_template and self.master_template_html:
                html_body = replace_template_placeholders(
                    self.master_template_html,
                    heading=event_name,
                    body=body_content
                )
            else:
                raise

        safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
        filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
        filename = truncate_filename_for_url(filename)
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': event_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym,
            'category': 'CATCHUP'
        }

    def create_reminder_campaigns(self) -> List[Dict]:
        """
        Create reminder campaigns for 3 days before each event.

        Uses category detection to route events to appropriate campaign builders:
        - TERM_BEGIN: Skipped (covered in term overview)
        - TERM_END: Grouped by term, one campaign per term with all programs
        - FEES: Individual campaign with fees content
        - CHEER_CLINICS: Individual campaign with clinic content
        - OTHER_IMPORTANT_DATES: Individual campaign with important date content
        - HOLIDAY_CLINICS: Grouped by holiday period
        - GYM_CLOSURE: Individual campaign with closure content
        - CATCHUP: Individual campaign with catchup content
        - EVENTS: Skipped entirely
        - SKIP/UNKNOWN: Skipped

        Returns:
            List of campaign dicts ready for Zoho API
        """
        campaigns = []
        processed_events = set()  # Track which events we've processed
        holiday_clinic_groups = {}  # Group clinics by holiday period
        term_end_groups = {}  # Group term end events by term name

        print(f"    📊 Processing {len(self.events)} events for reminders...")

        # First pass: detect categories and group events that need grouping
        for event in self.events:
            event_name = event.get('Event Name', '')
            category = self._detect_event_category(event)

            # Group cheer clinics by period
            if category == 'CHEER_CLINICS':
                holiday_period = self._extract_holiday_period(event_name)
                if holiday_period not in holiday_clinic_groups:
                    holiday_clinic_groups[holiday_period] = []
                holiday_clinic_groups[holiday_period].append(event)

            # Group term ends by term name
            elif category == 'TERM_END':
                import re
                term_base = re.split(r'\s+[-–]\s+', event_name)[0]  # e.g., "Term 3 ends"
                if term_base not in term_end_groups:
                    term_end_groups[term_base] = []
                term_end_groups[term_base].append(event)

        # Second pass: create campaigns using category-based routing
        for idx, event in enumerate(self.events):
            event_name = event.get('Event Name', '')
            event_date_str = event.get('Date', '')
            event_id = f"{event_name}_{event_date_str}"

            # Skip if already processed as part of a group
            if event_id in processed_events:
                continue

            # Parse date
            try:
                event_date = self._parse_date(event_date_str)
            except ValueError:
                print(f"    ❌ Event {idx+1}: Skipping '{event_name}' (invalid date '{event_date_str}')")
                continue

            # Calculate reminder date (3 days before)
            reminder_date = event_date - timedelta(days=3)

            # Detect category and route to appropriate handler
            category = self._detect_event_category(event)

            if category == 'TERM_BEGIN':
                # Skip - covered in term overview email
                print(f"    ⏭️  Event {idx+1}: Skipping '{event_name}' (covered in term overview)")
                processed_events.add(event_id)

            elif category == 'TERM_END':
                # Process grouped term end campaign
                import re
                term_base = re.split(r'\s+[-–]\s+', event_name)[0]
                if term_base in term_end_groups:
                    term_ends_for_term = term_end_groups[term_base]
                    campaign = self._build_grouped_term_end_campaign(
                        term_ends_for_term,
                        reminder_date
                    )
                    if campaign:
                        campaigns.append(campaign)
                        for term_event in term_ends_for_term:
                            processed_events.add(f"{term_event.get('Event Name', '')}_{term_event.get('Date', '')}")
                        print(f"    ✅ Grouped: {len(term_ends_for_term)} programs in '{term_base}' → reminder on {reminder_date.strftime('%Y-%m-%d')}")
                    del term_end_groups[term_base]

            elif category == 'FEES':
                # Build fees campaign
                campaign = self._build_fees_campaign(event, reminder_date)
                if campaign:
                    campaigns.append(campaign)
                    processed_events.add(event_id)
                    print(f"    ✅ Event {idx+1}: FEES - '{event_name}' → reminder on {reminder_date.strftime('%Y-%m-%d')}")

            elif category == 'CHEER_CLINICS':
                # Process grouped cheer clinics campaign (all are holiday/school-break related)
                holiday_period = self._extract_holiday_period(event_name)
                if holiday_period in holiday_clinic_groups:
                    campaign = self._build_cheer_clinics_campaign(
                        holiday_period,
                        holiday_clinic_groups[holiday_period],
                        reminder_date
                    )
                    if campaign:
                        campaigns.append(campaign)
                        for clinic_event in holiday_clinic_groups[holiday_period]:
                            processed_events.add(f"{clinic_event.get('Event Name', '')}_{clinic_event.get('Date', '')}")
                        print(f"    ✅ Grouped: '{holiday_period}' cheer clinics → reminder on {reminder_date.strftime('%Y-%m-%d')}")
                    del holiday_clinic_groups[holiday_period]

            elif category == 'OTHER_IMPORTANT_DATES':
                # Build other important dates campaign
                campaign = self._build_other_important_dates_campaign(event, reminder_date)
                if campaign:
                    campaigns.append(campaign)
                    processed_events.add(event_id)
                    print(f"    ✅ Event {idx+1}: OTHER_IMPORTANT_DATES - '{event_name}' → reminder on {reminder_date.strftime('%Y-%m-%d')}")

            elif category == 'GYM_CLOSURE':
                # Build gym closure campaign
                campaign = self._build_gym_closure_campaign(event, reminder_date)
                if campaign:
                    campaigns.append(campaign)
                    processed_events.add(event_id)
                    print(f"    ✅ Event {idx+1}: GYM_CLOSURE - '{event_name}' → reminder on {reminder_date.strftime('%Y-%m-%d')}")

            elif category == 'CATCHUP':
                # Build catch-up campaign
                campaign = self._build_catchup_campaign(event, reminder_date)
                if campaign:
                    campaigns.append(campaign)
                    processed_events.add(event_id)
                    print(f"    ✅ Event {idx+1}: CATCHUP - '{event_name}' → reminder on {reminder_date.strftime('%Y-%m-%d')}")

            elif category == 'EVENTS':
                # Skip regular events
                print(f"    ⏭️  Event {idx+1}: Skipping '{event_name}' (Events category - no campaigns needed)")
                processed_events.add(event_id)

            elif category == 'SKIP':
                # Skip school holiday closures
                print(f"    ⏭️  Event {idx+1}: Skipping '{event_name}' (school holiday closure)")
                processed_events.add(event_id)

            else:
                # Unknown category
                print(f"    ⚠️  Event {idx+1}: Skipping '{event_name}' (unknown category: {category})")
                processed_events.add(event_id)

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

    def _extract_term_number(self, text: str) -> Optional[str]:
        """
        Extract term number from text (e.g., "2" from "Term 2 ends" or "Term 2 End Date: Fri 25 Sep").

        Args:
            text: Text containing term reference

        Returns:
            Term number as string (e.g., "2"), or None if not found
        """
        import re
        match = re.search(r'Term\s+(\d+)', text)
        if match:
            return match.group(1)
        return None

    def _build_reminder_campaign(self, event: Dict, reminder_date: datetime) -> Dict:
        """Build a single reminder campaign."""
        event_name = event.get('Event Name', '')
        event_type = event.get('Event Type', '')
        event_date_str = event.get('Date', '')

        # Campaign name - replace em-dashes with regular hyphens to avoid Zoho import errors
        event_name_clean = event_name.replace('–', '-').replace('—', '-')
        campaign_name = f"{self.gym} {event_name_clean} - 3 Day Reminder"

        # Build email content based on event type
        subject = f"⏰ {event_name} - 3 Day Reminder"
        body_content = self._build_event_content(event_type, event_name, event_date_str, event)

        # Use master template if available
        if self.use_master_template and self.master_template_html:
            html_body = replace_template_placeholders(
                self.master_template_html,
                heading=event_name,
                body=body_content
            )
            # Save to GitHub Pages so Zoho can access it
            safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
            filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
            # Truncate filename to keep URL under Zoho's limit
            filename = truncate_filename_for_url(filename)
            content_url = self._save_html_and_get_url(html_body, filename)
        else:
            # Fallback to GitHub approach
            from brand_templates import ShireEliteTemplate
            html_body = ShireEliteTemplate.render(
                event_title=event_name,
                main_content=body_content,
                button_text="Event Details",
                button_url="https://www.shireelite.com.au/athletes",
                logo_url="https://laura-shireelite.github.io/season-calendar-zoho-campaigns/images/shire-elite-logo-email.png"
            )
            safe_event_name = sanitize_filename(event_name.lower().replace(' ', '-'))
            filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
            # Truncate filename to keep URL under Zoho's limit
            filename = truncate_filename_for_url(filename)
            content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': campaign_name,
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': event_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym
        }

    def _build_cheer_clinics_campaign(self, holiday_period: str, clinic_events: List[Dict], reminder_date: datetime) -> Dict:
        """Build a campaign for grouped cheer clinics using generic CHEER-CLINICS template."""
        # Combine dates from all clinic events (for email body)
        clinic_dates = [e.get('Date', '') for e in clinic_events]
        combined_dates = " / ".join(clinic_dates)

        # Simplified campaign name (for Zoho API - remove em-dashes to avoid import errors)
        holiday_period_clean = holiday_period.replace('–', '-').replace('—', '-')
        campaign_name = f"Cheer Clinics - {holiday_period_clean}"

        # Build email content for cheer clinics
        subject = f"🎉 Cheer Clinics – {holiday_period}"
        heading = f"Cheer Clinics – {holiday_period}"

        # Build specific body content with clinic dates (no <p> tags - template provides them)
        body_content = f"<strong>📅 Dates:</strong> {combined_dates}"

        # Load generic CHEER-CLINICS template and replace placeholders
        try:
            generic_template = self._load_generic_template('CHEER_CLINICS')
            html_body = replace_template_placeholders(
                generic_template,
                heading=heading,
                body=body_content
            )
        except FileNotFoundError:
            # Fallback to master template if generic template not found
            if self.use_master_template and self.master_template_html:
                html_body = replace_template_placeholders(
                    self.master_template_html,
                    heading=heading,
                    body=body_content
                )
            else:
                raise

        # Save to GitHub Pages so Zoho can access it
        safe_period = sanitize_filename(holiday_period.lower().replace(' ', '-'))
        filename = f"reminder-{self.gym.lower()}-cheer-clinics-{safe_period}-{reminder_date.strftime('%Y%m%d')}.html"
        # Truncate filename to keep URL under Zoho's limit
        filename = truncate_filename_for_url(filename)
        content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': f"{self.gym} {campaign_name} - 3 Day Reminder",
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': campaign_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym,
            'category': 'CHEER_CLINICS'
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

    def _find_related_gym_closure(self, term_end_event: Dict, all_events: List[Dict]) -> Optional[Dict]:
        """
        Find a gym closure event related to a term end event.

        Looks for gym closure events that occur within 2 weeks of the term end date.

        Args:
            term_end_event: The term end event
            all_events: List of all events to search through

        Returns:
            Gym closure event if found, None otherwise
        """
        try:
            term_end_date = self._parse_date(term_end_event.get('Date', ''))
        except ValueError:
            return None

        # Look for gym closure events within 2 weeks of term end
        for event in all_events:
            event_name = event.get('Event Name', '').lower()
            if 'gym' in event_name and 'closure' in event_name:
                try:
                    closure_date = self._parse_date(event.get('Date', ''))
                    days_apart = abs((closure_date - term_end_date).days)
                    # Consider it related if within 14 days
                    if days_apart <= 14:
                        return event
                except ValueError:
                    continue

        return None

    def _find_next_term_start_date(self, term_end_event: Dict) -> Optional[str]:
        """
        Find the start date of the next term after a term end event.

        Args:
            term_end_event: The term end event

        Returns:
            Start date of next term as formatted string (e.g., "Mon 12 Oct"), or None
        """
        try:
            term_end_date = self._parse_date(term_end_event.get('Date', ''))
        except ValueError:
            return None

        # Look for "Term X begins" or similar events that come after this term end
        # Search through all_events (which includes future terms) not just current term
        next_term = None
        min_days_after = float('inf')

        for event in self.all_events:
            event_name_lower = event.get('Event Name', '').lower()
            event_type_lower = event.get('Event Type', '').lower()

            # Look for term start events (not "ends")
            if ('term' in event_name_lower or 'term' in event_type_lower) and 'end' not in event_name_lower:
                try:
                    event_date = self._parse_date(event.get('Date', ''))
                    days_after = (event_date - term_end_date).days

                    # Find the closest term start that comes after the term end
                    if 0 < days_after < min_days_after:
                        min_days_after = days_after
                        next_term = event.get('Date', '')

                except ValueError:
                    continue

        return next_term

    def _build_grouped_term_end_campaign(self, term_end_events: List[Dict], reminder_date: datetime) -> Dict:
        """
        Build ONE campaign that groups all programs for a term (e.g., Recreational + Competitive).

        Shows all programs with their individual end dates, plus when the next term begins.
        Handles cases where different programs end on different dates.

        Args:
            term_end_events: List of term end events for this term (may have different dates)
            reminder_date: When to send the reminder

        Returns:
            Campaign dict ready for Zoho API
        """
        if not term_end_events:
            return {}

        # Find next term start date (use first event as reference)
        next_term_date = self._find_next_term_start_date(term_end_events[0])
        next_term_number = self._extract_term_number(next_term_date) if next_term_date else None

        # Build campaign name showing this is about term endings
        # Extract term base (e.g., "Term 3 ends")
        # Handle both regular hyphen (-) and en-dash (–)
        import re
        first_event = term_end_events[0].get('Event Name', '')
        campaign_name_base = re.split(r'\s+[-–]\s+', first_event)[0].replace('–', '-').replace('—', '-')

        # Extract term number (e.g., "3" from "Term 3 ends")
        current_term_number = self._extract_term_number(campaign_name_base)

        subject = f"⏰ {campaign_name_base} - 3 Day Reminder"

        # Build email content listing all programs with their individual end dates
        # NOTE: Do NOT wrap in <p> tags - the template's placeholder already does this
        # Avoid nested <p> tags by using <br> for line breaks instead
        body_sections = []

        # Check if all programs end on the same date
        unique_dates = set(e.get('Date', '') for e in term_end_events)
        all_same_date = len(unique_dates) == 1

        if all_same_date:
            # All programs end on same date - simpler format with term number
            term_date = term_end_events[0].get('Date', '')
            if current_term_number:
                body_sections.append(f"<strong>Term {current_term_number} End Date:</strong> {term_date}")
            else:
                body_sections.append(f"<strong>Term End Date:</strong> {term_date}")
        else:
            # Multiple programs with different end dates - show all with who they're for
            heading = f"<strong>Term {current_term_number} End Dates:</strong>" if current_term_number else "<strong>End Dates:</strong>"
            list_items = []
            for event in term_end_events:
                event_name = event.get('Event Name', '').replace('–', '-').replace('—', '-')
                event_date = event.get('Date', '')
                # Extract the program type (e.g., "Recreational programs" from "Term 3 ends - Recreational programs")
                if ' - ' in event_name:
                    program_type = event_name.split(' - ', 1)[1]
                else:
                    program_type = event_name
                list_items.append(f"<li>{program_type}: {event_date}</li>")

            # Combine heading with list
            ul_content = "<ul>" + "".join(list_items) + "</ul>"
            body_sections.append(heading)
            body_sections.append(ul_content)

        if next_term_date:
            if next_term_number:
                body_sections.append(f"<strong>Term {next_term_number} Resumes:</strong> {next_term_date}")
            else:
                body_sections.append(f"<strong>Term Resumes:</strong> {next_term_date}")

        body_sections.append("Please note these important dates for your gym schedule.")
        body_sections.append("Thanks!<br>Your Gym Team")

        # Join with <br> to separate sections, avoiding <br> inside list
        body_content = "<br>".join(body_sections)

        # Use master template if available
        if self.use_master_template and self.master_template_html:
            html_body = replace_template_placeholders(
                self.master_template_html,
                heading=campaign_name_base,
                body=body_content
            )
            # Save to GitHub Pages so Zoho can access it
            safe_event_name = sanitize_filename(campaign_name_base.lower().replace(' ', '-'))
            filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
            # Truncate filename to keep URL under Zoho's limit
            filename = truncate_filename_for_url(filename)
            content_url = self._save_html_and_get_url(html_body, filename)
        else:
            # Fallback
            from brand_templates import ShireEliteTemplate
            html_body = ShireEliteTemplate.render(
                event_title=campaign_name_base,
                main_content=body_content,
                button_text="Athletes Page",
                button_url="https://www.shireelite.com.au/athletes",
                logo_url="https://laura-shireelite.github.io/season-calendar-zoho-campaigns/images/shire-elite-logo-email.png"
            )
            safe_event_name = sanitize_filename(campaign_name_base.lower().replace(' ', '-'))
            filename = f"reminder-{self.gym.lower()}-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
            # Truncate filename to keep URL under Zoho's limit
            filename = truncate_filename_for_url(filename)
            content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': f"{self.gym} {campaign_name_base} - 3 Day Reminder",
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': campaign_name_base,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym
        }

    def _build_term_end_campaign(self, term_end_event: Dict, reminder_date: datetime) -> Dict:
        """
        Build a term end campaign that includes next term info.

        Simple strategy: just show when this term ends and when the next term begins.
        Athletes can figure out gym closure from the gap between dates.

        Args:
            term_end_event: The term end event
            reminder_date: When to send the reminder

        Returns:
            Campaign dict ready for Zoho API
        """
        term_name = term_end_event.get('Event Name', 'Term End')
        term_date = term_end_event.get('Date', '')

        # Find next term start date
        next_term_date = self._find_next_term_start_date(term_end_event)

        # Campaign name is just the term end
        campaign_name = term_name.replace('–', '-').replace('—', '-')
        subject = f"⏰ {campaign_name} - 3 Day Reminder"

        # Build simple email content
        body_lines = [
            f"<p><strong>Last Day of Term:</strong> {term_date}</p>"
        ]

        if next_term_date:
            body_lines.append(f"<p><strong>Term Resumes:</strong> {next_term_date}</p>")

        body_lines.append("<p>Please note these important dates for your gym schedule.</p>")
        body_lines.append("<p>Thanks!<br>Your Gym Team</p>")

        body_content = "\n".join(body_lines)

        # Use master template if available
        if self.use_master_template and self.master_template_html:
            html_body = replace_template_placeholders(
                self.master_template_html,
                heading=campaign_name,
                body=body_content
            )
            # Save to GitHub Pages so Zoho can access it
            safe_event_name = sanitize_filename(campaign_name.lower().replace(' ', '-'))
            filename = f"reminder-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
            # Truncate filename to keep URL under Zoho's limit
            filename = truncate_filename_for_url(filename)
            content_url = self._save_html_and_get_url(html_body, filename)
        else:
            # Fallback
            from brand_templates import ShireEliteTemplate
            html_body = ShireEliteTemplate.render(
                event_title=campaign_name,
                main_content=body_content,
                button_text="Athletes Page",
                button_url="https://www.shireelite.com.au/athletes",
                logo_url="https://laura-shireelite.github.io/season-calendar-zoho-campaigns/images/shire-elite-logo-email.png"
            )
            safe_event_name = sanitize_filename(campaign_name.lower().replace(' ', '-'))
            filename = f"reminder-{safe_event_name}-{reminder_date.strftime('%Y%m%d')}.html"
            # Truncate filename to keep URL under Zoho's limit
            filename = truncate_filename_for_url(filename)
            content_url = self._save_html_and_get_url(html_body, filename)

        return {
            'name': f"{campaign_name} - 3 Day Reminder",
            'subject': subject,
            'html_body': None,
            'content_url': content_url,
            'from_name': self._get_gym_from_name(),
            'type': 'reminder',
            'event_name': campaign_name,
            'reminder_date': reminder_date.strftime('%Y-%m-%d'),
            'target_gym': self.gym
        }

    def _get_gym_from_name(self) -> str:
        """Get the gym name for 'from' field based on target gym."""
        if self.gym == 'SCA':
            return "SCA Allstars"
        else:
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
