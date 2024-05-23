import os
import shutil
import base64
import traceback

import pdfplumber
from docx import Document


def read_docx(file_path):
    try:
        doc = Document(file_path)
        content = [paragraph.text for paragraph in doc.paragraphs]
        return "\n".join(content)
    except Exception as e:
        return f"Error reading DOCX file: {e}"


def read_pdf(file_path):
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
                text += page_text
                text += "\n\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF file: {e}"


def read_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading TXT file: {e}"


def read_file(folder_path, patent_name=None, file_name=None):
    if file_name:
        file_path = os.path.join(folder_path, patent_name, file_name)
    elif patent_name:
        file_path = os.path.join(folder_path, patent_name)
    else:
        file_path = os.path.join(folder_path)

    if os.path.basename(file_path).startswith("~$"):
        return "Skipping temporary file."

    if file_path.endswith(".docx"):
        return read_docx(file_path)
    elif file_path.endswith(".pdf"):
        return read_pdf(file_path)
    elif file_path.endswith(".txt") and file_name:
        return read_txt(file_path)
    else:
        raise ValueError("Unsupported file format or missing file name for .txt file")


def encode_image(file):
    """Encodes an image file to base64."""
    return base64.b64encode(file).decode("utf-8")


def save_text_to_file(folder_path, text, patent_name, file_name):
    try:
        file_path = os.path.join(folder_path, patent_name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(os.path.join(file_path, file_name), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as err:
        print(err, traceback.format_exc())


# Function to remove folder
def remove_folder(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            print(f"Error: {path} : {e.strerror}")
    else:
        print(f"Folder '{path}' does not exist.")
