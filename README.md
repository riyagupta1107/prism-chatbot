
# Prism Chatbot 🤖✨

A smart chatbot system built using a **Retrieval-Augmented Generation (RAG) model** with **Pinecone** as the vector database.
It is designed to answer queries related to items in a knowledge base with **fast, accurate, and context-aware responses**.

This repository also contains an **experimental alternate approach** (Work In Progress) where we explored building a custom LLM for model-related queries.

---

## 🚀 Features

* 🔍 **RAG-based retrieval** – fetches relevant context before generating responses.
* 📦 **Pinecone integration** – efficient, scalable vector search for item-related queries.
* 💬 **Conversational interface** – interact with the bot just like a human.
* 🧪 **Experimental LLM attempt** – an alternate design being explored (in progress).

---

## 🛠️ Tech Stack

* **Language Model**: OpenAI / compatible LLM API
* **Vector Database**: [Pinecone](https://www.pinecone.io/)
* **Backend**: Python
* **Frameworks**: LangChain (for RAG pipeline), FastAPI/Flask (if applicable)
* **Environment**: Conda / Virtualenv

---

## 📂 Folder Structure

```
prism-chatbot/
│
├── main/                 # ✅ Working chatbot (RAG + Pinecone)
│   ├── app.py            # Entry point for chatbot
│   ├── rag_pipeline.py   # Retrieval-Augmented Generation pipeline
│   ├── pinecone_utils.py # Pinecone database integration
│   └── requirements.txt  # Dependencies
│
├── alternate/            # 🧪 Experimental custom LLM approach (incomplete)
│   └── model_attempt.py  # Early work on a model-specific Q&A bot
│
└── README.md             # 📖 You are here
```

---

## ⚡ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/riyagupta1107/prism-chatbot.git
cd prism-chatbot/main
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_api_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=your_pinecone_environment
```

### 4. Run the chatbot

```bash
python app.py
```

---

## 🎯 Usage

Once running, you can ask the chatbot **item-related queries**, and it will:

1. Retrieve relevant context from Pinecone
2. Use the LLM to generate a contextual answer
3. Reply in natural language

---
## 🧪 Work in Progress: Alternate LLM Approach

In addition to the production-ready **RAG + Pinecone chatbot**, this repository also contains an **experimental project** under the `alternate/` folder.

### 🌟 The Vision

The idea behind this alternate approach is to **move beyond retrieval-based systems** and explore whether a **custom domain-focused LLM** could directly answer queries. Instead of always depending on Pinecone for context, this model aims to:

* Handle **model-related technical queries** more natively.
* Allow **fine-tuning and domain specialization**.
* Explore the trade-offs between **retrieval-based vs. generative-only** solutions.

This reflects a forward-looking exploration: “What if the chatbot could learn and answer intelligently on its own, without needing external lookups every time?”

---

### 🛠️ Current Progress (in `alternate/`)

* **`model_attempt.py`** → Early prototype script experimenting with generating responses directly from an LLM.
* **Key Concepts Tried**:

  * Prompt engineering for model-specific Q&A.
  * Structuring queries without Pinecone dependency.
  * Testing response quality with smaller datasets.

👉 While this path is still under construction, it highlights the team’s **curiosity and commitment to innovation**.
The progress so far provides a solid foundation to build on — and the lessons learned here will feed back into improving the main chatbot.

---
## 🌱 Future Scope

* Enhance **alternate LLM project** for domain-specific Q&A.
* Add **frontend UI** for better user interaction.
* Support **multi-database backends** beyond Pinecone.
* **Hybrid design** → Combine this LLM with lightweight embeddings for fallback retrieval.
* **Fine-tuning experiments** → Train a smaller domain-specific model for faster, focused answers.
* **Memory integration** → Enable multi-turn conversations with persistent context.
* **Benchmarking** → Compare this approach against the RAG system to measure accuracy vs. flexibility.

---




