from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from db.constants import Genders, Cities, Hours, CITY_COORDINATES, MeetingStatusEnum, BanReasonEnum
from PIL import Image
import os
import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


DEFAULT_USER_IMG = settings.STATIC_URL + "assets/default_avatar.webp"

def user_avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    today = timezone.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"{today}.{ext}"
    return os.path.join(instance.user.username, filename)


def generate_confirmation_code():
    return f"{random.randrange(100000):05d}"


class User(AbstractUser):
    email = models.EmailField(unique=True)

    # profile stuff
    gender = models.CharField(max_length=20,choices=Genders.choices,blank=True,default="")
    city = models.CharField(max_length=50,choices=Cities.choices,blank=True,default="")
    birthdate = models.DateField(blank=True,null=True)

    interest1 = models.CharField(max_length=25, blank=True, default="")
    interest2 = models.CharField(max_length=25, blank=True, default="")
    interest3 = models.CharField(max_length=25, blank=True, default="")
    interest4 = models.CharField(max_length=25, blank=True, default="")

    about_description = models.TextField(blank=True, default="")

    #friend stuff
    is_accepting_meetings = models.BooleanField(default=False)
    
    profit_per_hour = models.PositiveIntegerField(default=5, validators=[MinValueValidator(5)])

    banned = models.IntegerField(blank=True, null=True, choices=BanReasonEnum.choices)

    bank_recipient = models.CharField(max_length=100, blank=True, default="")
    bank_account_number = models.CharField(max_length=34, blank=True, default="")


    def __str__(self):
        return self.username
    
    @property
    def interests(self):
        temp_arr = []
        if self.interest1:
            temp_arr.append(self.interest1)
        if self.interest2:
            temp_arr.append(self.interest2)
        if self.interest3:
            temp_arr.append(self.interest3)
        if self.interest4:
            temp_arr.append(self.interest4)
        return temp_arr
    
    @property
    def age(self):
        if self.birthdate:
            return str(int((timezone.now().date() - self.birthdate).days / 365.25))
    
    @property
    def revenue_per_hour(self):
        # 20% of profit
        return int(self.profit_per_hour * 1.20 + 0.9999)
    

    @property
    def avatar_url(self):
        # prefetched in view
        if hasattr(self, "avatar") and self.avatar:
            return self.avatar[0].image.url
        return DEFAULT_USER_IMG
    
    @property
    def fetch_avatar_url(self):
        # only use for singular instance rendering
        avatar = UserProfilePicture.objects.filter(user=self, is_avatar=True).first()
        if avatar:
            return avatar.image.url
        return DEFAULT_USER_IMG
    
    @property
    def city_coords(self):
        lat,lng = CITY_COORDINATES[self.city]
        return [lat, lng]


class UserProfilePicture(models.Model):
    """User profile pictures"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_avatar_upload_path)
    is_avatar = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    def rebalance_avatar(self, *args, **kwargs):
        """after deleting an image, makes sure that there's an avatar image"""

        user_images = UserProfilePicture.objects.filter(user=self.user).order_by("uploaded_at")

        if user_images.count() == 0:
            return

        avatar = user_images.filter(is_avatar=True).first()

        if not avatar:
            image = user_images.first()
            image.is_avatar = True
            image.save()

    
    def delete(self, *args, **kwargs):
        super(UserProfilePicture, self).delete(*args, **kwargs)
        self.rebalance_avatar()
    
    def clean(self):
        #help later
        if hasattr(self, 'user'):
            if UserProfilePicture.objects.filter(user=self.user).count() >= 6:
                raise ValidationError(
                    {"image": "Negalima įkelti daugiau nei 6 nuotraukas"}
                )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # make square (center-crop)
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            right = (width + min_dim) // 2
            bottom = (height + min_dim) // 2
            img = img.crop((left, top, right, bottom))

            img = img.resize((512, 512), Image.LANCZOS)

            img.save(self.image.path, quality=95, optimize=True)
            self.rebalance_avatar()


