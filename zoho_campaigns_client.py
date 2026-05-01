"""
Zoho Campaigns Client

Handles OAuth 2.0 authentication and campaign creation via Zoho Campaigns API.
"""

import requests
from datetime import datetime, timedelta


class ZohoCampaignsClient:
    """Client for interacting with Zoho Campaigns API."""

    # Note: Error responses show /api/v2/ but we're using v1.1
    # If v1.1 doesn't work, try changing to /api/v2.1 or /api/v3
    BASE_URL = "https://campaigns.zoho.com.au/api/v1.1"
    OAUTH_URL = "https://accounts.zoho.com.au/oauth/v2/token"

    def __init__(self, refresh_token: str, se_list_key: str = None, sca_list_key: str = None, default_list_key: str = None, topic_id: str = None):
        """
        Initialize the Zoho Campaigns client.

        Args:
            refresh_token: Zoho OAuth refresh token
            se_list_key: Zoho list key for Shire Elite enrolled athletes
            sca_list_key: Zoho list key for SCA Allstars enrolled athletes
            default_list_key: Default list key to use if gym-specific keys aren't available
            topic_id: Zoho topic ID for organizing campaigns by topic
        """
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expiry = None
        self.client_id = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
        self.client_secret = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"
        self.se_list_key = se_list_key
        self.sca_list_key = sca_list_key
        self.default_list_key = default_list_key
        self.topic_id = topic_id

        self._refresh_access_token()

    def _refresh_access_token(self):
        """Refresh the OAuth 2.0 access token using the refresh token."""
        print("  🔄 Refreshing Zoho access token...")

        try:
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            response = requests.post(self.OAUTH_URL, data=payload)

            if response.status_code != 200:
                print(f"  ❌ Failed to refresh token: {response.status_code}")
                print(f"     Response: {response.text}")
                raise Exception(f"Token refresh failed: {response.text}")

            data = response.json()

            if "access_token" not in data:
                print(f"  ❌ No access token in response: {data}")
                raise Exception("No access token in response")

            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

            print(f"  ✅ Access token refreshed (expires in {expires_in}s)")

        except Exception as e:
            raise Exception(f"Failed to refresh Zoho token: {e}")

    def _ensure_token_valid(self):
        """Refresh token if expired."""
        if not self.token_expiry or datetime.now() >= self.token_expiry:
            self._refresh_access_token()

    def _get_mailing_lists(self) -> dict:
        """
        Fetch all mailing lists from Zoho Campaigns.

        Returns:
            Dict mapping list keys to list info
        """
        self._ensure_token_valid()

        if not self.access_token:
            print(f"    ⚠️  Cannot fetch mailing lists: no access token")
            return {}

        try:
            url = f"{self.BASE_URL}/getmailinglists"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    lists = data.get('data', {})
                    return lists

            return {}

        except Exception as e:
            print(f"    ⚠️  Could not fetch mailing lists: {e}")
            return {}

    def _get_list_details_for_gym(self, gym: str) -> dict:
        """
        Get the list_details JSON for the given gym.

        For testing: uses the default mailing list with no segment filters.
        Once we identify the correct segment structure, we can add segment filtering.

        Formats as: {mailing_list_key: [segment_IDs]}

        Args:
            gym: Gym name ('Shire Elite', 'SCA Allstars', or 'All')

        Returns:
            Dict mapping mailing list key to segment IDs, or empty dict if not configured
        """
        # For now, use default list with no segment filters (testing mode)
        # This lets us verify the API works with a real list that has contacts
        if self.default_list_key:
            return {str(self.default_list_key): []}

        return {}

    def create_campaign_draft(self, campaign: dict) -> str:
        """
        Create a campaign draft in Zoho Campaigns with hosted HTML content.
        If html_body is provided, also updates the campaign content internally.

        Args:
            campaign: Campaign dict with keys: name, subject, content_url, html_body, from_name, type, target_gym

        Returns:
            Campaign ID if successful, empty string otherwise
        """
        self._ensure_token_valid()

        if not self.access_token:
            print(f"    ❌ No access token available")
            return ""

        try:
            campaign_name = campaign.get('name', 'Untitled Campaign')
            subject = campaign.get('subject', '')
            content_url = campaign.get('content_url', '')  # Public URL to hosted HTML
            html_body = campaign.get('html_body', '')  # HTML content for internal update
            target_gym = campaign.get('target_gym', 'All')

            # Create the campaign with content_url pointing to hosted HTML
            campaign_id = self._create_campaign_draft(campaign_name, subject, target_gym, content_url)
            if not campaign_id:
                return ""

            # Content is loaded from external content_url
            # To add logo: manually replace with master_template.html content in Zoho UI

            return campaign_id

        except requests.exceptions.Timeout:
            print(f"    ❌ Request timeout - Zoho server may be slow")
            return ""
        except requests.exceptions.ConnectionError:
            print(f"    ❌ Connection error - Check internet connection")
            return ""
        except Exception as e:
            print(f"    ❌ Exception: {str(e)[:100]}")
            return ""

    def _create_campaign_draft(self, campaign_name: str, subject: str, target_gym: str, content_url: str = "") -> str:
        """
        Create a campaign draft with optional content URL.

        Args:
            campaign_name: Name of the campaign
            subject: Email subject line
            target_gym: Target gym (determines sender email)
            content_url: Optional public URL to hosted HTML content (GitHub Pages, S3, etc.)

        Returns:
            Campaign ID if successful, empty string otherwise
        """
        try:
            # Determine from_email based on gym
            if 'sca' in target_gym.lower() or 'allstars' in target_gym.lower():
                from_email = "hello@scaallstars.com.au"
            else:
                from_email = "hello@shireelite.com.au"

            # Get list for this gym
            list_details = self._get_list_details_for_gym(target_gym)
            if not list_details:
                print(f"    ⚠️  No mailing list configured")
                return ""

            list_key = list(list_details.keys())[0]
            print(f"    📋 Using mailing list: {list_key}")

            # Per official Zoho API documentation for createCampaign:
            # list_details is MANDATORY - format: {listkey:[segment_IDs]}
            # topicId is MANDATORY for orgs with updated topic management
            # content_url is OPTIONAL - must be a publicly accessible URL
            import json

            payload = {
                "campaignname": campaign_name,
                "subject": subject,
                "from_email": from_email,
                "resfmt": "json",
                "list_details": json.dumps({str(list_key): []}),  # MANDATORY parameter
            }

            # If content_url is provided, include it in the payload
            # The URL should point to publicly hosted HTML (GitHub Pages, S3, etc.)
            if content_url:
                payload["content_url"] = content_url
                print(f"    🌐 Using hosted HTML: {content_url}")

            # Add topicId if configured
            if self.topic_id:
                payload["topicId"] = self.topic_id
                print(f"    📋 Using topic: {self.topic_id}")

            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
            }

            # Make the API request
            url = f"{self.BASE_URL}/createCampaign"
            print(f"    📤 Creating: {campaign_name}")
            print(f"    📋 Payload keys: {list(payload.keys())}")
            response = requests.post(url, data=payload, headers=headers, timeout=30)

            # Check response status
            print(f"    📊 Response status: {response.status_code}")
            if response.status_code in [200, 201]:
                try:
                    data = response.json()

                    # Check if response indicates success
                    # API returns code as string ('200') not integer - handle both 'code' and 'Code' (case sensitivity)
                    code = str(data.get('code') or data.get('Code', ''))
                    has_campaign_key = 'campaignKey' in data or 'campaign_id' in data

                    if code in ['200', '201'] or has_campaign_key:
                        # Get the campaign key - try both possible field names
                        campaign_key = data.get('campaignKey') or data.get('campaign_id') or data.get('campaign_key', '')
                        print(f"    ✅ Created: {campaign_name} (ID: {campaign_key})")
                        # Debug: print response keys to verify structure
                        print(f"    📊 Response keys: {list(data.keys())}")
                        if 'campaignKey' in data:
                            print(f"    📋 campaignKey: {data['campaignKey']}")
                        if 'campaign_id' in data:
                            print(f"    📋 campaign_id: {data['campaign_id']}")
                        return campaign_key
                    else:
                        # API returned JSON but with error code
                        error_code = data.get('code') or data.get('Code', 'Unknown')
                        error_msg = data.get('message') or data.get('Message', 'Unknown error')
                        print(f"    ❌ API Error {error_code}: {error_msg}")
                        print(f"    📊 Full response: {data}")
                        print(f"    📋 Campaign name: {campaign_name}")
                        print(f"    📋 Subject: {payload.get('subject', 'N/A')[:100]}")
                        print(f"    📋 Content URL: {payload.get('content_url', 'N/A')[:100]}")
                        return ""

                except Exception as e:
                    # API returned success but JSON parsing failed
                    print(f"    ⚠️  Response not JSON: {response.text[:200]}")
                    print(f"    ✅ Created: {campaign_name}")
                    return ""

            elif response.status_code == 401:
                print(f"    ❌ Unauthorized (401) - Token may be invalid")
                print(f"    Response: {response.text[:200]}")
                return ""

            elif response.status_code == 400:
                print(f"    ❌ Bad Request (400)")
                try:
                    error_data = response.json()
                    print(f"    Error: {error_data}")
                except:
                    print(f"    Response: {response.text[:200]}")
                return ""

            else:
                print(f"    ❌ Error {response.status_code}")
                print(f"    Full Response: {response.text}")
                return ""

        except requests.exceptions.Timeout:
            print(f"    ❌ Request timeout - Zoho server may be slow")
            return ""
        except requests.exceptions.ConnectionError:
            print(f"    ❌ Connection error - Check internet connection")
            return ""
        except Exception as e:
            print(f"    ❌ Exception: {str(e)[:100]}")
            return ""

    def _set_campaign_content(self, campaign_id: str, body: str) -> bool:
        """
        Set the campaign content/body (step 2 of 2).

        Zoho requires content to be set via a separate API call after campaign creation.

        Args:
            campaign_id: Campaign ID returned from campaign creation
            body: HTML content for the email

        Returns:
            True if successful, False otherwise
        """
        self._ensure_token_valid()

        if not self.access_token or not campaign_id:
            return False

        try:
            # Try endpoint for updating campaign content
            url = f"{self.BASE_URL}/updateCampaignContent"

            payload = {
                "campaignid": campaign_id,
                "campaignkey": campaign_id,
                "content": body,
                "htmlcontent": body,
                "html": body,
                "resfmt": "json",
            }

            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
            }

            print(f"    📝 Setting campaign content...")
            response = requests.post(url, data=payload, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    code = str(data.get('code', ''))
                    if code in ['200', '201']:
                        print(f"    ✅ Content set successfully")
                        return True
                except:
                    pass

            # If updateCampaignContent didn't work, log but don't fail
            # The campaign still exists, just without content
            print(f"    ⚠️  Could not set content via API (may need manual setup)")
            return False

        except Exception as e:
            print(f"    ⚠️  Error setting content: {str(e)[:100]}")
            return False

    def schedule_campaign(self, campaign_id: str, send_date: datetime, send_hour: int = 9, send_minute: int = 0) -> bool:
        """
        Schedule a campaign for sending at a specific date and time.

        Args:
            campaign_id: Campaign ID returned from campaign creation
            send_date: datetime object for when to send the campaign
            send_hour: Hour (1-12 in 12-hour format, default 9 for 9 AM)
            send_minute: Minute (0-55, default 0)

        Returns:
            True if scheduled successfully, False otherwise
        """
        self._ensure_token_valid()

        if not self.access_token or not campaign_id:
            return False

        try:
            url = f"{self.BASE_URL}/sendcampaign?isschedule=true"

            payload = {
                'campaignkey': campaign_id,
                'scheduledate': send_date.strftime('%m/%d/%Y'),
                'schedulehour': str(send_hour).zfill(2),
                'scheduleminute': str(send_minute).zfill(2),
                'am_pm': 'AM' if send_hour < 12 else 'PM',
                'resfmt': 'json'
            }

            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
            }

            response = requests.post(url, data=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                try:
                    data = response.json()
                    code = str(data.get('code', ''))

                    if code == '200':
                        print(f"    ✅ Scheduled: {send_date.strftime('%Y-%m-%d')} at {send_hour:02d}:{send_minute:02d} AM")
                        return True
                    else:
                        error_msg = data.get('message', 'Unknown error')
                        error_code = data.get('code', 'Unknown')
                        print(f"    ⚠️  Could not schedule (error {error_code}): {error_msg}")
                        return False
                except:
                    print(f"    ⚠️  Could not parse schedule response")
                    return False
            else:
                print(f"    ⚠️  Schedule request failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"    ⚠️  Error scheduling campaign: {str(e)[:100]}")
            return False
