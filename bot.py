import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from matcher import get_services_for_product

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши мені назву товару, і я підкажу, які сервіси можна запропонувати."
    )

# Обработка обычного текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        reply = get_services_for_product(user_message)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Виникла помилка при обробці запиту. Спробуйте пізніше.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()


