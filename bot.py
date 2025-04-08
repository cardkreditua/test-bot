import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Твоя мета — точно й стисло повідомити, які сервіси SUPPORT.UA можна запропонувати до товару. "
    "Ти працюєш лише з переліком товарних категорій та сервісів, які тобі надані. "
    "Уважно аналізуй назву товару, навіть якщо вона містить помилки або додаткові слова, і визначай відповідну категорію. "
    "До кожної категорії можуть підходити різні сервіси, наприклад: '+1, +2, +3 роки гарантії', ' Захист від пошкоджень', ' Повний захист', 'Мій сервіс' тощо. "
    "Якщо категорія підтримує сервіс '+1, +2, +3 роки гарантії', але в товару гарантія менша за 6 місяців або він продається не ROZETKA, пропонуй варіант 'MARKETPLACE'. "
    "Не фантазуй і не вигадуй сервісів, якщо їх немає для товару. Якщо сервісів немає — напиши: ' На жаль, сервісів до цього товару немає'. "
    "Відповідай стисло, тільки українською, без емодзі та markdown. "
    "Приклад відповіді:\n\n"
    "Категорія: Смартфони\n"
    "Сервіси:\n"
    "- +1, +2, +3 роки гарантії\n"
    "- Захист від пошкоджень\n"
    "- Вільний вибір\n"
    "- Повний захист"
)

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши мені назву товару, і я підкажу, які сервіси SUPPORT.UA можна запропонувати."
    )

# Обробка текстових повідомлень
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
        await update.message.reply_text("Сталася помилка. Спробуй ще раз пізніше.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()


