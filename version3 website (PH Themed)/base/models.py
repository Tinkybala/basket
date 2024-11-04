


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from datetime import datetime, time
from django.utils import timezone



# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    username = models.CharField(max_length=200, unique=True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    tele = models.CharField(max_length=200, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class Topic(models.Model):
    name = models.CharField(max_length=200, default='Basketball')

    def __str__(self):
        return self.name
    

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=255, default="Unknown location")  # New field for location
    date = models.DateField(null=True, blank=True)  # New field for date
    start_time = models.TimeField(null=True, blank=True)  # New field for start time
    end_time = models.TimeField(null=True, blank=True)  # New field for end time
    pax_required = models.PositiveIntegerField(null=True, blank=True)  # New field for pax required
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


    @property
    def is_upcoming(self):
        if self.date and self.end_time:
            event_datetime = datetime.combine(self.date, self.end_time)

            # Ensure event_datetime is timezone-aware
            if timezone.is_naive(event_datetime):
                event_datetime = timezone.make_aware(event_datetime, timezone.get_current_timezone())

            # Compare with the current time
            return timezone.now() < event_datetime
        return False
    
    
    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self) :
        return self.body[0:50]