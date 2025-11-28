import pdfplumber
import hashlib
from typing import Tuple

def extract_text_from_pdf(file_path: str) -> Tuple[str, str]:
    """
    Extracts text from a PDF file and computes its SHA256 hash.
    Returns: (full_text, file_hash)
    """
    sha256_hash = hashlib.sha256()
    full_text = []

    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    file_hash = sha256_hash.hexdigest()

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    
    return "\n".join(full_text), file_hash
