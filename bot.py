import os
import openai
from telegram.ext import Updater, MessageHandler, Filters

# Загружаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def chatgpt_response(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}]
    )
    return response['choices'][0]['message']['content']

def handle_message(update, context):
    user_message = update.message.text
    update.message.chat.send_action(action="typing")
    try:
        reply = chatgpt_response(user_message)
        update.message.reply_text(reply)
    except Exception as e:
        update.message.reply_text("Произошла ошибка. Попробуй позже.")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

