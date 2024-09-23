import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from autovm.users.models import User, Customer
from autovm.billing.models import BillingAccount, RatePlan, Subscription, Transaction

# resources
from autovm.resources.models import OperatingSystem
from autovm.resources.models import OperatingSystemVersion
from autovm.resources.models import Region
from autovm.resources.models import VirtualMachine
from autovm.resources.models import VirtualMachineHistory

from autovm.billing.utils.payment_client import PaymentClient


@pytest.fixture
def fake_users(db):
    """
    Create fake users
    """
    customer1 = User.objects.create_user(
        name=f"customer1",
        email=f"customer1@mail.com",
        password="password",
    )
    customer2 = User.objects.create_user(
        name=f"customer2",
        email=f"customer2@mail.com",
        password="password",
    )

    new_admin = User.objects.create_user(
        name=f"admin1",
        email=f"admin1@mail.com",
        password="password",
        role="admin",
    )

    return customer1, customer2, new_admin


@pytest.fixture
def fake_rate_plans(db):
    """
    Create fake rate plans
    """
    bronze = RatePlan.objects.create(
        plan="bronze",
        price=200,
        vm_limit=2,
        backup_limit=2,
    )
    silver = RatePlan.objects.create(
        plan="silver",
        price=600,
        vm_limit=2,
        backup_limit=2,
    )
    gold = RatePlan.objects.create(
        plan="gold",
        price=800,
        vm_limit=3,
        backup_limit=3,
    )
    platinum = RatePlan.objects.create(
        plan="platinum",
        price=1200,
        vm_limit=8,
        backup_limit=8,
    )

    return bronze, silver, gold, platinum


@pytest.fixture
def fake_region_and_os(db):
    """
    Create fake region and os
    """
    region = Region.objects.create(
        name="United States",
    )

    operating_sys = OperatingSystem.objects.create(
        name="Ubuntu",
    )
    os_version = OperatingSystemVersion.objects.create(
        operating_system=operating_sys,
        version="20.04",
    )

    return region, operating_sys, os_version


@pytest.fixture
def authenticated_customer_client(db):
    """
    Authenticated customer client
    """
    # Create a user
    user = User.objects.create_user(
        name=f"customer3",
        email=f"customer3@mail.com",
        password="password",
    )
    customer = Customer.objects.get(user=user)
    billing_account = BillingAccount.objects.create(
        user=customer.user,
        amount=1000,
    )

    # Create an authenticated client
    client = APIClient()
    client.force_authenticate(user=user)

    yield client

    # Clean up: Delete the user
    user.delete()


@pytest.mark.django_db
class TestVirtualMachineEndpoints:
    """
    Test the virtual machine endpoints
    """

    def test_create_vm_only_for_subscribed_customers(self, fake_users):
        """
        Test creating a virtual machine
        """
        customer1, customer2, new_admin = fake_users

        client = APIClient()

        client.force_authenticate(user=customer1)

        response = client.post(
            reverse("api:virtualmachine-list"),
            data=json.dumps(
                {
                    "name": "test-vm",
                    "region": 1,
                    "os": 1,
                    "rate_plan": 1,
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 402

        # vm = VirtualMachine.objects.get(name="test-vm")

        # assert vm.region.id == 1
        # assert vm.os.id == 1
        # assert vm.rate_plan.id == 1
        # assert vm.owner == customer1

    def test_get_vms_is_accessible_by_authenticated_user(
        self, authenticated_customer_client
    ):
        url = reverse("api:virtualmachine-list")
        response = authenticated_customer_client.get(url)
        assert response.status_code == 200
        assert json.loads(response.content) == {
            "next": None,
            "previous": None,
            "results": [],
        }

    def test_get_vms_is_not_accessible_by_unauthenticated_user(self, client):
        """
        Test that an unauthenticated user cannot access the virtual machine list
        """
        url = reverse("api:virtualmachine-list")
        response = client.get(url)
        assert response.status_code == 403
        assert json.loads(response.content) == {
            "detail": "Authentication credentials were not provided."
        }

    def test_account_subscription(
        self,
        fake_rate_plans,
        fake_users,
        authenticated_customer_client,
        fake_region_and_os,
    ):
        """
        Test creating a subscription
        Check whether a user can subscribe to a plan
        """
        url = reverse("api:subscription-list")
        response = authenticated_customer_client.get(url)
        assert response.status_code == 200
        assert json.loads(response.content) == {
            "next": None,
            "previous": None,
            "results": [],
        }

        bronze, silver, gold, platinum = fake_rate_plans
        customer1, customer2, new_admin = fake_users
        # create a billing account for customer 1
        customer_account = BillingAccount.objects.create(
            user=customer1,
            amount=1000,
        )

        # Create a subscription
        response = authenticated_customer_client.post(
            url,
            data=json.dumps(
                {
                    "plan": str(bronze._id),
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert "_id" in json.loads(response.content)
        assert "account" in json.loads(response.content)

    def test_virtualmachine_assignment(
        self,
        fake_rate_plans,
        fake_users,
        authenticated_customer_client,
        fake_region_and_os,
    ):
        """
        Test creating a virtual machine
        """
        url = reverse("api:virtualmachine-list")
        response = authenticated_customer_client.get(url)
        assert response.status_code == 200
        assert json.loads(response.content) == {
            "next": None,
            "previous": None,
            "results": [],
        }

        bronze, silver, gold, platinum = fake_rate_plans
        customer1, customer2, new_admin = fake_users
        region, operating_sys, os_version = fake_region_and_os

        # create a billing account for customer 1
        customer_account = BillingAccount.objects.create(
            user=customer1,
            amount=1000,
        )

        # Create a subscription
        subscription = Subscription.objects.create(
            plan=bronze,
            account=customer_account,
        )
        # authenticate this user
        client = APIClient()
        client.force_authenticate(user=customer1)

        # Create a virtual machine
        response = client.post(
            url,
            data=json.dumps(
                {
                    "description": "test-vm",
                    "region": str(region._id),
                    "disk_size": 200,
                    "operating_system_version": str(os_version._id),
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        assert "_id" in json.loads(response.content)
        assert "region" in json.loads(response.content)
        assert "disk_size" in json.loads(response.content)
        assert "user" in json.loads(response.content)
