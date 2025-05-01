from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.app.rag_utils import search_pinecone_stream
from dotenv import load_dotenv
import asyncio
import json
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
    async def stream_response():
        if x_api_key != os.getenv("FAST_API_KEY"):
            yield '0:"Sorry, something went wrong while processing your request. Can you try again?"\n'
            return

        try:
            async for chunk in search_pinecone_stream(request.user_query):
                yield f'0:{json.dumps(chunk)}\n'
        except asyncio.TimeoutError:
            yield '0:"Sorry, your request timed out. Can you try again?"\n'
        except Exception as e:
            yield '0:"Sorry, something went wrong while processing your query. Can you try again?"\n'

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
        headers={"x-vercel-ai-data-stream": "v1"}
    )