class FriendMeetingTime(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    mon_day = models.BooleanField(default=True, verbose_name="Available Monday")
    mon_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    mon_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    tue_day = models.BooleanField(default=True, verbose_name="Available Tuesday")
    tue_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    tue_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    wed_day = models.BooleanField(default=True, verbose_name="Available Wednesday")
    wed_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    wed_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    thu_day = models.BooleanField(default=True, verbose_name="Available Thursday")
    thu_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    thu_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    fri_day = models.BooleanField(default=True, verbose_name="Available Friday")
    fri_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    fri_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    sat_day = models.BooleanField(default=True, verbose_name="Available Saturday")
    sat_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    sat_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    sun_day = models.BooleanField(default=True, verbose_name="Available Sunday")
    sun_from = models.IntegerField(choices=Hours.choices, default=Hours.H00)
    sun_to = models.IntegerField(choices=Hours.choices, default=Hours.H24)

    def __str__(self):
        return f"{self.user.username}'s Meeting Availability"
    
    @property
    def schedule_data(self):
        return [
            [self.mon_day, self.mon_from, self.mon_to],
            [self.tue_day, self.tue_from, self.tue_to],
            [self.wed_day, self.wed_from, self.wed_to],
            [self.thu_day, self.thu_from, self.thu_to],
            [self.fri_day, self.fri_from, self.fri_to],
            [self.sat_day, self.sat_from, self.sat_to],
            [self.sun_day, self.sun_from, self.sun_to],
        ]
    
    @property
    def is_available(self):
        if self.mon_day or self.tue_day or self.wed_day or self.thu_day or self.fri_day or self.sat_day or self.sun_day:
            return True
        else:
            return False
        
class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")

    lat = models.FloatField()
    lng = models.FloatField()
    meeting_date_from = models.DateTimeField()
    meeting_date_to = models.DateTimeField()
    meeting_description = models.TextField()
    revenue_total = models.PositiveIntegerField()
    platform_fee = models.PositiveIntegerField()

    status = models.IntegerField(choices=MeetingStatusEnum, default=MeetingStatusEnum.CREATED)

    declined_reason = models.CharField(max_length=200, blank=True, default="")
    confirmation_code = models.CharField(max_length=5,default=generate_confirmation_code)

    created = models.DateTimeField(auto_now_add=True)
    
    @property
    def profit(self):
        return self.revenue_total - self.platform_fee

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def google_maps_url(self):
        return f"https://www.google.com/maps/place/{self.lat},{self.lng}"
    
    @property
    def day_month_str(self):
        months = [
            "Sausio", "Vasario", "Kovo", "Balandžio", "Gegužės",
            "Birželio", "Liepos", "Rugpjūčio", "Rugsėjo", "Spalio",
            "Lapkričio", "Gruodžio"
        ]
        dt = self.meeting_date_from
        month_name = months[dt.month - 1]

        return f"{month_name} {dt.day:02d} d."
    
    @property
    def time_range_str(self):
        if not self.meeting_date_from or not self.meeting_date_to:
            return ""
        
        local_from = timezone.localtime(self.meeting_date_from)
        local_to = timezone.localtime(self.meeting_date_to)

        return (
            f"{local_from:%H:%M} - "
            f"{local_to:%H:%M}"
        )
    
    @property
    def time_left_to_confirm(self):
        if not self.meeting_date_from:
            return ""

        deadline = self.meeting_date_from - timedelta(hours=3)

        return deadline
    
    def __str__(self):
        return f"{self.user} X {self.friend}"

class MeetingEmailLog(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    email_type = models.CharField(max_length=50)

    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meeting", "email_type")

class UserEmailLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_type = models.CharField(max_length=50)

    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    

class Payment(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.PROTECT)
    payer = models.ForeignKey(User, on_delete=models.PROTECT)
    payer_email = models.EmailField()
    platform_fee = models.PositiveIntegerField()
    reference_code = models.PositiveBigIntegerField(unique=True, editable=False, blank=True, null=True)

    has_paid = models.BooleanField(default=False)
    is_grace_period = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.reference_code:
            year = self.created.year if self.created else timezone.now().year
            self.reference_code = int(f"{year-2000}{self.pk:04d}")
            super().save(update_fields=["reference_code"])

class Review(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewed")

    liked_meeting = models.BooleanField()
    comment = models.CharField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    was_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]