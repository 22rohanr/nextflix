from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.rag_utils import search_pinecone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QueryRequest(BaseModel):
    user_query: str

from fastapi import HTTPException
import asyncio

@app.post("/recommend")
async def recommend(request: QueryRequest):
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(search_pinecone, request.user_query),
            timeout=60
        )
        return result

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Sorry, the request timed out. Please try again.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Sorry, something went wrong while processing your query.")

