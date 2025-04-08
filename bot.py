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

# Створення клієнта OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# SYSTEM PROMPT з повною інструкцією та категоріями
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, посилання на товар або код,\n"
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати.\n"
    "Серед сервісів: +1/+2/+3 роки гарантії, Альфа-сервіс, Вільний вибір, Бумеранг, Повернення без проблем,\n"
    "SUPPORT для смартфонів та інші.\n"
    "Твоя база знань включає всі категорії та сервіси, що відповідають кожному товару згідно документа.\n"
    "Не додавай нічого зайвого, не вигадуй. Якщо сервісів нема — скажи про це чітко.\n"
    "Відповідай тільки українською мовою.\n"
    "Приклад відповіді: \"Для товару 'Смартфон Samsung Galaxy A54' доступні сервіси: +1/+2/+3 роки гарантії, Повний захист.\"\n"
    "Категорії товарів та їх сервіси: Холодильники — +1/+2/+3 роки гарантії, Захист від пошкоджень, Мій сервіс. Смартфони — +1/+2/+3 роки гарантії, Повний захист, SUPPORT для смартфонів, Вільний вибір. Ноутбуки — +1/+2/+3 роки гарантії, Захист від пошкоджень. Телевізори — +1/+2/+3 роки гарантії, Повний захист, Захист від пошкоджень. Кавомашини — +1/+2/+3 роки гарантії, Повний захист. Пилососи — +1/+2/+3 роки гарантії, Повний захист. Пральні машини — +1/+2/+3 роки гарантії, Захист від пошкоджень, Мій сервіс. Іграшки — Бумеранг. І т.д. (вся таблиця вставлена)"
)

# Обробка команди /start
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

