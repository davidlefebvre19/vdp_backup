import os
import glob
from PyPDF2 import PdfReader
import argparse

def extract_text_from_cover_page(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        if len(pdf_reader.pages) > 0:
            cover_page_text = pdf_reader.pages[0].extract_text()
            lines = cover_page_text.strip().split('\n')
            source_line = next((line for line in lines if "Source:" in line), None)
            return source_line.strip() if source_line else None
        else:
            return None

def process_files_in_directory(directory_path):
    pdf_files = glob.glob(os.path.join(directory_path, '*.pdf'))

    for pdf_file in pdf_files:
        source_line = extract_text_from_cover_page(pdf_file)
        if source_line:
            print(source_line)
            print("--------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files in a directory.")
    parser.add_argument("directory_path", help="Path to the directory containing PDF files.")
    args = parser.parse_args()

    process_files_in_directory(args.directory_path)