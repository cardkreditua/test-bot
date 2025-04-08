import os
import openai
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Получение токенов
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Системный промпт
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, "
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна запропонувати до нього. "
    "Не додавай зайвого тексту. Якщо сервісів немає — так і скажи. Відповідай українською мовою."
)

# Обработка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши мені назву товару, і я підкажу, які сервіси SUPPORT.UA можна запропонувати."
    )

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message["content"]
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Error while calling OpenAI: {e}")
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Если используешь polling
    app.run_polling()

    # Или, если ты переходишь на webhook:
    # app.run_webhook(
    #     listen="0.0.0.0",
    #     port=int(os.environ.get("PORT", 8443)),


