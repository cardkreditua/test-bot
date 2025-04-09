import os
import json
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import openai

# Завантаження змінних середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад: https://test-bot-olnr.onrender.com/webhook

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)
app = FastAPI()

# Ініціалізація Telegram застосунку
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Системний промпт
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, "
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати. "
    "Серед сервісів: +1/+2/+3 роки гарантії, Альфа-сервіс, Вільний вибір, Бумеранг, Повернення без проблем, "
    "SUPPORT для смартфонів, інші. "
    "Враховуй тип товару. Якщо сервісів немає — чітко вкажи це. Відповідай українською, без вигадок чи зайвого тексту."
)

# Завантаження бази знань
if os.path.exists("knowledge_base.json"):
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
else:
    raise FileNotFoundError("Файл knowledge_base.json не знайдено")

# Хендлери Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши мені назву товару, і я підкажу, які сервіси можна запропонувати.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("Сталася помилка. Спробуйте пізніше.")
        print(f"[GPT error] {e}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))

# Webhook endpoint
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    await telegram_app.update_queue.put(Update.de_json(data, bot))
    return {"ok": True}

# Set webhook on startup
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(url=WEBHOOK_URL)



