import telebot
from config import token
import requests
from collections import defaultdict
from logic import quiz_questions
from time import sleep
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Adjust level as needed

user_responses = {}
points = defaultdict(int)

bot = telebot.TeleBot(token)

def send_question(chat_id):
    question_index = user_responses[chat_id]
    if question_index < len(quiz_questions):
        bot.send_message(chat_id, quiz_questions[question_index].text, reply_markup=quiz_questions[question_index].gen_markup())
    else:
        bot.send_message(chat_id, f"Quiz finished! You scored {points[chat_id]} points.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "correct":
        bot.answer_callback_query(call.id, "Answer is correct")
        points[chat_id] += 1
    elif call.data == "wrong":
        bot.answer_callback_query(call.id, "Answer is wrong")

    user_responses[chat_id] += 1
    send_question(chat_id)  # Send next question or end quiz

@bot.message_handler(commands=['start'])
def start(message):
    try:
        chat_id = message.chat.id
        if chat_id not in user_responses:
            user_responses[chat_id] = 0
            points[chat_id] = 0
            send_question(chat_id)
    except Exception as e:
        logging.error(f"Error in /start command handler: {e}")

def start_bot():
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        logging.error(f"Error in bot polling: {e}")

def make_request_with_retries(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info("Request successful")
            break
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            sleep(2)

url = "https://example.com"  # Replace with your actual URL
make_request_with_retries(url)

bot_thread = threading.Thread(target=start_bot)
bot_thread.start()
