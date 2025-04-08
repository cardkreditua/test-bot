import os
import json
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Завантаження бази знань
loader = JSONLoader(
    file_path="knowledge_base.json",
    jq_schema=".",  # завантажує весь json
    text_content=False
)
data = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=20)
docs = text_splitter.split_documents(data)

# Індексування
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
db = FAISS.from_documents(docs, embedding)
retriever = db.as_retriever()

# Ланцюжок QA
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Введи назву товару, і я підкажу, які сервіси можна запропонувати.")

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    try:
        answer = qa_chain.run(query)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("Помилка при обробці запиту.")
        print(e)

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
