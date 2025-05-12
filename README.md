# 🎬 NextFlix — AI-Powered Media Recommender

NextFlix is a fullstack AI-powered recommendation system for movies, TV shows, and anime. It uses semantic search via Pinecone and a Retrieval-Augmented Generation (RAG) pipeline with Llama 3 (via Groq) to return high-quality, natural language recommendations based on user prompts.

🌐 **Live Demo:** [nextflix.rohanrashingkar.com](https://nextflix.rohanrashingkar.com)

---

## 🚀 Features

- 🔎 **Semantic Search** over 10,000+ entries using vector embeddings on Pinecone
- 🧠 **Query Refinement** with Llama 3 to understand user intent
- 🤖 **LLM Ranking + Response Generation** also with Llama 3 for clean text output
- 📦 Built with **FastAPI** and **deployed on Render**
- 🔍 Supports filters for anime, type (`movie` / `tv`), plot, genre, director, actors, music composer, and more

---

## 💡 How It Works

1. **User inputs a natural language query** (e.g., "Give me 10 anime series about another world")
2. A **Groq-hosted Llama 3 model** rewrites it into a structured semantic search prompt
3. The query is embedded using `llama-text-embed-v2` and searched against a Pinecone vector DB
4. The top 10 results are passed into another Llama call to format a clean recommendation list

---

## 🛠️ How It Was Built

- **Backend:**  
  Built with **FastAPI**, the backend exposes a single endpoint that processes user prompts.  
  - A custom dataset of over 10,000 movie, TV, and anime titles was collected by scraping the TMDB API, including metadata like genres, language, and ratings.
  - First, it sends the prompt to **Llama 3 (via Groq)** to transform it into a semantic query suitable for vector search.
  - This transformed query is embedded and searched against a **Pinecone vector database**.
  - The results are then passed through Llama 3 again to generate a clean, natural language response.
  - The final output relies **only on Pinecone results**, ensuring it doesn't "hallucinate" information beyond the indexed content.

- **Frontend:**  
  Built with **Next.js**, using the assistant-ui library's LLM template as a starting point.  
  - The UI includes thread history, input handling, and a clean chat-style interface.
  - Hosted on **Vercel**, connected to a custom domain at `nextflix.rohanrashingkar.com`.

---
