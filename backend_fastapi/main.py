from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from models import QueryRequest, QueryResponse
from contextlib import asynccontextmanager
from models import QueryRequest, QueryResponse
from rag_engine import get_rag_chain, rebuild_index
import logging

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for the chain
rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the RAG chain
    global rag_chain
    try:
        rag_chain = get_rag_chain()
        logger.info("RAG Chain initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Chain: {e}")
        logger.warning("Did you run 'python ingest.py' first?")
    yield
    # Shutdown logic if needed

app = FastAPI(title="Product RAG API", lifespan=lifespan)

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Receives a question, queries the Vector DB, and generates an answer using LLM.
    """
    global rag_chain
    if not rag_chain:
        # Try to initialize again (lazy load)
        try:
            rag_chain = get_rag_chain()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RAG Engine not ready. Run ingest.py first. Error: {e}")

    logger.info(f"Received question: {request.question}")
    
    try:
        # Invoke the chain
        response_text = rag_chain.invoke(request.question)
        return QueryResponse(answer=response_text)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "running", "rag_ready": rag_chain is not None}

@app.post("/refresh")
async def refresh_chain():
    """
    Forces a reload of the RAG chain. Call this after running ingest.py.
    """
    global rag_chain
    try:
        rag_chain = get_rag_chain()
        logger.info("RAG Chain re-initialized successfully via /refresh.")
        return {"status": "success", "message": "RAG Chain reloaded."}
    except Exception as e:
        logger.error(f"Failed to refresh RAG Chain: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh: {e}")

@app.post("/ingest")
async def ingest_endpoint():
    """
    Triggers a full rebuild of the vector database from sample_data.json,
    then automatically reloads the RAG chain.
    """
    global rag_chain
    try:
        # 1. Rebuild Index (In-Process)
        rebuild_index()
        logger.info("Index rebuild complete.")
        
        # 2. Reload Chain
        rag_chain = get_rag_chain()
        logger.info("RAG Chain reloaded after ingest.")
        return {"status": "success", "message": "Ingestion and Refresh Complete."}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
