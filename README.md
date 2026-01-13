# RAG Product Information Chatbot

## A. Complete Architecture Diagram + Explanation

This project implements a Retrieval-Augmented Generation (RAG) chatbot system designed to answer product-related questions using a Vector Database and LLM.

### System Flow
```mermaid
graph LR
    User[User] -->|HTTP Request| Django[Django Frontend]
    Django -->|HTTP POST JSON| FastAPI[FastAPI Backend]
    subgraph FastAPI Backend
        FastAPI_App[FastAPI App/Router] -->|Query| RAG[LangChain RAG Pipeline]
        RAG -->|Embed Query| Embed[Embedding Model]
        Embed -->|Search| VectorDB[(ChromaDB Vector Store)]
        VectorDB -->|Context Retrieval| RAG
        RAG -->|Prompt + Context| LLM[LLM (OpenAI/Groq)]
        LLM -->|Answer| RAG
    end
    RAG -->|Response| FastAPI_App
    FastAPI_App -->|JSON Response| Django
    Django -->|HTML/JS| User
```

### Component Details

1.  **User**: Interacts with the chat interface in the browser.
2.  **Django Frontend**:
    -   Acts as the presentation layer.
    -   Serves the HTML template and static assets.
    -   **Does NOT** perform any AI logic.
    -   Takes the user's input and forwards it to the FastAPI backend via a secure server-side HTTP request (or proxies the request from the client).
    -   *Note: In this implementation, we use JavaScript `fetch` on the client side to hit the Django view, which then proxies to FastAPI, or we can hit FastAPI directly if CORS allows. For security and to keep to the "Django -> FastAPI" requirement strictly, we will have a Django View proxy the request.*

3.  **FastAPI Backend**:
    -   The core calculation engine.
    -   Exposes a `/chat` endpoint.
    -   Initializes the LangChain pipeline.
    -   Manages the connection to the Vector Database.

4.  **LangChain RAG Pipeline**:
    -   **Ingestion**: Loads raw product data, breaks it into chunks (if necessary), and creates embeddings.
    -   **Retrieval**: Converts the user's question into a vector and finds the most similar product descriptions in ChromaDB.
    -   **Generation**: Combines the retrieved context with the user's question into a prompt for the LLM.

5.  **Vector DB (ChromaDB)**:
    -   Stores high-dimensional vectors of the product data.
    -   Allows for semantic search (finding meanings, not just keyword matches).

6.  **LLM**:
    -   Generates the natural language response based on the factual context provided by the Vector DB.

---

## D. Product Database Structure

### SQL Version (Relational)
Used if you were syncing from a traditional DB.
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    material TEXT,
    size TEXT,
    color TEXT,
    price NUMERIC(10, 2),
    stock INT
);
```

### NoSQL Version (JSON/Document)
The format often used before embedding.
```json
{
  "id": "prod_123",
  "name": "Classic Leather Jacket",
  "description": "A timeless black leather jacket made from genuine cowhide.",
  "attributes": {
    "material": "Leather",
    "size": "M, L, XL",
    "color": "Black"
  },
  "price": 199.99,
  "stock": 50
}
```

### Vector DB Structure (ChromaDB)
ChromaDB stores data in collections. Each item contains:
-   **ids**: Unique identifier (e.g., "prod_123").
-   **embeddings**: List of floats provided by the embedding model (e.g., `[0.12, -0.45, ...]`).
-   **documents**: The raw text content used for retrieval (e.g., "Name: Classic Leather Jacket. Description: ...").
-   **metadatas**: Structured data for filtering (e.g., `{"price": 199.99, "category": "clothing"}`).

---
