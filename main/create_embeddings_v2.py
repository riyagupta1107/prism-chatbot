import os
import pandas as pd
from sentence_transformers import SentenceTransformer

# --- Configuration (doesn't change) ---
MAX_CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100
MODEL_NAME = 'all-MiniLM-L6-v2'

def smart_chunker(text, chunk_size, chunk_overlap):
    """A more robust function to split text into consistently sized chunks."""
    paragraphs = text.split("\n\n")
    final_chunks = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(p) <= chunk_size:
            final_chunks.append(p)
        else:
            start = 0
            while start < len(p):
                end = start + chunk_size
                chunk = p[start:end]
                final_chunks.append(chunk)
                start += (chunk_size - chunk_overlap)
    return final_chunks

# --- NEW: Reusable Main Function ---
def generate_embeddings_for_product(data_folder, product_name, model):
    """
    Loads text from a folder, chunks it, creates embeddings, and saves to a Parquet file.
    """
    print(f"--- Processing product: {product_name.upper()} ---")
    
    # 1. Load the text and create chunks with metadata
    all_chunks = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".txt"): # Assuming you have processed .txt files for each product
            file_path = os.path.join(data_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
                file_chunks = smart_chunker(text_content, MAX_CHUNK_SIZE, CHUNK_OVERLAP)
                
                # Add metadata, including the crucial product_type tag
                for i, chunk in enumerate(file_chunks):
                    chunk_metadata = {
                        "source": filename,
                        "chunk_id": i,
                        "text": chunk,
                        "product_type": product_name # <-- KEY ADDITION
                    }
                    all_chunks.append(chunk_metadata)
    
    if not all_chunks:
        print(f"Warning: No text files found in {data_folder}. Skipping.")
        return

    print(f"Created {len(all_chunks)} chunks for {product_name}.")

    # 2. Create the Embeddings for all chunks
    print(f"Creating embeddings for {product_name} chunks...")
    texts_to_embed = [chunk['text'] for chunk in all_chunks]
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    # 3. Store the Text and its Vector Together
    output_filename = f'{product_name}_embeddings.parquet'
    print(f"Saving chunks and embeddings to '{output_filename}'...")
    df = pd.DataFrame(all_chunks)
    df['embedding'] = embeddings.tolist()
    df.to_parquet(output_filename)
    
    print(f"Successfully created '{output_filename}'.\n")

# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    # First, make sure you have processed text files in these folders
    # (e.g., from a 'process_data.py' script)
    product_folders = {
        "microwave": "processed_text/microwave",
        "washing_machine": "processed_text/washing_machine",
        "fridge": "processed_text/fridge"
    }

    # Load the model once to be efficient
    print("Loading the embedding model...")
    embedding_model = SentenceTransformer(MODEL_NAME)
    print("Model loaded successfully.\n")

    # Loop through and process each product
    for name, folder in product_folders.items():
        if os.path.exists(folder):
            generate_embeddings_for_product(
                data_folder=folder, 
                product_name=name, 
                model=embedding_model
            )
        else:
            print(f"Warning: Data folder not found at '{folder}'. Skipping {name}.")

    print("--- All products processed! ---")