import os
import json
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Завантаження повної бази знань
with open("knowledge_base.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)

documents = []
for entry in knowledge_base:
    services_text = "\n".join([f"- {s['name']}: {s['desc']}" for s in entry["services"]])
    keywords_text = ", ".join(entry["keywords"])
    content = f"Категорія: {entry['category']}\nКлючові слова: {keywords_text}\nСервіси:\n{services_text}"
    documents.append(Document(page_content=content))

# Створення індексу
embeddings = OpenAIEmbeddings()
faiss_index = FAISS.from_documents(documents, embeddings)

# Збереження індексу
faiss_index.save_local("faiss_index")
print("✅ FAISS індекс успішно згенеровано.")
