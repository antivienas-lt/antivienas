from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from app.tasks import notify_about_new_user


@receiver(user_signed_up)
def notify_new_oauth_user(request, user, **kwargs):
    notify_about_new_user.delay_on_commit(user.username)