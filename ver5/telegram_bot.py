import os
import requests
import telebot
from dotenv import load_dotenv




load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Extract session ID if provided
    params = message.text.split()
    if len(params) > 1:
        session_id = params[1]
        telegram_id = message.from_user.id
        telegram_name = message.from_user.username

        try:
            # Make POST request to Django server to link Telegram with user session
            response = requests.post(
                'http://127.0.0.1:8000/telegram',
                data={
                    'telegram_id': telegram_id,
                    'telegram_name': telegram_name,
                    'session_id': session_id,
                }
            )

            if response.status_code == 200:
                bot.reply_to(message, "Sup, welcome baller!")
            else:
                bot.send_message(message.chat.id, "Something went wrong. Try again later baller!")
        except Exception as e:
            bot.send_message(message.chat.id, f'An error occurred: {str(e)}')

@bot.message_handler(commands=['activity'])
def send_activity(message):
    user_id = message.from_user.id
    try:
        # Make a GET request to Django API to retrieve activity information
        response = requests.get('http://127.0.0.1:8000/telegram', headers={'Authorization': f"{user_id}"})
        if response.status_code == 200:
            data = response.json()
            rooms = data.get('rooms', [])
            if rooms:
                for room in rooms:
                    message_str = f"Event Name: {room['room_name']}\nDate: {room['date']}\n Time: {room['time']}"
                    bot.send_message(message.chat.id, message_str)
            else:
                bot.send_message(message.chat.id, "You are not in any events.")
        elif response.status_code == 404:
            bot.send_message(message.chat.id, 'You have not linked your account to telegram. Link your account on the BallersLyfe website to enable telegram updates')
        else:
            bot.send_message(message.chat.id, 'Failed to retrieve information from the website.')
    except Exception as e:
        bot.send_message(message.chat.id, f'An error occurred: {str(e)}')

bot.infinity_polling()