from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import MinValueValidator
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from .models import Room, User
from django.utils import timezone

# To ownself create the forms


class RoomForm(forms.ModelForm):


    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': date.today().isoformat()  # Sets today's date as the minimum selectable date
            }
        )
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time', 
            'min': '07:00',  
            'max': '23:00',  
        })
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time', 
            'min': '07:00', 
            'max': '23:00'
        })
    )

    pax_required = forms.IntegerField(
        label='Pax Required',
        validators=[MinValueValidator(2)],  # Enforce minimum value of 2
    )
    


    def clean(self):
            cleaned_data = super().clean()
            self.validate_dates(cleaned_data)
            return cleaned_data

    def validate_dates(self, cleaned_data):
            start_time = cleaned_data.get("start_time")
            end_time = cleaned_data.get("end_time")
            selected_date = self.cleaned_data['date']
            today = timezone.localdate()  # Localized current date
            current_time = timezone.localtime().time()

            # If the selected date is before today, raise a validation error
            if selected_date < today:
                self.add_error('date', "Please select a date that is later than today.")

            elif selected_date == today and start_time:
                if start_time < current_time:
                    self.add_error('start_time', f"Please select a start time that is later than the current time: {current_time.strftime('%H:%M:%S')}.")

            if start_time and end_time:
                # Simplified comparison to check the 30-minute difference
                if (end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute) < 30:
                    self.add_error('end_time', "End time must be at least 30 minutes after the start time.")

    class Meta:
        model = Room
        fields = ['name', 'location', 'date', 'start_time', 'end_time', 'pax_required', 'description', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'bio']


class MyUserCreationForm(UserCreationForm):
    class Meta: 
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']




# For email notif (Testing)
class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email_notifications_enabled', 'telegram_notifications_enabled']  # Add more fields if necessary

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize your form here if needed
