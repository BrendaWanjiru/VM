import logging
from rest_framework import serializers

from autovm.billing.models import BillingAccount
from autovm.billing.models import RatePlan
from autovm.billing.models import Subscription
from autovm.billing.models import Transaction
from autovm.billing.utils.payment_client import PaymentClient

logger = logging.getLogger(__name__)


class RatePlanSerializer(serializers.ModelSerializer):
    """
    Rate plan serializer.
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = RatePlan
        fields = ["_id", "plan", "price", "vm_limit", "backup_limit"]


class BillingAccountSerializer(serializers.ModelSerializer):
    """
    A virtual space for the amount the user has within the system
    """

    class Meta:
        """
        Fields to render
        """

        model = BillingAccount
        fields = ["_id", "user", "amount"]


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Subscription serializer.
    """

    plan_info = RatePlanSerializer(source="plan", read_only=True)

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = Subscription
        fields = ["_id", "plan", "plan_info", "account", "status", "created"]

    def create(self, validated_data):
        """
        Create a new subscription.
        """
        user = self.context["request"].user

        user_account, created = BillingAccount.objects.get_or_create(user=user)

        validated_data["account"] = user_account
        plan = validated_data["plan"]
        # get or create a subscription
        # match the user account with the subscription. that is, only create
        # a new subscription if the user has an account
        subscription, created = Subscription.objects.get_or_create(
            account=user_account,
            status="active",
            defaults={"plan": plan},
        )

        updated_balance = user_account.amount - subscription.plan.price

        if updated_balance < 0:
            logger.info(f"Customer {user.email} has insufficient funds")
            raise serializers.ValidationError("Insufficient funds")

        if not created:
            subscription.status = "inactive"
            subscription.save()

        # create a new subscription
        subscription = Subscription.objects.create(account=user_account, plan=plan)
        # create a transaction related with this subscription
        details = PaymentClient().make_payment()

        transaction = Transaction.objects.create(
            account=user_account, amount=subscription.plan.price, **details
        )
        logger.info(f"Customer {user.email} has made a payment of {transaction.amount}")

        user_account.amount = updated_balance
        user_account.save()

        return subscription


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction serializer.
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = Transaction
        fields = "__all__"

    def create(self, validated_data):
        """
        Create a new transaction.
        """
        user = self.context["request"].user

        user_account, created = BillingAccount.objects.get_or_create(user=user)

        validated_data["account"] = user_account
        details = PaymentClient().make_payment()
        validated_data.update(details)
        transaction = Transaction.objects.create(**validated_data)
        logger.info(f"Customer {user.email} has made a payment of {transaction.amount}")
        # test
        # update the billing account
        # account = transaction.account
        user_account.amount += transaction.amount
        user_account.save()

        return transaction
