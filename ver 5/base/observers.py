from abc import ABC, abstractmethod
from django.core.mail import send_mail
import requests

class Observer(ABC):
    @abstractmethod
    def notify(self, user, event):
        """Send a notification to the user about an event."""
        pass

class EmailObserver(Observer):
    def notify(self, user, event):
        if user.email_notifications_enabled:
            send_mail(
                'Reminder: Upcoming Event',
                (
                    f"Dear {user.username},\n\n"
                    f"You have an upcoming event: {event.name} at {event.start_time.strftime('%I:%M %p')}.\n"
                    "Check it out at: http://127.0.0.1:8000/\n\n"
                    "Best regards,\nBallersLyfe Team"
                ),
                'scprojectballerlyfe@gmail.com',
                [user.email],
                fail_silently=False,
            )
            print(f"Email sent to {user.username} for event {event.name}")

class TelegramObserver(Observer):
    def notify(self, user, event):
        if user.telegram_notifications_enabled:
            # Use your actual bot token here, ideally from a secure settings file
            bot_token = '7945531515:AAEBPKD67Jr1aAiXuy-WW-QCIUnBsdNGUDw'
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Compose the notification message
            message = (
                f"Dear {user.username},\n\n"
                f"Your event '{event.name}' is starting soon at {event.start_time}. See you there!!"
            )
            
            # Send the message using the Telegram API
            response = requests.post(
                url, 
                data={
                    'chat_id': user.telegram_id,  # Unique identifier for the Telegram user
                    'text': message
                }
            )
            
            # Check the response to confirm it was sent
            if response.status_code == 200:
                print(f"Telegram notification sent to {user.username} for event {event.name}")
            else:
                print(f"Failed to send Telegram notification to {user.username}: {response.json()}")





