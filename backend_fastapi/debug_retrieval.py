
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "chroma_db")

def debug_retrieval():
    print(f"Checking ChromaDB at: {PERSIST_DIRECTORY}")
    
    if not os.path.exists(PERSIST_DIRECTORY):
        print("ERROR: ChromaDB directory not found.")
        return

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
    
    # 1. Count Total Documents
    # Chroma doesn't have a direct 'len', so we search for something generic to hopefully get everything, 
    # or just trust the search results.
    print("\n--- Running Similarity Search for 'produk' (k=10) ---")
    results = vectorstore.similarity_search("produk", k=10)
    
    print(f"Found {len(results)} documents:")
    for i, doc in enumerate(results):
        print(f"[{i+1}] {doc.metadata.get('name', 'Unknown')}")
        print(f"    Source ID: {doc.metadata.get('id')}")
        # print(f"    Content Preview: {doc.page_content[:50]}...")

    print("\n--- Running Similarity Search for 'ada apa saja produk di toko ini?' (k=6) ---")
    results_query = vectorstore.similarity_search("ada apa saja produk di toko ini?", k=6)
    for i, doc in enumerate(results_query):
        print(f"[{i+1}] {doc.metadata.get('name')}")

if __name__ == "__main__":
    debug_retrieval()
