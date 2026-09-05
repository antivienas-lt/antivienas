from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.cache import cache

from db.models import Meeting, User, MeetingEmailLog, UserEmailLog
from db.constants import MeetingStatusEnum


meeting_manager_link = f"{settings.FRONTEND_DOMAIN}/meetings/"


@shared_task
def mark_failed_meetings():
    now = timezone.now()
    threshold_time = now - timedelta(hours=24)

    meetings = (Meeting.objects.select_related("user", "friend")
        .filter(status=MeetingStatusEnum.CONFIRMED,
                meeting_date_to__lte=threshold_time
    ))

    meeting_ids = list(meetings.values_list("id", flat=True))

    if not meeting_ids:
        return "0 meetings marked as FAILED"
    
    Meeting.objects.filter(id__in=meeting_ids).update(
        status=MeetingStatusEnum.FAILED
    )

    user_logs = [
        MeetingEmailLog(
            meeting_id=mid,
            email_type="meeting_failed_user"
        )
        for mid in meeting_ids
    ]
    friend_logs = [
        MeetingEmailLog(
            meeting_id=mid,
            email_type="meeting_failed_friend"
        )
        for mid in meeting_ids
    ]

    MeetingEmailLog.objects.bulk_create(user_logs, ignore_conflicts=True)
    MeetingEmailLog.objects.bulk_create(friend_logs, ignore_conflicts=True)

    return f"{len(meeting_ids)} meetings marked as FAILED"

@shared_task
def mark_expired_meetings():
    now = timezone.now()
    threshold_time = now + timedelta(hours=3)

    meetings = (Meeting.objects.select_related("user", "friend")
        .filter(status=MeetingStatusEnum.CREATED,
                meeting_date_from__lte=threshold_time
    ))

    meeting_ids = list(meetings.values_list("id", flat=True))

    if not meeting_ids:
        return "0 meetings marked as EXPIRED"
    
    Meeting.objects.filter(id__in=meeting_ids).update(
        status=MeetingStatusEnum.EXPIRED
    )

    user_logs = [
        MeetingEmailLog(
            meeting_id=mid,
            email_type="meeting_expired_user"
        )
        for mid in meeting_ids
    ]

    friend_logs = [
        MeetingEmailLog(
            meeting_id=mid,
            email_type="meeting_expired_friend"
        )
        for mid in meeting_ids
    ]

    MeetingEmailLog.objects.bulk_create(user_logs, ignore_conflicts=True)
    MeetingEmailLog.objects.bulk_create(friend_logs, ignore_conflicts=True)

    return f"{len(meeting_ids)} meetings marked as EXPIRED"


@shared_task
def send_meeting_failed_emails(connection):
    user_logs = MeetingEmailLog.objects.select_related("meeting__user").filter(email_type="meeting_failed_user",sent=False)
    friend_logs = MeetingEmailLog.objects.select_related("meeting__friend").filter(email_type="meeting_failed_friend",sent=False)
    log_ids = []

    if not user_logs and not friend_logs:
        return
         
    context = {"support_email": settings.DEFAULT_SUPPORT_EMAIL}

    subject = "Automatiškai atšauktas susitikimas"
    text_content = render_to_string("email/meeting-failed.txt", context)
    html_content = render_to_string("email/meeting-failed.html", context)


    for log in user_logs:
        try:
            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.meeting.user.email]
                ,reply_to=[settings.DEFAULT_SUPPORT_EMAIL], connection=connection)

            email.attach_alternative(html_content, "text/html")
            res = email.send(fail_silently=True)

            if res == 1: #email sent succesffuly 0 - err
                log_ids.append(log.pk)
        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.user.email}: {e}")
            continue
    
    for log in friend_logs:
        try:
            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.meeting.friend.email]
                ,reply_to=[settings.DEFAULT_SUPPORT_EMAIL], connection=connection)

            email.attach_alternative(html_content, "text/html")
            res = email.send(fail_silently=True)

            if res == 1:
                log_ids.append(log.pk)
        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.friend.email}: {e}")
            continue

    MeetingEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    return f"sent meeting_failed emails to: {len(log_ids)}/{len(user_logs) + len(friend_logs)} recipients."


