import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
import asyncio

# === Конфігурація ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

openai.api_key = OPENAI_API_KEY
bot = Bot(BOT_TOKEN)

# === FastAPI ===
app = FastAPI()

# === LangChain: підключення бази знань ===
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
db = FAISS.load_local("kb_index", embedding, allow_dangerous_deserialization=True)
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0),
    retriever=db.as_retriever()
)

SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, посилання на товар або код, ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати."
    "Використовуй лише дані з бази знань. Якщо сервісів немає — чітко вкажи це. Не вигадуй. Відповідай українською."
)

# === Обробка команд ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши назву товару, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    try:
        response = qa_chain.run(f"{SYSTEM_PROMPT}\n\n{user_message}")
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")
        print(f"[LangChain error]: {e}")

# === Telegram webhook endpoint ===
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

# === Ініціалізація Telegram application ===
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Запуск бота з webhook ===
async def run():
    await application.initialize()
    await bot.delete_webhook()
    await bot.set_webhook(url=WEBHOOK_URL)
    await application.start()

loop = asyncio.get_event_loop()
loop.create_task(run())
