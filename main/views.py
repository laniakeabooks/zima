from django.conf import settings
from django.core.mail import mail_admins, send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from main import models


class CreateEntry(CreateView):
    model = models.Entry
    fields = ["email", "contact", "resource", "terms"]
    template_name = "main/index.html"

    def notify_admin(self):
        mail_admins(
            f"admin: new entry: {self.object.resource}",
            render_to_string(
                "main/admin_email.txt",
                {
                    "email": self.object.email,
                    "resource": self.object.resource,
                    "contact": self.object.contact,
                    "canonical_url": settings.CANONICAL_URL,
                },
            ),
        )

    def form_valid(self, form):
        if not form.cleaned_data.get("terms", False):
            form.add_error(
                "terms", "we’d love to but cannot proceed unless this is fine"
            )
            return super().form_invalid(form)

        self.object = form.save()
        url = f"{settings.CANONICAL_URL}{reverse_lazy('verify_success')}"
        url += f"?key={str(self.object.verify_key)}"
        subject = f"01z: verify email for {self.object.resource}"
        content = render_to_string(
            "main/welcome_email.txt",
            {
                "email": self.object.email,
                "resource": self.object.resource,
                "contact": self.object.contact,
                "verify_url": url,
            },
        )
        send_mail(subject, content, settings.DEFAULT_FROM_EMAIL, [self.object.email])
        self.notify_admin()
        return super().form_valid(form)

    def get_success_url(self):
        url = reverse_lazy("submit_success")
        url += "?key="
        url += str(self.object.verify_key)
        return url


def submit_success(request):
    if request.GET.get("key") is not None:
        return render(request, "main/submit_success.html")
    else:
        return redirect("index")


def verify_success(request):
    if request.GET.get("key") is not None:
        entry = get_object_or_404(
            models.Entry,
            verify_key=request.GET.get("key"),
        )
        entry = models.Entry.objects.get(verify_key=request.GET.get("key"))
        entry.is_verified = True
        entry.save()
        return render(request, "main/verify_success.html", {"email": entry.email})
    else:
        return redirect("index")


def about(request):
    return render(request, "main/about.html")


def privacy(request):
    return render(request, "main/privacy.html")
