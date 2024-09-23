from rest_framework import serializers

from autovm.resources.models import Backup
from autovm.resources.models import Notification
from autovm.resources.models import OperatingSystemVersion
from autovm.resources.models import Region
from autovm.resources.models import VirtualMachine
from autovm.resources.models import VirtualMachineHistory


class VirtualMachineHistorySerializer(serializers.ModelSerializer):
    """
    Virtual Machine history serializer.
    """

    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = VirtualMachineHistory
        fields = ["_id", "virtual_machine", "description", "user", "action", "created"]

    def get_user(self, obj) -> dict:
        """
        Get the user of the virtual machine history.
        """
        return {
            "id": obj.user.id,
            "name": obj.user.name,
            "email": obj.user.email,
            "role": obj.user.role,
        }


class BackupSerializer(serializers.ModelSerializer):
    """
    Backup serializer.
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = Backup
        fields = ["_id", "vm", "size", "created"]


class RegionSerializer(serializers.ModelSerializer):
    """
    Region serializer.
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = Region
        fields = ["_id", "name", "created", "updated"]


class VirtualMachineSerializer(serializers.ModelSerializer):
    """
    Virtual Machine serializer.
    """

    operating_system = serializers.SerializerMethodField(read_only=True)
    region_name = serializers.SerializerMethodField(read_only=True)
    last_backup = serializers.SerializerMethodField(read_only=True)
    backups = serializers.SerializerMethodField(read_only=True)
    history = VirtualMachineHistorySerializer(required=False, many=True, read_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = VirtualMachine
        fields = [
            "_id",
            "name",
            "region",
            "region_name",
            "description",
            "last_backup",
            "operating_system",
            "backups",
            "history",
            "operating_system_version",
            "is_active",
            "disk_size",
            "user",
            "user_info",
            "created",
            "updated",
        ]

        read_only_fields = ["name"]

    def create(self, validated_data):
        """G
        Create a virtual machine and associated history.
        """
        user = self.context["request"].user

        if user.role == "customer" or user.role == "admin":
            validated_data["user"] = user

        # get the subscription of the user

        virtual_machine = VirtualMachine.objects.create(**validated_data)
        VirtualMachineHistory.objects.create(
            virtual_machine=virtual_machine,
            action="create_vm",
            description="created a virtual machine",
            user=validated_data["user"],
        )

        return virtual_machine

    def get_operating_system(self, obj):
        """
        Get the operating system of the virtual machine.
        """
        return obj.operating_system_version.operating_system.name

    def get_last_backup(self, obj):
        """
        Get the last backup of the virtual machine.
        """
        backup = Backup.objects.filter(vm=obj).last()
        if backup:
            return backup.created
        return None

    def get_backups(self, obj):
        """
        Get the backups of the virtual machine.
        """
        backups = Backup.objects.filter(vm=obj)
        # serialize backups
        backups = BackupSerializer(backups, many=True).data
        return backups

    def get_user_info(self, obj):
        """
        Get the user info of the virtual machine.
        """
        return {
            "id": obj.user.id,
            "name": obj.user.name,
            "email": obj.user.email,
            "role": obj.user.role,
        }

    def get_region_name(self, obj):
        """
        Return teh name of teh region this server belongs to
        """
        name = None  # use this since test data has no region
        if obj.region:
            name = obj.region.name
        return name


class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification serializer.
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = Notification
        fields = ["_id", "user", "message", "read", "created"]


class OperatingSystemVersionSerializer(serializers.ModelSerializer):
    """
    Operating System Version serializer.
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = OperatingSystemVersion
        fields = ["_id", "operating_system", "version", "created", "updated"]
        depth = 1


class AssignmentSerializer(serializers.Serializer):
    """
    Assignment serializer
    todo: GEt user from the request
    """

    user_id = serializers.IntegerField()  # wehre the vm will be assigned
