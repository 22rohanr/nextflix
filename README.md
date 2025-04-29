# 🎬 NextFlix — AI-Powered Media Recommender

NextFlix is a fullstack AI-powered recommendation system for movies, TV shows, and anime. It uses semantic search via Pinecone and a Retrieval-Augmented Generation (RAG) pipeline with LLaMA 3 (via Groq) to return high-quality, natural language recommendations based on user prompts.

🌐 **Live Demo:** [nextflix.rohanrashingkar.com](https://nextflix.rohanrashingkar.com)

---

## 🚀 Features

- 🔎 **Semantic Search** over 10,000+ entries using vector embeddings
- 🧠 **Query Refinement** with LLaMA 3 to understand user intent
- 🤖 **LLM Ranking + Response Generation** for clean, friendly recommendations
- 📦 Built with **FastAPI** and **deployed on Render**
- 🔍 Supports filters for anime, type (`movie` / `tv`), genre, and more

---

## 💡 How It Works

1. **User inputs a natural language query** (e.g., "Give me 10 anime series about another world")
2. A **Groq-hosted LLaMA 3 model** rewrites it into a structured semantic search prompt
3. The query is embedded using `llama-text-embed-v2` and searched against Pinecone
4. The top 10 results are passed into another LLaMA call to format a clean recommendation list