"""
Email Templates for Different Event Types

Simplified templates focused on content, minimal styling to fit Zoho's length limits.
"""

from typing import Dict


class EmailTemplates:
    """Collection of email templates for different gym event types."""

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
    def _template_events() -> Dict:
        """Template for events and competitions."""
        return {
            'subject': lambda name, date: f"📢 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name}</h2>
<p><strong>Date:</strong> {date}</p>
<p>You're invited to this exciting event! Check your calendar and join us.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Learn More'
        }

    @staticmethod
    def _template_terms() -> Dict:
        """Template for term information."""
        return {
            'subject': lambda name, date: f"📅 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name} – {date}</h2>
<p>A new term is starting! Review your schedule and prepare for the upcoming events.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'View Calendar'
        }

    @staticmethod
    def _template_gym_closures() -> Dict:
        """Template for facility closures."""
        return {
            'subject': lambda name, date: f"🔒 Gym Closure Notice – {date}",
            'body': lambda name, date, event: f"""<html><body>
<h2>⏸️ We're Closed {date}</h2>
<p>Our facility will be closed during this period for maintenance and staff break.</p>
<p><strong>We'll be back and ready for you!</strong></p>
<p>If you have any urgent questions, please don't hesitate to contact us.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Contact Us'
        }

    @staticmethod
    def _template_catch_ups() -> Dict:
        """Template for check-ins and meetings."""
        return {
            'subject': lambda name, date: f"📞 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name}</h2>
<p><strong>Date:</strong> {date}</p>
<p>We'd like to catch up with you. This is a great opportunity to discuss your goals and progress.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Mark Calendar'
        }

    @staticmethod
    def _template_fees() -> Dict:
        """Template for payment reminders."""
        return {
            'subject': lambda name, date: f"💳 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name}</h2>
<p><strong>Due:</strong> {date}</p>
<p>A friendly reminder about an upcoming payment. Please ensure payment is made by this date.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Make Payment'
        }

    @staticmethod
    def _template_cheer_clinics() -> Dict:
        """Template for cheer clinics and workshops."""
        return {
            'subject': lambda name, date: f"🎀 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name}</h2>
<p><strong>Date:</strong> {date}</p>
<p>Join us for this exciting clinic! Learn new skills and techniques from experienced instructors. Perfect for all levels.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Sign Up'
        }

    @staticmethod
    def _template_holiday_clinics() -> Dict:
        """Template for grouped holiday clinic sessions (e.g., all Winter Holiday Clinics together)."""
        return {
            'subject': lambda name, date: f"🎀 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>✨ Holiday Clinics Coming Up!</h2>
<p><strong>{name}</strong></p>
<p><strong>Dates:</strong> {date}</p>
<p>Don't let the holidays be boring! Join us for exciting clinic sessions where members can improve their skills, make new friends, and have a blast.</p>
<p><strong>What to expect:</strong></p>
<ul>
<li>Fun, high-energy sessions</li>
<li>Learn new techniques</li>
<li>Perfect for all levels</li>
</ul>
<p>Spots fill up fast during holidays—secure your place today!</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Register Now'
        }

    @staticmethod
    def _template_important_dates() -> Dict:
        """Template for important dates and deadlines."""
        return {
            'subject': lambda name, date: f"📌 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name}</h2>
<p><strong>Date:</strong> {date}</p>
<p>This is an important date to remember. Mark it in your calendar and stay tuned for more details.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
            'cta_text': 'Learn More'
        }

    @staticmethod
    def _template_other() -> Dict:
        """Default template for other event types."""
        return {
            'subject': lambda name, date: f"📌 {name}",
            'body': lambda name, date, event: f"""<html><body>
<h2>{name}</h2>
<p><strong>Date:</strong> {date}</p>
<p>Save the date! More details coming soon.</p>
<p>Best,<br>Your Gym Team</p>
</body></html>""",
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
