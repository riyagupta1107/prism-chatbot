import os
import json
import pdfplumber

def extract_text_from_pdf(pdf_path):
    """Opens a PDF and extracts all the text from it using pdfplumber."""
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n\n"
    except Exception as e:
        print(f"Could not read {pdf_path}: {e}")
    return full_text

def process_product_data(raw_data_folder, processed_data_folder, product_name):
    """
    Extracts text from all .pdf, .jsonl, and .txt files in a raw data folder
    and saves the combined content to a single .txt file for that product.
    """
    print(f"--- Processing raw data for: {product_name.upper()} ---")
    
    product_output_dir = os.path.join(processed_data_folder, product_name)
    os.makedirs(product_output_dir, exist_ok=True)
    
    all_text_content = ""
    file_count = 0
    
    for filename in os.listdir(raw_data_folder):
        file_path = os.path.join(raw_data_folder, filename)
        file_ext = filename.lower().split('.')[-1]
        
        print(f"Processing {filename}...")
        file_count += 1
        
        if file_ext == "pdf":
            all_text_content += extract_text_from_pdf(file_path)
            
        elif file_ext == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                all_text_content += f.read() + "\n\n"
                
        elif file_ext == "jsonl":
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # Each line in a .jsonl file is a separate JSON object
                        data = json.loads(line)
                        # Convert each JSON object into a clean text string
                        for key, value in data.items():
                            all_text_content += f"{key.replace('_', ' ').title()}: {value}\n"
                        all_text_content += "\n---\n\n" # Separator between entries
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode a line in {filename}: {line.strip()}")

    if file_count > 0 and all_text_content.strip():
        # Save all the extracted text into one consolidated file for the product
        output_filename = f"{product_name}_content.txt"
        output_path = os.path.join(product_output_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(all_text_content)
        print(f"Successfully created '{output_path}' from {file_count} source file(s).")
    else:
        print(f"No processable files (.pdf, .jsonl, .txt) found or no text extracted in '{raw_data_folder}'.")
        
    print(f"Finished processing for {product_name.upper()}.\n")

# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    PROCESSED_TEXT_BASE_FOLDER = "processed_text"

    # Map your raw data folders to the product names
    product_map = {
        "microwave_data": "microwave",
        "wm_data": "washing_machine",
        "fridge_data": "fridge"
    }
    
    for raw_folder, product_name in product_map.items():
        if os.path.exists(raw_folder):
            process_product_data(raw_folder, PROCESSED_TEXT_BASE_FOLDER, product_name)
        else:
            print(f"Warning: Raw data folder not found at '{raw_folder}'. Skipping {product_name}.")
            
    print("--- All raw data has been processed! ---")