from django.db import transaction
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


from autovm.billing.models import RatePlan, BillingAccount, Subscription, Transaction
from autovm.billing.api.serializers import (
    RatePlanSerializer,
    SubscriptionSerializer,
    TransactionSerializer,
    BillingAccountSerializer,
)


class RatePlanViewSet(ModelViewSet):
    """
    Rate Plan viewset.
    """

    serializer_class = RatePlanSerializer
    queryset = RatePlan.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["plan", "price", "vm_limit", "backup_limit"]
    search_fields = ["plan", "price", "vm_limit", "backup_limit"]


class SubscriptionViewSet(ModelViewSet):
    """
    Subscription viewset.
    """

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["plan", "account", "account__user__id", "status"]
    search_fields = ["plan", "account__user__name", "account__user__email", "status"]


class TransactionViewSet(ModelViewSet):
    """
    Transaction viewset.
    """

    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        "amount",
        "account",
        "account__user__id",
        "account__user__email",
        "status",
    ]
    search_fields = ["amount", "account", "status"]

    def get_queryset(self) -> QuerySet:
        """
        Show all records if the user is admin else only for this user
        """
        if self.request.user.role == "admin":
            return Transaction.objects.all()
        return Transaction.objects.filter(account__user=self.request.user)


class BillingAccountViewSet(ModelViewSet):
    """
    Billing Account viewset.
    """

    serializer_class = BillingAccountSerializer
    queryset = BillingAccount.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["user", "amount", "user__id", "user__email"]
    search_fields = ["user", "amount"]

    @action(detail=False, methods=["post"])
    def deposit(self, request):
        """
        Deposit money into the user account.
        Work in progress: Creating a transaction will have the same effect.
        """
        user = request.user
        amount = request.data.get("amount")

        with transaction.atomic():
            account, created = BillingAccount.objects.get_or_create(user=user)
            account.amount += amount
            account.save()
            # thought:
            Transaction.objects.create(account=account, amount=amount)

        return Response(
            {"message": f"Successfully deposited {amount} into your account"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def balance(self, request):
        """
        Get the user account balance.
        """
        user = request.user
        account = BillingAccount.objects.get(user=user)
        return Response(
            {"balance": account.amount},
            status=status.HTTP_200_OK,
        )
