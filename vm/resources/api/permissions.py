import logging
from rest_framework.permissions import BasePermission
from rest_framework import permissions
from autovm.users.models import Customer


logger = logging.getLogger(__name__)


class IsNotSuspendedCustomer(BasePermission):
    """
    Permission class that grants access only to customers who are not suspended.
    """

    message = "Suspended account"

    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            return False

        if user.role == "admin" or user.role == "staff":
            return True

        if user.role == "guest" and (request.method in permissions.SAFE_METHODS):
            return True

        customer = None
        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            return False

        # Check if the customer is suspended
        if customer.suspended and (request.method not in permissions.SAFE_METHODS):
            return False

        return True


class IsAdminOrReadOnly(BasePermission):
    """
    Permission class that grants access to admins and read-only access to other users.
    """

    message = "You are not an admin"

    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow full access to admins
        return (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role == "admin"
        )
