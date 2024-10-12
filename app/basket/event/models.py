from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    pax = models.IntegerField()
    additional_info = models.CharField(max_length=500)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

class Participation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event_id = models.ForeignKey("Event", on_delete=models.CASCADE)

    def __str__(self):
        return f"user_id: {self.user_id}, event_id: {self.event_id}"
