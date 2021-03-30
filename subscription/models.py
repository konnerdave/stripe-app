from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models

from core.models import NamedModel, TimeStampedModel


class Plan(NamedModel, TimeStampedModel):
    MONTHLY = "M"

    RECURRENCE = [
        (MONTHLY, "Monthly"),
    ]
    stripe_product = models.TextField(
        "stripe product id",
        blank=True,
        null=True,
        help_text="Stripe product id, please!",
    )
    stripe_price = models.TextField(
        "stripe product price id",
        blank=True,
        null=True,
        help_text="Stripe product price id, please!",
    )
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0.0)
    duration = models.CharField(
        max_length=1,
        choices=RECURRENCE,
        default=MONTHLY,
    )

    def __str__(self):
        return f"{self.name} - {self.duration}"

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)


class Subscription(TimeStampedModel):
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="subscriptions"
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="subscription"
    )
    customer = models.TextField("stripe customer", blank=True, null=True)
    subscription = models.TextField("stripe subscription", blank=True, null=True)
    start_date = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        db_index=True,
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.plan}"

    @property
    def end_date(self):
        self.start_date += timedelta(days=7)

    @property
    def expired(self):
        self.end_date > self.start_date
