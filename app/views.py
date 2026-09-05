from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models import Prefetch, Q, Count, Case, When
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from django.conf import settings
from django.utils.safestring import mark_safe

from db.models import UserProfilePicture, FriendMeetingTime, Meeting, Review, Message, UserEmailLog, MeetingEmailLog
from db.constants import Cities, Genders, Months, DAYS, YEARS, MeetingStatusEnum, BanReasonEnum
from db.services import complete_meeting

from app.forms import UserProfilePictureForm, FriendSettingsTimeForm, FriendSettingsForm, CreateMeetingForm, ReviewForm, RegisterForm
from app.rate_limit import ip_key
from app.tasks import send_activation_emails, send_password_reset_emails

import json
from datetime import date
from datetime import timedelta
from pathlib import Path
import markdown

User = get_user_model()

def FriendPage(request):

    city = request.GET.get("city", "")
    gender = request.GET.get("gender", "")
    page_number = request.GET.get("page", 1)

    if city not in Cities:
        city = ""

    if gender not in Genders:
        gender = ""

    try:
        page_number = int(page_number)
        page_number = max(1, min(page_number, 100))
    except ValueError:
        page_number = 1

    friends = (User.objects.filter(is_accepting_meetings=True)
    .annotate(review_count=Count('reviewed'))
    .prefetch_related(
        Prefetch('userprofilepicture_set',queryset=UserProfilePicture.objects.filter(is_avatar=True),to_attr='avatar')))

    if city:
        friends = friends.filter(city=city)

    if gender:
        friends = friends.filter(gender=gender)

    paginator = Paginator(friends, 20)
    page_obj = paginator.get_page(page_number)


    response = render(request, "Friends.html", {
        "friends": page_obj,
        "page_obj": page_obj,
        "friend_count": friends.count(),
        "cities": Cities,
        "genders": Genders
    })

    return response

def LoginPage(request):
    if request.user.is_authenticated:
        return redirect("index")

    email = ""
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")

        user_obj = User.objects.filter(email=email).first()
        
        if user_obj and not user_obj.is_active:
            last_log = UserEmailLog.objects.filter(user=user_obj, email_type="account_activate").order_by("-created_at").first()
            if not last_log or last_log.created_at <= timezone.now() - timedelta(minutes=5):
                log = UserEmailLog(user=user_obj,email_type="account_activate")
                log.save()
                send_activation_emails.delay_on_commit()
            return render(request, "RegisterSuccess.html", {"email": email})
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        messages.add_message(request, messages.ERROR, "Neteisingas el. paštas arba slaptažodis.")

    return render(request, "Login.html", {"email":email})

def LogoutFunc(request):
    logout(request)
    return redirect("login")

@ratelimit(key=ip_key, rate="5/m", block=True, method="POST")
def RegisterPage(request):

    if request.user.is_authenticated:
        return redirect("index")

    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            log = UserEmailLog(user=user,email_type="account_activate")
            log.save()
            send_activation_emails.delay_on_commit()

            return render(request, "RegisterSuccess.html", {"email": user.email})
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    
    return render(request, "Register.html", {"form": form})

def AboutLinksPage(request):
    return render(request, "AboutLinks.html")


def ProfilePage(request, username):
    
    user = get_object_or_404(
        User.objects.prefetch_related(
            Prefetch("userprofilepicture_set", queryset=UserProfilePicture.objects.filter(is_avatar=True), to_attr="avatar")), username=username)
    meeting_times = FriendMeetingTime.objects.filter(user=user).first()
    pics = UserProfilePicture.objects.filter(user=user)
    reviews = Review.objects.filter(friend=user)

    meeting_data = []
    if meeting_times:
        weekdays = meeting_times.schedule_data
        labels = ["Pr", "An", "Tr", "Kt", "Pn", "Št", "Sk"]
        for i, day in enumerate(weekdays):
            if day[0]:
                meeting_data.append({"day": labels[i],"from": day[1],"to": day[2],})

    response = render(request, "Profile.html", {
        "profile": user,
        "meeting_data": meeting_data,
        "images": pics,
        "reviews": reviews
    })
    return response

