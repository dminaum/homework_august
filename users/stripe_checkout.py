from django.urls import reverse
from django.http import HttpRequest
from decimal import Decimal
from django.conf import settings

from .models import Payment
from .stripe_gateway import StripeGateway


def build_item_name(payment: Payment) -> str:
    """Имя позиции: только курс."""
    if hasattr(payment, "course_id") and payment.course_id is not None:
        return payment.course.name
    return "Course"


def kickoff_checkout(payment: Payment, request: HttpRequest) -> tuple[str, str]:
    """
    Создаёт в Stripe Product+Price+CheckoutSession для оплаты курса.
    Возвращает (session_id, checkout_url).
    """
    gw = StripeGateway()
    item_name = build_item_name(payment)
    currency = getattr(settings, "STRIPE_CURRENCY", "rub")

    price_id = gw.create_product_and_price(
        name=item_name,
        amount=Decimal(payment.amount),
        currency=currency,
    )

    success_url = request.build_absolute_uri(reverse("payment-list"))
    cancel_url = request.build_absolute_uri(reverse("payment-list"))

    return gw.start_checkout(price_id=price_id, success_url=success_url, cancel_url=cancel_url)
