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
    "Ти асистент-продавець ROZETKA. Твоє завдання — чітко і стисло відповідати, які сервіси SUPPORT.UA доступні до товару, назву якого ввів користувач.\n"
    "В основі твоїх відповідей — база даних категорій та сервісів.\n"
    "---\n"
    "Якщо товар належить до категорії, де доступні сервіси — надай перелік сервісів із коротким поясненням (до 1 речення) для кожного.\n"
    "Якщо сервісів немає — чітко скажи, що сервісів SUPPORT.UA для цього товару не існує.\n"
    "---\n"
    "Правила:\n"
    "1. Не вигадуй сервіси. Тільки з дозволеного списку.\n"
    "2. Відповідай українською.\n"
    "3. Не пиши зайвих фраз, не вітаєшся.\n"
    "4. Якщо товар невідомий або не входить у базу — напиши: 'На жаль, я не можу знайти відповідну інформацію. Рекомендуємо звернутись до менеджерів SUPPORT.UA для консультації.'\n"
    "5. При згадці смартфонів, ноутбуків, телевізорів, холодильників, пральних машин, електросамокатів — знайди відповідну категорію та сервіси.\n"
    "---\n"
    "СМАРТФОНИ: +1, +2, +3 роки гарантії; Захист від пошкоджень; Повний захист; Вільний вибір.\n"
    "НОУТБУКИ: +1, +2, +3 роки гарантії; Захист від пошкоджень; Повний захист.\n"
    "ТЕЛЕВІЗОРИ: +1, +2, +3 роки гарантії; Захист від пошкоджень; Повний захист.\n"
    "ХОЛОДИЛЬНИКИ: Мій Сервіс для великої побутової техніки.\n"
    "ПРАЛЬНІ МАШИНИ: Мій Сервіс для великої побутової техніки.\n"
    "ЕЛЕКТРОСАМОКАТИ: Альфа-сервіс для електротранспорту.\n"
    "---\n"
    "Формат відповіді:\n"
    "Категорія: [назва категорії]\n"
    "Сервіси:\n"
    "- [Назва сервісу]: [короткий опис]"
)

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напишіть назву товару, і я підкажу, які сервіси SUPPORT.UA можна запропонувати."
    )

# Обробка повідомлень
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

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()


