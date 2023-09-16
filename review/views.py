from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView
from review.models import *
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SignUpForm


class HomeView(TemplateView):
    template_name = "review/home.html"

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "review/signup.html"
    success_url = reverse_lazy("review:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())
