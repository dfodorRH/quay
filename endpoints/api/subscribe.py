"""
Subscribe to plans.
"""
import logging
import stripe
import features
from app import billing
from endpoints.api import request_error, log_action
from data.billing import PLANS
from endpoints.api.subscribe_models_pre_oci import data_model as model
from endpoints.exception import NotFound


logger = logging.getLogger(__name__)


def check_repository_usage(user_or_org, plan_found):
    private_repos = model.get_private_repo_count(user_or_org.username)
    if plan_found is None:
        repos_allowed = 0
    else:
        repos_allowed = plan_found["privateRepos"]

    if private_repos > repos_allowed:
        model.create_unique_notification(
            "over_private_usage", user_or_org.username, {"namespace": user_or_org.username}
        )
    else:
        model.delete_notifications_by_kind(user_or_org.username, "over_private_usage")


def carderror_response(exc):
    return {"carderror": str(exc)}, 402


def connection_response(exc):
    return {"message": "Could not contact Stripe. Please try again."}, 503


def subscription_view(stripe_subscription, used_repos):
    view = {
        "hasSubscription": True,
        "isExistingCustomer": True,
        "currentPeriodStart": stripe_subscription.current_period_start,
        "currentPeriodEnd": stripe_subscription.current_period_end,
        "plan": stripe_subscription.plan.id,
        "usedPrivateRepos": used_repos,
        "trialStart": stripe_subscription.trial_start,
        "trialEnd": stripe_subscription.trial_end,
    }

    return view


def get_price(plan, require_business_plan):
    """Billing Price (previously stripe Plan) from id."""
    if not features.BILLING:
        return

    plan_found = None
    for plan_obj in PLANS:
        if plan_obj["stripeId"] == plan:
            plan_found = plan_obj

    if not plan_found or plan_found["deprecated"]:
        logger.warning("Plan not found or deprecated: %s", plan)
        raise NotFound()

    if require_business_plan and not plan_found["bus_features"] and not plan_found["price"] == 0:
        logger.warning("Business attempting to subscribe to personal plan: %s", user.username)
        raise request_error(message="No matching plan found")

    return plan_found


def change_subscription(user, plan):
    private_repos = model.get_private_repo_count(user.username)

    # This is the default response
    response_json = {
        "plan": plan,
        "usedPrivateRepos": private_repos,
    }
    status_code = 200

    try:
        cus = billing.Customer.retrieve(user.stripe_id)
    except stripe.error.APIConnectionError as e:
        return connection_response(e)

    if plan["price"] == 0:
        if cus.subscription is not None:
            # We only have to cancel the subscription if they actually have one
            try:
                billing.Subscription.delete(cus.subscription.id)
            except stripe.error.APIConnectionError as e:
                return connection_response(e)

            check_repository_usage(user, plan)
            log_action("account_change_plan", user.username, {"plan": plan["stripeId"]})

    else:
        # User may have been a previous customer who is resubscribing
        modify_cus_args = {"plan": plan["stripeId"], "payment_behavior": "default_incomplete"}

        try:
            billing.Customer.modify(cus.id, **modify_cus_args)
        except stripe.error.CardError as e:
            return carderror_response(e)
        except stripe.error.APIConnectionError as e:
            return connection_response(e)

        cus = cus.refresh()
        response_json = subscription_view(cus.subscription, private_repos)
        check_repository_usage(user, plan)
        log_action("account_change_plan", user.username, {"plan": plan["stripeId"]})

    return response_json, status_code
