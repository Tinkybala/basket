from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.conf import settings
from celery import shared_task
from django.utils import timezone
import requests
from math import radians, sin, cos, sqrt, atan2
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import telebot
from django.views.decorators.http import require_GET




# Create your views here. 
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


def registerUser(request):
    form = MyUserCreationForm()

    if request.method =="POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})



@login_required(login_url = 'login')
def home(request):
     # Rooms created by the user
    rooms_joined = Room.objects.filter(participants=request.user)  # Rooms joined by the user
    activities = list(rooms_joined)

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    # Additional filters: Location, Date, and Time
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')
    time = request.GET.get('time', '')

    # Filters:
    if location:
        rooms = rooms.filter(location__icontains=location)
    if date:
        rooms = rooms.filter(date=date)
    if time:
        rooms = rooms.filter(start_time__lte=time, end_time__gte=time)


    # Filter out past events
    rooms = rooms.filter(date__gte=timezone.now()) 
    rooms = rooms.order_by('date')
            

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.all()



    # For each room, check if the current user has joined
    for room in rooms:
        participants_count = room.participants.count()  # Get the number of participants

        room.has_joined = room.participants.filter(id=request.user.id).exists()

        room.is_full = participants_count >= room.pax_required  # Check if the room is full


        
    context =  {
        'rooms': rooms, 
        'topics': topics, 
        'room_count': room_count, 
        'room_messages': room_messages,
        'activities': activities,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,

        }
    
    return render(request, 'base/home.html',context)


@login_required(login_url = 'login')
def room(request,pk):
    room = Room.objects.get(id=pk)
    participants = room.participants.all()
    rooms_joined = Room.objects.filter(participants=request.user)  # Rooms joined by the user
    activities = list(rooms_joined)
    participants_count = room.participants.count()
    room.is_full = participants_count >= room.pax_required  # Check if room is full
    room.has_joined = room.participants.filter(id=request.user.id).exists() 

    
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={room.location}&key={settings.GOOGLE_API_KEY}"
    response = requests.get(geocode_url)
    geocode_data = response.json()

    if geocode_data['status'] == 'OK':
        latitude = geocode_data['results'][0]['geometry']['location']['lat']
        longitude = geocode_data['results'][0]['geometry']['location']['lng']


    context = {'room': room,  'participants': participants, 'activities': activities,
                'GOOGLE_API_KEY': settings.GOOGLE_API_KEY, 
                'latitude': latitude,
                'longitude': longitude,}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def mainJoinEvent(request, pk):
    room = Room.objects.get(id=pk)
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


# Deals with the backend of the join button when user is in the event information page
# @login_required(login_url='login')
# def roomJoinEvent(request, pk):
#     room = Room.objects.get(id=pk)
#     participants = room.participants.all()

#     if request.method == 'POST':
#         room.participants.add(request.user)

#     context = {
#         'room': room,
#         'participants': participants
#     }
#     return render(request, 'base/room.html', context)


@login_required(login_url='login')
def quitEvent(request, pk):
    room = Room.objects.get(id=pk)
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


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    # Filter only the rooms hosted by this specific user
    rooms_hosted_by_user = Room.objects.filter(host=user)  # Filter rooms hosted by this user

    rooms_joined = Room.objects.filter(participants=user)  # Rooms joined by the user
    activities = list(rooms_joined)
    # Add 'is_full' and 'has_joined' checks
    for room in rooms_hosted_by_user:
        participants_count = room.participants.count()
        room.is_full = participants_count >= room.pax_required  # Check if room is full
        room.has_joined = room.participants.filter(id=request.user.id).exists() 


    
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'rooms_hosted_by_user': rooms_hosted_by_user, 'activities': activities,}
    return render(request, 'base/profile.html', context)


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



@login_required(login_url='login')
def updateRoom(request, pk):
    # Get the room by its primary key
    room = Room.objects.get(id=pk)

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
            return redirect('room')  # Redirect to home after successful update
        
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



# @login_required(login_url = 'login')
# def deleteRoom(request, pk):
#     room = Room.objects.get(id=pk)

#     if request.user != room.host:
#         return HttpResponse('Not allowed')    
    
#     if request.method == "POST":
#         room.delete()

#     if 'user-profile' in request.META.get('HTTP_REFERER', ''):
#         return redirect('user-profile')
#     else:
#         return redirect('home')
        
#     return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Not allowed')  # Only the host can delete

    if request.method == "POST":
        room.delete()
        return redirect('home')

    # Render the delete confirmation page if request is GET
    return render(request, 'base/delete.html', {'obj': room})


# NOT NEEDED
@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Not allowed')    
    
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


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

bot = telebot.TeleBot('7945531515:AAEBPKD67Jr1aAiXuy-WW-QCIUnBsdNGUDw')



@require_GET
def get_info(request):
    req_header = request.headers
    user_id = req_header.get('Authorization')
    print(user_id)
    user = User.objects.get(tele=user_id)
    # Logic to get the information you want to send
    rooms_joined = list(Room.objects.filter(participants=user))

    #user not in any event
    if not rooms_joined:
        return JsonResponse({'info': "You are not in any events"})
    
    messages = []
    for room in rooms_joined:
        room_message = {
            'room_name': room.name,
            'date': room.date.isoformat()  # Convert date to ISO format for better JSON compatibility
        }
        #print(room_message)
        messages.append(room_message)
        
    data = {
        'info': 'This is the information from the Django site.',
        'rooms': messages  # List of rooms with their details
    }
    #print(JsonResponse(data))
    return JsonResponse(data)