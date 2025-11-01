import os
from PyPDF2 import PdfReader

def parse_pdf(file_path: str) -> str:
    """
    Parse PDF and return plain text.
    """
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text
