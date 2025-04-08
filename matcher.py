import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)
from openai import OpenAI
from matcher import get_services_for_product

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ответ на запрос
def support_response(product_name):
    category, services = get_services_for_product(product_name)
    if not category:
        return "Не вдалося визначити категорію товару. Будь ласка, перевірте назву або зверніться до менеджера SUPPORT.UA."

    response = f"✅ Категорія: *{category}*\n📦 Доступні сервіси:\n"
    for service in services:
        response += f"• {service}\n"
    return response

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        reply = support_response(user_message)
    except Exception as e:
        reply = f"Сталася помилка: {e}"

    await update.message.reply_text(reply, parse_mode="Markdown")

# Запуск
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    )

if __name__ == '__main__':
    main()

