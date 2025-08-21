from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.username


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счёт'

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

    class Meta:
        verbose_name = 'платёж'
        verbose_name_plural = 'платежи'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['paid_at']),
        ]
        ordering = ['-paid_at']
