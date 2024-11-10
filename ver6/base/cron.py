# from django.utils import timezone
# from datetime import timedelta
# from .models import Room

# def send_event_reminders():
#     now = timezone.localtime(timezone.now())
#     reminder_start_time = now + timedelta(hours=1, minutes=59)
#     reminder_end_time = now + timedelta(hours=2)
#     reminder_start_time = reminder_start_time.replace(second=0, microsecond=0)
#     reminder_end_time = reminder_end_time.replace(second=0, microsecond=0)

#     rooms = Room.objects.filter(
#         start_time__gte=reminder_start_time,
#         start_time__lte=reminder_end_time,
#         reminder_sent=False,
#         date=now.date()
#     )

#     for room in rooms:
#         room.notify_participants()  # Trigger notifications

#         # Mark the reminder as sent to avoid duplicates
#         room.reminder_sent = True
#         room.save()


import logging
from django.utils import timezone
from datetime import timedelta
from base.models import Room  # Make sure Room is correctly imported

# Configure logging if you prefer logging over print
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_event_reminders():
    now = timezone.localtime(timezone.now())
    reminder_start_time = now + timedelta(hours=1, minutes=59)
    reminder_end_time = now + timedelta(hours=2)
    reminder_start_time = reminder_start_time.replace(second=0, microsecond=0)
    reminder_end_time = reminder_end_time.replace(second=0, microsecond=0)

    # Print or log the computed times
    print(f"Current time: {now}")
    print(f"Reminder Start Time: {reminder_start_time}")
    print(f"Reminder End Time: {reminder_end_time}")

    rooms = Room.objects.filter(
        start_time__gte=reminder_start_time,
        start_time__lte=reminder_end_time,
        reminder_sent=False,
        date=now.date()
    )

    # Print the count of rooms that match the filter criteria
    print(f"Rooms to notify: {rooms.count()}")

    for room in rooms:
        # Print room details for debugging
        print(f"Room ID: {room.id}, Start Time: {room.start_time}, Date: {room.date}")

        room.notify_participants()  # Trigger notifications

        # Mark the reminder as sent to avoid duplicates
        room.reminder_sent = True
        room.save()

        # Confirm reminder was marked as sent
        print(f"Reminder sent for Room ID: {room.id}")























# SECOND EDITION

# from django.utils import timezone
# from django.core.mail import send_mail
# from .models import Room
# from datetime import timedelta

# def send_event_reminders():
#     # Get the current time in the specified timezone (Asia/Singapore)
#     now = timezone.localtime(timezone.now())

#     # Calculate reminder times
#     reminder_start_time = now + timedelta(hours=1, minutes=59)
#     reminder_end_time = now + timedelta(hours=2)

#     # Normalize both times to the start of the minute
#     reminder_start_time = reminder_start_time.replace(second=0, microsecond=0)
#     reminder_end_time = reminder_end_time.replace(second=0, microsecond=0)

#     # Filter for rooms starting within the defined time range
#     rooms = Room.objects.filter(
#         start_time__gte=reminder_start_time,
#         start_time__lte=reminder_end_time,
#         reminder_sent=False,
#         date=now.date()
#     )

#     for room in rooms:
#         for participant in room.participants.all():
#             # Check if email notifications are enabled for the user
#             if participant.email_notifications_enabled:
#                 try:
#                     # Send reminder email to each participant
#                     send_mail(
#                         'Reminder: Upcoming Event',
#                         (
#                             f'Dear {participant.username},\n\n'  
#                             f'Reminder: You have an event "{room.name}" today!\n'
#                             f'Start Time: {room.start_time.strftime("%I:%M %p")}\n'
#                             f'Check it out at: http://127.0.0.1:8000/\n\n'
#                             'Best regards,\n'
#                             'BallersLyfe Team'
#                         ),
#                         'scprojectballerlyfe@gmail.com',
#                         [participant.email],
#                         fail_silently=False,
#                     )

#                 except Exception as e:
#                     print(f"Failed to send email to {participant.username}: {str(e)}")
                    
#             if participant.telegram_notifications_enabled:

#                 #  logic to send Telegram notification 

#                 print(f"Telegram notification sent to {participant.username} for event: {room.name}")

            
#         # Mark the reminder as sent to avoid duplicates
#         room.reminder_sent = True
#         room.save()










            

























# FIRST EDITION

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
