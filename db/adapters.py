import secrets
import re

from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        email = data.get("email", "")

        # Use the email prefix as the username base.
        base = email.split("@")[0].lower() if email else "user"

        # Remove characters that aren't suitable for a username.
        base = re.sub(r"[^a-z0-9._-]", "", base)

        base = base[:25] or "user"

        # Generate a username that doesn't already exist.
        while True:
            suffix = secrets.token_hex(3)
            username = f"{base}_{suffix}"

            if not User.objects.filter(
                username__iexact=username
            ).exists():
                break

        user.username = username

        if email:
            user.email = email.strip().lower()

        return user