from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email or self.username


class Payment(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'

    class Method(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счёт'
        STRIPE = 'stripe', 'Stripe'

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='payments'
    )
    paid_at = models.DateTimeField(verbose_name='Дата оплаты', auto_now_add=True)
    course = models.ForeignKey(
        'lms.Course',
        on_delete=models.PROTECT,
        verbose_name='Оплаченный курс',
        null=True, blank=True,
        related_name='payments',
    )

    lesson = models.ForeignKey(
        'lms.Lesson',
        on_delete=models.PROTECT,
        verbose_name='Оплаченный урок',
        null=True, blank=True,
        related_name='payments',
    )

    amount = models.DecimalField(
        verbose_name='Сумма оплаты',
        max_digits=10, decimal_places=2
    )

    method = models.CharField(
        verbose_name='Способ оплаты',
        max_length=20,
        choices=Method.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус платежа',
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name='ID сессии Stripe'
    )

    checkout_url = models.URLField(
        max_length=2048,
        blank=True, null=True,
        verbose_name='Ссылка на оплату'
    )

    class Meta:
        verbose_name = 'платёж'
        verbose_name_plural = 'платежи'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['paid_at']),
        ]
        ordering = ['-paid_at']
