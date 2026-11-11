from django.contrib.auth import get_user_model
from django.utils import timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from rest_framework.exceptions import AuthenticationFailed
import redis
from django.conf import settings

User = get_user_model()


def google_validate_and_get_user_data(code, client_id, client_secret, redirect_uri):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    token_request = Request(
        token_url,
        data=urlencode(data).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(token_request) as response:
        token_data = json.loads(response.read().decode("utf-8"))

    if "error" in token_data:
        raise AuthenticationFailed("Не удалось авторизоваться через Google.")

    access_token = token_data.get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    user_info_request = Request(
        user_info_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urlopen(user_info_request) as response:
        user_data = json.loads(response.read().decode("utf-8"))

    email = user_data.get("email")
    if not email:
        raise AuthenticationFailed("Google не предоставил email пользователя.")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "first_name": user_data.get("given_name", ""),
            "last_name": user_data.get("family_name", ""),
            "is_active": True,
            "registration_source": "google",
        },
    )

    if not created:
        user.first_name = user_data.get("given_name", user.first_name)
        user.last_name = user_data.get("family_name", user.last_name)

    user.last_login = timezone.now()
    user.save()

    return user


redis_client = redis.Redis(
    host=getattr(settings, "REDIS_HOST", "127.0.0.1"),
    port=getattr(settings, "REDIS_PORT", 6379),
    decode_responses=True,
)


def save_confirmation_code(email, code):
  redis_client.set(f"code:{email}", code, ex=300)


def verify_confirmation_code(email, entered_code):
  redis_key = f"code:{email}"
  stored_code = redis_client.get(redis_key)

  if not stored_code:
    return False

  if str(stored_code) == str(entered_code):
    redis_client.delete(redis_key)
    return True

  return False