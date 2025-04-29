from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.rag_utils import search_pinecone
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/recommend")
async def recommend(request: QueryRequest, x_api_key: str = Header(None)):
    if x_api_key != os.getenv("FAST_API_KEY"):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access. A valid API key is required."
        )

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(search_pinecone, request.user_query),
            timeout=60
        )
        return result

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Sorry, the request timed out. Please try again."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Sorry, something went wrong while processing your query."
        )