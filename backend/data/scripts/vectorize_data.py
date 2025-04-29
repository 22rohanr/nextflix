import json
import time
from tqdm import tqdm
from backend.app.config import connect_pinecone
from backend.app.rag_utils import embed_texts

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
    try:
        pc, index = connect_pinecone()
        index.delete(delete_all=True)

    finally:
        upsert_to_pinecone("backend/data/raw/movies_cleaned.json")
        upsert_to_pinecone("backend/data/raw/tv_cleaned.json")