from rest_framework import serializers
from django.contrib.auth import get_user_model

from autovm.users.models import User, Customer, Guest
from autovm.billing.models import BillingAccount
from autovm.billing.api.serializers import RatePlanSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer[User]):
    """
    user serializer
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = User
        fields = ["name", "username", "role", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class CustomUserSerializer(serializers.ModelSerializer[User]):
    """
    user serializer
    """

    pk = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = User
        fields = ["pk", "name", "email", "username", "role", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }

    def get_pk(self, obj):
        """
        Return the id as a pk
        """
        # the id is same as pk
        return obj.id


class GeneralAdminSerializer(serializers.ModelSerializer[User]):
    """
    A serializer for general admin users.
    """

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        """
        Allowed fields for the serializer.
        """

        model = User
        fields = ["id", "name", "email"]

    def get_name(self, obj):
        """
        Name of the customer user.
        """
        return obj.user.name

    def get_email(self, obj):
        """
        Email of the customer user.
        """
        return obj.user.email


class CustomerUserSerializer(serializers.ModelSerializer[User]):
    """
    A serializer for customer users.
    """

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    guests = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    suspended = serializers.SerializerMethodField()
    account_balance = serializers.SerializerMethodField()
    current_plan = serializers.SerializerMethodField()
    # virtual_machines = serializers.SerializerMethodField()

    class Meta:
        """
        Allowed fields for the serializer.
        """

        model = User
        fields = [
            "id",
            "user_id",
            "name",
            "suspended",
            "account_balance",
            "current_plan",
            # "virtual_machines",
            "email",
            "guests",
            "created",
        ]

    def get_name(self, obj):
        """
        Name of the customer user.
        """
        return obj.user.name

    def get_email(self, obj):
        """
        Email of the customer user.
        """
        return obj.user.email

    def get_user_id(self, obj):
        """
        Email of the customer user.
        """
        return obj.user.id

    def get_guests(self, obj):
        """
        Get the number of guests for this user.
        """
        return Guest.objects.filter(customer=obj.user.customer_profile).count()

    def get_created(self, obj):
        """
        Get the date the user was created.
        """
        return obj.user.customer_profile.created

    def get_suspended(self, obj):
        """
        Status of the customer account
        """
        return obj.user.customer_profile.suspended

    def get_account_balance(self, obj):
        """
        Get the account balance of the customer.
        """
        billing_account = 0

        billing_account, created = BillingAccount.objects.get_or_create(user=obj.user)

        return billing_account.amount

    def get_current_plan(self, obj):
        """
        Get the current plan of the customer.
        """
        billing_account, created = BillingAccount.objects.get_or_create(user=obj.user)
        # get the subscription
        subscription = billing_account.subscription_set.filter(status="active").first()
        if subscription:
            # serialize the plan
            return RatePlanSerializer(subscription.plan).data

        return "No active plan"

    # def get_virtual_machines(self, obj):
    #     """
    #     Return the number of virtual machines for this customer.
    #     """

    #     return VirtualMachine.objects.filter(user=obj.user).count()


class GuestUserSerializer(serializers.ModelSerializer):
    """
    A serializer for guest users.
    """

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        """
        Allowed fields for the serializer.
        """

        model = Guest
        fields = ["id", "name", "email", "status", "created"]

    def get_name(self, obj):
        """
        Name of the guest user.
        """
        return obj.user.name

    def get_email(self, obj):
        """
        Email of the guest user.
        """
        return obj.user.email


class GuestRegistrationSerializer(serializers.Serializer):
    """
    Serializer for registering a guest user.
    """

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def create(self, validated_data):
        current_user = self.context["request"].user.id

        # get the customer making the request
        customer = Customer.objects.get(user_id=current_user)

        password = User.objects.make_random_password()
        # get the user making the request
        new_user = None
        new_user = User(
            # username=username,
            name=validated_data["name"],
            email=validated_data["email"],
            role="guest",
        )
        new_user.set_password(password)
        new_user.save()

        new_user.guest_profile.customer = customer
        new_user.guest_profile.save()

        # send the password and confirmation email to the user
        message = f"Dear {new_user.name}, \n Your VMControlHub guest account has been created. Your details are as below: \n Login email {new_user.email} \n\n is: {password}"
        # send a confirmation email to the user
        new_user.email_user(
            "VMControl Manager Account Creation",
            message,
            "VMControl Manager <no-reply@example.com>",
        )

        return new_user

    def validate(self, attrs):

        if User.objects.filter(email=attrs["email"]).exists():
            serializers.ValidationError("This email is already registered")

        if User.objects.filter(name=attrs["name"]).exists():
            raise serializers.ValidationError("A user with this name already exists.")

        return attrs


class CustomerSusensionSerializer(serializers.Serializer):
    """
    Serializer for suspending a customer account.
    """

    suspend = serializers.BooleanField()


class GoogleSocialSerializer(serializers.Serializer):
    """
    Authenticate with google
    """

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()


class RegistrationSerializer(serializers.ModelSerializer[User]):
    """
    Serializer for registering a new user.
    """

    role = serializers.CharField(default="customer", required=False)

    class Meta:
        """
        Errata
        """

        model = User
        fields = ["id", "name", "email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # Create the user with the validated data
        user = User(
            name=validated_data["name"],
            email=validated_data["email"],
        )

        user.set_password(validated_data["password"])

        user.save()
        return user
