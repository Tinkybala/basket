from django.shortcuts import render
from django.template import loader
from event.models import Event

# Create your views here.
def main(request):
    #get all events (by order in db for now)
    events = Event.objects.all()
    context = {
        'events': events
    }
    return render(request, "base/main.html", context)

