"""
jobs/utils.py
-------------
Extracts plain text from an uploaded resume file (PDF or DOCX) so we can
store it in Resume.raw_text and reuse the existing AI-matching pipeline
without changing matcher.py at all.
"""
import os
import pdfplumber
import docx


def extract_text_from_file(uploaded_file):
    """
    uploaded_file: a Django UploadedFile object (from request.FILES).
    Returns extracted plain text as a string.
    """
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    if ext == ".pdf":
        text_parts = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    elif ext == ".docx":
        document = docx.Document(uploaded_file)
        return "\n".join(p.text for p in document.paragraphs)

    else:
        raise ValueError("Unsupported file type. Upload a .pdf or .docx file.")