import os
import glob
import uuid

from PyPDF2 import PdfReader
import argparse
import shutil
import re
import time

regex_year = r'\b\d{4}\b'
regex_page_range = r'\bpp\.\s*\d+-\d+\b'
regex_page_single = r'\bp\.\s*\d+\b'
regex_source = r'^\s*Source:\s*'
regex_name = r'^[^,]+'
regex_nb = r'\d+'

def rename_file(source_line):
    year = re.search(regex_year, source_line)
    page = re.search(regex_page_range, source_line) or re.search(regex_page_single, source_line)
    name = re.search(regex_name, source_line)

    numbers = re.findall(regex_nb, source_line)
    first_number = numbers[0]
    second_number = numbers[1]

    new_name = name.group() + " " +first_number + "," +  " ." + second_number + "_" +year.group() + "_" +page.group()
    return new_name

def match_regex(lines):
    for line in lines:
        if re.search(regex_year, line) and (re.search(regex_page_range, line) or re.search(regex_page_single, line)):
            if re.search(regex_source, line):
                return re.sub(regex_source, '', line)
            return line
    return None

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
                source_line = match_regex(lines)
                newname = rename_file(source_line)
                return (0,newname) if source_line else (1, None)
            else:
                return (1, None)
        else:
            return None

def process_files_in_directory_monothread(directory_path):
    pdf_files = glob.glob(os.path.join(directory_path, '*.pdf'))
    non_jstor_dir = os.path.join(directory_path,'non_jstor_files')  # Nom du dossier pour stocker les fichiers non conformes

    if not os.path.exists(non_jstor_dir):
        os.makedirs(non_jstor_dir)

    total_files = len(pdf_files)-1
    print(f"Total number of PDF files in the directory: {total_files}")

    jstor = 0
    nonjstor = 0
    errors = 0

    # Loop à travers les fichiers
    for i,pdf_file in enumerate(pdf_files):
        print(f"Fichier pdf {i} sur {total_files} - jstor file : {jstor} - non jstor files : {nonjstor} - errors : {errors}")
        try :
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
                    jstor += 1
                elif source_line[0] == 1:
                    nonjstor+=1
                    print("NON JSTOR")
                    # Déplacer le fichier vers le dossier des fichiers non conformes
                    destination_file = os.path.join(non_jstor_dir, os.path.basename(pdf_file))
                    shutil.move(pdf_file, destination_file)
        except:
            errors+=1
            print("ERROR ON PDF - the program can still continue")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files in a directory.")
    parser.add_argument("directory_path", help="Path to the directory containing PDF files.")
    args = parser.parse_args()

    start = time.perf_counter()
    process_files_in_directory_monothread(args.directory_path)
    end = time.perf_counter()
    exec_time = end-start
    print("--------------------------------------------------------------------------------------")
    print(f"Opération terminée en {exec_time} secondes")
