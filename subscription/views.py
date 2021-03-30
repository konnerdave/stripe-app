import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from subscription.models import Plan, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(login_required, name="dispatch")
class SubscriptionView(View):
    def post(self, request, *args, **kwargs):
        DOMAIN = "http://127.0.0.1:8000"

        # Get plan id
        pk = self.kwargs["pk"]
        # Get the plan from id
        plan = Plan.objects.get(id=pk)

        customer = stripe.Customer.create(
            email=request.user.email,
        )

        try:
            # Create a checkout session
            session = stripe.checkout.Session.create(
                customer=customer,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": plan.stripe_price,
                        "quantity": 1,
                    },
                ],
                metadata={"product_id": plan.stripe_product},
                mode="subscription",
                subscription_data={"trial_period_days": 7},
                success_url=f"{DOMAIN}/subscription/success/",
                cancel_url=f"{DOMAIN}/subscription/failure/",
            )

            # Get or create subscription with an updated customer id
            try:
                subscription = Subscription.objects.get(user=request.user)
                subscription.customer = customer.id
                subscription.save()

            except Subscription.DoesNotExist:
                subscription = Subscription.objects.create(
                    user=request.user, plan=plan, customer=customer.id
                )

            return JsonResponse({"id": session.id})

        except Exception as error:
            print(error)
            return JsonResponse({"error": "Something went wrong!"})


class ConfirmSubscriptionView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ConfirmSubscriptionView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # Get payload
        payload = request.body
        # Get header
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        # Intialize event
        event = None

        try:
            # Construct event
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Get the session
        session = event["data"]["object"]

        # Handle the checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            print(f"checkout.session.completed", event)
            # Get the email of the user
            email = session["customer_details"]["email"]
            # Get the user from the database
            user = User.objects.get(email=email)
            # Set the user subscription as active
            user.subscription.subscription = session["subscription"]
            user.subscription.is_active = True
            # Update the user subscription
            user.subscription.save()

            product_id = session["metadata"]["product_id"]

            # TODO - Can, send an email to the customer

        elif event["type"] == "customer.subscription.deleted":
            customer = session.customer
            # Get the subscription based on stripe customer
            subscription = Subscription.objects.get(customer=customer)
            # Set subscription as inactive
            subscription.is_active = False
            # Update the subscription
            subscription.save()
            print(f"customer.subscription.deleted", event)

        return HttpResponse(status=200)


class SuccessView(TemplateView):
    template_name = "subscription/success.html"


class FailureView(TemplateView):
    template_name = "subscription/failure.html"


class CancelSubscriptionView(View):
    def get(self, request):
        subscription = request.user.subscription
        stripe.Subscription.delete(subscription.subscription)
        return HttpResponseRedirect(reverse("cancelled"))


class CancelledView(TemplateView):
    template_name = "subscription/cancelled.html"
