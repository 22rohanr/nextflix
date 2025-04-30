from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.app.rag_utils import search_pinecone_stream
from dotenv import load_dotenv
import os
import asyncio

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
    async def timeout_wrapper():
        gen = search_pinecone_stream(request.user_query)
        try:
            while True:
                chunk = await asyncio.wait_for(gen.__anext__(), timeout=60)
                yield chunk
        except StopAsyncIteration:
            return
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Request timed out after 60 seconds."
            )
    try:
        return StreamingResponse(
            timeout_wrapper(),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sorry, something went wrong while processing your query."
        )