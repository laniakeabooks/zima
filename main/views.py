from random import randint

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from main import models


class CreateEntry(CreateView):
    model = models.Entry
    fields = ["contact", "resource"]
    template_name = "main/index.html"

    def get_success_url(self):
        url = reverse_lazy("submit_success")
        url += "?id="
        url += str(randint(1_000_000, 10_000_000))
        return url


def submit_success(request):
    if request.GET.get("id") is not None:
        return render(request, "main/submit_success.html")
    else:
        return redirect("index")


def about(request):
    return render(request, "main/about.html")
