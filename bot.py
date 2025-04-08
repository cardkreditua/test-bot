import os
import logging
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# Настройка логирования для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ BOT_TOKEN или OPENAI_API_KEY не заданы в переменных окружения.")

openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "Ты ассистент-продавец ROZETKA. Когда пользователь вводит название товара, "
    "ты чётко и кратко отвечаешь, какие сервисы SUPPORT.UA можно предложить к нему. "
    "Не добавляй лишнего текста. Если сервисов нет — так и скажи. Отвечай на украинском языке."
)

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши мне название товара, и я подскажу, какие сервисы SUPPORT.UA можно предложить."
    )

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    logging.info(f"🔹 Получен запрос: {user_message}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2
        )
        reply = response.choices[0].message["content"]
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"❌ Ошибка OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз позже.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("✅ Бот запущен")
    app.run_polling()

