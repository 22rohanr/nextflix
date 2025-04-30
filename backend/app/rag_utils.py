import json
import os
from dotenv import load_dotenv
from backend.app.config import connect_pinecone
import asyncio

from openai import AsyncOpenAI  # Make sure openai>=1.0.0

load_dotenv()

def embed_texts(pc, texts, embed_type):
    response = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=texts,
        parameters={"input_type": embed_type, "truncate": "END", "dimension": 1024}
    )
    return response

def load_prompt(prompt):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(base_dir, "data", "raw", prompt)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

async def call_groq_llm_stream(user_query, prompt, temperature):
    client = AsyncOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    system_prompt = load_prompt(prompt)
    stream = await client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=temperature,
        stream=True
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content

async def search_pinecone_stream(user_query: str):
    try:
        pc, index = await asyncio.to_thread(connect_pinecone)
        input_llm_response = await asyncio.to_thread(
            call_groq_llm, user_query, "input_prompt.txt", 0.3
        )
        input_llm_response = json.loads(input_llm_response)
        embedded_query = (await asyncio.to_thread(
            embed_texts, pc, [input_llm_response["query"]], "query"
        ))[0]['values']
        results = await asyncio.to_thread(
            index.query,
            vector=embedded_query,
            filter=input_llm_response.get("filters", {}),
            top_k=10,
            include_metadata=True
        )
        metadata_json = json.dumps(
            [match["metadata"] for match in results["matches"]],
            indent=2
        )
        output_query = f"User prompt: {user_query}\n\nTop 10 results:\n{metadata_json}"

        async for chunk in call_groq_llm_stream(output_query, "output_prompt.txt", 0.5):
            yield chunk

    except Exception as e:
        yield f"\n[ERROR]: {str(e)}"

def call_groq_llm(user_query, prompt, temperature):
    import openai
    client = openai.OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    system_prompt = load_prompt(prompt)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content
