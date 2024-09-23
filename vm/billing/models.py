import uuid

from django.db import models

from autovm.users.models import User


class CommonBaseModel(models.Model):
    """
    Common fields shared in this app
    """

    _id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        primary_key=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Errata for all models
        """

        abstract = True
        ordering = ["-created"]


class RatePlan(CommonBaseModel):
    """
    Rate plan model.
    """

    SUBSCRIPTION_OPTS = (
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
    )
    plan = models.CharField(max_length=10, choices=SUBSCRIPTION_OPTS, default="bronze")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vm_limit = models.IntegerField(default=2)
    backup_limit = models.IntegerField(default=2)

    def __str__(self) -> str:
        return self.plan


class BillingAccount(CommonBaseModel):
    """
    A virtual space for the amount the user has within the system
    """

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=200)

    def __str__(self):
        return f"{self.user}: {self.amount}"


class Subscription(CommonBaseModel):
    """
    Rates at which users can subscribe to the platform.
    users can see previous subscriptions and current subscriptions
    """

    plan = models.ForeignKey(RatePlan, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(BillingAccount, on_delete=models.SET_NULL, null=True)
    STATUS = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )
    status = models.CharField(max_length=10, choices=STATUS, default="active")

    def __str__(self):
        return f"{self.account}: {self.plan} plan"


class Transaction(CommonBaseModel):
    """
    This model is used to store transaction details.
    """

    STATUS = (
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )
    account = models.ForeignKey(
        BillingAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=8, null=True)
    transaction_no = models.CharField(max_length=255, null=True, blank=True)
    receipt_no = models.CharField(max_length=255, null=True, blank=True)
    payment_ref = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default="processing")

    def __str__(self):
        return f"{self.account}:{self.get_status_display()}"
