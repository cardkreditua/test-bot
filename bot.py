import os
import json
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from langchain_openai import OpenAIEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import openai
from contextlib import asynccontextmanager

# 🔐 Токени
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = OPENAI_API_KEY
bot = Bot(BOT_TOKEN)

# 🎯 System prompt
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Відповідай коротко, чітко, без вигадок, українською. "
    "На основі категорії товару з бази знань, надай перелік сервісів SUPPORT.UA, які можна запропонувати."
)

# 📚 Завантаження бази знань
with open("knowledge_base.json", encoding="utf-8") as f:
    raw_data = json.load(f)

documents = []
for entry in raw_data:
    category = entry.get("category", "")
    keywords = ", ".join(entry.get("keywords", []))
    services = "\n".join([f"- {s['name']}: {s['desc']}" for s in entry.get("services", [])])
    content = f"Категорія: {category}\nКлючові слова: {keywords}\nСервіси:\n{services}"
    documents.append(Document(page_content=content))

vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY))

# 📦 Telegram Application
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# 📬 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши назву товару, і я підкажу сервіси SUPPORT.UA.")

# 🧠 Обробка повідомлень з повним логуванням
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    print(f"⚡️ Отримано повідомлення від користувача: {query}")

    try:
        # Пошук в базі
        docs = vectorstore.similarity_search(query, k=3)
        if docs:
            context_text = "\n".join(doc.page_content for doc in docs)
            print(f"📚 Знайдено {len(docs)} документ(и): {context_text}")
        else:
            context_text = ""
            print(f"⚠️ Документів не знайдено за запитом: {query}")

        # Запит до OpenAI
            response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\nКонтекст:\n" + context_text},
                {"role": "user", "content": query}
            ]
        )
        reply = response.choices[0].message.content

        print(f"💬 Відповідь OpenAI: {reply}")

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Вибач, сталася помилка. Спробуй ще раз пізніше.")
        print(f"❗ Помилка в обробці повідомлення: {e}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

# 🛠 Lifespan для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Webhook встановлено")
    yield

# 🤖 FastAPI з lifespan
app = FastAPI(lifespan=lifespan)

# 🛡 Обробник для кореня (щоб не було 404 в логах)
@app.get("/")
async def root():
    return {"message": "Бот працює! Webhook на /webhook"}

# 📬 Обробка Telegram вебхука
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return {"ok": True}

