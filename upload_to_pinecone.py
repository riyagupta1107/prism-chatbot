import os
import pandas as pd
from pinecone import Pinecone
from getpass import getpass

# --- 1. Initialize Connection to Pinecone ---
print("Initializing connection to Pinecone...")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY") or getpass("Enter your Pinecone API Key: ")
pc = Pinecone(api_key=PINECONE_API_KEY)

# --- 2. Define Index Details and Connect ---
index_name = "samsung-support-index" # A more general name is better
index_host = "https://microwave-support-lhzdo1l.svc.aped-4627-b74a.pinecone.io" # This host is tied to the old name, that's okay

print(f"Connecting to index '{index_name}' with host: {index_host}")
index = pc.Index(host=index_host)
print("\nConnected to index. Initial stats:")
print(index.describe_index_stats())

# --- NEW: List of all embedding files to upload ---
files_to_upload = [
    'microwave_embeddings.parquet',
    'washing_machine_embeddings.parquet',
    'fridge_embeddings.parquet'
]

# --- 3. Loop Through Each File and Upsert Data ---
for file_path in files_to_upload:
    print(f"\n--- Processing file: {file_path} ---")
    
    # 3.1. Load and Prepare Data
    try:
        df = pd.read_parquet(file_path)
        # Convert dataframe to a list of dictionaries
        records = df.to_dict('records')
        print(f"Loaded {len(records)} records.")
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Skipping.")
        continue # Skip to the next file

    # 3.2. Upsert (Upload) the Data in Batches
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        vectors_to_upsert = []
        for record in batch:
            # Create a unique ID for each vector
            # Including product_type makes IDs even more unique
            vector_id = f"{record['product_type']}-{record['source']}-{record['chunk_id']}"
            
            # Prepare the metadata, now including the crucial 'product_type'
            metadata = {
                "text": record['text'],
                "source": record['source'],
                "product_type": record['product_type'] # <-- THE KEY CHANGE!
            }
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": record['embedding'],
                "metadata": metadata
            })
        
        # Upsert the batch to Pinecone
        index.upsert(vectors=vectors_to_upsert)
        print(f"Upserted batch {i//batch_size + 1} of {(len(records)-1)//batch_size + 1}")

print("\n--- All files have been processed and uploaded! ---")
print("Final index stats:")
print(index.describe_index_stats())