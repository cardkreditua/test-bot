import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Промпт для GPT
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. "
    "Користувач вводить назву товару або опис. "
    "Твоя задача — коротко і чітко відповісти, які послуги SUPPORT.UA можна запропонувати до цього товару. "
    "Якщо товару немає у списку категорій, напиши: 'На жаль, я не можу визначити категорію товару. Зверніться до менеджера SUPPORT.UA.'."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши мені назву товару, і я підкажу, які сервіси можна запропонувати."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text


