from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm
from django import forms


# To ownself create the forms


class RoomForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # HTML5 date picker
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))  # HTML5 time picker
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))  # HTML5 time picker

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


