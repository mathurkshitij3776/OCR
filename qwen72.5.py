# import ollama
# import base64
# import fitz  # PyMuPDF
# from pathlib import Path
# from PIL import Image
# import io
# import os

# # --- CONFIGURATION ---
# # The model name as you have it in Ollama.
# MODEL_NAME = 'qwen2.5vl:7b'
# # The prompt to instruct the model.
# OCR_PROMPT = "This is a page from a document. Extract all the text from this image exactly as it appears. Do not summarize, translate, or add any commentary. The text may be in Hindi or English."

# # --- USER INPUTS ---
# # The full path to the document you want to process (.pdf, .png, .jpg).
# INPUT_FILE = r"C:\Users\kodec\Downloads\OCRDOC\DOC\file4.pdf"
# # The full path where the final extracted text file will be saved.
# OUTPUT_FILE = r"C:\Users\kodec\Downloads\qwen7b2.5\file4_extracted.txt"

# # --- SCRIPT ---

# def image_to_base64(image_path):
#     """Converts an image file to a base64 encoded string."""
#     try:
#         with Image.open(image_path) as img:
#             with io.BytesIO() as buffer:
#                 # Convert RGBA to RGB if necessary (e.g., for PNGs)
#                 if img.mode == 'RGBA':
#                     img = img.convert('RGB')
#                 img.save(buffer, format="JPEG")
#                 return base64.b64encode(buffer.getvalue()).decode('utf-8')
#     except Exception as e:
#         print(f"Error encoding image {image_path}: {e}")
#         return None

# def process_image_with_ollama(client, image_base64):
#     """Sends a base64 image to the Ollama model and returns the text response."""
#     if not image_base64:
#         return ""
#     try:
#         print("  Sending image to model...")
#         response = client.chat(
#             model=MODEL_NAME,
#             messages=[
#                 {
#                     'role': 'user',
#                     'content': OCR_PROMPT,
#                     'images': [image_base64]
#                 }
#             ]
#         )
#         print("  Received response from model.")
#         return response['message']['content']
#     except Exception as e:
#         print(f"  An error occurred while communicating with Ollama: {e}")
#         return f"[ERROR: Could not process image. Details: {e}]"

# def main():
#     """Main function to process the document."""
#     input_path = Path(INPUT_FILE)
#     output_path = Path(OUTPUT_FILE)

#     if not input_path.exists():
#         print(f"Error: Input file not found at '{INPUT_FILE}'")
#         return

#     # Ensure the output directory exists
#     output_path.parent.mkdir(parents=True, exist_ok=True)

#     print(f"Processing document: {input_path.name}")
    
#     # Initialize Ollama client
#     try:
#         client = ollama.Client()
#         # Check if the model is available
#         client.show(MODEL_NAME) 
#         print(f"Successfully connected to Ollama and found model '{MODEL_NAME}'.")
#     except Exception as e:
#         print(f"Fatal Error: Could not connect to Ollama or find model '{MODEL_NAME}'.")
#         print("Please make sure Ollama is running and you have pulled the model by running:")
#         print(f"  ollama run {MODEL_NAME}")
#         print(f"Details: {e}")
#         return

#     extracted_texts = []
#     temp_image_paths = []
    
#     # --- PDF Processing ---
#     if input_path.suffix.lower() == '.pdf':
#         print("PDF detected. Converting pages to images...")
#         try:
#             doc = fitz.open(input_path)
#             if not doc.page_count:
#                 print("Error: PDF file is empty or corrupted.")
#                 doc.close()
#                 return

#             for i, page in enumerate(doc):
#                 print(f"- Converting page {i + 1}/{doc.page_count}...")
#                 pix = page.get_pixmap(dpi=200)  # Higher DPI for better quality
#                 temp_img_path = output_path.parent / f"temp_page_{i + 1}.jpg"
#                 pix.save(temp_img_path)
#                 temp_image_paths.append(temp_img_path)
#             doc.close()
#             print("PDF conversion complete.")
#         except Exception as e:
#             print(f"Error during PDF processing: {e}")
#             return
            
#     # --- Image Processing ---
#     elif input_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
#         print("Image file detected.")
#         temp_image_paths.append(input_path)
    
#     else:
#         print(f"Error: Unsupported file type '{input_path.suffix}'. Please provide a PDF or an image file.")
#         return

#     # --- Ollama OCR Processing ---
#     for i, img_path in enumerate(temp_image_paths):
#         print(f"Processing image {i + 1}/{len(temp_image_paths)} ('{img_path.name}')...")
#         img_base64 = image_to_base64(img_path)
#         page_text = process_image_with_ollama(client, img_base64)
#         extracted_texts.append(f"--- TEXT FROM PAGE {i + 1} ---\n{page_text}\n\n")

#     # --- Cleanup and Save ---
#     print("Combining extracted text...")
#     with open(output_path, 'w', encoding='utf-8') as f:
#         f.writelines(extracted_texts)

