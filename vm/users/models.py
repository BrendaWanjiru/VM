from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for VMControlHub.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = models.EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    CHOICES = (("admin", "General Admin"), ("customer", "Customer"), ("guest", "Guest"))

    role = models.CharField(max_length=8, choices=CHOICES, default="customer")

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """
        Save user and create profile if it doesn't exist.
        All users are customers if their role is not specified.
        """
        super().save(*args, **kwargs)
        if self.role == "admin":
            GeneralAdmin.objects.get_or_create(user=self)
        elif self.role == "guest":
            Guest.objects.get_or_create(user=self)
        else:
            # register as a customer by default
            Customer.objects.get_or_create(user=self)


class ProfileBase(models.Model):
    """
    Base user profile model. Should contain fields common to all users.
    """

    # _id = models.UUIDField(
    #     default=uuid.uuid4, unique=True, editable=False, primary_key=True
    # )
    profile_image = models.ImageField(upload_to="profile_images", null=True, blank=True)
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    updated = models.DateField(auto_now_add=True, null=True, blank=True)

    class Meta:
        """
        Meta class for ProfileBase model.
        """

        abstract = True


class GeneralAdmin(ProfileBase):
    """
    Admin profile model.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profile",
    )

    def __str__(self) -> str:
        return self.user.email

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("profile:detail", kwargs={"email": self.user.email})


class Customer(ProfileBase):
    """
    Customer profile model.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    suspended = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.email


class Guest(ProfileBase):
    """
    A guest invited by a customer.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="guest_profile",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="guests",
        null=True,
        blank=True,
    )
    CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )
    status = models.CharField(max_length=8, choices=CHOICES, default="active")

    def __str__(self):
        return self.user.email
