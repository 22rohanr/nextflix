import os
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone

load_dotenv()

def connect_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index = pc.Index("nextflix-index")
    return pc, index