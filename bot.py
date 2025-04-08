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

# 🔧 Логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ BOT_TOKEN або OPENAI_API_KEY не задані в середовищі (Render > Environment).")

openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, "
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна запропонувати до нього. "
    "Не додавай зайвого тексту. Якщо сервісів немає — так і скажи. Відповідай українською мовою."
)

# 👉 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши мені назву товару, і я підкажу, які сервіси SUPPORT.UA можна запропонувати."
    )

# 👉 Обробка повідомлення
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    logging.info(f"🔹 Отримано запит: {user_message}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"❌ Помилка OpenAI: {e}")
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")

# 👉 Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("✅ Бот запущено")
    app.run_polling()
