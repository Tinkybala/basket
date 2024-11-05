# General Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.utils import timezone
import requests
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

# Authentification
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required

# Email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# From base
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from .utils import filter_rooms, get_home_related_data, get_geocode_location, get_user_activities, get_profile_data
from .tokens import account_activation_token
from .forms import NotificationPreferenceForm

# For Future Use
from math import radians, sin, cos, sqrt, atan2
from django.urls import reverse
from django.http import HttpResponseRedirect


# Email Related:
def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")

    else:
        messages.error(request, "Activation link is invalid!")
    return redirect('login')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account"
    message = render_to_string("base/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send() == False:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


# Registration & Login
def registerUser(request):
    form = MyUserCreationForm()

    if request.method =="POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return render(request, 'base/checkemailpage.html')
        else:
            messages.error(request, 'Error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})

def loginUser(request):
    page = 'login'

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect ('home')
        else:
            messages.error(request, 'Username/Password incorrect')
    
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


# Main Page:
@login_required(login_url='login')
def home(request):
    # Fetch search and filter criteria from request
    search_term = request.GET.get('q', '')
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')
    time = request.GET.get('time', '')

    rooms = filter_rooms(search_term, location, date, time)

    topics, room_count, room_messages = get_home_related_data(request.user, rooms)

    activities = get_user_activities(request.user)

    # Check if the current user has joined and if the room is full for each room
    for room in rooms:
        room.has_joined = room.user_has_joined(request.user)
        room.is_full = room.is_full

    session_id = request.user.id
    request.session['session_id'] = session_id
    telegram_link = f"https://t.me/basketballReminderbot?start={session_id}"

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'activities': activities,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        'telegram_link': telegram_link,
    }

    return render(request, 'base/home.html', context)

@login_required(login_url = 'login')
def createRoom(request):
    form = RoomForm()
    # Query all locations from the Room model (not distinct)
    locations = Room.objects.values_list('location', flat=True)

    if request.method == "POST":
        form = RoomForm(request.POST)
        
        if form.is_valid():
            # Get or create the 'basketball' topic
            topic, created = Topic.objects.get_or_create(name='basketball')

            # Save the form data but don't commit yet
            room = form.save(commit=False)
            room.host = request.user  # Set the current user as the host
            room.topic = topic  # Set the topic to 'basketball'
            room.save()  # Save the room instance
            
            room.participants.add(request.user)
            return redirect('home')
        else:
            # Print form errors for debugging purposes
            print(form.errors)

    context = {
        'form': form, 
        'locations': locations,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        }
    return render(request, 'base/room_form.html', context)




# Room Page:
@login_required(login_url = 'login')
def room(request,pk):
    room = get_object_or_404(Room, id=pk)

    participants = room.participants.all()
    activities = get_user_activities(request.user)
    participants_count = room.participants.count()

    room.is_full = room.is_full
    room.has_joined = room.user_has_joined(request.user)

    latitude, longitude = get_geocode_location(room.location)


    context = {'room': room,  'participants': participants, 'activities': activities,
                'GOOGLE_API_KEY': settings.GOOGLE_API_KEY, 
                'latitude': latitude,
                'longitude': longitude,}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def mainJoinEvent(request, pk):
    room = get_object_or_404(Room, id=pk)
    participants = room.participants.all()  # Retrieve all participants
    
    # Check if the user is already in participants
    has_joined = participants.filter(id=request.user.id).exists()

    if request.method == 'POST':
        room.participants.add(request.user)
        return redirect(request.META.get('HTTP_REFERER', ''))

    context = {
        'room': room,
        'participants': participants,
        'user': request.user,
    }
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def quitEvent(request, pk):
    room = get_object_or_404(Room, id=pk)
    participants = room.participants.all()  # Retrieve all participants
    
    # Check if the user is already in participants
    has_joined = participants.filter(id=request.user.id).exists()


    if request.method == 'POST':
        room.participants.remove(request.user)
        return redirect(request.META.get('HTTP_REFERER', ''))

    context = {
        'room': room,
        'participants': participants,
        'user': request.user,
    }
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    # Get the room by its primary key
    room = get_object_or_404(Room, id=pk)

    # Only allow the host of the room to update the details
    if request.user != room.host:
        return HttpResponse('Not allowed')

    # Query all locations from the Room model (not distinct)
    locations = Room.objects.values_list('location', flat=True)

    # Handle the form submission
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)  # Pass the instance to update

        if form.is_valid():
            # Get or create the 'basketball' topic
            topic, created = Topic.objects.get_or_create(name='basketball')

            # Save the form data but don't commit yet
            room = form.save(commit=False)
            host = request.user
            room.topic = topic  # Set the topic to 'basketball'
            room.location = request.POST.get('location')
            room.date = request.POST.get('date')
            room.start_time = request.POST.get('start_time')
            room.end_time = request.POST.get('end_time')
            room.pax_required = request.POST.get('pax_required')
            room.description = request.POST.get('description')
            room.save()  # Save the room instance
            return redirect('room', pk=room.pk)  
        
        else:
            print(form.errors)  # Debugging: print form errors if any

    else:
        # Display the form with the current room instance data
        form = RoomForm(instance=room)

    context = {
        'form': form,
        'locations': locations,
        'room': room,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.user != room.host:
        return HttpResponse('Not allowed')  # Only the host can delete


    if request.method == "POST":
        room.delete()
        
        # Get the previous page URL
        previous_page = request.META.get('HTTP_REFERER', '')
        
        # Get the current delete room URL to prevent redirecting back to it
        profile_url = request.build_absolute_uri(reverse('user-profile', args=[request.user.id]))
        
        # Redirect back if previous page is not the delete page, else to home
        if previous_page == profile_url:
            return HttpResponseRedirect(previous_page)
        else:
            return redirect('home')
        
    # if request.method == "POST":
    #     room.delete()
    #     return redirect(request.META.get('HTTP_REFERER', ''))
        # return redirect('home')

    # Render the delete confirmation page if request is GET
    return render(request, 'base/delete.html', {'obj': room})


# User Profile:
@login_required(login_url = 'login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    # Filter only the rooms hosted by this specific user
    rooms_hosted_by_user = Room.objects.filter(host=user)  # Filter rooms hosted by this user
    rooms_joined = Room.objects.filter(participants=user)  # Rooms joined by the user

    activities = get_user_activities(request.user)

    for room in rooms_hosted_by_user:
        participants_count = room.participants.count()
        room.has_joined = room.user_has_joined(request.user)
        room.is_full = room.is_full

    
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'rooms_hosted_by_user': rooms_hosted_by_user, 'activities': activities,}
    return render(request, 'base/profile.html', context)



@login_required(login_url = 'login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})



# Notif Testing:
def updateNotificationPreferences(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # Save the updated preferences
            return redirect('home')  # Redirect to home after saving
    else:
        form = NotificationPreferenceForm(instance=user)  # Pre-fill the form with current user data
    
    return render(request, 'base/notification_preferences.html', {'form': form})



@method_decorator(csrf_exempt, name='dispatch')
class Telegram(View):
    def get(self, request):
        req_header = request.headers
        telegram_id = req_header.get('Authorization')
        try:
            user = User.objects.get(telegram_id=telegram_id)
            rooms_joined = Room.objects.filter(participants=user)

            # No events found
            if not rooms_joined.exists():
                return JsonResponse({'info': "You are not in any events"})

            # Prepare room details for response
            messages = [{'room_name': room.name, 'date': room.date.isoformat()} for room in rooms_joined]
            
            return JsonResponse({
                'info': 'This is the information from the Django site.',
                'rooms': messages
            })

        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    def post(self, request):
        # Extract data from POST request
        telegram_id = request.POST.get('telegram_id')
        telegram_name = request.POST.get('telegram_name')
        session_id = request.POST.get('session_id')

        if not telegram_id or not session_id:
            return HttpResponseBadRequest("Missing Data")
        
        try:
            # Retrieve user by session ID and link Telegram details
            user = User.objects.get(id=session_id)
            user.telegram_id = telegram_id
            user.telegram_name = telegram_name
            user.save()

            return JsonResponse({
                'status': 'success',
                'telegram_id': telegram_id,
                'user_id': user.id,
                'message': "Successfully linked to Telegram"
            })

        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Session ID invalid or expired'}, status=400)




















# NOT NEEDED (For Now)
@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Not allowed')    
    
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


# Not Needed
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # Distance in kilometers


# Not Needed
def filter_events(request):
    # Get the latitude and longitude from the form submission
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    location_name = request.GET.get('location_name', '')

    # Print for debugging
    print(f"Latitude: {latitude}, Longitude: {longitude}, Location: {location_name}")

    # Initialize an empty list for nearby events
    nearby_events = []

    # If latitude and longitude are provided, filter based on proximity
    if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)

            # Get all rooms/events
            events = Room.objects.all()

            # Filter events within 1.5 km using the Haversine formula
            for event in events:
                if event.latitude and event.longitude:
                    distance = haversine(latitude, longitude, event.latitude, event.longitude)
                    if distance <= 1.5:
                        nearby_events.append(event)

        except ValueError:
            # Handle invalid latitude/longitude values
            pass

    # Filter by location name if provided
    if location_name:
        # Match events based on location name or add to existing nearby_events
        location_match_events = Room.objects.filter(location_name__icontains=location_name)
        
        # Combine the two sets (events within 1.5km + location name match)
        combined_events = set(nearby_events) | set(location_match_events)
    else:
        # If no location name is provided, just use nearby events
        combined_events = set(nearby_events)

    # Return filtered events to the template
    return render(request, 'home.html', {'events': combined_events})




# @login_required(login_url = 'login')
# def home(request):
#      # Rooms created by the user
#     rooms_joined = Room.objects.filter(participants=request.user)  # Rooms joined by the user
#     activities = list(rooms_joined)

#     q = request.GET.get('q') if request.GET.get('q') != None else ''
#     rooms = Room.objects.filter(
#         Q(topic__name__icontains=q) |
#         Q(name__icontains=q) |
#         Q(description__icontains=q)
#         )

#     # Additional filters: Location, Date, and Time
#     location = request.GET.get('location', '')
#     date = request.GET.get('date', '')
#     time = request.GET.get('time', '')

#     # Filters:
#     if location:
#         rooms = rooms.filter(location__icontains=location)
#     if date:
#         rooms = rooms.filter(date=date)
#     if time:
#         rooms = rooms.filter(start_time__lte=time, end_time__gte=time)


#     # Filter out past events
#     rooms = rooms.filter(date__gte=timezone.now()) 
#     rooms = rooms.order_by('date')
            

#     topics = Topic.objects.all()
#     room_count = rooms.count()
#     room_messages = Message.objects.all()



#     # For each room, check if the current user has joined
#     for room in rooms:
#         participants_count = room.participants.count()  # Get the number of participants

#         room.has_joined = room.participants.filter(id=request.user.id).exists()

#         room.is_full = participants_count >= room.pax_required  # Check if the room is full


        
#     context =  {
#         'rooms': rooms, 
#         'topics': topics, 
#         'room_count': room_count, 
#         'room_messages': room_messages,
#         'activities': activities,
#         'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,

#         }
    
#     return render(request, 'base/home.html',context)