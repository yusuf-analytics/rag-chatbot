import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

# Load env vars
load_dotenv()

PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "chroma_db")

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def get_rag_chain():
    """
    Creates and returns the LangChain RAG pipeline.
    """
    if not os.path.exists(PERSIST_DIRECTORY):
        raise FileNotFoundError(f"ChromaDB not found at {PERSIST_DIRECTORY}. Please run ingest.py first.")

    # 1. Initialize Embeddings (HuggingFace - Local)
    # Must match ingestion
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 2. Connect to Vector DB
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )
    
    # 3. Create Retriever
    # Increased k to 6 to handle "List all products" queries better
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    # 4. Define Prompt
    template = """You are a helpful product assistant. Answer the question based ONLY on the following context.
    If the answer is not in the context, say "I don't have information about that product."

    IMPORTANT INSTRUCTIONS:
    1. If the user asks for a LIST of products (e.g., "what products do you have?"), ONLY list the product names as bullet points. Do NOT include price or description in the list unless explicitly asked.
    2. If the user asks for specific attributes (e.g., "what is the material/color/size?"), provided ONLY that specific information. Do NOT repeat the price or other unrelated details unless asked.
    3. Format your response using proper Markdown:
       - Use bullet points for lists.
       - Bold product names (**Product Name**).

    Context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 5. Initialize LLM (Groq - Llama 3)
    # Using Llama 3.3 70B via Groq for super fast inference
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    # 6. Build Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def rebuild_index():
    """
    Rebuilds the ChromaDB index using data from sample_data.json.
    Designed to be called from within the running FastAPI process.
    """
    import json
    from langchain_core.documents import Document
    
    DATA_FILE = os.path.join(os.path.dirname(__file__), "sample_data.json")
    print(f"Loading data from {DATA_FILE}...")
    
    with open(DATA_FILE, 'r') as f:
        products = json.load(f)

    documents = []
    for product in products:
        content = f"Product Name: {product['name']}. \n" \
                  f"Gender: {product['attributes']['gender']}. \n" \
                  f"Category: {product['attributes']['category']}. \n" \
                  f"Description: {product['description']}. \n" \
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
        documents.append(Document(page_content=content, metadata=metadata))

    # Initialize Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Connect to existing DB
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )
    
    # Clear and Add
    print("Clearing and rebuilding collection...")
    try:
        vectorstore.delete_collection()
        # Re-init after delete
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY, 
            embedding_function=embeddings
        )
    except Exception as e:
        print(f"Rebuild warning: {e}")

    if documents:
        vectorstore.add_documents(documents=documents)
        print(f"Added {len(documents)} documents.")
    
    return True
