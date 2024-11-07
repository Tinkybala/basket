from django.db.models import Q
from django.utils import timezone
from .models import Room, Topic, Message, User
import requests
from django.conf import settings

def filter_rooms(search_term='', location='', date='', time=''):
    # Base query with search term
    rooms = Room.objects.filter(
        Q(topic__name__icontains=search_term) |
        Q(name__icontains=search_term) |
        Q(description__icontains=search_term)
    )

    # Apply additional filters
    if location:
        rooms = rooms.filter(location__icontains=location)
    if date:
        rooms = rooms.filter(date=date)
    if time:
        rooms = rooms.filter(start_time__lte=time, end_time__gte=time)

    # Filter out past events
    rooms = rooms.filter(date__gte=timezone.now()).order_by('date')

    return rooms


def get_home_related_data(user, rooms):
    rooms_joined = Room.objects.filter(participants=user)
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.all()
    
    return topics, room_count, room_messages


def get_geocode_location(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={settings.GOOGLE_API_KEY}"
    response = requests.get(geocode_url)
    geocode_data = response.json()

    if geocode_data['status'] == 'OK':
        latitude = geocode_data['results'][0]['geometry']['location']['lat']
        longitude = geocode_data['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    return None, None

def get_user_activities(user):
    rooms_joined = Room.objects.filter(participants=user)
    return list(rooms_joined)


def get_profile_data(user):
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    rooms_hosted_by_user = Room.objects.filter(host=user)
    rooms_joined = Room.objects.filter(participants=user)
    return rooms, room_messages, topics, rooms_hosted_by_user, rooms_joined

