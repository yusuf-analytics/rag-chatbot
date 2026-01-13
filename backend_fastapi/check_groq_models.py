import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("Error: GROQ_API_KEY not found.")
else:
    client = Groq(api_key=api_key)
    print("Listing available Groq models...")
    try:
        models = client.models.list()
        for m in models.data:
            print(f"- {m.id}")
    except Exception as e:
        print(f"Error listing models: {e}")
