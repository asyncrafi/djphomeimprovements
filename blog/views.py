import logging
import requests
from django.shortcuts import redirect, render
from django.conf import settings
from .forms import ContactForm
from .utils import send_contact_emails

logger = logging.getLogger(__name__)


def verify_recaptcha(token):
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': token,
            },
            timeout=5,
        )
        result = response.json()
        return result.get('success') and result.get('score', 0) >= settings.RECAPTCHA_SCORE_THRESHOLD
    except Exception as exc:
        logger.error("reCAPTCHA verification failed: %s", exc)
        return False


def home(request):
    success_message = None
    error_message = None

    if request.method == "POST":
        if request.POST.get("honeypot"):
            return redirect("/")

        recaptcha_token = request.POST.get("g-recaptcha-response")
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            error_message = "We couldn't verify your submission. Please try again."
            form = ContactForm(request.POST)
            return render(request, "blog/index.html", {
                "form": form,
                "error_message": error_message,
                "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
            })

        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                send_contact_emails(form.cleaned_data)
                logger.info(
                    "Contact enquiry sent — %s %s <%s>",
                    form.cleaned_data["first_name"],
                    form.cleaned_data["last_name"],
                    form.cleaned_data["email"],
                )
                success_message = (
                    "Thanks! Your enquiry has been sent. "
                    "Check your inbox for a confirmation email."
                )
                form = ContactForm()  # clear form on success
            except Exception as exc:
                logger.error("Failed to send contact emails: %s", exc, exc_info=True)
                error_message = (
                    "We couldn't send your enquiry right now. "
                    "Please try again or call us directly."
                )
        else:
            error_message = "Please check the highlighted fields and try again."
    else:
        form = ContactForm()

    return render(
        request,
        "blog/index.html",
        {
            "form": form,
            "success_message": success_message,
            "error_message": error_message,
            "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
        },
    )