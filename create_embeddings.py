import os
import json
from sentence_transformers import SentenceTransformer
import pandas as pd

# Define the folder with our processed text files
OUTPUT_FOLDER = "processed_text"

def chunk_text(text):
    """Splits text into smaller chunks based on paragraphs."""
    paragraphs = text.split("\n\n")
    chunks = [p.strip() for p in paragraphs if p.strip()]
    return chunks

# --- 1. Load the text chunks from Step 1 ---
print("Loading text chunks...")
all_chunks = []
for filename in os.listdir(OUTPUT_FOLDER):
    if filename.endswith(".txt"):
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
            file_chunks = chunk_text(text_content)
            
            # Add metadata to each chunk
            for i, chunk in enumerate(file_chunks):
                chunk_metadata = {
                    "source": filename,
                    "chunk_id": i,
                    "text": chunk
                }
                all_chunks.append(chunk_metadata)

print(f"Loaded {len(all_chunks)} chunks.")

# --- 2. Load the Embedding Model ---
# This will download the model from the internet the first time you run it.
print("Loading the embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.")

# --- 3. Create the Embeddings for Each Chunk ---
print("Creating embeddings for all text chunks...")

# Extract just the text from our list of dictionaries
texts_to_embed = [chunk['text'] for chunk in all_chunks]

# The model.encode() function does all the magic.
# It takes a list of texts and returns a list of vectors.
embeddings = model.encode(texts_to_embed, show_progress_bar=True)

print(f"Embeddings created successfully! The shape of our embeddings is: {embeddings.shape}")
# The output will be something like (number_of_chunks, 384)
# This means we have a vector of 384 numbers for each chunk.

# --- 4. Store the Text and its Vector Together ---
print("Saving the chunks and their embeddings...")

# Create a pandas DataFrame for easy handling
df = pd.DataFrame(all_chunks)
# Add the embeddings as a new column
# We convert the numpy array to a list so it can be easily saved.
df['embedding'] = embeddings.tolist()

# Save to a file. A Parquet file is efficient for this kind of data.
df.to_parquet('microwave_embeddings.parquet')

print("\nStep 2 is complete! You now have a file named 'microwave_embeddings.parquet' with all your data and its vector representation.")