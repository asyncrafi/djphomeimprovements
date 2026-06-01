import logging
from django.shortcuts import redirect, render
from .forms import ContactForm
from .utils import send_contact_emails

logger = logging.getLogger(__name__)


def home(request):
    success_message = None
    error_message = None

    if request.method == "POST":
        if request.POST.get("honeypot"):
            return redirect("/")

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
        },
    )