#     # Clean up temporary image files if they were created from a PDF
#     if input_path.suffix.lower() == '.pdf':
#         print("Cleaning up temporary images...")
#         for path in temp_image_paths:
#             try:
#                 os.remove(path)
#             except OSError as e:
#                 print(f"  Could not remove temp file {path}: {e}")
    
#     print("-" * 50)
#     print("Processing complete!")
#     print(f"Output saved to: {output_path}")
#     print("-" * 50)


# if __name__ == "__main__":
#     main()

# from pathlib import Path
# import base64
# from PIL import Image
# import fitz  # PyMuPDF
# import subprocess
# import io

# # ---------- CONFIG ----------
# INPUT_FILE = r"C:\Users\kodec\Downloads\OCRDOC\DOC\file4.pdf"  # PDF or image
# OUTPUT_FILE = Path(r"C:\Users\kodec\Downloads\qwen7b2.5\output.txt")
# OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# # ---------- HELPER FUNCTIONS ----------
# def image_to_base64(img: Image.Image) -> str:
#     buffered = io.BytesIO()
#     img.save(buffered, format="PNG")
#     return base64.b64encode(buffered.getvalue()).decode()

# def extract_images_from_pdf(pdf_path):
#     """Convert each PDF page to a PIL image"""
#     doc = fitz.open(pdf_path)
#     images = []
#     for page in doc:
#         pix = page.get_pixmap()
#         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#         images.append(img)
#     return images

# def extract_text_with_qwen_from_image(img: Image.Image):
#     """Send Base64 image to Qwen2.5-VL-7B via stdin"""
#     img_base64 = image_to_base64(img)
#     prompt = f"Extract all text from this image. Return as plain text.\n![image](data:image/png;base64,{img_base64})"
#     process = subprocess.Popen(
#         ["ollama", "run", "qwen2.5vl:7b", "--stdin"],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#     stdout, stderr = process.communicate(input=prompt)
#     if stderr:
#         print("Error:", stderr)
#     return stdout

# # ---------- MAIN ----------
# input_path = Path(INPUT_FILE)
# all_text = ""

# if input_path.suffix.lower() == ".pdf":
#     images = extract_images_from_pdf(input_path)
#     for i, img in enumerate(images, 1):
#         print(f"Processing page {i}...")
#         text = extract_text_with_qwen_from_image(img)
#         all_text += f"\n--- Page {i} ---\n{text}\n"
# elif input_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
#     img = Image.open(input_path)
#     all_text = extract_text_with_qwen_from_image(img)
# else:
#     raise ValueError("Unsupported file type. Use PDF or image.")

# # Save extracted text
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     f.write(all_text)

# print(f"Text extracted and saved to: {OUTPUT_FILE}")


import ollama
import base64
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import io
import os

# --- CONFIGURATION ---
# The model name as you have it in Ollama.
MODEL_NAME = 'qwen2.5vl:7b'
# The prompt to instruct the model.
OCR_PROMPT = "This is a page from a document. Extract all the text from this image exactly as it appears. Do not summarize, translate, or add any commentary. The text may be in Hindi or English."
# A threshold to decide if a page is scanned. If digital text extraction yields fewer characters than this, we assume it's an image.
MIN_TEXT_LENGTH_FOR_DIGITAL = 50 

# --- USER INPUTS ---
# The full path to the document you want to process (.pdf, .png, .jpg).
INPUT_FILE = r"C:\Users\kodec\Downloads\OCRDOC\DOC\file23.pdf"
# The full path where the final extracted text file will be saved.
OUTPUT_FILE = r"C:\Users\kodec\Downloads\qwen7b2.5\file23_extracted.txt"

# --- SCRIPT ---

def image_to_base64(image_path_or_object):
    """Converts a PIL Image object or an image file path to a base64 encoded string."""
    try:
        if isinstance(image_path_or_object, (str, Path)):
             img = Image.open(image_path_or_object)
        else: # Assumes it is a PIL Image object
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
    """Sends a base64 image to the Ollama model and returns the text response."""
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
    """Main function to process the document."""
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
    
    # --- PDF Processing (Optimized Hybrid Approach) ---
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
            
    # --- Standard Image Processing ---
    elif input_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        print("Image file detected. Processing with Vision Model...")
        img_base64 = image_to_base64(input_path)
        page_text = process_image_with_ollama(client, img_base64)
        extracted_texts.append(f"--- TEXT FROM IMAGE ---\n{page_text}\n\n")
    
    else:
        print(f"Error: Unsupported file type '{input_path.suffix}'.")
        return

    # --- Save Final Output ---
    print("Combining extracted text...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(extracted_texts)
    
    print("-" * 50)
    print("Processing complete!")
    print(f"Output saved to: {output_path}")
    print("-" * 50)


if __name__ == "__main__":
    main()



