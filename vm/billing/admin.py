from django.contrib import admin

from autovm.billing.models import BillingAccount
from autovm.billing.models import RatePlan
from autovm.billing.models import Subscription
from autovm.billing.models import Transaction


@admin.register(RatePlan)
class RatePlanAdmin(admin.ModelAdmin):
    """
    Rate plan admin panel
    """

    list_display = ["plan", "price", "vm_limit", "backup_limit"]
    search_fields = ["plan", "price", "vm_limit", "backup_limit"]
    list_filter = ["plan", "price", "vm_limit", "backup_limit"]


@admin.register(BillingAccount)
class BillingAccountAdmin(admin.ModelAdmin):
    """
    Billing account admin panel
    """

    list_display = ["user", "amount"]
    search_fields = ["user", "amount"]
    list_filter = ["user", "amount"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Subscription admin panel
    """

    list_display = ["plan", "account", "status"]
    search_fields = ["plan", "account", "status"]
    list_filter = ["plan", "status"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Transaction admin panel
    """

    list_display = ["account", "amount", "status"]
    search_fields = ["account", "amount", "status"]
    list_filter = ["account", "amount", "status"]
