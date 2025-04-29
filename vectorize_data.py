import json
import os
import time
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from tqdm import tqdm

load_dotenv()

def connect_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index = pc.Index("nextflix-index")
    return pc, index

def embed_texts(pc, texts, embed_type):
    response = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=texts,
        parameters={"input_type": embed_type, "truncate": "END", "dimension": 1024}
    )
    return response

def batch(data, n=50):
    for i in range(0, len(data), n):
        yield data[i:i + n]

def upsert_to_pinecone(name):
    pc, index = connect_pinecone()

    with open(name, "r", encoding="utf-8") as f:
        data = json.load(f)

        ids = [item["id"] for item in data]
        texts = [item["text"] for item in data]
        metas = [item["metadata"] for item in data]

        for ids_batch, texts_batch, metas_batch in tqdm(zip(batch(ids), batch(texts), batch(metas)), total=(len(ids) // 100) + 1):
            embed_response = embed_texts(pc, texts_batch, "passage")
            vectors = embed_response
            pinecone_vectors = []
            
            for idx, v in enumerate(vectors):
                pinecone_vectors.append({
                    "id": ids_batch[idx],
                    "values": v['values'],
                    "metadata": metas_batch[idx]
                })

            index.upsert(vectors=pinecone_vectors)
            time.sleep(0.2)


if __name__ == "__main__":
    print("Inserting...")
    # try:
    #     pc, index = connect_pinecone()
    #     index.delete(delete_all=True)

    # finally:
    #     upsert_to_pinecone("data/movies_cleaned.json")
    #     upsert_to_pinecone("data/tv_cleaned.json")