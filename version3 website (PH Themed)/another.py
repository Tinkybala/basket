import os
import requests
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN', '7945531515:AAEBPKD67Jr1aAiXuy-WW-QCIUnBsdNGUDw')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['activity'])
def send_activity(message):
    user_id = message.from_user.id
    try:
        # Make a GET request to the Django API
        response = requests.get('http://127.0.0.1:8000/get-info', headers={'Authorization': f"{user_id}"})
        if response.status_code == 200:
            data = response.json()
            rooms = data.get('rooms', 'No information available.')
            for room in rooms:
                message_str = room['room_name'] + ":" + room["date"]

                bot.send_message(message.chat.id, message_str)
            #bot.send_message(message.chat.id, info)
        else:
            bot.send_message(message.chat.id, 'Failed to retrieve information from the website.')
    except Exception as e:
        bot.send_message(message.chat.id, f'An error occurred: {str(e)}')

bot.infinity_polling()

