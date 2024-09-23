from django.contrib import admin

from autovm.resources.models import Backup
from autovm.resources.models import Notification
from autovm.resources.models import OperatingSystem
from autovm.resources.models import OperatingSystemVersion
from autovm.resources.models import Region
from autovm.resources.models import VirtualMachine
from autovm.resources.models import VirtualMachineHistory


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    """
    Virtual machine admin panel
    """

    list_display = ["name", "user", "is_active", "created", "updated"]
    search_fields = ["name", "user__name"]
    list_filter = ["user", "is_active", "region"]
    # ordering = ["id"]


@admin.register(VirtualMachineHistory)
class VirtualMachineHistoryAdmin(admin.ModelAdmin):
    """
    Virtual machine history admin panel
    """

    list_display = ["virtual_machine", "user", "created"]
    search_fields = ["virtual_machine__name"]
    list_filter = ["user", "virtual_machine"]
    # ordering = ["id"]


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    """
    Operating system admin panel
    """

    list_display = ["name", "created"]
    search_fields = ["name"]
    # ordering = ["id"]


@admin.register(OperatingSystemVersion)
class OperatingSystemVersionAdmin(admin.ModelAdmin):
    """
    Operating system version admin panel
    """

    list_display = ["operating_system", "version", "created"]
    search_fields = ["operating_system__name", "version"]
    # ordering = ["id"]


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """
    Region admin panel
    """

    list_display = ["name", "created"]
    search_fields = ["name"]
    # ordering = ["id"]


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    """
    Backup admin panel
    """

    list_display = ["vm", "size", "created"]
    search_fields = ["vm__name"]
    list_filter = ["vm", "created"]
    # ordering = ["id"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Notification admin panel
    """

    list_display = ["user", "message", "read", "created"]
    search_fields = ["user__name", "user__email", "message"]
    list_filter = ["user", "read", "created"]
    # ordering = ["id"]
