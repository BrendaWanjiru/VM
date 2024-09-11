import requests
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.registration.views import SocialLoginView

from autovm.users.models import Customer, GeneralAdmin, Guest, User

from .serializers import (
    CustomerUserSerializer,
    GeneralAdminSerializer,
    GuestRegistrationSerializer,
    GuestUserSerializer,
    UserSerializer,
    CustomerSusensionSerializer,
)


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    """
    User vuiew
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        """
        Retrieve the current user profile
        """
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class GeneralAdminViewSet(viewsets.ModelViewSet):
    """
    Platform administrators and superusers.
    """

    serializer_class = GeneralAdminSerializer
    queryset = GeneralAdmin.objects.all()
    lookup_field = "pk"
    filter_backends = [SearchFilter]
    search_fields = ["user__name", "user__email"]


class CustomerViewset(viewsets.ModelViewSet):
    """
    An API viewset for customer users.
    """

    serializer_class = CustomerUserSerializer
    queryset = Customer.objects.all()
    lookup_field = "pk"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["user__name", "user__email"]
    filterset_fields = ["suspended"]

    @action(detail=False, methods=["get"], name="Statistics")
    def statistics(self, request, pk=None):
        """
        Get statistics of customers
        """
        queryset = self.get_queryset()
        total = queryset.count()
        active = queryset.filter(suspended=False).count()
        inactive = queryset.filter(suspended=True).count()

        total_guests = Guest.objects.count()

        return Response(
            {
                "total": total,
                "active": active,
                "inactive": inactive,
                "guests": total_guests,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        name="Suspend",
        serializer_class=CustomerSusensionSerializer,
    )
    def suspend(self, request, pk=None):
        """
        Suspend a customer account
        """
        customer = self.get_object()
        serializer = CustomerSusensionSerializer(data=request.data)
        if serializer.is_valid():
            customer.suspended = serializer.data["suspend"]
            customer.save()
            return Response(
                {"success": "Customer account suspended successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestViewset(viewsets.ModelViewSet):
    """
    An API viewset for guest users.
    """

    serializer_class = GuestUserSerializer
    queryset = Guest.objects.all()
    lookup_field = "pk"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["user__name", "user__email"]
    filterset_fields = ["status", "customer__user__email", "customer__user__id"]

    def get_queryset(self):
        """
        A customer should be able to list only the guest users they have created.
        """
        user = self.request.user
        if user.role == "admin":
            return self.queryset
        customer = Customer.objects.get(user=self.request.user)
        return self.queryset.filter(customer=customer)

    @action(detail=False, methods=["get"], name="Statistics")
    def statistics(self, request, pk=None):
        """
        Get statistics of guest users
        """
        queryset = self.get_queryset()
        total = queryset.count()
        active = queryset.filter(status="active").count()
        inactive = queryset.filter(status="inactive").count()

        return Response(
            {
                "total": total,
                "active": active,
                "inactive": inactive,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(
    name="post",
    decorator=extend_schema(
        request=GuestRegistrationSerializer,
    ),
)
class GuestRegistrationView(APIView):
    """
    Register guest under a customer
    """

    serializer_class = GuestRegistrationSerializer

    def post(self, request):
        """
        Create a guest associated with the current user.
        """
        serializer = GuestRegistrationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "Guest created successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def check_required_fields(data, required_fields):
    """
    Check if the required fields are present in the given data.
    """
    for field in required_fields:
        if field not in data:
            return Response(
                {"detail": f"{field.capitalize()} is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return None


class GoogleSocialLoginViewSet(ModelViewSet):
    """
    Google Social Login, Use the url below to test the endpoint;
    https://www.googleapis.com/auth/userinfo.email
    https://developers.google.com/oauthplayground/
    return access_token from the url above
    """

    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        required_fields = ["token"]

        fields = check_required_fields(request.data, required_fields)
        if fields:
            return fields

        token = request.data.get("token")

        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                params={"access_token": token},
                timeout=300,
            )
            response.raise_for_status()

            response_data = response.json()
            required_fields = ["email"]

            fields = check_required_fields(response_data, required_fields)
            if fields:
                return fields

            email = response_data.get("email")
            # Validate email address format
            try:
                validate_email(email)
            except ValidationError:
                return Response(
                    {"detail": "Invalid email address"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user, created = User.objects.get_or_create(email=email)
            if created:
                user.name = response_data.get("name", "")
                user.is_active = True
                user.set_unusable_password()
                user.save()

            serializer = UserSerializer(user)

            token = RefreshToken.for_user(user)
            return Response(
                {
                    "user": serializer.data,
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                },
                status=status.HTTP_200_OK,
            )
        except requests.HTTPError as e:
            return Response(
                {"detail": f"Google API request failed: {e.response.text}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
