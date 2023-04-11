import cv2
from pytesseract import image_to_string
import PyPDF2

def process_pdf(pdf_path):
    full_text = ""
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)
        for i in range(num_pages):
            page = reader.pages[i]
            text = page.extract_text()
            
            full_text += text
    return full_text

def process_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text = image_to_string(gray)
    return text