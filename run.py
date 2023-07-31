import os
import glob
from PyPDF2 import PdfReader
import argparse
from pprint import pprint


regex_year = r'\b\d{4}\b'
regex_page_range = r'\bpp\.\s*\d+-\d+\b'
regex_page_single = r'\bp\.\s*\d+\b'
regex_source = r'^\s*Source:\s*'
regex_name = r'^[^,]+'
regex_nb = r'\d+'



def extract_text_from_cover_page(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        if len(pdf_reader.pages) > 0:
            cover_page_text = pdf_reader.pages[0].extract_text()
            lines = cover_page_text.strip().split('\n')
            source_line = match_regex(lines)
            rename_file(source_line, pdf_path)

def rename_file(source_line, pdf_path):
    year = re.search(regex_year, source_line)
    page = re.search(regex_page_range, source_line) or re.search(regex_page_single, source_line)
    name = re.search(regex_name, source_line)

    numbers = re.findall(regex_nb, source_line)
    first_number = numbers[0]
    second_number = numbers[1]
    #vol = re.search(regex_word_bf_2_nb_pattern, source_line[:second_number_index])
    #sourcez = source_line[:second_number_index]
    #last_word= r'\b\w+\b'
    #vol = re.finditer(last_word, sourcez)
    #for match in vol:
    #    last_words = match.group()
    #if last_words != "H":
    new_name = name.group() + " " +first_number + "," +  "." + second_number + "_" +year.group() + "_" +page.group()
    print(new_name)

def match_regex(lines):
    for line in lines:
        if re.search(regex_year, line) and (re.search(regex_page_range, line) or re.search(regex_page_single, line)):
            if re.search(regex_source, line):
                return re.sub(regex_source, '', line)
            return line
    return None

def process_files_in_directory(directory_path):
    pdf_files = glob.glob(os.path.join(directory_path, '*.pdf'))
    for pdf_file in pdf_files:
        extract_text_from_cover_page(pdf_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files in a directory.")
    parser.add_argument("directory_path", help="Path to the directory containing PDF files.")
    args = parser.parse_args()
    process_files_in_directory(args.directory_path)


