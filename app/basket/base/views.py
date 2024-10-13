from django.shortcuts import render, redirect
from django.template import loader
from event.models import Event, Participation
from django.db.models import Count, F

# Create your views here.
def main(request):
    #check if user is logged in 
    if request.user.is_authenticated:
        # Get all events
        all_events = Event.objects.all()
        user_events = all_events.filter(creator=request.user)    #request.user is the logged in user's id: 

        # Get filter values
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        available = request.GET.get("availability")

        # Apply filters
        if start_date:
            all_events = all_events.filter(start__gte = start_date)
        if end_date:
            all_events = all_events.filter(end__lte = start_date)
        if available:
            #count current pax signed up for each event
            all_events = all_events.annotate(current_pax=Count('participation'))
            #filter for current pax < max pax
            all_events = all_events.filter(current_pax__lt=F('pax'))

        
        context = {
            'all_events': all_events,
            'user_events': user_events,
        }
        return render(request, "base/main.html", context)
    else:
        return render(request, 'base/default.html')





