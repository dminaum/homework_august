from decimal import Decimal
from typing import Tuple
from django.conf import settings
import stripe


class StripeGateway:
    """Тонкая, тестируемая обёртка над stripe SDK."""
    def __init__(self, api_key: str | None = None):
        stripe.api_key = api_key or settings.STRIPE_SECRET_KEY

    def create_product_and_price(self, *, name: str, amount: Decimal, currency: str = "usd") -> str:
        """Создать Product + Price; вернуть price_id."""
        product = stripe.Product.create(name=name)
        price = stripe.Price.create(
            unit_amount=int(Decimal(amount) * 100),
            currency=currency,
            product=product["id"],
        )
        return price["id"]

    def start_checkout(self, *, price_id: str, success_url: str, cancel_url: str) -> Tuple[str, str]:
        """Создать Checkout Session; вернуть (session_id, checkout_url)."""
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session["id"], session["url"]
