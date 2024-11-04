from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Employee
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class EmployeeViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

    def test_create_employee(self):
        url = reverse('employees:employee-list')
        data = {'name': 'John Doe', 'email': 'john@example.com', 'department': 'HR', 'role': 'Manager'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_employee_with_existing_email(self):
        Employee.objects.create(name='Jane Doe', email='jane@example.com')
        url = reverse('employees:employee-list')
        data = {'name': 'John Doe', 'email': 'jane@example.com', 'department': 'HR', 'role': 'Manager'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_employees(self):
        Employee.objects.create(name='Alice', email='alice@example.com')
        url = reverse('employees:employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_employee(self):
        employee = Employee.objects.create(name='Bob', email='bob@example.com')
        url = reverse('employees:employee-detail', kwargs={'pk': employee.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], employee.name)

    def test_update_employee(self):
        employee = Employee.objects.create(name='Charlie', email='charlie@example.com')
        url = reverse('employees:employee-detail', kwargs={'pk': employee.id})
        data = {'name': 'Charlie Brown', 'email': 'charlie@example.com'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        employee.refresh_from_db()
        self.assertEqual(employee.name, 'Charlie Brown')

    def test_destroy_employee(self):
        employee = Employee.objects.create(name='Dave', email='dave@example.com')
        url = reverse('employees:employee-detail', kwargs={'pk': employee.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(id=employee.id).exists())
