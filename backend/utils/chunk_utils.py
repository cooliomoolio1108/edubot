import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_slide_by_slide(file_path):
    doc = fitz.open(file_path)  # Open the PDF file
    slides = []
    for page_num, page in enumerate(doc):  # Iterate through each page (slide)
        text = page.get_text()  # Extract text from the slide
        slides.append({
            "slide_number": page_num + 1,  # Slide number (1-based index)
            "text": text
        })
    return slides

def chunk_text(text, chunk_size=300, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]  # Split by paragraphs, lines, and words
    )
    chunks = text_splitter.split_text(text)
    return chunks