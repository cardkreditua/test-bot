import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import openai
from flask import Flask, request
from threading import Thread

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # наприклад: https://your-app-name.onrender.com/webhook

openai.api_key = OPENAI_API_KEY

# Ініціалізація Flask для Webhook
flask_app = Flask(__name__)

# SYSTEM PROMPT
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, посилання на товар або код, "
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати. "
    "Серед сервісів: +1/+2/+3 роки гарантії, Альфа-сервіс, Вільний вибір, Бумеранг, Повернення без проблем, "
    "SUPPORT для смартфонів, інші. "
    "Враховуй тип товару. Якщо сервісів немає — чітко вкажи це. Відповідай українською, без фантазій чи зайвого тексту."
)

# Створення індексу
with open("knowledge_base.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

documents = []
for entry in raw_data:
    category = entry.get("category", "")
    keywords = ", ".join(entry.get("keywords", []))
    services = "\n".join([f"- {s['name']}: {s['desc']}" for s in entry.get("services", [])])
    content = f"Категорія: {category}\nКлючові слова: {keywords}\nСервіси:\n{services}"
    documents.append(Document(page_content=content))

vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY))

# Обробка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши назву товару, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати."
    )

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    try:
        docs = vectorstore.similarity_search(user_message, k=3)
        context_text = "\n".join([doc.page_content for doc in docs])

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\nКонтекст:\n" + context_text},
                {"role": "user", "content": user_message},
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")
        print(f"[OpenAI error]: {e}")

# Telegram Webhook логіка
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@flask_app.post("/webhook")
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put(update)
        return "ok"

# Запуск Webhook сервера
if __name__ == "__main__":
    telegram_app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    Thread(target=lambda: telegram_app.run_polling()).start()
    flask_app.run(host="0.0.0.0", port=8080)


