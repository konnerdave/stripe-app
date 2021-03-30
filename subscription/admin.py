from django.contrib import admin

from subscription.models import Plan, Subscription


class PlanAdmin(admin.ModelAdmin):
    """
    Plan admin
    """

    model = Plan
    list_display = ("name", "created_at", "updated_at")


admin.site.register(Plan, PlanAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    """
    Subscription admin
    """

    model = Subscription
    list_display = ("plan", "user", "is_active", "created_at", "updated_at")


admin.site.register(Subscription, SubscriptionAdmin)
