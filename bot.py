import os
import json
import openai
from fastapi import FastAPI, Request
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from telegram import Bot

# Завантаження токенів
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Системний промпт
SYSTEM_PROMPT = (
    "Ти асистент-продавець ROZETKA. Коли користувач вводить назву товару, посилання на товар або код, "
    "ти чітко і стисло відповідаєш, які сервіси SUPPORT.UA можна до нього запропонувати. "
    "Серед сервісів: +1/+2/+3 роки гарантії, Альфа-сервіс, Вільний вибір, Бумеранг, Повернення без проблем, "
    "SUPPORT для смартфонів, інші. "
    "Враховуй тип товару. Якщо сервісів немає — чітко вкажи це. Відповідай українською, без фантазій чи зайвого тексту."
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

# FastAPI app
app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    try:
        message = data.get("message") or data.get("edited_message")
        if not message:
            return {"ok": True}

        user_message = message["text"]
        chat_id = message["chat"]["id"]

        docs = vectorstore.similarity_search(user_message, k=3)
        context_text = "\n".join([doc.page_content for doc in docs])

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\nКонтекст:\n" + context_text},
                {"role": "user", "content": user_message},
            ]
        )
        reply = completion.choices[0].message.content
        await bot.send_message(chat_id=chat_id, text=reply)

    except Exception as e:
        print(f"[Webhook error]: {e}")
        if "chat_id" in locals():
            await bot.send_message(chat_id=chat_id, text="Сталася помилка. Спробуйте ще раз пізніше.")

    return {"ok": True}


