"""
Email Templates for Different Event Types

Professional email templates with responsive design, Outlook compatibility,
and styling suitable for email clients.
"""

from typing import Dict


class EmailTemplates:
    """Collection of professional email templates for gym event types."""

    # Brand colors - customize these for your gym
    PRIMARY_COLOR = "#d4164e"  # Shire Elite branded pink/magenta
    ACCENT_COLOR = "#f4bbdd"   # Light pink for highlights
    DARK_TEXT = "#333333"
    FOOTER_BG = "#f5f5f5"
    BUTTON_COLOR = "#d4164e"

    @staticmethod
    def get_template(event_type: str) -> Dict:
        """Get the email template for a given event type."""
        event_type = event_type.strip().lower()

        templates = {
            'events': EmailTemplates._template_events(),
            'terms': EmailTemplates._template_terms(),
            'gym closures': EmailTemplates._template_gym_closures(),
            'catch ups': EmailTemplates._template_catch_ups(),
            'fees': EmailTemplates._template_fees(),
            'cheer clinics': EmailTemplates._template_cheer_clinics(),
            'holiday clinics': EmailTemplates._template_holiday_clinics(),
            'important dates': EmailTemplates._template_important_dates(),
            'other': EmailTemplates._template_other()
        }

        return templates.get(event_type, templates['other'])

    @staticmethod
    def _base_template(title: str, content_html: str, cta_button: tuple = None) -> str:
        """
        Create a professional email template with responsive design.

        Args:
            title: Email title/heading
            content_html: Main content HTML
            cta_button: Tuple of (button_text, button_color) or None

        Returns:
            Complete HTML email template
        """
        button_html = ""
        if cta_button:
            btn_text, btn_color = cta_button
            button_html = f"""
            <table cellpadding="0" cellspacing="0" style="margin: 20px 0; width: 100%;">
              <tr>
                <td style="text-align: center;">
                  <table cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                    <tr>
                      <td style="background-color: {btn_color}; border-radius: 4px; padding: 12px 30px;">
                        <a href="#" style="color: white; text-decoration: none; font-weight: bold; font-size: 16px; display: block;">
                          {btn_text}
                        </a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            """

        footer_html = """
            <table cellpadding="0" cellspacing="0" style="width: 100%; background-color: #f5f5f5; margin-top: 30px;">
              <tr>
                <td style="padding: 20px; text-align: center; color: #666666; font-size: 12px;">
                  <p style="margin: 5px 0;">Shire Elite Gyms</p>
                  <p style="margin: 5px 0;">
                    <a href="#" style="color: #d4164e; text-decoration: none; margin: 0 8px;">Contact Us</a> |
                    <a href="#" style="color: #d4164e; text-decoration: none; margin: 0 8px;">Preferences</a> |
                    <a href="#" style="color: #d4164e; text-decoration: none; margin: 0 8px;">Unsubscribe</a>
                  </p>
                </td>
              </tr>
            </table>
        """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shire Elite</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #333333;
      margin: 0;
      padding: 0;
      background-color: #f9f9f9;
    }}
    table {{
      border-collapse: collapse;
    }}
    img {{
      max-width: 100%;
      height: auto;
      display: block;
    }}
    a {{
      color: #d4164e;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: white;
    }}
    .header {{
      background: linear-gradient(135deg, #d4164e 0%, #e63a6b 100%);
      color: white;
      padding: 30px 20px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 28px;
      font-weight: bold;
    }}
    .content {{
      padding: 30px 20px;
      color: #333333;
    }}
    .content h2 {{
      color: #d4164e;
      font-size: 24px;
      margin-top: 0;
      margin-bottom: 15px;
    }}
    .content p {{
      margin: 10px 0;
      font-size: 15px;
    }}
    .highlight {{
      background-color: #f4bbdd;
      padding: 15px;
      border-left: 4px solid #d4164e;
      margin: 15px 0;
    }}
    .highlight strong {{
      color: #d4164e;
    }}
    .event-list {{
      margin: 15px 0;
    }}
    .event-list li {{
      margin: 8px 0;
    }}
    @media (max-width: 480px) {{
      .container {{
        width: 100% !important;
      }}
      .content {{
        padding: 20px 15px;
      }}
      .header {{
        padding: 20px 15px;
      }}
      .header h1 {{
        font-size: 22px;
      }}
      .content h2 {{
        font-size: 20px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <table cellpadding="0" cellspacing="0" style="width: 100%;">
      <tr>
        <td style="background: linear-gradient(135deg, #d4164e 0%, #e63a6b 100%); color: white; padding: 30px 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px; font-weight: bold;">{title}</h1>
        </td>
      </tr>
      <tr>
        <td style="padding: 30px 20px; color: #333333;">
          {content_html}
          {button_html}
        </td>
      </tr>
      <tr>
        <td style="padding: 0;">
          {footer_html}
        </td>
      </tr>
    </table>
  </div>
</body>
</html>"""

    @staticmethod
    def _template_events() -> Dict:
        """Template for events and competitions."""
        return {
            'subject': lambda name, date: f"📢 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                name,
                f"""<p style="font-size: 16px;">You're invited to an exciting event!</p>
<div class="highlight">
  <strong>📅 Date:</strong> {date}<br>
  <strong>📍 Location:</strong> Shire Elite Gyms
</div>
<p>Join us for this amazing opportunity to compete, challenge yourself, and be part of our gym community. Whether you're competing or cheering, this promises to be an unforgettable event!</p>
<p>Get ready to shine! 🌟</p>""",
                ('Learn More & Register', '#d4164e')
            ),
            'cta_text': 'Learn More'
        }

    @staticmethod
    def _template_terms() -> Dict:
        """Template for term information."""
        return {
            'subject': lambda name, date: f"📅 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                f"Term Begins – {date}",
                f"""<p style="font-size: 16px;">Get ready for an exciting new term!</p>
<div class="highlight">
  <strong>Term Start:</strong> {date}
</div>
<p>A new term is here and we're thrilled to have you back! Review your schedule, check out the upcoming events, and make sure you're ready for all the action ahead.</p>
<p>You'll receive reminders for all upcoming events throughout the term.</p>""",
                ('View Full Calendar', '#d4164e')
            ),
            'cta_text': 'View Calendar'
        }

    @staticmethod
    def _template_gym_closures() -> Dict:
        """Template for facility closures."""
        return {
            'subject': lambda name, date: f"🔒 Gym Closure Notice – {date}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                "We're Closed",
                f"""<div class="highlight" style="background-color: #fff3cd; border-left-color: #ff6b6b;">
  <strong style="color: #ff6b6b;">⏸️ Closed: {date}</strong>
</div>
<p>Our facility will be closed during this period for maintenance and staff break. We appreciate your patience!</p>
<p><strong>We'll be back and ready for you!</strong></p>
<p>If you have any urgent questions or concerns, please don't hesitate to reach out to us. We're here to help!</p>""",
                ('Contact Us', '#ff6b6b')
            ),
            'cta_text': 'Contact Us'
        }

    @staticmethod
    def _template_catch_ups() -> Dict:
        """Template for check-ins and meetings."""
        return {
            'subject': lambda name, date: f"📞 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                "Let's Catch Up",
                f"""<p style="font-size: 16px;">We'd love to connect with you!</p>
<div class="highlight">
  <strong>📅 When:</strong> {date}
</div>
<p>We believe in building strong relationships with our community. This is a great opportunity to:</p>
<ul class="event-list">
  <li>Discuss your goals and progress</li>
  <li>Get personalized feedback</li>
  <li>Learn about new programs and opportunities</li>
</ul>
<p>We look forward to seeing you!</p>""",
                ('Schedule Your Catch-up', '#d4164e')
            ),
            'cta_text': 'Mark Calendar'
        }

    @staticmethod
    def _template_fees() -> Dict:
        """Template for payment reminders."""
        return {
            'subject': lambda name, date: f"💳 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                "Payment Reminder",
                f"""<div class="highlight" style="background-color: #fff3cd; border-left-color: #ffc107;">
  <strong style="color: #ff6b6b;">Due: {date}</strong>
</div>
<p>This is a friendly reminder about an upcoming payment.</p>
<p><strong>Please ensure payment is made by the due date to keep your membership active.</strong></p>
<p>Payment is quick and easy through our online portal. If you have any questions or need assistance, our team is here to help!</p>""",
                ('Make Payment Now', '#d4164e')
            ),
            'cta_text': 'Make Payment'
        }

    @staticmethod
    def _template_cheer_clinics() -> Dict:
        """Template for cheer clinics and workshops."""
        return {
            'subject': lambda name, date: f"🎀 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                "Cheer Clinic Reminder",
                f"""<p style="font-size: 16px;">Don't miss this exciting clinic!</p>
<div class="highlight">
  <strong>📅 Date:</strong> {date}
</div>
<p>Join us for an amazing cheer clinic! Learn new skills and techniques from our experienced instructors in a fun, supportive environment.</p>
<p><strong>What to expect:</strong></p>
<ul class="event-list">
  <li>✨ Learn new skills and techniques</li>
  <li>✨ Fun, high-energy sessions</li>
  <li>✨ Perfect for all levels</li>
  <li>✨ Make new friends and be part of the cheer family</li>
</ul>
<p>Spots are limited—secure yours today!</p>""",
                ('Sign Up Now', '#d4164e')
            ),
            'cta_text': 'Sign Up'
        }

    @staticmethod
    def _template_holiday_clinics() -> Dict:
        """Template for grouped holiday clinic sessions."""
        return {
            'subject': lambda name, date: f"Holiday Clinics - {date.split('/')[0].strip() if '/' in date else date}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                "Holiday Clinics Coming Up!",
                f"""<p style="font-size: 16px;">Don't let the holidays be boring!</p>
<div class="highlight">
  <strong>Dates:</strong> {date}
</div>
<p>Join us for exciting clinic sessions where you can improve your skills, make new friends, and have an absolute blast!</p>
<p><strong>Why attend our holiday clinics?</strong></p>
<ul class="event-list">
  <li>🎯 Fun, high-energy sessions led by experienced coaches</li>
  <li>🎯 Learn new techniques and perfect your skills</li>
  <li>🎯 Perfect for all levels—beginner to advanced</li>
  <li>🎯 Build friendships with other team members</li>
  <li>🎯 Keep your skills sharp over the break</li>
</ul>
<p><strong style="color: #ff6b6b;">⚡ Spots fill up FAST during holidays—secure your place today!</strong></p>""",
                ('Register Now', '#d4164e')
            ),
            'cta_text': 'Register Now'
        }

    @staticmethod
    def _template_important_dates() -> Dict:
        """Template for important dates and deadlines."""
        return {
            'subject': lambda name, date: f"📌 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                "Important Date Reminder",
                f"""<div class="highlight">
  <strong>📅 Mark your calendar:</strong> {date}
</div>
<p>This is an important date to remember. We wanted to make sure it's on your radar!</p>
<p>Stay tuned for more details coming soon. In the meantime, make sure to block off this time in your calendar.</p>""",
                ('Add to Calendar', '#d4164e')
            ),
            'cta_text': 'Learn More'
        }

    @staticmethod
    def _template_other() -> Dict:
        """Default template for other event types."""
        return {
            'subject': lambda name, date: f"📌 {name}",
            'body': lambda name, date, event: EmailTemplates._base_template(
                name,
                f"""<div class="highlight">
  <strong>📅 Date:</strong> {date}
</div>
<p>Save the date! This is something special you won't want to miss.</p>
<p>More details are coming soon. We'll keep you updated every step of the way!</p>""",
                ('Learn More', '#d4164e')
            ),
            'cta_text': 'Learn More'
        }

    @staticmethod
    def render_template(event_type: str, event_name: str, event_date: str, event_dict: Dict) -> Dict:
        """Render a complete email from a template."""
        template = EmailTemplates.get_template(event_type)

        return {
            'subject': template['subject'](event_name, event_date),
            'body': template['body'](event_name, event_date, event_dict),
            'cta_text': template['cta_text']
        }
