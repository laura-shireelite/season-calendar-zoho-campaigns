#!/usr/bin/env python3
"""
Generate a new Zoho refresh token compatible with your current OAuth credentials.

This script walks you through the OAuth authorization flow to get a fresh refresh token
that will work with your Client ID and Secret.
"""

import webbrowser
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Your current Zoho OAuth credentials
CLIENT_ID = "1000.VMOQZ5WQ8E7K0R7UE76X7B8ZL1ZQ0M"
CLIENT_SECRET = "e4435b8cc4b3de0bff11171caacdefe6ed5d233127"
REDIRECT_URI = "http://localhost:8080/callback"

# Zoho OAuth endpoints (Australia region)
AUTH_URL = "https://accounts.zoho.com.au/oauth/v2/auth"
TOKEN_URL = "https://accounts.zoho.com.au/oauth/v2/token"

# Storage for the authorization code
auth_code = None
auth_event = threading.Event()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback from Zoho."""

    def do_GET(self):
        """Handle GET request from Zoho redirect."""
        global auth_code

        # Parse the callback URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if "code" in query_params:
            auth_code = query_params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
                <html>
                <head><title>Authorization Successful</title></head>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: green;">Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <p>Your refresh token is being generated...</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode())
            auth_event.set()
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            error = query_params.get("error", ["Unknown error"])[0]
            self.wfile.write(f"<html><body>Authorization failed: {error}</body></html>".encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def get_refresh_token():
    """Complete the OAuth flow to get a refresh token."""
    global auth_code

    print("\n" + "="*70)
    print("ZOHO OAUTH REFRESH TOKEN GENERATOR")
    print("="*70)

    print("\n📱 Starting OAuth authorization flow...")
    print(f"   Client ID: {CLIENT_ID}")

    # Step 1: Build authorization URL
    auth_url = (
        f"{AUTH_URL}?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=ZohoCampaigns.campaign.ALL&"
        f"access_type=offline"
    )

    print("\n🔗 Opening authorization URL in your browser...")
    print("   If the browser doesn't open, copy this URL:")
    print(f"   {auth_url}\n")

    # Step 2: Start local server to receive callback
    server = HTTPServer(("localhost", 8080), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Step 3: Open browser
    webbrowser.open(auth_url)

    # Step 4: Wait for callback
    print("⏳ Waiting for authorization...")
    print("   (Check your browser for the Zoho login screen)")
    auth_event.wait(timeout=300)  # 5 minute timeout

    server.shutdown()

    if not auth_code:
        print("❌ Authorization timed out or failed")
        return None

    print(f"✅ Authorization code received")

    # Step 5: Exchange code for refresh token
    print("\n🔄 Exchanging authorization code for refresh token...")

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    try:
        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        data = response.json()

        refresh_token = data.get("refresh_token")
        access_token = data.get("access_token")

        if refresh_token:
            print("✅ Refresh token generated successfully!")
            print("\n" + "="*70)
            print("YOUR NEW REFRESH TOKEN:")
            print("="*70)
            print(f"\n{refresh_token}\n")
            print("="*70)

            print("\n📝 Next steps:")
            print("   1. Copy the refresh token above")
            print("   2. Edit config.txt")
            print('   3. Replace the ZOHO_REFRESH_TOKEN line with:')
            print(f'      export ZOHO_REFRESH_TOKEN="{refresh_token}"')
            print("   4. Save config.txt")
            print("   5. Run: source config.txt")
            print("   6. Run: python3 main.py")

            return refresh_token
        else:
            error = data.get("error", "Unknown error")
            print(f"❌ Failed to get refresh token: {error}")
            print(f"   Full response: {data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    try:
        token = get_refresh_token()
        if token:
            print("\n✅ REFRESH TOKEN READY")
            print("   Copy it to config.txt and run main.py again")
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
