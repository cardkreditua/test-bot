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

# Обработка команд /start и других
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши мені назву товару, і я підкажу, які сервіси можна запропонувати.")

# Основная логика ответа
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        reply = get_services_