@login_required
def ManageProfilePhotosPage(request):
    pics = UserProfilePicture.objects.filter(user=request.user).order_by("uploaded_at")
    action = request.POST.get("action", None)
    form = UserProfilePictureForm()

    if request.method == 'POST':
        action = request.POST.get("action")

        if action == "delete":
            pk = request.POST.get("img-id")
            pic = UserProfilePicture.objects.filter(pk=pk, user=request.user).first()
            if pic:
                pic.delete()

        elif action == "upload":
            form = UserProfilePictureForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                new_image = form.save(commit=False)
                new_image.user = request.user
                new_image.save()
        
        elif action == "set-avatar":
            pk = request.POST.get("img-id")
            pic = UserProfilePicture.objects.filter(pk=pk, user=request.user).first()
            if pic:
                UserProfilePicture.objects.filter(user=request.user).update(is_avatar=False)
                pic.is_avatar = True
                pic.save()

    return render(request, "ProfilePhotos.html", {"images": pics, "form": form})


@login_required
def EditProfilePage(request):
    if request.method == "POST":
        return redirect("profile", request.user.username)
    return render(request, "EditProfile.html", {'cities': Cities, 'genders': Genders, 'months': Months, 'days': DAYS, 'years': YEARS})

@login_required
def AutoSaveProfileFunc(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        field = data.get('field')
        value = data.get('value')
        user = request.user

        allowed_fields = ['city', 'gender', 'interest1', 'interest2', 'interest3', 'interest4','about_description', 'birthdate']

        if field not in allowed_fields:
            return JsonResponse({'error': f'Invalid field: {field}'}, status=400)

        if field == 'birthdate':
            try:
                day = int(value.get('day'))
                month = int(value.get('month'))
                year = int(value.get('year'))
                user.birthdate = date(year, month, day)
            except Exception as e:
                return JsonResponse({'error': f'Invalid date: {e}'}, status=400)
        elif field == 'about_description':
            if len(value) > 1000:
                return JsonResponse({'error': f"About description too long"}, status=400)   
            setattr(user, field, value)
        else:
            value = value.strip().replace("\n", "").replace("\r", "")
            setattr(user, field, value)

        # Run model validation (only for changed field)
        try:
            user.full_clean(validate_unique=False)  # skip unique check if not needed
            user.save(update_fields=[field] if field != 'birthdate' else ['birthdate'])
            return JsonResponse({'status': 'ok', 'saved_field': field})
        except ValidationError as e:
            return JsonResponse({'error': e.message_dict.get(field, e.messages)}, status=400)


def ActivateUserFunc(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect("index")
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        messages.success(request, "Paskyra aktyvuota sėkmingai!")
        return redirect("edit-profile")

    messages.error(request, "Nepavyko aktyvuoti paskyros, nes nuoroda arba buvo panaudota, arba baigėsi jos galiojimo laikas.")
    return redirect("login")
        

@login_required
def FriendSettingsPage(request):
    user = request.user
    instance, _ = FriendMeetingTime.objects.get_or_create(user=request.user)

    if request.method == "POST":
        data = request.POST.copy()
        time_form = FriendSettingsTimeForm(data, instance=instance)
        user_form = FriendSettingsForm(data, instance=user)

        if time_form.is_valid() and user_form.is_valid():
            time_form.save()

            if not instance.is_available:
                settings = user_form.save(commit=False)
                settings.is_accepting_meetings = False

            user_form.save()
            messages.success(request, "Išsaugota!")
            return redirect("friend-settings")
            
    else:
        user_form = FriendSettingsForm(instance=user)
        time_form = FriendSettingsTimeForm(instance=instance)

    return render(request, "FriendSettings.html", {"time_form": time_form, "user_form": user_form})

@login_required
def CreateMeetingPage(request, username):

    # Get friend
    friend = (User.objects.filter(username=username, is_accepting_meetings=True)
        .prefetch_related(Prefetch("userprofilepicture_set", queryset=UserProfilePicture.objects.filter(is_avatar=True), to_attr="avatar")).first())

    if not friend:
        return redirect("index")
    
    if request.user.username == friend.username:
        messages.info(request, "Negalima susitikti su savimi :)")
        return redirect("index")
    
    meeting_count = Meeting.objects.filter(user=request.user, friend=friend, status=MeetingStatusEnum.CREATED).count()

    if meeting_count > 1:
        messages.error(request, "Per daug sukurtų susitikimų su šiuo draugu. Palaukite kol draugas juos peržiūrės.")
        return redirect("index")

    meeting_times = FriendMeetingTime.objects.get(user=friend)

    if request.method == "POST":
        create_meeting_form = CreateMeetingForm(request.POST, user=request.user, friend=friend)
        if create_meeting_form.is_valid():
            meeting = create_meeting_form.save()
            MeetingEmailLog.objects.get_or_create(meeting=meeting,email_type="meeting_created")
            messages.success(request, "Susitikimas sukurtas sėkmingai!")
            return redirect("meetings-manager")
        else:
            return render(request, "CreateMeeting.html",
                {"friend": friend,"meeting_times": meeting_times.schedule_data, "form": create_meeting_form})

    # GET request or first render
    return render(request, "CreateMeeting.html", {"friend": friend, "meeting_times": meeting_times.schedule_data})

@login_required
def MeetingManagerPage(request):

    if request.method == "POST":
        action = request.POST.get('action', None)
        pk = request.POST.get('meeting-id', None)
        meeting = Meeting.objects.filter(pk=pk).first()
        if not meeting:
            return HttpResponseBadRequest("Susitikimas nerastas")
        if request.user != meeting.friend:
            return HttpResponseForbidden("Neturite teisės keisti susitikimo statuso")
        
        if action == "confirm":
            if meeting.status != MeetingStatusEnum.CREATED:
                return HttpResponseBadRequest("Susitikimo statusas buvo atnaujintas automatiškai.")
            
            meeting.status = MeetingStatusEnum.CONFIRMED
            meeting.save()
            MeetingEmailLog.objects.get_or_create(meeting=meeting,email_type="meeting_confirmed")
        elif action == "decline":
            if meeting.status != MeetingStatusEnum.CREATED:
                return HttpResponseBadRequest("Susitikimo statusas buvo atnaujintas automatiškai.")
            
            #decline_text = request.POST.get("decline-text", "").strip()         
            #if len(decline_text) > 200:
            #    decline_text = decline_text[:200]

            meeting.status = MeetingStatusEnum.DECLINED
            #meeting.declined_reason = decline_text
            meeting.save()
            MeetingEmailLog.objects.get_or_create(meeting=meeting,email_type="meeting_declined")
        elif action == "complete":
            if meeting.status != MeetingStatusEnum.CONFIRMED:
                return HttpResponseBadRequest("Susitikimo statusas buvo atnaujintas automatiškai. Nebegalite užbaigti šio susitikimo.")
            
            confirmation_code = request.POST.get("confirmation-code", "").strip()
            if confirmation_code == meeting.confirmation_code:
                complete_meeting(meeting)
                MeetingEmailLog.objects.get_or_create(meeting=meeting,email_type="meeting_review")
                return render(request, "MeetingSuccess.html")
            else:
                messages.error(request, "Patvirtinimo kodas neteisingas. Bandykite dar kartą")

    avatar_qs = UserProfilePicture.objects.filter(is_avatar=True)
    meetings = Meeting.objects.filter(Q(user=request.user) | Q(friend=request.user)).select_related(
        'user', 'friend', 'review').prefetch_related(
            Prefetch("user__userprofilepicture_set", queryset=avatar_qs, to_attr="avatar"),
            Prefetch("friend__userprofilepicture_set", queryset=avatar_qs, to_attr="avatar")).order_by(
        Case(When(status__in=[
            MeetingStatusEnum.CREATED,
            MeetingStatusEnum.CONFIRMED,],
            then=0,),default=1,),"-created")
    return render(request, "MeetingManager.html", {"meetings": meetings, "statusEnum": MeetingStatusEnum})

@login_required
def ReviewMeetingPage(request, meeting_id):
    meeting = Meeting.objects.filter(pk=meeting_id).first()
    if not meeting:
        return HttpResponseBadRequest("Tokio susitikimo nėra.")
    if request.user != meeting.user:
        return HttpResponseForbidden("Negalite įvertinti šio draugo, nes nedalyvavote susitikime.")
    
    was_reviewed = Review.objects.filter(meeting=meeting).first()
    if was_reviewed:
        return redirect('meetings-manager')
    
    form = ReviewForm()
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.meeting = meeting
            review.user = meeting.user
            review.friend = meeting.friend
            review.save()
            return render(request, "ReviewMeetingSuccess.html")
    return render(request, "ReviewMeeting.html", {'form': form,})

@login_required
def MeetingChatPage(request, meeting_id):
    meeting = get_object_or_404(
        Meeting.objects.select_related("user", "friend"),
        Q(pk=meeting_id) &
        Q(status__in=[MeetingStatusEnum.CONFIRMED, MeetingStatusEnum.COMPLETED]) &
        (Q(user=request.user) | Q(friend=request.user))
    )
    
    messages = (
        Message.objects
        .filter(meeting=meeting)
        .select_related("sender")[:400]
    )

    avatar_map = {}
    avatar_map[meeting.user.pk] = meeting.user.fetch_avatar_url
    avatar_map[meeting.friend.pk] = meeting.friend.fetch_avatar_url
    
    return render(request, "MeetingChat.html", {"meeting": meeting, "chat_messages": messages, 
                                                "avatar_map": avatar_map, "meetingStatusEnum": MeetingStatusEnum})

@login_required
def BanPage(request):
    if request.user.banned:
        return render(request, "BanPage.html", context={"banEnum": BanReasonEnum})
    else:
        return redirect("index")

@ratelimit(key=ip_key, rate="5/m", block=True, method="POST")
def ResetPasswordLinkPage(request):
    if request.method == "POST":
        email = request.POST.get("email", "")
        if email:
            user = User.objects.filter(email=email).first()
            if user:
                last_log = UserEmailLog.objects.filter(user=user, email_type="password_reset").order_by("-created_at").first()
                if not last_log or last_log.created_at <= timezone.now() - timedelta(minutes=5):
                    log = UserEmailLog(user=user,email_type="password_reset")
                    log.save()
                    send_password_reset_emails.delay_on_commit()
        messages.success(request, "Slaptažodžio keitimo nuoroda išsiųsta.")
        messages.info(request, "Jeigu negausite laiško per 5 minutes. Bandykite dar kartą.")
        return redirect("login")
    return render(request, "ResetPasswordLink.html")

@login_required
def ModReviewChatPage(request, meeting_id):
    if request.user.is_superuser:
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if meeting:
            chat = Message.objects.filter(meeting=meeting).select_related("sender")[:400]
            avatar_map = {}
            avatar_map[meeting.user.pk] = meeting.user.fetch_avatar_url
            avatar_map[meeting.friend.pk] = meeting.friend.fetch_avatar_url
            return render(request, "MeetingChatModerator.html", {"chat": chat, "avatar_map":avatar_map})


def ResetPasswordFormPage(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if not user or not default_token_generator.check_token(user, token):
        messages.error(request, "Slaptažodžio keitimo nuoroda nebegalioja.")
        return redirect("login")

    if request.method == "POST":
        password = request.POST.get("password", "")
        if password:
            user.set_password(password)
            user.save()

            """ try:
                validate_password(password, user)
            except ValidationError as e:
                for error in e.messages: messages.error(request, error)
                return render(request, "ResetPasswordForm.html") 
            """

            messages.success(request, "Slaptažodis atnaujintas sėkmingai.")
            return redirect("login")
        else:
            messages.error(request, "Nepavyko pakeisti slaptažodžio. Bandykite dar kartą.")
            
    return render(request, "ResetPasswordForm.html")

def PrivacyPolicyPage(request):
    md_path = Path(settings.BASE_DIR) / "templates/text_pages/privacy.md"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["extra", "nl2br"])
    
    return render(request, "PrivacyPolicy.html", {
        "privacy_policy_html": mark_safe(html),
    })

def FAQPage(request):
    md_path = Path(settings.BASE_DIR) /"templates/text_pages/faq.md"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["extra", "nl2br"])
    
    return render(request, "AboutFAQ.html", {
        "faq_html": mark_safe(html),
    })

def RulesPage(request):
    md_path = Path(settings.BASE_DIR) / "templates/text_pages/rules.md"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["extra", "nl2br"])
    
    return render(request, "AboutRules.html", {
        "rules_html": mark_safe(html),
    })

def AboutUsPage(request):
    md_path = Path(settings.BASE_DIR) / "templates/text_pages/about.md"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["extra", "nl2br"])
    
    return render(request, "AboutUs.html", {
        "about_html": mark_safe(html),
    })