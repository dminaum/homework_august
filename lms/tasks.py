from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django.db import transaction
from django.conf import settings

from .models import Course, Subscription

FOUR_HOURS = timedelta(hours=4)


@shared_task
def email_course_updated(course_id: int):
    try:
        with transaction.atomic():
            course = Course.objects.select_for_update().get(id=course_id)

            if course.last_notification_sent and course.last_notification_sent > now() - FOUR_HOURS:
                return

            subs = Subscription.objects.filter(course=course).select_related("user")
            recipient_list = [s.user.email for s in subs if s.user and s.user.email]

            if recipient_list:
                send_mail(
                    subject=f'Курс "{course.name}" обновлён',
                    message=f'В курсе "{course.name}" появились обновления.',
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or "noreply@example.com",
                    recipient_list=recipient_list,  # можно пачкой
                    fail_silently=False,
                )

            course.last_notification_sent = now()
            course.save(update_fields=["last_notification_sent"])
    except Course.DoesNotExist:
        pass
