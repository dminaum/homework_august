from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from lms.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed payments data'

    def handle(self, *args, **options):
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not (user and course and lesson):
            self.stdout.write(self.style.ERROR('Нужны хотя бы 1 user, 1 course и 1 lesson'))
            return

        Payment.objects.get_or_create(
            user=user, course=course, lesson=None,
            defaults={'amount': Decimal('1990.00'), 'method': Payment.Method.TRANSFER},
        )
        Payment.objects.get_or_create(
            user=user, course=None, lesson=lesson,
            defaults={'amount': Decimal('299.00'), 'method': Payment.Method.CASH},
        )
        self.stdout.write(self.style.SUCCESS('Созданы тестовые платежи'))
