import logging
import threading
from django.conf import settings
import resend
from resend import Emails

logger = logging.getLogger(__name__)


def _build_contact_html(cleaned_data: dict) -> str:
    work_type = cleaned_data.get('work_type') or 'General Enquiry'
    phone = cleaned_data.get('phone') or 'Not provided'
    message = cleaned_data.get('message') or 'No message provided'
    return f"""
    <h2 style="color:#1a3328;">New Enquiry — DJP Home Improvements</h2>
    <table style="font-family:sans-serif;font-size:15px;line-height:1.8;border-collapse:collapse;">
      <tr><td style="padding:4px 16px 4px 0;color:#4a7c62;font-weight:600;">Name</td><td>{cleaned_data['first_name']} {cleaned_data['last_name']}</td></tr>
      <tr><td style="padding:4px 16px 4px 0;color:#4a7c62;font-weight:600;">Email</td><td><a href="mailto:{cleaned_data['email']}">{cleaned_data['email']}</a></td></tr>
      <tr><td style="padding:4px 16px 4px 0;color:#4a7c62;font-weight:600;">Phone</td><td>{phone}</td></tr>
      <tr><td style="padding:4px 16px 4px 0;color:#4a7c62;font-weight:600;">Service</td><td>{work_type}</td></tr>
    </table>
    <p style="font-family:sans-serif;font-size:15px;margin-top:16px;">
      <strong style="color:#4a7c62;">Message:</strong><br>{message}
    </p>
    """


def _build_confirmation_html(cleaned_data: dict) -> str:
    work_type = cleaned_data.get('work_type') or 'General Enquiry'
    phone = cleaned_data.get('phone') or 'Not provided'
    first_name = cleaned_data['first_name']
    return f"""
    <div style="font-family:'Jost',Arial,sans-serif;max-width:580px;margin:0 auto;background:#f5f2ec;padding:40px 20px;">
      <div style="background:#1a3328;padding:32px 36px;text-align:center;">
        <div style="font-family:'Georgia',serif;font-size:2rem;color:#c9a84c;letter-spacing:4px;font-weight:400;">DJP</div>
        <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);letter-spacing:3px;text-transform:uppercase;margin-top:4px;">Home Improvements Ltd</div>
      </div>
      <div style="background:#ffffff;padding:40px 36px;border:1px solid #d8d3c8;">
        <p style="font-size:0.72rem;letter-spacing:3px;text-transform:uppercase;color:#4a7c62;margin-bottom:8px;">Enquiry Received</p>
        <h1 style="font-family:'Georgia',serif;font-size:1.8rem;color:#1a3328;margin:0 0 20px;font-weight:500;line-height:1.2;">Thank you, {first_name}.</h1>
        <p style="font-size:0.92rem;color:#5a5a5a;line-height:1.8;margin-bottom:16px;">
          We've received your enquiry and one of our team will be in touch within <strong>24 hours</strong> to discuss your project.
        </p>
        <p style="font-size:0.92rem;color:#5a5a5a;line-height:1.8;margin-bottom:28px;">
          In the meantime, if you need to reach us urgently, feel free to call us directly.
        </p>
        <div style="border-left:3px solid #c9a84c;padding:16px 20px;background:#f5f2ec;margin-bottom:28px;">
          <p style="margin:0 0 6px;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;color:#4a7c62;font-weight:600;">Your Enquiry Summary</p>
          <p style="margin:4px 0;font-size:0.88rem;color:#1c1c1c;"><strong>Service:</strong> {work_type}</p>
          <p style="margin:4px 0;font-size:0.88rem;color:#1c1c1c;"><strong>Phone:</strong> {phone}</p>
        </div>
        <div style="text-align:center;margin-top:32px;padding-top:24px;border-top:1px solid #d8d3c8;">
          <p style="font-size:0.78rem;color:#4a7c62;letter-spacing:1px;margin-bottom:4px;">&#128222; 07415 143796</p>
          <p style="font-size:0.78rem;color:#4a7c62;letter-spacing:1px;margin-bottom:4px;">&#9993; Enquire@djphomeimprovements.co.uk</p>
          <p style="font-size:0.78rem;color:#4a7c62;letter-spacing:1px;">Essex &amp; Surrounding Areas</p>
        </div>
      </div>
      <div style="text-align:center;padding:20px;">
        <p style="font-size:0.72rem;color:#999;letter-spacing:1px;">&copy; 2025 DJP Home Improvements Ltd &middot; Registered in England &amp; Wales</p>
      </div>
    </div>
    """


def _send_single(payload: dict) -> None:
    """Fire a single Resend email; logs on failure."""
    try:
        Emails.send(payload)
    except Exception as exc:
        logger.error("Resend send failed to %s — %s", payload.get('to'), exc, exc_info=True)
        raise


def send_contact_emails(cleaned_data: dict) -> None:
    """
    Send both the internal enquiry email and the user confirmation email.
    Both are dispatched in parallel threads so the view doesn't wait twice.
    Raises if either call fails (threads re-raise into the main thread).
    """
    if not settings.RESEND_API_KEY:
        raise ValueError("Missing RESEND_API_KEY in settings")

    resend.api_key = settings.RESEND_API_KEY

    sender    = settings.RESEND_EMAIL_FROM
    recipient = settings.RESEND_EMAIL_TO
    work_type = cleaned_data.get('work_type') or 'General'

    enquiry_payload = {
        "from":     sender,
        "to":       [recipient],
        "reply_to": cleaned_data["email"],
        "subject":  f"New enquiry from {cleaned_data['first_name']} {cleaned_data['last_name']} — {work_type}",
        "html":     _build_contact_html(cleaned_data),
    }

    confirmation_payload = {
        "from":    sender,
        "to":      [cleaned_data["email"]],
        "subject": "We've received your enquiry — DJP Home Improvements",
        "html":    _build_confirmation_html(cleaned_data),
    }

    errors = []

    def run(payload):
        try:
            _send_single(payload)
        except Exception as exc:
            errors.append(exc)

    threads = [
        threading.Thread(target=run, args=(enquiry_payload,)),
        threading.Thread(target=run, args=(confirmation_payload,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if errors:
        raise errors[0]  # surface the first error to the view