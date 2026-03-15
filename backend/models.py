from django.db import models
from django.db.models import Q, CheckConstraint
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal


USER_CHOICES = (
    ('buyer', 'Покупатель'),
    ('supplier', 'Поставщик'),
)

STATUS_CHOICES = (
    ('basket', 'Формирование'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('completed', 'Скомплектован'),
    ('delivered', 'Доставлен'),
    ('cancelled', 'Отменен'),
)


class UserManager(BaseUserManager):
    """
    Manager for create user and superuser
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Укажите email'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь значение is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь значение is_superuser=True'))

        return self.create_user(email, password, **extra_fields)
   

class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=50, unique=True, verbose_name=_('Email'))
    surname = models.CharField(max_length=20, blank=True, verbose_name=_('Отчество'))
    user_type = models.CharField(
                    max_length=8,
                    choices=USER_CHOICES,
                    verbose_name=_('Тип пользователя')
    )    
    is_active = models.BooleanField(default=False, verbose_name=_('Активный пользователь'))
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('last_name',)



class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    url = models.CharField(max_length=50, blank=True, verbose_name=_('Ссылка'))
    user = models.OneToOneField(
                        User,
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                        verbose_name=_('Пользователь')
    )
    accept_orders = models.BooleanField(default=True, verbose_name=_('Готовность принимать заказы'))

    class Meta:
        verbose_name = _('Магазин')
        verbose_name_plural = _('Магазины')
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name=_('Магазин'))
    name = models.CharField(max_length=30, verbose_name=_('Название'))

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('Категория'))
    name = models.CharField(max_length=70, verbose_name=_('Название'))

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class ProductInfo(models.Model):
    external_id = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="ID по прайс-листу")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_info', verbose_name=_('Продукт'))
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products_info', verbose_name=_('Магазин'))
    model = models.CharField(max_length=100, verbose_name=_('Модель'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Количество'))
    price = models.DecimalField(
                    max_digits=10,
                    decimal_places=2,
                    validators=[MinValueValidator(Decimal('0.01'))],
                    help_text=_("Цена должна быть не менее 0.01"),
                    verbose_name=_('Цена')
    )
    price_rrc = models.DecimalField(
                    max_digits=10,
                    decimal_places=2,
                    validators=[MinValueValidator(Decimal('0.01'))],
                    help_text=_("Рекомендуемая розничная цена должна быть не менее 0.01"),
                    verbose_name=_('Рекомендуемая розничная цена')
    )

    class Meta:
        verbose_name = _('Информация о продукте')
        verbose_name_plural = _('Информация о продуктах')
        constraints = [
            CheckConstraint(
                condition=Q(price__gte=0.01),
                name='positiv_price'
            ),
            CheckConstraint(
                condition=Q(price_rrc__gte=0.01),
                name='positiv_price_rrc'
            ),
        ]

    def __str__(self):
        return str(f'{self.product}, {self.price}')

   
class Parameter(models.Model):
    name = models.CharField(max_length=30, verbose_name=_('Параметр'))

    class Meta:
        verbose_name = _('Параметр')
        verbose_name_plural = _('Параметры')
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class ProductParameter(models.Model):
    product_info = models.ForeignKey(
                    ProductInfo,
                    blank=True,
                    on_delete=models.CASCADE,
                    related_name='product_parameters',
                    verbose_name=_('Информация о продукте')
    )
    parameter = models.ForeignKey(
                    Parameter,
                    blank=True,
                    on_delete=models.CASCADE,
                    related_name='product_parameters',
                    verbose_name=_('Параметр')
    )
    value = models.CharField(max_length=50, verbose_name=_('Значение параметра'))

    class Meta:
        verbose_name = _('Значение параметра продукта')
        verbose_name_plural = _('Значения параметров продукта')

    def __str__(self):
        return self.value


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Пользователь'))
    date_create = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, verbose_name=_('Статус заказа'))


    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ('-date_create',)

    def __str__(self):
        return self.status


class OrdeItem(models.Model):
    order = models.OneToOneField(
                        Order,
                        on_delete=models.CASCADE,
                        primary_key=True,
                        verbose_name=_('Заказ'))
    product_info = models.ForeignKey(
                        ProductInfo,
                        on_delete=models.CASCADE,
                        blank=True,
                        related_name='order_items',
                        verbose_name=_('Информация о продукте')
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Количество'))

    class Meta:
        verbose_name = _('Информация о заказе')
        verbose_name_plural = _('Информация о заказах')


class Contact(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name=_('Пользователь'))
    phone = PhoneNumberField(region="RU", verbose_name=_('Телефон'))
    city = models.CharField(max_length=50, verbose_name=_('Город'))
    street = models.CharField(max_length=50, verbose_name=_('Улица'))
    house = models.CharField(max_length=50, verbose_name=_('Дом'))
    building = models.CharField(max_length=50, blank=True, verbose_name=_('Корпус'))
    apartment = models.CharField(max_length=50, blank=True, verbose_name=_('Квартира'))

    class Meta:
        verbose_name = _('Контактные данные пользователя')
        verbose_name_plural = _('Контактные данные пользователей')

    def __str__(self):
        return str(self.phone)
