from django.shortcuts import render
from .models import User

def profile(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "user/profile.html", {"user": user})

# Create your views here.
