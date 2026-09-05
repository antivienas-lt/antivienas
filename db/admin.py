from django.contrib import admin
from django.db.models.signals import post_delete
from django.dispatch import receiver

from db.models import User, UserProfilePicture, FriendMeetingTime, Meeting, Payment, Review, Message, UserEmailLog, MeetingEmailLog
from db.constants import MeetingStatusEnum
from db.services import complete_meeting

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  list_display=['username', 'email', 'is_superuser']


@admin.register(UserProfilePicture)
class UserProfilePictureAdmin(admin.ModelAdmin):
  list_display=['user', 'image', 'is_avatar', 'uploaded_at']

@admin.register(FriendMeetingTime)
class FriendMeetingTimeAdmin(admin.ModelAdmin):
   list_display= ['user']

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
   list_display=['created', 'user','friend', 'meeting_date_from', 'meeting_date_to', 'status', 'revenue_total', 'platform_fee', 'profit']

   def save_model(self, request, obj, form, change):
      if change:
         old = Meeting.objects.get(pk=obj.pk)

         if (old.status != obj.status and obj.status == MeetingStatusEnum.COMPLETED):
               complete_meeting(obj)
               return

      super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
   list_display=['created', 'payer', 'payer_email', 'reference_code', 'platform_fee', 'has_paid', 'is_grace_period']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
   list_display=['user', 'friend', 'liked_meeting']

@admin.register(UserEmailLog)
class UserEmailLogAdmin(admin.ModelAdmin):
   list_display=['email_type', 'user', 'sent', 'created_at']

@admin.register(MeetingEmailLog)
class MeetingEmailLogAdmin(admin.ModelAdmin):
   list_display=['email_type', 'meeting', 'sent', 'created_at']

admin.site.register([Message])

@receiver(post_delete, sender=UserProfilePicture)
def delete_avatar_file(sender, instance, **kwargs):
    """Deletes avatar file from filesystem when UserProfilePicture object is deleted."""
    if instance.image:
        instance.image.delete(save=False)