from celery import shared_task
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

@shared_task
def deactivate_inactive_users():
    month_ago = now() - relativedelta(months=1)
    qs = User.objects.filter(is_active=True).filter(
    )
    qs = qs.filter(Q(last_login__lt=month_ago) | Q(last_login__isnull=True))
    updated = qs.update(is_active=False)
    return updated