@shared_task
def send_meeting_expired_emails(connection):
    user_logs = MeetingEmailLog.objects.select_related("meeting__user").filter(email_type="meeting_expired_user",sent=False)
    friend_logs = MeetingEmailLog.objects.select_related("meeting__friend").filter(email_type="meeting_expired_friend",sent=False)    
    log_ids = []

    if not user_logs and not friend_logs:
        return
        
    context = {"meeting_manager_link": meeting_manager_link,"support_email": settings.DEFAULT_SUPPORT_EMAIL}

    subject = "Automatiškai atšauktas susitikimas"
    text_content = render_to_string("email/meeting-expired.txt", context)
    html_content = render_to_string("email/meeting-expired.html", context)

    for log in user_logs:
        try:
            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.meeting.user.email],connection=connection)

            email.attach_alternative(html_content, "text/html")
            res = email.send()

            if res == 1:
                log_ids.append(log.pk)
        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.user.email}: {e}")
            continue
    
    for log in friend_logs:
        try:
            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.meeting.friend.email],connection=connection)

            email.attach_alternative(html_content, "text/html")
            res = email.send()

            if res == 1:
                log_ids.append(log.pk)
        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.friend.email}: {e}")
            continue

    MeetingEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    return f"sent meeting_expired emails to: {len(log_ids)}/{len(user_logs) + len(friend_logs)} recipients."

@shared_task
def send_meeting_declined_emails(connection):
    logs = MeetingEmailLog.objects.select_related('meeting__user').filter(email_type="meeting_declined", sent=False)
    log_ids = []

    if not logs:
        return

    context = {"meeting_manager_link": meeting_manager_link,"support_email": settings.DEFAULT_SUPPORT_EMAIL}

    subject = "Draugas atmetė pasiūlymą susitikti"
    text_content = render_to_string("email/meeting-declined.txt",context)
    html_content = render_to_string("email/meeting-declined.html",context)

    for log in logs:
        try:
            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.meeting.user.email], connection=connection)

            email.attach_alternative(html_content, "text/html")
            print(f"sending meeting_declined email to: {log.meeting.user.email}")

            res = email.send()
            
            if res == 1:
                log_ids.append(log.pk)

        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.user.email}: {e}")
            continue

    MeetingEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    print(f"Task: Sent meeting_declined emails: ({len(log_ids)}/{len(logs)})")


@shared_task
def send_meeting_created_emails(connection):
    logs = MeetingEmailLog.objects.select_related('meeting__friend').filter(email_type="meeting_created", sent=False)
    log_ids = []

    if not logs:
        return
    
    context = {"meeting_manager_link": meeting_manager_link,"support_email": settings.DEFAULT_SUPPORT_EMAIL}
    subject = "Naujas pasiūlymas susitikti"
    text_content = render_to_string("email/meeting-created.txt",context)
    html_content = render_to_string("email/meeting-created.html",context)

    for log in logs:
        try:

            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.meeting.friend.email], connection=connection)

            email.attach_alternative(html_content, "text/html")
            print(f"sending meeting_created email to: {log.meeting.friend.email}")
            
            res = email.send()
            
            if res == 1:
                log_ids.append(log.pk)
        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.friend.email}: {e}")
            continue

    MeetingEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    print(f"Task: Sent meeting_created emails: ({len(log_ids)}/{len(logs)})")

@shared_task
def send_meeting_confirmed_emails(connection):
    logs = MeetingEmailLog.objects.select_related('meeting__user').filter(email_type="meeting_confirmed", sent=False)
    log_ids = []

    if not logs:
        return

    for log in logs:
        try: 
            user_email = log.meeting.user.email

            context = {
                "confirmation_code": log.meeting.confirmation_code,
                "support_email": settings.DEFAULT_SUPPORT_EMAIL,
                "meeting_manager_link": meeting_manager_link,
            }

            subject = "Pasiūlymas susitikti priimtas!"

            text_content = render_to_string("email/meeting-confirmed.txt",context)
            html_content = render_to_string("email/meeting-confirmed.html",context)

            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[user_email], connection=connection)

            email.attach_alternative(html_content, "text/html")
            print(f"Sending meeting_confirmed email to: {user_email}")

            res = email.send()
            
            if res == 1:
                log_ids.append(log.pk)

        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.user.email}: {e}")
            continue

    MeetingEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    print(f"Task: Sent meeting_confirmed emails: ({len(log_ids)}/{len(logs)})")

