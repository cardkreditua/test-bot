import os
import json
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import openai

# Токени та ключі
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
openai.api_key = OPENAI_API_KEY

# SYSTEM PROMPT
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, код або посилання, ти визначаєш категорію товару і чітко стисло пропонуєш сервіси SUPPORT.UA до нього."
)

# Завантаження knowledge_base.json
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

# FastAPI app
app = FastAPI()

# Telegram bot
telegram_app = Application.builder().token(BOT_TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши назву товару, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати."
    )

# handle message
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

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Webhook endpoint
@app.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    update = Update.de_json(body, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


