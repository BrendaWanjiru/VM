from django.conf import settings
from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter

from vm.users.api.views import (
    UserViewSet,
    GeneralAdminViewSet,
    CustomerViewset,
    GuestViewset,
    GoogleSocialLoginViewSet,
)

from vm.resources.api.views import (
    RegionViewSet,
    OperatingSystemVersionViewSet,
    VirtualMachineViewSet,
    VirtualMachineHistoryViewSet,
    BackupViewSet,
    NotificationViewSet,
)

from vm.billing.api.views import (
    RatePlanViewSet,
    SubscriptionViewSet,
    TransactionViewSet,
    BillingAccountViewSet,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# users
router.register("users", UserViewSet)
router.register("admins", GeneralAdminViewSet)
router.register("customers", CustomerViewset)
router.register("guests", GuestViewset)
router.register("google-auth", GoogleSocialLoginViewSet, basename="google-auth")

# resources
router.register("regions", RegionViewSet)
router.register("os-versions", OperatingSystemVersionViewSet)
router.register("virtual-machines", VirtualMachineViewSet)
router.register("vm-history", VirtualMachineHistoryViewSet)
router.register("backups", BackupViewSet)
router.register("notifications", NotificationViewSet)

# billing
router.register("rate-plans", RatePlanViewSet)
router.register("subscriptions", SubscriptionViewSet)
router.register("transactions", TransactionViewSet)
router.register("billing-accounts", BillingAccountViewSet)

app_name = "api"
urlpatterns = router.urls