@shared_task
def send_review_meeting_emails(connection):
    now = timezone.now()
    logs = MeetingEmailLog.objects.select_related('meeting__user').filter(email_type="meeting_review", sent=False, meeting__meeting_date_to__lte=now)
    log_ids = []

    if not logs:
        return

    for log in logs:
        try: 
            user_email = log.meeting.user.email
            review_link = f"{settings.FRONTEND_DOMAIN}/meeting/{log.meeting.id}/review/"

            context = {
                "support_email": settings.DEFAULT_SUPPORT_EMAIL,
                "review_link": review_link,
            }

            subject = "Kaip sekėsi susitikime? Papasakok."

            text_content = render_to_string("email/meeting-review.txt",context)
            html_content = render_to_string("email/meeting-review.html",context)

            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[user_email], connection=connection)

            email.attach_alternative(html_content, "text/html")
            print(f"Sending meeting_review email to: {user_email}")

            res = email.send()
            
            if res == 1:
                log_ids.append(log.pk)

        except Exception as e:
            print(f"ERROR: Could not send email to {log.meeting.user.email}: {e}")
            continue

    MeetingEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    print(f"Task: Sent meeting_review emails: ({len(log_ids)}/{len(logs)})")
    

@shared_task
def send_activation_emails():
    connection = get_connection()
    connection.open()

    logs = UserEmailLog.objects.select_related('user').filter(email_type="account_activate", sent=False)
    log_ids = []

    if not logs:
        return

    for log in logs:
        try:
            uid = urlsafe_base64_encode(force_bytes(log.user.pk))
            token = default_token_generator.make_token(log.user)

            activation_link = f"{settings.FRONTEND_DOMAIN}/activate/{uid}/{token}/"

            context = {"activation_link": activation_link,"support_email": settings.DEFAULT_SUPPORT_EMAIL}

            subject = "Paskyros aktyvavimo nuoroda"
            text_content = render_to_string("email/activate-account.txt",context)
            html_content = render_to_string("email/activate-account.html",context)

            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.user.email], connection=connection)

            email.attach_alternative(html_content, "text/html")
            print(f"Sending activation email to: {log.user.email}")

            res = email.send()

            if res == 1:
                log_ids.append(log.pk)

        except Exception as e:
            print(f"ERROR: Could not send email to {log.user.email}: {e}")
            continue
    
    UserEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    print(f"Task: Sent account_activate emails: ({len(log_ids)}/{len(logs)})")

    connection.close()

@shared_task
def send_password_reset_emails():
    connection = get_connection()
    connection.open()

    logs = UserEmailLog.objects.select_related('user').filter(email_type="password_reset", sent=False)
    log_ids = []

    if not logs:
        return
    
    for log in logs:

        try:
            uid = urlsafe_base64_encode(force_bytes(log.user.pk))
            token = default_token_generator.make_token(log.user)

            reset_link = f"{settings.FRONTEND_DOMAIN}/password/reset/{uid}/{token}/"

            context = {"reset_link": reset_link,"support_email": settings.DEFAULT_SUPPORT_EMAIL}

            subject = "Slaptažodžio keitimas"
            text_content = render_to_string("email/reset-password.txt",context)
            html_content = render_to_string("email/reset-password.html",context)

            email = EmailMultiAlternatives(subject=subject,body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,to=[log.user.email], connection=connection)

            email.attach_alternative(html_content, "text/html")
            print(f"sending password_reset email to: {log.user.email}")

            res = email.send()

            if res == 1:
                log_ids.append(log.pk)

        except Exception as e:
            print(f"ERROR: Could not send email to {log.user.email}: {e}")
            continue
    
    UserEmailLog.objects.filter(id__in=log_ids).update(sent=True, sent_at=timezone.now())
    print(f"Task: Sent password_reset emails: ({len(log_ids)}/{len(logs)})")

    connection.close()
        


@shared_task
def delete_unactivated_users():
    threshold = timezone.now() - timedelta(hours=24)

    deleted_count, _ = (
        User.objects
        .filter(
            is_active=False,
            date_joined__lte=threshold
        )
        .delete()
    )

    return f"{deleted_count} users deleted"


@shared_task
def send_all_emails():
    lock_key = "send_all_emails_lock"
    lock_timeout = 60 * 10  # 10 minutes

    acquired = cache.add(lock_key, "true", lock_timeout)

    if not acquired:
        return "send_all_emails task is already running"

    try: 
        connection = get_connection()
        connection.open()

        send_meeting_created_emails(connection)
        send_meeting_confirmed_emails(connection)
        send_meeting_declined_emails(connection)
        send_meeting_expired_emails(connection)
        send_meeting_failed_emails(connection)
        send_review_meeting_emails(connection)

        connection.close()
    finally:
        cache.delete(lock_key)
