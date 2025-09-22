from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, datetime, timedelta
from decimal import Decimal

from .models import (
    ServiceType, Service, DeviceType, Device, PartType, Part,
    Client, Employee, Contract, Order, Review, PromoCode,
    EmployeeSpecialization, PassportData
)

class ServiceModelTest(TestCase):
    def setUp(self):
        self.service_type = ServiceType.objects.create(
            name="Ремонт",
            description="Ремонт техники"
        )
        
    def test_service_creation(self):
        service = Service.objects.create(
            name="Замена экрана",
            description="Замена разбитого экрана",
            price=Decimal('150.00'),
            service_type=self.service_type
        )
        self.assertEqual(str(service), "Замена экрана")
        self.assertTrue(service.is_active)

class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testclient',
            email='test@example.com',
            first_name='Тест',
            last_name='Клиент'
        )
        
    def test_client_creation(self):
        client = Client.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Минск, ул. Тестовая, 1',
            birth_date=date(1990, 1, 1)
        )
        self.assertEqual(str(client), 'Тест Клиент')
        self.assertEqual(client.age, date.today().year - 1990)

class OrderModelTest(TestCase):
    def setUp(self):
        # Создаем пользователей
        self.client_user = User.objects.create_user(
            username='client1',
            first_name='Клиент',
            last_name='Тестовый'
        )
        self.employee_user = User.objects.create_user(
            username='employee1',
            first_name='Сотрудник',
            last_name='Тестовый'
        )
        
        # Создаем клиента
        self.client = Client.objects.create(
            user=self.client_user,
            phone='+375 (29) 123-45-67',
            address='Минск',
            birth_date=date(1990, 1, 1)
        )
        
        # Создаем сотрудника
        self.employee = Employee.objects.create(
            user=self.employee_user,
            position='master',
            phone='+375 (29) 987-65-43',
            email='master@example.com',
            birth_date=date(1985, 1, 1),
            hire_date=date.today(),
            description='Мастер по ремонту'
        )
        
        # Создаем услугу
        self.service_type = ServiceType.objects.create(name="Ремонт")
        self.service = Service.objects.create(
            name="Диагностика",
            description="Диагностика неисправностей",
            price=Decimal('50.00'),
            service_type=self.service_type
        )
        
        # Создаем договор
        self.contract = Contract.objects.create(
            number="CT-001",
            client=self.client,
            employee=self.employee,
            date_signed=date.today(),
            deadline=date.today() + timedelta(days=7)
        )
        
    def test_order_creation(self):
        order = Order.objects.create(
            contract=self.contract,
            service=self.service,
            quantity=1,
            service_sum=self.service.price,
            total_sum=self.service.price
        )
        self.assertEqual(order.service, self.service)
        self.assertEqual(order.total_sum, Decimal('50.00'))

class ViewsTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_index_view(self):
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
        
    def test_services_view(self):
        response = self.client.get(reverse('main:service_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_protected_view_requires_login(self):
        response = self.client.get(reverse('main:client_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_statistics_view_requires_staff(self):
        response = self.client.get(reverse('main:statistics'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Login as regular user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:statistics'))
        self.assertEqual(response.status_code, 302)  # Redirect (access denied)

class APITest(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )
        
    def test_services_api_accessible(self):
        response = self.client.get('/api/services/')
        self.assertEqual(response.status_code, 200)
        
    def test_statistics_api_requires_staff(self):
        # Unauthenticated
        response = self.client.get('/api/statistics/')
        self.assertEqual(response.status_code, 401)
        
        # Regular user
        self.client.login(username='apiuser', password='apipass123')
        response = self.client.get('/api/statistics/')
        self.assertEqual(response.status_code, 403)
        
        # Staff user
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get('/api/statistics/')
        self.assertEqual(response.status_code, 200)

class FormTest(TestCase):
    def test_review_form_validation(self):
        from .forms import ReviewForm
        
        # Valid data
        form_data = {
            'rating': 5,
            'text': 'Отличный сервис, все быстро и качественно!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid data (text too short)
        form_data = {
            'rating': 5,
            'text': 'Хорошо'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

class UtilsTest(TestCase):
    def test_calculate_order_total(self):
        from .utils import calculate_order_total
        
        # Setup
        user = User.objects.create_user(username='test')
        client = Client.objects.create(
            user=user, phone='+375 (29) 123-45-67',
            address='Test', birth_date=date(1990, 1, 1)
        )
        employee = Employee.objects.create(
            user=User.objects.create_user(username='emp'),
            position='master', phone='+375 (29) 987-65-43',
            email='emp@test.com', birth_date=date(1985, 1, 1),
            hire_date=date.today(), description='Test'
        )
        service_type = ServiceType.objects.create(name="Test")
        service = Service.objects.create(
            name="Test Service", description="Test",
            price=Decimal('100.00'), service_type=service_type
        )
        contract = Contract.objects.create(
            number="TEST-001", client=client, employee=employee,
            date_signed=date.today(), deadline=date.today() + timedelta(days=1)
        )
        order = Order.objects.create(
            contract=contract, service=service, quantity=2,
            service_sum=Decimal('0'), total_sum=Decimal('0')
        )
        
        # Test calculation
        total = calculate_order_total(order)
        self.assertEqual(total, Decimal('200.00'))  # 100 * 2
