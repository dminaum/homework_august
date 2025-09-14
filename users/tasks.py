from celery import shared_task
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

@shared_task
def deactivate_inactive_users():
    cutoff = now() - timedelta(days=30)
    qs = User.objects.filter(is_active=True).filter(
    )
    qs = qs.filter(Q(last_login__lt=cutoff) | Q(last_login__isnull=True))
    updated = qs.update(is_active=False)
    return updated
