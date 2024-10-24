from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import MinValueValidator
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError

# To ownself create the forms


class RoomForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time', 
            'min': '07:00',  # Earliest allowed time is 8 AM
            'max': '23:00',  # Latest allowed time is 11 PM
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
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        selected_date = self.cleaned_data['date']
        today = date.today()


        # If the selected date is before today, raise a validation error
        if selected_date < today:
            self.add_error('date', "Please select a date that is later than today.")


        if start_time and end_time:
            # Simplified comparison to check the 30-minute difference
            if (end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute) < 30:
                self.add_error('end_time', "End time must be at least 30 minutes after the start time.")


        return cleaned_data
    

    class Meta:
        model = Room
        fields = ['name', 'location', 'date', 'start_time', 'end_time', 'pax_required', 'description', 'participants']


class MyUserCreationForm(UserCreationForm):
    class Meta: 
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

# class RoomForm(ModelForm):
#     class Meta:
#         model = Room
#         fields = ['location', 'name', 'date', 'start_time', 'end_time', 'pax_required', 'description']
#         widgets = {
#             'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#             'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#         }


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email']


