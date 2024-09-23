import logging
from django.db import transaction

from config import celery_app

from autovm.users.models import User
from autovm.resources.models import (
    Notification,
    VirtualMachine,
    VirtualMachineHistory,
)


logger = logging.getLogger(__name__)


@celery_app.task()
def notify_user(
    previous_user: int,
    machine: int = None,
    assigned_user: int = None,
):
    """
    Create a notification for users about assigned and unassigned virtual machines
    """
    previous_user = User.objects.get(id=previous_user)
    machine = VirtualMachine.objects.get(_id=machine)
    assigned_user = User.objects.get(id=assigned_user)

    with transaction.atomic():
        notifications = [
            Notification(
                user=previous_user,
                message=f"""Virtual machine {machine.name} has been unassigned from you.""",
            ),
            Notification(
                user=assigned_user,
                message=f"""You have been assigned a virtual machine {machine.name}""",
            ),
        ]
        Notification.objects.bulk_create(notifications)


@celery_app.task()
def create_machine_history(machine: int, actor: int, assigned: int):
    """
    Create a machine history from the background
    """
    actor = User.objects.get(id=actor)
    machine = VirtualMachine.objects.get(_id=machine)
    assigned = User.objects.get(id=assigned)
    VirtualMachineHistory.objects.create(
        virtual_machine=machine,
        action="assign_vm",
        description=f"assigned this virtual machine to {assigned.name}",
        user=actor,
    )


@celery_app.task()
def notify_suspended_user(user: int, suspended: str):
    """
    Notify a suspended a user
    """
    user = User.objects.get(id=user)
    status = "suspended"
    if not suspended:
        status = "activated"
    Notification.objects.create(
        user=user,
        message=f"""Your account has been {status}""",
    ),
    logger.info(f"Customer {user.name} has been {status}")
