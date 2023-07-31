from multiprocessing import Pool
import os
import glob
import uuid
import time

from PyPDF2 import PdfReader
import argparse
import shutil


def is_JSTOR(cover_page_text):
    return "JSTOR" in cover_page_text


def extract_text_from_cover_page(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        if len(pdf_reader.pages) > 0:
            cover_page_text = pdf_reader.pages[0].extract_text()
            if is_JSTOR(cover_page_text):
                # Recherche de source
                lines = cover_page_text.strip().split('\n')
                source_line = next((line for line in lines if "Source:" in line), None)
                return (0, source_line.strip()) if source_line else None
            else:
                return (1, None)
        else:
            return None


def process_pdf(pdf_file):
    non_jstor_dir = os.path.join(directory_path,
                                 'non_jstor_files')  # Nom du dossier pour stocker les fichiers non conformes
    try:
        # Vérifier si le pdf viens de jstore ou pas, si oui, extract source
        source_line = extract_text_from_cover_page(pdf_file)
        if source_line != None:
            if source_line[0] == 0:
                print(f"JSTOR FILE : {source_line[1]}")
                file_name = os.path.basename(pdf_file)
                file_name_without_extension = os.path.splitext(file_name)[0]
                unique_id = str(uuid.uuid4())[:8]  # Utiliser les 8 premiers caractères de l'ID unique
                new_file_name = f"{source_line[1]}_{unique_id}.pdf"
                new_file_path = os.path.join(directory_path, new_file_name)
                os.rename(pdf_file, new_file_path)
            elif source_line[0] == 1:
                print("NON JSTOR")
                # Déplacer le fichier vers le dossier des fichiers non conformes
                destination_file = os.path.join(non_jstor_dir, os.path.basename(pdf_file))
                shutil.move(pdf_file, destination_file)
    except:
        print("ERROR ON PDF - the program can still continue")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files in a directory.")
    parser.add_argument("directory_path", help="Path to the directory containing PDF files.")
    args = parser.parse_args()

    directory_path = args.directory_path
    pdf_files = glob.glob(os.path.join(directory_path, '*.pdf'))

    non_jstor_dir = os.path.join(directory_path, 'non_jstor_files')
    if not os.path.exists(non_jstor_dir):
        os.makedirs(non_jstor_dir)

    total_files = len(pdf_files)
    print(f"Total number of PDF files in the directory: {total_files}")

    start = time.perf_counter()
    # Using multiprocessing Pool
    with Pool() as p:
        p.map(process_pdf, pdf_files)
    end = time.perf_counter()
    print(f"took {end-start}")
