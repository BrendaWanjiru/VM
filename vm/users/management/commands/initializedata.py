import random
from django.core.management.base import BaseCommand
from django.conf import settings

from autovm.users.models import User
from autovm.billing.models import BillingAccount, RatePlan, Subscription, Transaction

# resources
from autovm.resources.models import OperatingSystem
from autovm.resources.models import OperatingSystemVersion
from autovm.resources.models import Region
from autovm.resources.models import VirtualMachine
from autovm.resources.models import VirtualMachineHistory

from autovm.billing.utils.payment_client import PaymentClient


class Command(BaseCommand):
    """
    Create startup data for local development
    """

    help = "Initialize data for local development"

    def handle(self, *args, **kwargs):
        """
        This will create 5 instances of each model
        """

        # create RatePlan 4
        bronze, created = RatePlan.objects.get_or_create(
            plan="bronze", price=200, vm_limit=2, backup_limit=2
        )
        silver, created = RatePlan.objects.get_or_create(
            plan="silver", price=600, vm_limit=2, backup_limit=2
        )
        gold, created = RatePlan.objects.get_or_create(
            plan="gold", price=800, vm_limit=3, backup_limit=3
        )
        platinum, created = RatePlan.objects.get_or_create(
            plan="platinum", price=1200, vm_limit=8, backup_limit=8
        )

        all_plans = [bronze, silver, gold, platinum]

        # create 5 customers
        for i in range(5):
            new_customer = None

            try:
                new_customer = User.objects.get(
                    email=f"customer{i}@mail.com",
                )
            except Exception as e:
                new_customer = User.objects.create_user(
                    name=f"customer{i}",
                    email=f"customer{i}@mail.com",
                    password="password",
                )

            # create a billing account for each user
            billing, is_created = BillingAccount.objects.get_or_create(
                user=new_customer, amount=1000
            )
            # create a subscription for each user
            plan = random.choice(all_plans)
            sub = Subscription.objects.get_or_create(
                account=billing,
                plan=plan,
            )
            # create a transaction for this plan
            details = PaymentClient().make_payment()

            Transaction.objects.create(account=billing, amount=plan.price, **details)

            # create a vm for each user
            possibles = ["ubuntu", "centos", "fedora"]
            chosen = random.choice(possibles)
            operating_sys, is_created = OperatingSystem.objects.get_or_create(
                name=chosen
            )
            os_version, is_created = OperatingSystemVersion.objects.get_or_create(
                operating_system=operating_sys, version="20.04"
            )
            possible_regions = ["south Africa", "Us West", "Germany-central", "Eu East"]
            chosen_region = random.choice(possible_regions)
            region, is_new_region = Region.objects.get_or_create(name=chosen_region)
            vm = VirtualMachine.objects.create(
                name=f"vm{i}",
                description=f"customer{i} vm",
                operating_system_version=os_version,
                region=region,
                user=new_customer,
            )

            # create historical data for each vm
            VirtualMachineHistory.objects.create(
                virtual_machine=vm,
                description=f"customer{i} created machine",
                user=new_customer,
            )

        # create 3 general admins
        for i in range(3):
            new_admin = User.objects.create_user(
                name=f"admin{i}",
                email=f"admin{i}@mail.com",
                password="password",
                role="admin",
            )

        if not User.objects.filter(name=settings.ADMIN_USERNAME).exists():
            User.objects.create_superuser(
                name=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                role="admin",
            )
            self.stdout.write(
                self.style.SUCCESS(f"Admin user '{settings.ADMIN_USERNAME}' created")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Admin user '{settings.ADMIN_USERNAME}' already exists"
                )
            )
