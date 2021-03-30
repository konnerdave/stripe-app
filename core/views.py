from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView

from subscription.models import Plan

# Create your views here.


class HomeView(TemplateView):
    template_name="core/index.html"

    def get_context_data(self, **kwargs):
        plan = Plan.objects.get(pk=1)
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            "plan": plan,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
        })
        return context
