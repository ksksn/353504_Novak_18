from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    is_vip = models.BooleanField(default=False, verbose_name="VIP клиент")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class DeviceType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип устройства"
        verbose_name_plural = "Типы устройств"

    def __str__(self):
        return self.name

class Device(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, verbose_name="Тип")
    model = models.CharField(max_length=100, verbose_name="Модель")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="Серийный номер")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"

    def __str__(self):
        return f"{self.name} ({self.model})"

class SparePart(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    category = models.CharField(max_length=100, verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity_in_stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")

    class Meta:
        verbose_name = "Запчасть"
        verbose_name_plural = "Запчасти"

    def __str__(self):
        return self.name

class ServiceType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Типы услуг"

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, verbose_name="Тип услуги")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name

class EmployeeSpecialization(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    hire_date = models.DateField(verbose_name="Дата найма")
    specializations = models.ManyToManyField(EmployeeSpecialization, blank=True, verbose_name="Специализации")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Repair(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент", related_name="repairs")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="Устройство")
    description = models.TextField(verbose_name="Описание проблемы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость работ")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")

    class Meta:
        verbose_name = "Ремонт"
        verbose_name_plural = "Ремонты"

    def __str__(self):
        return f"Ремонт #{self.id} - {self.device}"

class RepairSparePart(models.Model):
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE, verbose_name="Ремонт")
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, verbose_name="Запчасть")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Запчасть в ремонте"
        verbose_name_plural = "Запчасти в ремонте"

class Contract(models.Model):
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер договора")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    date_signed = models.DateField(verbose_name="Дата подписания")
    deadline = models.DateField(verbose_name="Срок выполнения")
    total_sum = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Общая сумма")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнен")
    admin_notes = models.TextField(blank=True, verbose_name="Заметки администратора")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"

    def __str__(self):
        return f"Договор {self.number}"

class PartType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип детали"
        verbose_name_plural = "Типы деталей"

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    part_type = models.ForeignKey(PartType, on_delete=models.CASCADE, verbose_name="Тип")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        verbose_name = "Деталь"
        verbose_name_plural = "Детали"

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name="Договор")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="Устройство")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    parts = models.ManyToManyField(Part, blank=True, verbose_name="Детали")
    service_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма услуг")
    parts_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма деталей")
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.id} по договору {self.contract.number}"

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'Общие'),
        ('repair', 'Ремонт'),
        ('warranty', 'Гарантия'),
        ('payment', 'Оплата'),
    ]
    
    question = models.TextField(verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question[:50]

class JobVacancy(models.Model):
    EMPLOYMENT_CHOICES = [
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('contract', 'Контракт'),
        ('internship', 'Стажировка'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('no_experience', 'Без опыта'),
        ('1_year', '1 год'),
        ('2_3_years', '2-3 года'),
        ('3_5_years', '3-5 лет'),
        ('5_plus_years', 'Более 5 лет'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание")
    requirements = models.TextField(verbose_name="Требования")
    responsibilities = models.TextField(verbose_name="Обязанности")
    salary_min = models.PositiveIntegerField(verbose_name="Зарплата от", help_text="В рублях")
    salary_max = models.PositiveIntegerField(verbose_name="Зарплата до", help_text="В рублях")
    employment_type = models.CharField(
        max_length=20, 
        choices=EMPLOYMENT_CHOICES, 
        default='full_time',
        verbose_name="Тип занятости"
    )
    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='no_experience',
        verbose_name="Требуемый опыт"
    )
    location = models.CharField(max_length=200, default='Москва', verbose_name="Местоположение")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-date_posted']

    def __str__(self):
        return self.title

    @property
    def created_at(self):
        """Алиас для совместимости с админ классами"""
        return self.date_posted

    @property
    def salary(self):
        """Форматированная строка зарплаты"""
        if self.salary_min and self.salary_max:
            return f"от {self.salary_min:,} до {self.salary_max:,} руб."
        elif self.salary_min:
            return f"от {self.salary_min:,} руб."
        elif self.salary_max:
            return f"до {self.salary_max:,} руб."
        return "По договоренности"

class Cart(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.client}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.cartitem_set.all())

    @property
    def items_count(self):
        return self.cartitem_set.count()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Корзина")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    def __str__(self):
        return f"{self.service} x{self.quantity}"

    @property
    def total_price(self):
        return self.service.price * self.quantity

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрена'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")
    notes = models.TextField(blank=True, verbose_name="Примечания клиента")
    admin_notes = models.TextField(blank=True, verbose_name="Заметки администратора")
    assigned_employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Назначенный сотрудник")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Заявка на услугу"
        verbose_name_plural = "Заявки на услуги"

    def __str__(self):
        return f"Заявка #{self.id} от {self.client}"

class ServiceRequestItem(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, verbose_name="Заявка")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    class Meta:
        verbose_name = "Элемент заявки"
        verbose_name_plural = "Элементы заявки"

    def __str__(self):
        return f"{self.service} x{self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity
