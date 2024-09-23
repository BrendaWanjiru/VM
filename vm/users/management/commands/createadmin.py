from django.core.management.base import BaseCommand
from django.conf import settings

from autovm.users.models import User


class Command(BaseCommand):
    help = "Create an admin user for local development if it does not exist"

    def handle(self, *args, **kwargs):
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
