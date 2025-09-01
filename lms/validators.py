from urllib.parse import urlparse
from rest_framework import serializers

ALLOWED_YT_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"
}


def validate_youtube_url(value: str):
    """Разрешаем только http/https ссылки на YouTube."""
    if value is None:
        return value
    value = value.strip()
    if not value:
        return value

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise serializers.ValidationError("Разрешены только http/https ссылки.")

    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_YT_HOSTS:
        raise serializers.ValidationError(
            "Ссылка должна вести на YouTube (youtube.com или youtu.be)."
        )
    return value
