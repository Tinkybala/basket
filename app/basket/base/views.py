from django.shortcuts import render, redirect
from django.template import loader
from event.models import Event

# Create your views here.
def main(request):
    #check if user is logged in 
    if request.user.is_authenticated:
        #get all events (by order in db for now)
        all_events = Event.objects.all()
        user_events = Event.objects.filter(creator=request.user)    #request.user is the logged in user's id: 
        context = {
            'all_events': all_events,
            'user_events': user_events,
        }
        return render(request, "base/main.html", context)
    else:
        return render(request, 'base/default.html')





