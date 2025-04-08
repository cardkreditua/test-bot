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
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import JSONLoader

# Завантаження токенів
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # наприклад: https://your-app-name.onrender.com/webhook

# Ініціалізація OpenAI
openai.api_key = OPENAI_API_KEY

# SYSTEM PROMPT
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, ти відповідаєш, які сервіси SUPPORT.UA доступні до нього. "
    "Відповідай чітко, українською, без фантазій. Не вигадуй. Якщо сервісів немає — скажи про це."
)

# Завантаження бази знань
loader = JSONLoader(
    file_path="knowledge_base.json",
    jq_schema=".[]",
    text_content=False
)
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=False
)

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напишіть назву товару, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати."
    )

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    try:
        result = qa_chain.run(f"{SYSTEM_PROMPT}\n\nТовар: {user_message}")
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")
        print(f"[OpenAI RAG error]: {e}")

# Запуск бота (Webhook)
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )
