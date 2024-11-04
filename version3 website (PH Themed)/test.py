from telegram import Bot
from datetime import datetime, timedelta
import schedule
import time

bot = Bot(token='7945531515:AAEBPKD67Jr1aAiXuy-WW-QCIUnBsdNGUDw')

def send_reminder(chat_id, event_name, event_date):
    message = f"Reminder event"
    bot.send_message(chat_id=chat_id, text=message)


def schedule_reminder(chat_id, event_name, event_date):
    reminder_time = (event_date - timedelta(days=1)).strftime('%H:%M')
    schedule.every().day.at(reminder_time).do(send_reminder, chat_id, event_name, event_date)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(f'Your chat ID is: {message.chat.id}')
    bot.reply_to(message, f'Your chat ID is: {message.chat.id}')


#example event
chat_id = 123
event_name = "sample event"
event_date = datetime(2024, 11, 5, 18, 0)

schedule_reminder(chat_id, event_name, event_date)

while True:
    schedule.run_pending()
    time.sleep(60)