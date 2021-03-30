from django.urls import path

from subscription.views import (
    SubscriptionView,
    SuccessView,
    FailureView,
    ConfirmSubscriptionView,
    CancelSubscriptionView,
    CancelledView,
)


urlpatterns = [
    path("webhook/", ConfirmSubscriptionView.as_view(), name="webhook"),
    path("checkout/<pk>/", SubscriptionView.as_view(), name="checkout"),
    path("success/", SuccessView.as_view(), name="success"),
    path("failure/", FailureView.as_view(), name="failure"),
    path("cancel-subscription/", CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path("cancelled/", CancelledView.as_view(), name="cancelled"),
]
