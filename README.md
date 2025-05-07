# 🍽️ ClareMenu – Claremont College AI Dining Assistant

A web app that aggregates daily menus from all 7 Claremont Colleges' dining halls and helps students make informed dining choices. It includes nutrition info, meal categories, and an AI chatbot that answers natural language questions like:  
> *“Where can I get a high-protein vegan dinner tonight?”*

---

## 🚀 Features

- ✅ Web scraping of menus from 7 dining hall websites  
- 🥦 Nutrition and dietary labels (vegan, halal, gluten-free, etc.)  
- 🤖 AI chatbot for meal recommendations based on user queries  
- 📅 Automatically updates daily with current meal info  
- 📂 JSON-formatted storage for easy querying & vector search

---

## 🧠 AI-Powered Chatbot (RAG-based)

- Uses **Weaviate** as a vector store to embed and index dining data  
- Powered by **OpenAI** for generating responses  
- Built-in support for semantic search and dietary preference memory

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **Web Scraping**: Selenium 
- **AI/NLP**: OpenAI API, Weaviate vector DB
- **Data Storage**: JSON files per menu day  
- **Task Automation**: Daily refresh via scheduled script

