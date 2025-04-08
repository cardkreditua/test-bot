import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Завантаження токенів з середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# SYSTEM PROMPT (адаптовано під твою задачу)
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, посилання на товар або код, "
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати. "
    "Серед сервісів: +1/+2/+3 роки гарантії, Альфа-сервіс, Вільний вибір, Бумеранг, Повернення без проблем, "
    "SUPPORT для смартфонів, інші. "
    "Враховуй тип товару. Якщо сервісів немає — чітко вкажи це. Відповідай українською мовою. "
    "Не вигадуй і не додавай зайвого тексту. "
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши назву товару або встав посилання, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати."
    )

# Обробка запитів
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")
        print(f"[OpenAI error]: {e}")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

