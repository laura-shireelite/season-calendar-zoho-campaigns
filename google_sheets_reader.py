"""
Google Sheets Reader Module

Handles reading calendar events from your gym's Google Sheet.
Uses the Google Sheets API with service account authentication.

Expected sheet structure:
- Row 1: Title (skipped)
- Row 2: Headers (SE | SCA | Event | See more details →)
- Row 3+: Data
  - Column A: SE date
  - Column B: SCA date (or "—" if SE only)
  - Column C: Event name
  - Column D: Event type
"""

import re
import json
import time
from typing import List, Dict
from datetime import datetime, timedelta
import requests


class GoogleSheetsReader:
    """Reads calendar events from a Google Sheet using the Google Sheets API."""

    GOOGLE_OAUTH_URL = "https://oauth2.googleapis.com/token"
    SHEETS_API_URL = "https://sheets.googleapis.com/v4/spreadsheets"

    def __init__(self, sheet_url: str, service_account_json_path: str):
        """
        Initialize the reader.

        Args:
            sheet_url: Full Google Sheets URL (e.g., https://docs.google.com/spreadsheets/d/...)
            service_account_json_path: Path to Google service account JSON file
        """
        self.sheet_url = sheet_url
        self.sheet_id = self._extract_sheet_id(sheet_url)

        # Load service account credentials
        with open(service_account_json_path, 'r') as f:
            self.service_account = json.load(f)

        self.access_token = None
        self.token_expiry = None
        self._get_access_token()

    def _get_access_token(self):
        """Generate a JWT token and exchange it for an access token."""
        import base64
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend

        print("  🔑 Generating Google access token from service account...")

        # Create JWT header and payload
        now = int(time.time())
        expiry = now + 3600  # 1 hour

        header = {
            "alg": "RS256",
            "typ": "JWT"
        }

        payload = {
            "iss": self.service_account['client_email'],
            "scope": "https://www.googleapis.com/auth/spreadsheets.readonly",
            "aud": self.GOOGLE_OAUTH_URL,
            "exp": expiry,
            "iat": now
        }

        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')

        # Create signature with RSA
        message = f"{header_b64}.{payload_b64}".encode()
        private_key_str = self.service_account['private_key']

        # Load the private key
        private_key = serialization.load_pem_private_key(
            private_key_str.encode(),
            password=None,
            backend=default_backend()
        )

        # Sign the message
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        jwt_token = f"{header_b64}.{payload_b64}.{signature_b64}"

        # Exchange JWT for access token
        try:
            response = requests.post(
                self.GOOGLE_OAUTH_URL,
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': jwt_token
                }
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

            print(f"  ✅ Access token generated (expires in {expires_in}s)")

        except Exception as e:
            raise Exception(f"Failed to get access token: {e}")

    def _ensure_token_valid(self):
        """Refresh token if expired."""
        if not self.token_expiry or datetime.now() >= self.token_expiry:
            self._get_access_token()

    @staticmethod
    def _extract_sheet_id(url: str) -> str:
        """Extract the sheet ID from a Google Sheets URL."""
        # Format: https://docs.google.com/spreadsheets/d/{ID}/edit
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract sheet ID from URL: {url}")

    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from the Google Sheet.

        Reads the first tab and expects columns:
        - A: Date
        - B: Gym (SE/SCA/Both)
        - C: Event Name
        - D: Event Type
        - E+: Additional info (optional)

        Returns:
            List of event dictionaries with keys: Date, Gym, Event Name, Event Type, etc.

        Raises:
            Exception: If the API call fails or data format is unexpected
        """
        self._ensure_token_valid()
        print("  Reading from sheet ID:", self.sheet_id)

        # First, get sheet metadata to find the first sheet name
        metadata_url = f"{self.SHEETS_API_URL}/{self.sheet_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            metadata_response = requests.get(metadata_url, headers=headers)
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            # Get the first sheet name
            sheet_name = metadata['sheets'][0]['properties']['title']
            print(f"  Found sheet: {sheet_name}")

        except Exception as e:
            raise Exception(f"Failed to get sheet metadata: {e}")

        # Use Google Sheets API to read the range A:H from the first sheet
        url = f"{self.SHEETS_API_URL}/{self.sheet_id}/values/{sheet_name}!A:H"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Google Sheet: {e}")

        if 'values' not in data:
            print("  ⚠️  No data found in sheet")
            return []

        rows = data['values']
        if not rows:
            return []

        # Row 0 is title, Row 1 is headers, Row 2+ is data
        if len(rows) < 2:
            raise ValueError("Sheet has fewer than 2 rows (need title and headers)")

        headers = rows[1] if len(rows) > 1 else []
        if not headers:
            raise ValueError("Sheet has no headers in row 2")

        print(f"  Found columns: {', '.join(headers)}")

        # Expected columns (check for either the standard names or user's actual names)
        # Standard names: Date, Gym, Event Name, Event Type
        # User's sheet: SE, SCA, Event, See more details →
        expected_standard = ['Date', 'Gym', 'Event Name', 'Event Type']
        expected_user = ['SE', 'SCA', 'Event', 'See more details →']

        has_standard = all(col in headers for col in expected_standard)
        has_user = all(col in headers for col in expected_user)

        if not (has_standard or has_user):
            print(f"  ⚠️  Warning: Unexpected column structure")
            print(f"      Expected either: {expected_standard}")
            print(f"      Or: {expected_user}")
            print(f"      Found: {headers}")

        # Parse data rows (skip title row 0, header row 1, data starts at row 2)
        events = []
        for i, row in enumerate(rows[2:], start=3):  # Skip title (row 0) and header (row 1), start at data (row 2)
            if not row or all(cell.strip() == '' for cell in row):
                # Skip empty rows
                continue

            # Ensure we have at least 4 columns
            while len(row) < 4:
                row.append('')

            se_date = row[0].strip() if len(row) > 0 else ''
            sca_date = row[1].strip() if len(row) > 1 else ''
            event_name = row[2].strip() if len(row) > 2 else ''
            event_type = row[3].strip() if len(row) > 3 else ''

            # Skip rows with missing event name
            if not event_name:
                print(f"  ⚠️  Skipping row {i}: missing Event Name")
                continue

            # Skip rows with no dates
            if not se_date and not sca_date:
                print(f"  ⚠️  Skipping row {i}: no dates for either gym")
                continue

            # Determine gym assignment based on SE and SCA dates
            # SE only: SE has date, SCA is empty or "—"
            if se_date and (not sca_date or sca_date == '—'):
                events.append({
                    'Date': se_date,
                    'Gym': 'SE',
                    'Event Name': event_name,
                    'Event Type': event_type
                })

            # SCA only: SCA has date, SE is empty or "—"
            elif sca_date and (not se_date or se_date == '—'):
                events.append({
                    'Date': sca_date,
                    'Gym': 'SCA',
                    'Event Name': event_name,
                    'Event Type': event_type
                })

            # Both gyms: both have dates
            elif se_date and sca_date and sca_date != '—':
                if se_date == sca_date:
                    # Same date at both: use "Both"
                    events.append({
                        'Date': se_date,
                        'Gym': 'Both',
                        'Event Name': event_name,
                        'Event Type': event_type
                    })
                else:
                    # Different dates: create separate events for each gym
                    events.append({
                        'Date': se_date,
                        'Gym': 'SE',
                        'Event Name': event_name,
                        'Event Type': event_type
                    })
                    events.append({
                        'Date': sca_date,
                        'Gym': 'SCA',
                        'Event Name': event_name,
                        'Event Type': event_type
                    })

        print(f"  ✅ Parsed {len(events)} events from sheet")
        return events

    def validate_sheet_format(self, events: List[Dict]) -> bool:
        """
        Validate that the sheet has the expected format.

        Your sheet should have:
        - Row 1: Title (skipped)
        - Row 2: Headers (SE | SCA | Event | See more details →)
        - Row 3+: Data

        Returns:
            True if valid, False otherwise
        """
        if not events:
            print("  ❌ Sheet has no events")
            return False

        required_fields = ['Date', 'Gym', 'Event Name', 'Event Type']
        sample = events[0]

        missing = [field for field in required_fields if field not in sample]
        if missing:
            print(f"  ❌ Missing required fields: {missing}")
            return False

        # Check for at least one "Terms" event to identify term boundaries
        term_events = [e for e in events if e.get('Event Type', '').lower() == 'terms']
        if not term_events:
            print("  ⚠️  Warning: No 'Terms' type events found. Auto-detection may not work.")
            print("      Make sure your sheet has at least one event with Event Type = 'Terms'")

        return True
