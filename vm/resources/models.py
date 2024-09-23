import uuid

import slugify
from django.db import models

from autovm.resources.utils.generate_vm_name import generate_vm_name
from autovm.users.models import User


class CommonBaseModel(models.Model):
    """
    Common fields shared by all models in the app
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
        Do not create a table for this model
        """

        abstract = True


class OperatingSystem(CommonBaseModel):
    """
    Operating System model.
    We can have ubuntu, fedora, debian, centos, almnaLinux etc. managed from the admin
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        """
        Return the name of the operating system
        """
        return self.name


class OperatingSystemVersion(CommonBaseModel):
    """
    Specific version of an operating system.
    Example: ubuntu 20.04, fedora 32, debian 10, centos 8, almnaLinux 8
    """

    operating_system = models.ForeignKey(
        OperatingSystem,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.operating_system.name} {self.version}"


class Region(CommonBaseModel):
    """
    Region model.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify.slugify(self.name)
        super().save(*args, **kwargs)


class VirtualMachine(CommonBaseModel):
    """
    Virtual Machine model.
    """

    name = models.CharField(max_length=15, unique=True)
    description = models.TextField(blank=True, help_text="Human readable description")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="virtual_machines",
    )

    operating_system_version = models.ForeignKey(
        OperatingSystemVersion,
        on_delete=models.SET_NULL,
        null=True,
    )
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    backup_frequency = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]
    backup_freq = models.CharField(
        max_length=20,
        choices=backup_frequency,
        default="daily",
    )
    is_active = models.BooleanField(default=True)

    STORAGE_CHOICES = [
        ("200", "200 GB SSD"),
        ("300", "300 GB SSD"),
        ("400", "400 GB SSD"),
        ("600", "600 GB SSD"),
        ("1000", "1 TB SSD"),
    ]

    disk_size = models.CharField(max_length=20, choices=STORAGE_CHOICES, default="200")

    class Meta:
        """
        Errata info on ordering
        """

        ordering = ["-created"]

    def __str__(self):
        return f"{self.name} ({self.user})"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = generate_vm_name(type(self))
        super().save(*args, **kwargs)


class VirtualMachineHistory(CommonBaseModel):
    """
    Virtual Machine history model.
    """

    virtual_machine = models.ForeignKey(
        VirtualMachine,
        on_delete=models.SET_NULL,
        null=True,
        related_name="history",
    )
    ACTION_CHOICES = [
        ("create_vm", "Create VM"),
        ("delete_vm", "Delete VM"),
        ("move_vm", "Move VM"),
        ("backup_vm", "Backup VM"),
        ("start_vm", "Start VM"),
        ("stop_vm", "Stop VM"),
    ]
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        default="create_vm",
    )
    description = models.TextField(blank=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        """
        Errata info on ordering
        """

        ordering = ["-created"]

    def __str__(self):
        return f"{self.user.name} {self.get_action_display()} at {self.created}"


class Backup(CommonBaseModel):
    """
    Backup model.
    """

    vm = models.ForeignKey(
        VirtualMachine,
        on_delete=models.CASCADE,
        related_name="backups",
    )

    # since the size of a vm can be edited, we store this at the time of backup
    size = models.IntegerField(help_text="Backup size in GB")

    def __str__(self):
        return f"Backup of {self.vm.name} at {self.created}"


class Notification(CommonBaseModel):
    """
    Handle notifications for users upon vm movement
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)

    class Meta:
        """
        Order for notifications
        """

        ordering = ["-created"]

    def __str__(self):
        return f"Notification for {self.user.name}"
