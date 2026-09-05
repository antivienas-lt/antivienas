from django import forms
from db.models import UserProfilePicture, FriendMeetingTime, User, Meeting, Review
from db.constants import Hours
from django.utils import timezone
from datetime import datetime, timedelta, time

# forms.py

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegisterForm(forms.ModelForm):

    is_of_age = forms.BooleanField(
        required=True,
        error_messages={"required": "Turite patvirtinti, kad jums yra 18+"}
    )
    rules = forms.BooleanField(
        required=True,
        error_messages={"required": "Turite sutikti su taisyklėmis"}
    )
    privacy = forms.BooleanField(
        required=True,
        error_messages={"required": "Turite sutikti su privatumo sąlygomis"}
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

        error_messages = {
            "username": {
                "required": "Slapyvardis yra privalomas laukas.",
            },
            "email": {
                "required": "El. paštas yra privalomas laukas.",
                "invalid": "El. pašto adresas neatitinka formato",
            },
            "password":{
                "required": "Slaptažodis yra privalomas laukas",
            }
        }

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip().lower()

        if User.objects.filter(username=username).exists():
            raise ValidationError("Toks slapyvardis jau egzistuoja.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if User.objects.filter(email=email).exists():
            raise ValidationError("Toks el. paštas jau egzistuoja.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        #validate_password(password)  # uses Django validators
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        user.is_active = False

        if commit:
            user.save()

        return user

class UserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfilePicture
        fields = ['image']
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned = super().clean()

        if UserProfilePicture.objects.filter(user=self.user).count() >= 6:
            raise forms.ValidationError("Klaida: galite įkelti iki 6 nuotraukų")
        return cleaned

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Klaida: failo dydis viršija 5MB limitą.")
        return image
    

class FriendSettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "is_accepting_meetings",
            "profit_per_hour"
        ]

    
class FriendSettingsTimeForm(forms.ModelForm):

    class Meta:
        model = FriendMeetingTime
        fields = [
            "mon_day", "mon_from", "mon_to",
            "tue_day", "tue_from", "tue_to",
            "wed_day", "wed_from", "wed_to",
            "thu_day", "thu_from", "thu_to",
            "fri_day", "fri_from", "fri_to",
            "sat_day", "sat_from", "sat_to",
            "sun_day", "sun_from", "sun_to",
        ]

    WEEKDAYS = {
        "mon": "Pirmadienis",
        "tue": "Antradienis",
        "wed": "Trečiadienis",
        "thu": "Ketvirtadienis",
        "fri": "Penktadienis",
        "sat": "Šeštadienis",
        "sun": "Sekmadienis",
    }

    def clean(self):
        cleaned = super().clean()

        for key in self.WEEKDAYS:
            day = cleaned.get(f"{key}_day")
            time_from = cleaned.get(f"{key}_from")
            time_to = cleaned.get(f"{key}_to")

            if day:
                if time_from == 0 and time_to == 0:
                    cleaned[f"{key}_day"] = False
                    continue

                if time_from >= time_to:
                    self.add_error(
                        f"{key}_day",
                        f"{self.WEEKDAYS[key]}: laikas „nuo“ turi būti ankstesnis nei „iki“."
                    )
                    continue

        return cleaned
    
class CreateMeetingForm(forms.ModelForm):
    # Raw user input fields (not part of the model)
    meeting_date = forms.DateField(
        required=True,
        error_messages={
            "required": "Prašome pasirinkti susitikimo datą.",})

    time_from = forms.ChoiceField(
        choices=Hours.choices,
        required=True,
        error_messages={"required": "Prašome pasirinkti pradžios laiką."})

    time_to = forms.ChoiceField(
        choices=Hours.choices,
        required=True, error_messages={"required": "Prašome pasirinkti pabaigos laiką.",})

    final_price = forms.IntegerField(required=False)

    #lat = forms.FloatField(required=False)
    #lng = forms.FloatField(required=False)

    class Meta:
        model = Meeting
        fields = [
            "meeting_description",
            "lat",
            "lng"
        ]

        error_messages = {
            "meeting_description": {"required": "Susitikimo aprašymas negali būti tuščias."},
            "lat": {"required": ""},
            "lng": {"required": ""},
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.friend = kwargs.pop("friend", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        # Validate user/friend
        
        if self.user == self.friend:
            self.add_error(None, "Negalite susitikti su pačiu savimi.")

        cleaned = super().clean()

        meeting_date = cleaned.get("meeting_date")
        time_from = cleaned.get("time_from")
        time_to = cleaned.get("time_to")
        client_price = cleaned.get("final_price")
        lat = cleaned.get("lat")
        lng = cleaned.get("lng")

        print("latlng:", lat, lng)
        if lng is None or lat is None:
            self.add_error(None, "Nenurodėte susitikimo vietos žemėlapyje.")

        # Convert time choices to integers

        if time_from and time_to:
            try:
                time_from = int(time_from)
                time_to = int(time_to)
            except (TypeError, ValueError):
                self.add_error(None, "Nėra nurodyto laiko, arba netinkamas laiko formatas.")
                return cleaned
    
        if self.errors:
            return cleaned

        # Validate time range
        if time_from >= time_to:
            self.add_error("time_to", "Laikas 'nuo' negali būti didesnis arba lygus 'iki'.")
            return cleaned

        # Convert to datetime
        try:
            date_obj = meeting_date
            meeting_date_from = timezone.make_aware(
                datetime.combine(date_obj, time(hour=time_from))
            )

            if time_to == Hours.H24:
                date_obj += timedelta(days=1)
                time_to = 0

            meeting_date_to = timezone.make_aware(
                datetime.combine(date_obj, time(hour=time_to))
            )

        except Exception:
            raise forms.ValidationError("Klaida konvertuojant datą / laiką.")

        # Revenue calculations
        duration_hours = (meeting_date_to - meeting_date_from).total_seconds() / 3600
        revenue = self.friend.revenue_per_hour * duration_hours
        profit = self.friend.profit_per_hour * duration_hours

        if revenue != client_price:
            self.add_error("final_price", "Vartotojo kaina nesutampa su serverio kaina.")

        # Store computed fields for save()
        cleaned["computed_meeting_date_from"] = meeting_date_from
        cleaned["computed_meeting_date_to"] = meeting_date_to
        cleaned["computed_revenue_total"] = revenue
        cleaned["computed_platform_fee"] = revenue - profit

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Assign user and friend
        instance.user = self.user
        instance.friend = self.friend

        # Assign computed values
        instance.lat = self.cleaned_data["lat"]
        instance.lng = self.cleaned_data["lng"]
        instance.meeting_date_from = self.cleaned_data["computed_meeting_date_from"]
        instance.meeting_date_to = self.cleaned_data["computed_meeting_date_to"]
        instance.revenue_total = self.cleaned_data["computed_revenue_total"]
        instance.platform_fee = self.cleaned_data["computed_platform_fee"]

        if commit:
            instance.save()

        return instance
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["comment", "liked_meeting"]