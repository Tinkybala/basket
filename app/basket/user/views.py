from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .models import Profile
from django.shortcuts import render, redirect   
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render
from .models import User



# Create your views here.
def register(request):

    if request.method == "POST":
        # Get for inputs
        email = request.POST.get('email')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")


        error = None

        #input validation
        if User.objects.filter(username=username).exists():
            error = "Username is already in use. Please try another username."
        elif User.objects.filter(email=email).exists():
            error = "An account has already been linked to the email provided. Please try another email."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 10:
            error = "Password has to be at least 10 charactes long"
        
        #create user and login
        if not error:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            Profile.objects.create(user=user)
            login(request, user) #Django's login function is session based
            return redirect("main")
        
        return render(request, "user/register.html", {"error": error})

    return render(request, "user/register.html")

def login_view(request):
    if request.method == "POST":
        # Get for inputs
        username = request.POST.get('username')
        password = request.POST.get("password")
    
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect(reverse("main"))
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "user/login.html")

def logout_view(request):
    logout(request)
    return redirect(reverse("login"))

# update user details to be fixed
def profile(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        print("fix this part")
        # Fix this
    return render(request, "user/profile.html", {"user": user})