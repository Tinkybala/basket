from django.utils import timezone
from django.core.mail import send_mail
from .models import Room
from datetime import timedelta

def send_event_reminders():
    # Get the current time in the specified timezone (Asia/Singapore)
    now = timezone.localtime(timezone.now())  # This should give you the current time in Singapore time
    # print(f"Current time: {now}")

    # Calculate reminder times
    reminder_start_time = now + timedelta(hours=1, minutes=59)  # Start reminding 1 hour 59 minutes from now
    reminder_end_time = now + timedelta(hours=2)  # Window End 2hour min from now

    # Normalize both times to the start of the minute
    reminder_start_time = reminder_start_time.replace(second=0, microsecond=0)
    reminder_end_time = reminder_end_time.replace(second=0, microsecond=0)

    # print(f"Reminder start time (1 hour 59 minutes from now): {reminder_start_time}")
    # print(f"Reminder end time (2 hours from now): {reminder_end_time}")

    # Filter for rooms starting within the defined time range
    rooms = Room.objects.filter(
        start_time__gte=reminder_start_time,  # Events starting at or after this time
        start_time__lte=reminder_end_time,     # Events starting at or before this time
        reminder_sent=False,
        date=now.date()  # Ensure the event is today
    )

    for room in rooms:
        for participant in room.participants.all():
            # Check for email notification preference
            email_preference = participant.notification_preferences.filter(notification_type='email', is_enabled=True).exists()
            if email_preference:
                # Send reminder email to each participant
                send_mail(
                    'Reminder: Upcoming Event',
                    (
                        f'Dear {participant.username},\n\n'  
                        f'Reminder: You have an event "{room.name}" today!\n'
                        f'Start Time: {room.start_time.strftime("%I:%M %p")}\n'
                        f'Check it out at: http://127.0.0.1:8000/\n\n'
                        'Best regards,\n'
                        'BallersLyfe Team'
                    ),
                    'scprojectballerlyfe@gmail.com',
                    [participant.email],
                    fail_silently=False,
                )
            
            # Placeholder for future Telegram notification logic
            # if participant.notification_preferences.filter(notification_type='telegram', is_enabled=True).exists():
            #     # Logic to send Telegram notification goes here
            #     pass
        
        # Mark the reminder as sent to avoid duplicates
        room.reminder_sent = True
        room.save()






































# from django.utils import timezone
# from django.core.mail import send_mail
# from .models import Room
# from datetime import timedelta

# def send_event_reminders():
#     # Get the current time in the specified timezone (Asia/Singapore)
#     now = timezone.localtime(timezone.now())  # This should give you the current time in Singapore time
#     # print(f"Current time: {now}")

#     # Calculate reminder times
#     reminder_start_time = now + timedelta(hours=1, minutes=59)  # Start reminding 1 hour 59 minutes from now
#     reminder_end_time = now + timedelta(hours=2)  # Window End 2hour min from now

#     # Normalize both times to the start of the minute
#     reminder_start_time = reminder_start_time.replace(second=0, microsecond=0)
#     reminder_end_time = reminder_end_time.replace(second=0, microsecond=0)

#     # print(f"Reminder start time (1 hour 59 minutes from now): {reminder_start_time}")
#     # print(f"Reminder end time (2 hours from now): {reminder_end_time}")

#     # Filter for rooms starting within the defined time range
#     rooms = Room.objects.filter(
#         start_time__gte=reminder_start_time,  # Events starting at or after this time
#         start_time__lte=reminder_end_time,     # Events starting at or before this time
#         reminder_sent=False,
#         date=now.date()  # Ensure the event is today
#     )

#     for room in rooms:
#         # print(f"Sending reminder for event: {room.name} at {room.start_time}")
#         for participant in room.participants.all():
#             # Send reminder email to each participant
#             send_mail(
#                 'Reminder: Upcoming Event',
#                 (
#                     f'Dear {participant.username},\n\n'  
#                     f'Reminder: You have an event "{room.name}" today!\n'
#                     f'Start Time: {room.start_time.strftime("%I:%M %p")}\n'
#                     f'Check it out at: http://127.0.0.1:8000/\n\n'
#                     'Best regards,\n'
#                     'BallersLyfe Team'
#                 ),
#                 'scprojectballerlyfe@gmail.com',
#                 [participant.email],
#                 fail_silently=False,
#             )
        
#         # Mark the reminder as sent to avoid duplicates
#         room.reminder_sent = True
#         room.save()
