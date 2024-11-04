import logging
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from .models import Employee
from .serializers import EmployeeSerializer

logger = logging.getLogger(__name__)


class WelcomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("Welcome endpoint accessed.")
        return Response("Welcome to Employee Management System App", status=status.HTTP_200_OK)


def uniform_response(status_code, message, data=None):
    return Response({
        "status": status_code,
        "message": message,
        "data": data
    }, status=status_code)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = None
        if '@' in username:
            try:
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                logger.warning(f"Login failed for email {username}: User does not exist.")
        if not user:
            user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            logger.info(f"User {username} logged in successfully.")
            return uniform_response(status.HTTP_200_OK, "User logged in successfully.", {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            })
        logger.warning(f"Login failed for {username}: Invalid credentials.")
        return uniform_response(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {serializer.data['username']} registered successfully.")
            return uniform_response(status.HTTP_201_CREATED, "user registered successfully", serializer.data)
        logger.warning("User registration failed due to invalid data.")

        return uniform_response(status.HTTP_400_BAD_REQUEST, "User registration failed due to invalid data.",
                                serializer.errors)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("User logged out successfully.")
            return uniform_response(status.HTTP_200_OK, "message': 'Successfully logged out.")
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return uniform_response(status.HTTP_400_BAD_REQUEST, {'error': str(e)})


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['department', 'role']

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            employee = serializer.save()

            logger.info(f"Employee {employee.id} created successfully.")

            return uniform_response(status.HTTP_201_CREATED, "Employee created successfully.", serializer.data)

        except ValidationError as e:
            logger.warning(f"Employee creation failed: {str(e)}")
            return uniform_response(status.HTTP_400_BAD_REQUEST, "Employee creation failed.", {'error': str(e)})

    def retrieve(self, request, *args, **kwargs):
        try:
            employee_instance = self.get_object()
            serializer = self.get_serializer(employee_instance)
            logger.info(f"Employee {employee_instance.id} retrieved successfully.")
            return uniform_response(status.HTTP_200_OK, "Employee retrieved successfully.", serializer.data)

        except Http404:
            logger.warning("Employee not found.")
            return uniform_response(status.HTTP_404_NOT_FOUND, "No Employee matches the given query.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Employee {instance.id} updated successfully.")
            return uniform_response(status.HTTP_200_OK, "Employee updated successfully.", serializer.data)
        except Http404:
            logger.warning("Employee not found for update.")
            return uniform_response(status.HTTP_404_NOT_FOUND, "Employee not found for update.")
        except ValidationError as e:
            logger.warning(f"Employee update failed: {str(e)}")
            return uniform_response(status.HTTP_400_BAD_REQUEST, "Employee update failed due to invalid data.",
                                    {'errors': str(e)})

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info(f"Employee {instance.id} deleted successfully.")

            return uniform_response(status.HTTP_204_NO_CONTENT, "Employee deleted successfully.")

        except Http404:
            logger.warning("Employee not found for deletion.")
            return uniform_response(status.HTTP_404_NOT_FOUND, "Employee not found for deletion.")
