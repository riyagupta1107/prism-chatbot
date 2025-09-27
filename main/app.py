import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pinecone
import google.generativeai as genai
# --- MODIFICATION: Import the specific exception for rate limiting ---
from google.api_core import exceptions as google_exceptions
from sentence_transformers import SentenceTransformer

# --- 1. INITIALIZATION ---

# Load environment variables from .env file
load_dotenv()
print("Initializing connections and loading models...")

# Initialize Flask App
app = Flask(__name__)

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in .env file")

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index_host = "https://microwave-support-lhzdo1l.svc.aped-4627-b74a.pinecone.io"
index = pc.Index(host=index_host)

# Initialize Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the Embedding Model (this can take a moment)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

print("✅ System is ready.")

# --- 2. THE CORE RAG FUNCTION (from your script) ---

def get_answer(query):
    """
    The main logic for the RAG system.
    """
    # --- Step 1: Classify the product category ---
    classification_prompt = f"""
    Based on the user's question, identify which of the following product categories it belongs to:
    microwave, washing_machine, fridge.
    Return only the single category name and nothing else.
    Question: "{query}"
    Category:
    """
    # --- MODIFICATION: Improved error handling for the API call ---
    try:
        classification_response = gemini_model.generate_content(classification_prompt)
        product_category = classification_response.text.strip().lower()
        if product_category not in ["microwave", "washing_machine", "fridge"]:
            return "I can only answer questions about microwaves, washing machines, or fridges. Please be more specific."
    
    except google_exceptions.ResourceExhausted as e:
        print(f"RATE LIMIT ERROR: {e}")
        return "Sorry, I've hit my daily usage limit for the API. Please try again tomorrow or upgrade to a paid plan."
        
    except Exception as e:
        print(f"Error in classification: {e}")
        return "I had trouble understanding which product you're asking about. Please rephrase."

    print(f"--> Detected product: {product_category}")

    # --- Step 2: Create a query vector ---
    query_vector = embedding_model.encode(query).tolist()

    # --- Step 3: Search Pinecone with a metadata filter ---
    search_results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True,
        filter={"product_type": product_category}
    )

    # --- Step 4: Build the context ---
    context = ""
    if search_results['matches']:
        for match in search_results['matches']:
            context += match['metadata']['text'] + "\n---\n"
    else:
        return f"I couldn't find any specific information about that in my {product_category} documents."

    # --- Step 5: Generate the final answer ---
    prompt = f"""
    You are a helpful AI assistant for troubleshooting {product_category} issues.
    Answer the user's question based ONLY on the following context.
    If the context doesn't contain enough information, say "I don't have enough information in my documents to answer that."
    CONTEXT:
    {context}
    USER'S QUESTION:
    {query}
    ANSWER:
    """
    final_response = gemini_model.generate_content(prompt)
    return final_response.text


# --- 3. FLASK ROUTES ---

@app.route('/')
def home():
    """Renders the main chat page."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Handles the user's question and returns the AI's answer."""
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    print(f"Received query: {user_query}")
    answer = get_answer(user_query)
    
    # Return the answer as a JSON object
    return jsonify({"answer": answer})

# --- 4. RUN THE APP ---
if __name__ == '__main__':
    # The host='0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)