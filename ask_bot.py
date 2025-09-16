import os
import pinecone
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from getpass import getpass

# --- 1. Initialize Connections ---
print("Initializing connections...")

# Initialize Pinecone
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY") or getpass("Enter your Pinecone API Key: ")
# This host URL is for your specific index.
index_host = "https://microwave-support-lhzdo1l.svc.aped-4627-b74a.pinecone.io" 

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host=index_host)

# Initialize Google Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or getpass("Enter your Google AI API Key: ")
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the Embedding Model
print("Loading embedding model...")
# This model creates the vectors for searching.
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded. System is ready.")


# --- 2. Define the Upgraded RAG Function ---

def get_answer(query):
    """
    Takes a user query, classifies the product, retrieves filtered context 
    from Pinecone, and generates an answer using Google Gemini.
    """
    
    # --- NEW: Step 1 - Classify the product category ---
    classification_prompt = f"""
    Based on the user's question, identify which of the following product categories it belongs to: 
    microwave, washing_machine, fridge.
    Return only the single category name and nothing else.

    Question: "{query}"
    Category:
    """
    try:
        classification_response = gemini_model.generate_content(classification_prompt)
        product_category = classification_response.text.strip().lower()
        
        # A quick check to ensure the response is a valid category
        if product_category not in ["microwave", "washing_machine", "fridge"]:
             return "I'm sorry, I can only answer questions about microwaves, washing machines, or fridges. Please clarify which product you're asking about."

    except Exception as e:
        print(f"Error during classification: {e}")
        return "I had trouble understanding which product you're asking about. Please try rephrasing your question."

    print(f"--> Detected product: {product_category}")
    
    # --- Step 2: Create a query vector ---
    query_vector = model.encode(query).tolist()

    # --- Step 3: Search Pinecone with a metadata filter ---
    print("Searching for relevant documents...")
    search_results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True,
        # THIS IS THE KEY: Filter the search by the detected product type
        filter={"product_type": product_category}
    )

    # --- Step 4: Build the context ---
    context = ""
    if search_results['matches']:
        for match in search_results['matches']:
            context += match['metadata']['text'] + "\n---\n"
    else:
        # Handle case where no documents were found for that filter
        return f"I'm sorry, I couldn't find any specific information about that in my {product_category} documents."
    
    # --- Step 5: Generate the final answer ---
    # The prompt is now dynamic and changes based on the detected product
    prompt = f"""
    You are a helpful AI assistant for troubleshooting {product_category} issues.
    Answer the user's question based ONLY on the following context.
    If the context doesn't contain enough information to answer, say "I'm sorry, I don't have enough information in my documents to answer that question."

    CONTEXT:
    {context}

    USER'S QUESTION:
    {query}

    ANSWER:
    """
    
    print("Generating answer...")
    final_response = gemini_model.generate_content(prompt)
    
    return final_response.text


# --- 3. Run the Chatbot ---

if __name__ == "__main__":
    print("\nWelcome to the Samsung Product Support Bot! Type 'exit' to quit.")
    while True:
        user_query = input("\nPlease ask your question about a microwave, fridge, or washing machine: ")
        if user_query.lower() == 'exit':
            break
        
        answer = get_answer(user_query)
        print("\nANSWER:")
        print(answer)