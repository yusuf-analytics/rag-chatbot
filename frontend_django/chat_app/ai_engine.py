import os
import json
from django.conf import settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

# Define paths
# Use a specific path for ChromaDB
PERSIST_DIRECTORY = getattr(settings, 'CHROMA_DB_PATH', os.path.join(settings.BASE_DIR, "chroma_db"))
DATA_FILE = os.path.join(settings.BASE_DIR, "sample_data.json")

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def get_rag_chain():
    """
    Creates and returns the LangChain RAG pipeline.
    """
    if not os.path.exists(PERSIST_DIRECTORY):
        # Auto-ingest if missing
        print(f"ChromaDB not found at {PERSIST_DIRECTORY}. Building index now...")
        rebuild_index()

    # 1. Initialize Embeddings (HuggingFace - Local)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 2. Connect to Vector DB
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )
    
    # 3. Create Retriever
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    # 4. Define Prompt
    template = """You are a helpful product assistant. Answer the question based ONLY on the following context.
    If the answer is not in the context, say "Maaf, saya tidak punya informasi tentang produk tersebut."

    IMPORTANT INSTRUCTIONS:
    1. If the user asks for a LIST of products, ONLY list the product names as bullet points.
    2. Format your response using proper Markdown.
    3. Be polite and helpful.

    Context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 5. Initialize LLM (Groq)
    groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not groq_api_key:
        return RunnablePassthrough() | (lambda x: "Error: GROQ_API_KEY is not set.")

    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0, groq_api_key=groq_api_key)

    # 6. Build Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def rebuild_index():
    """
    Rebuilds the ChromaDB index using data directly from Django Models to ensure freshness.
    """
    print("Rebuilding Index from Django Database...")
    
    # Avoid circular import by importing inside function
    from chat_app.models import Product
    
    products = Product.objects.all()
    documents = []
    
    for p in products:
        content = f"Product Name: {p.name}. \n" \
                  f"Gender: {p.gender}. \n" \
                  f"Category: {p.category}. \n" \
                  f"Description: {p.description}. \n" \
                  f"Material: {p.material}. \n" \
                  f"Size: {p.size}. \n" \
                  f"Color: {p.color}. \n" \
                  f"Price: ${p.price}."
        
        metadata = {
            "id": p.id,
            "name": p.name,
            "price": float(p.price) if p.price else 0,
            "stock": p.stock
        }
        documents.append(Document(page_content=content, metadata=metadata))

    # Initialize Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Clear and Add
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )
    
    try:
        vectorstore.delete_collection()
        # Refresh client
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY, 
            embedding_function=embeddings
        )
    except Exception as e:
        print(f"Warning during delete_collection: {e}")

    if documents:
        vectorstore.add_documents(documents=documents)
        print(f"Index updated with {len(documents)} products.")
    else:
        print("No products found in database to index.")
    
    return True

def get_answer(question):
    """
    Simple wrapper to get answer.
    """
    try:
        chain = get_rag_chain()
        return chain.invoke(question)
    except Exception as e:
        return f"Error processing request: {str(e)}"
