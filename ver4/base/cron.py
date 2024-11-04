from django.utils import timezone
from django.core.mail import send_mail
from .models import Room
from datetime import timedelta

def send_event_reminders():
    # Current time
    now = timezone.now()

    # Define the window for reminders
    reminder_window_start = now + timedelta(hours=2)  # Start reminding 2 hours before
    reminder_window_end = now + timedelta(hours=1)    # End reminding 30 minutes before

    # Filter for rooms starting within the defined window
    rooms = Room.objects.filter(
        start_time__gte=reminder_window_start.time(),
        start_time__lte=reminder_window_end.time(),
        reminder_sent=False,
        date=now.date()  # Ensure the event is today
    )

    for room in rooms:
        for participant in room.participants.all():
            # Send reminder email to each participant
            send_mail(
                'Reminder: Upcoming Event',
                f'Reminder: Your event "{room.name}" starts at {room.start_time.strftime("%I:%M %p")}! Check it out at http://127.0.0.1:8000/',
                'scprojectballerlyfe@gmail.com',
                [participant.email],
                fail_silently=False,
            )
        
        # Mark the reminder as sent to avoid duplicates
        room.reminder_sent = True
        room.save()