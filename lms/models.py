from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название курса')
    image = models.ImageField(upload_to='lms/', verbose_name='Превью (картинка)', blank=True, null=True)
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Владелец',
        blank=True,
        null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена" )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'
        ordering = ['name']


class Lesson(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название урока')
    image = models.ImageField(upload_to='lms/', verbose_name='Превью (картинка)', blank=True, null=True)
    description = models.TextField(verbose_name='Описание')
    video_url = models.URLField(verbose_name='Ссылка на видео')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name='Курс', related_name='lessons')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Владелец',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
        ordering = ['id']


class Subscription(models.Model):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions'
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.PROTECT,
        verbose_name='Оплаченный курс',
        null=True, blank=True,
        related_name='subscriptions',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f"{self.user} → {self.course}"
