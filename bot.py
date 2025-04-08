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
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.chains import RetrievalQA
from openai import OpenAI

# Завантаження токенів
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ініціалізація клієнта OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Шлях до бази знань
KB_PATH = "knowledge_base.json"
INDEX_PATH = "faiss_index"

# Функція для створення FAISS-індексу
def create_faiss_index():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        kb_data = json.load(f)

    documents = []
    for category in kb_data:
        name = category.get("category", "")
        keywords = ", ".join(category.get("keywords", []))
        services = "\n".join([f"- {srv['name']}: {srv['desc']}" for srv in category.get("services", [])])

        full_text = f"Категорія: {name}\nКлючові слова: {keywords}\nСервіси:\n{services}"
        documents.append(Document(page_content=full_text))

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(INDEX_PATH)

# Ініціалізація або завантаження індексу
if not os.path.exists(INDEX_PATH):
    create_faiss_index()

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = FAISS.load_local(INDEX_PATH, embeddings)
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(llm=client.chat.completions, retriever=retriever, return_source_documents=False)

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши назву товару, і я підкажу, які сервіси SUPPORT.UA можна до нього запропонувати."
    )

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    try:
        result = qa_chain.run(user_message)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз пізніше.")
        print(f"[LangChain error]: {e}")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
