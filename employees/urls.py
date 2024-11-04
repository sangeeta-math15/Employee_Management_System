from .views import RegisterUserView, UserLoginView, UserLogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

# router.register(r'employees', EmployeeViewSet, basename='employee')



urlpatterns = [
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('', include(router.urls)),
]
app_name = 'employees'
