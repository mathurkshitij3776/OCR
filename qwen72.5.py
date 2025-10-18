

import ollama
import base64
import fitz  
from pathlib import Path
from PIL import Image
import io
import os



MODEL_NAME = 'qwen2.5vl:7b'

OCR_PROMPT = "This is a page from a document. Extract all the text from this image exactly as it appears. Do not summarize, translate, or add any commentary. The text may be in Hindi or English."
MIN_TEXT_LENGTH_FOR_DIGITAL = 50 
INPUT_FILE = r"C:\Users\kodec\Downloads\OCRDOC\DOC\file23.pdf"
OUTPUT_FILE = r"C:\Users\kodec\Downloads\qwen7b2.5\file23_extracted.txt"

# --- SCRIPT ---

def image_to_base64(image_path_or_object):
    try:
        if isinstance(image_path_or_object, (str, Path)):
             img = Image.open(image_path_or_object)
        else: 
            img = image_path_or_object

        with io.BytesIO() as buffer:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(buffer, format="JPEG")
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def process_image_with_ollama(client, image_base64):
    
    if not image_base64:
        return ""
    try:
        print("    >> Sending image to Vision Model for OCR...")
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'user',
                    'content': OCR_PROMPT,
                    'images': [image_base64]
                }
            ]
        )
        print("    >> Received response from model.")
        return response['message']['content']
    except Exception as e:
        print(f"    >> An error occurred while communicating with Ollama: {e}")
        return f"[ERROR: Could not process image. Details: {e}]"

def main():

    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    if not input_path.exists():
        print(f"Error: Input file not found at '{INPUT_FILE}'")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Processing document: {input_path.name}")
    
    try:
        client = ollama.Client()
        client.show(MODEL_NAME) 
        print(f"Successfully connected to Ollama and found model '{MODEL_NAME}'.")
    except Exception as e:
        print(f"Fatal Error: Could not connect to Ollama or find model '{MODEL_NAME}'.")
        print(f"Details: {e}")
        return

    extracted_texts = []
    
    if input_path.suffix.lower() == '.pdf':
        print("PDF detected. Using optimized hybrid extraction method...")
        try:
            doc = fitz.open(input_path)
            if not doc.page_count:
                print("Error: PDF file is empty or corrupted.")
                doc.close()
                return

            for i, page in enumerate(doc):
                page_num = i + 1
                print(f"- Processing page {page_num}/{doc.page_count}...")
                
                # Step 1: Attempt fast digital extraction
                digital_text = page.get_text().strip()
                
                # Step 2: Decide whether to use digital text or fallback to OCR
                if len(digital_text) > MIN_TEXT_LENGTH_FOR_DIGITAL:
                    print(f"  > Digital text found. Using fast extraction.")
                    page_text = digital_text
                else:
                    print(f"  > Digital text is minimal. Assuming scanned page.")
                    pix = page.get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img_base64 = image_to_base64(img)
                    page_text = process_image_with_ollama(client, img_base64)

                extracted_texts.append(f"--- TEXT FROM PAGE {page_num} ---\n{page_text}\n\n")

            doc.close()
        except Exception as e:
            print(f"Error during PDF processing: {e}")
            return
            
   
    elif input_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        print("Image file detected. Processing with Vision Model...")
        img_base64 = image_to_base64(input_path)
        page_text = process_image_with_ollama(client, img_base64)
        extracted_texts.append(f"--- TEXT FROM IMAGE ---\n{page_text}\n\n")
    
    else:
        print(f"Error: Unsupported file type '{input_path.suffix}'.")
        return

 
    print("Combining extracted text...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(extracted_texts)
    
    print("-" * 50)
    print("Processing complete!")
    print(f"Output saved to: {output_path}")
    print("-" * 50)


if __name__ == "__main__":
    main()



