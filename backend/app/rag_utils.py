import json
import os
import openai
from dotenv import load_dotenv
from backend.app.config import connect_pinecone

load_dotenv()

def embed_texts(pc, texts, embed_type):
    response = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=texts,
        parameters={"input_type": embed_type, "truncate": "END", "dimension": 1024}
    )
    return response


def load_prompt():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(base_dir, "data", "raw", "prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
    
def call_groq_llm(user_query):
    client = openai.OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    system_prompt = load_prompt()

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

def search_pinecone(user_query):
    pc, index = connect_pinecone()

    llm_response = call_groq_llm(user_query)
    llm_response = json.loads(llm_response)
    print(llm_response)
    embedded_query = embed_texts(pc, [llm_response["query"]], "query")[0]['values']

    filter_metadata = llm_response.get("filters", {})
    
    results = index.query(
        vector=embedded_query,
        filter=filter_metadata,
        top_k=10,
        include_metadata=True
    )

    return results

if __name__ == "__main__":
    user_query = input("Enter your search query: ")
    search_results = search_pinecone(user_query)

    for match in search_results["matches"]:
        print(f"{match['metadata']['title']} - Score: {match['score']:.3f}")