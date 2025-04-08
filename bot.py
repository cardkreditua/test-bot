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

# Завантаження токенів
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ініціалізація клієнта OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Системний промпт з повним переліком сервісів і правилами
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, посилання або код, "
    "ти чітко й стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати. Відповідь тільки українською мовою.\n"
    "\n"
    "Ось приклади категорій і сервісів, які можна до них запропонувати:\n"
    "Смартфони: +1, +2, +3 роки гарантії, Повний захист, Захист від пошкоджень, Вільний вибір\n"
    "Холодильники, Пральні машини: +1, +2, +3 роки гарантії, Захист від пошкоджень, Мій сервіс для великої побутової техніки\n"
    "Планшети, Ноутбуки: +1, +2, +3 роки гарантії, Повний захист, Захист від пошкоджень\n"
    "Телевізори: +1, +2, +3 роки гарантії, Повний захист, Захист від пошкоджень\n"
    "Мікрохвильовки, Блендери, Кавомашини: +1, +2, +3 роки гарантії, Повний захист, Захист від пошкоджень\n"
    "Фітнес-браслети, Навушники: +1, +2, +3 роки гарантії, Захист від пошкоджень, Повний захист\n"
    "Іграшки, дитячі пристрої: Бумеранг\n"
    "Електротранспорт: Альфа-сервіс, +1, +2, +3 роки гарантії\n"
    "Інше — якщо сервісів немає, напиши: На жаль, немає сервісів для цієї категорії.\n"
    "\n"
    "Не вигадуй сервісів, яких не існує. Якщо не впевнений — порадь звернутись до менеджерів SUPPORT.UA."
)

# Обробка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши назву товару, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати."
    )

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]
        )
        reply = response.choices[0].message.content
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

