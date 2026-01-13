import json
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.path.join(os.path.dirname(__file__), "sample_data.json")
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "chroma_db")

def ingest_data():
    print(f"Loading data from {DATA_FILE}...")
    
    with open(DATA_FILE, 'r') as f:
        products = json.load(f)

    documents = []
    for product in products:
        content = f"Product Name: {product['name']}. \nDescription: {product['description']}. \n" \
                  f"Material: {product['attributes']['material']}. \n" \
                  f"Size: {product['attributes']['size']}. \n" \
                  f"Color: {product['attributes']['color']}. \n" \
                  f"Price: ${product['price']}."
        
        metadata = {
            "id": product['id'],
            "name": product['name'],
            "price": product['price'],
            "stock": product['stock']
        }
        
        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)

    print(f"Prepared {len(documents)} documents.")

    # Uses a small, fast, local model (CPU friendly)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Initialize Chroma Manager
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )

    print("Clearing existing collection (avoiding file locks)...")
    try:
        # Instead of deleting the folder (locked on Windows), we delete the collection contents
        vectorstore.delete_collection() 
        # Re-initialize to create a fresh empty collection
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY, 
            embedding_function=embeddings
        )
    except Exception as e:
        print(f"Warning during cleanup: {e}")

    print("Creating embeddings and storing in ChromaDB...")
    # Add documents to the fresh collection
    vectorstore.add_documents(documents=documents)
    
    print(f"Success! Vector DB created at {PERSIST_DIRECTORY}")

if __name__ == "__main__":
    ingest_data()
