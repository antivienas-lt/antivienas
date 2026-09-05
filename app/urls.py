from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from app.consumers import ChatConsumer

urlpatterns = [
    path("", views.FriendPage, name="index"),
    path("login/", views.LoginPage, name="login"),
    path("logout/", views.LogoutFunc, name="logout"),
    path("register/", views.RegisterPage, name="register"),
    path("info/", views.AboutLinksPage, name="about-links"),
    path("about/", views.AboutUsPage, name="about-us"),
    path("privacy/", views.PrivacyPolicyPage, name="privacy-policy"),
    path("rules/", views.RulesPage, name="rules"),
    path("faq/", views.FAQPage, name="faq"),
    path("av/<str:username>/", views.ProfilePage, name="profile"),
    path("edit-profile/", views.EditProfilePage, name="edit-profile"),
    path("manage-photos/", views.ManageProfilePhotosPage, name="manage-photos"),
    path('friend-settings/', views.FriendSettingsPage, name='friend-settings'),

    path('meeting/<str:username>/new/', views.CreateMeetingPage, name='new-meeting'),
    path('meeting/<int:meeting_id>/review/', views.ReviewMeetingPage, name='review-meeting'),
    path('meeting/<int:meeting_id>/chat/', view=views.MeetingChatPage, name='meeting-chat'),
    path('meetings/', views.MeetingManagerPage, name="meetings-manager"),

    path('banned/', views.BanPage, name="ban-page"),

    path('password-reset/', views.ResetPasswordLinkPage, name="reset-password-link"),
    path('password/reset/<uidb64>/<token>/', views.ResetPasswordFormPage, name="reset-password-form"),

    path('modtools/chat/<int:meeting_id>/', view=views.ModReviewChatPage),
    
    path("activate/<uidb64>/<token>/", views.ActivateUserFunc, name="activate_user"),
    path('api/edit-profile/autosave/', views.AutoSaveProfileFunc, name='autosave-profile'),
]

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<meeting_id>\d+)/$", ChatConsumer.as_asgi()),
]

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    
    # In production, you’ll want to serve /media/ via Nginx or Apache, not Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)