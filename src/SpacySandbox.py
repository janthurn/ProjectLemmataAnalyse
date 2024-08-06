import spacy
import time
from typing import Dict, List, Union, Optional

from PandasWithSpacy import lemmata_einlesen
from FileHandler import FileHandler

file_handler = FileHandler()


def analysiere_zeitpunkt(stadt_name:str):

    conversion = {"2": "Ende April", "3": "Ende Mai"}

    if "_" not in stadt_name:
        return "Ende März"

    zeitpunkt = stadt_name.split("_")[1]
    return conversion.get(zeitpunkt)

def get_content(search_dir: str):
    file_list = file_handler.find_relevant_files(search_dir)
    file_contents = []  # type: List[Dict]

    for file in file_list:

        # get file data
        file_json_new = str(file).replace(".txt", ".json")
        stadt_name = file.stem
        zeitpunkt = analysiere_zeitpunkt(stadt_name)
        file_handler.convert_txt_to_json(
            file_name_txt=str(file),
            file_name_json=file_json_new
        )
        data_dict = file_handler.read_json_file(file_json_new)

        file_contents.append(data_dict)

    return file_contents


def testing_reading_from_txt_to_json():
    files_content = get_content(search_dir="C:\\Repos\\ProjektAnna\\res")
    nlp = spacy.load(name="de_core_news_sm")

    for content in files_content:
        for job_id, job_text in enumerate(content.values()):
            doc = nlp(text=job_text)
            if job_id == 0:
                token_list = [token for token in doc]
                print(token_list)
                for token in token_list:
                    if str(token) != str(token.lemma_):
                        print(f"{str(token):>20} : {str(token.lemma_)}")

def text_lesbar_machen(input_txt: str):

    satz_liste = input_txt.split(". ")
    satz_liste = [satz.strip() for satz in satz_liste]
    return ".\n".join(satz_liste)

def nlp_vs_in_analyse(model, file_path):

    # Datenvorbereitung
    print(f"\nAnalysing {file_path}\n")
    content = file_handler.read_txt_file(file_path=file_path)
    content_upper = content.upper()
    doc = model(text=content)
    token_list = [token for token in doc]
    token_text_list = [token.text for token in doc]
    token_lemma_list = [token.lemma_ for token in doc]
    print(f"Es wurden {len(token_lemma_list)} Token in der Anzeige gefunden.")

    # lemmata laut Literatur
    lemmata_file = "../res/german_gender_bias_word_list.CSV"
    codierte_lemmata = lemmata_einlesen(lemmata_file)


    # Text analyse
    all_lemma = []
    for idx, row in codierte_lemmata.iterrows():
        all_lemma.append(row["wordstem"].upper())

    header = f"     coded_word     |   coded_word(upper)   |    search_word     | DIFF | found via 'in' | found via 'nlp text' | found via 'nlp lemmata' "
    print(header)
    for idx, row in codierte_lemmata.iterrows():
        coded_word = row["wordstem"]
        coded_word_upper = coded_word.upper()

        search_word = coded_word_upper
        result_string = f"{coded_word:>20}|{coded_word_upper:>23}|{search_word:>20}"

        # standard analyse ohne nlp per string 'in'
        found_via_in = False
        if search_word in content_upper:
            found_via_in = True

        # nlp text liste
        found_via_text_list = False
        if search_word in [text.upper() for text in token_text_list]:
            found_via_text_list = True

        # nlp lemma liste
        found_via_lemma_list = False
        if search_word in [text.upper() for text in token_lemma_list]:
            found_via_lemma_list = True

        # method compare
        diff_in_methods = False
        if (found_via_in and not found_via_lemma_list) or (found_via_lemma_list and not found_via_in):
            diff_in_methods = True

        final_string = f"{result_string}| {diff_in_methods} |   {str(found_via_in):>10}   |   {str(found_via_text_list):>16}   |   {str(found_via_lemma_list):>13} \n"
        if diff_in_methods:
            print(final_string)

    text_lesbar = text_lesbar_machen(content)
    print(text_lesbar)

    return len(token_lemma_list)


def analyse_single_words_in_detail(model, word: str, lemma_liste: list[str]):
    """
    special analysis made for connected words in german
    :param model:
    :param word:
    :return:
    """
    word_options = []

    # build all "word options" from the front and back
    for i, letter in enumerate(word):
        if i == 0:
            continue
        word_options.append(word[:i])
        word_options.append(word[i:])

    all_options_str = " ".join(word_options)
    doc = model(text=all_options_str)
    token_lemma_list = [token.lemma_ for token in doc]
    found_lemmata = []
    for lemma in lemma_liste:
        if lemma in [text.upper() for text in token_lemma_list]:
            found_lemmata.append(lemma)

    return found_lemmata


def advanced_nlp_analysis(model, text: str, lemmata_info: list):

    doc = model(text=text)
    token_text_list = [token.text.upper() for token in doc]
    text_lemmata = []
    for idx, word in enumerate(token_text_list):
        if idx % 50 == 0:
            print(f"Token {idx} / {len(token_text_list)}")
        text_lemmata.append(
            (word, analyse_single_words_in_detail(model=model, word=word, lemma_liste=lemmata_info))
        )
    return text_lemmata

def eliminate_false_positives():
    pass


if __name__ == '__main__':
    nlp = spacy.load(name="de_core_news_sm")

    all_lemmata = ['ANGENEHM', 'ANSPRECHEND', 'ANSTÄNDIG', 'ANVERTRAUEN', 'AUFMERKSAM', 'BEHUTSAM', 'BESCHEIDEN',
                   'DIPLOMATISCH',
                   'EHRLICH', 'EINFÜHLSAM', 'EMOTIONAL', 'EMPATHISCH', 'ENGAGIERT', 'FAIR', 'FAMILIÄR', 'FEINFÜHLIG',
                   'FREUNDLICH',
                   'FRÖHLICH', 'FÜRSORGLICH', 'GEPFLEGT', 'GEWISSENHAFT', 'HERZLICH', 'HILFSBEREIT', 'HÖFLICH', 'KIND',
                   'KOMMUNIKATIV', 'KONTAKTFREUDIG', 'KOOPERATIV', 'KREATIV', 'KUNDENORIENTIERT', 'LIEBEVOLL', 'LOYAL',
                   'MITFÜHLEND',
                   'MOTIVIEREND', 'RESPEKTVOLL', 'RÜCKSICHTSVOLL', 'SENSIBEL', 'SERVICEORIENTIERT', 'SORGFÄLTIG',
                   'SOZIALKOMPETENZ',
                   'TEAMBILDEND', 'TOLERANT', 'UNTERSTÜTZEND', 'VERANTWORTUNGSVOLL', 'VERLÄSSLICH', 'VERSTÄNDNISVOLL',
                   'VERTRAUEN',
                   'WARMHERZIG', 'ZUVERLÄSSIG', 'ZWISCHENMENSCHLICH', 'ABENTEUERLUSTIGE', 'ABSOLUT', 'AGGRESSIV',
                   'AKTIV',
                   'AMBITIONIERT', 'ANALYSIEREND', 'AUFGABENORIENTIERT', 'AUFSTIEGSMÖGLICHKEIT', 'AUTONOMIE',
                   'AUTORITÄT', 'CLEVER',
                   'DIREKT', 'DOMINANT', 'DURCHSETZUNGSSTARK', 'EHRGEIZIG', 'EIGENINITIATIV', 'ENTSCHEIDUNGSFREUDIG',
                   'ENTSCHLOSSEN',
                   'ERGEBNISORIENTIERT', 'FÜHRUNGSKOMPETENT', 'HARTNÄCKIG', 'HERAUSFORDERND', 'HIERARCHISCH',
                   'INDIVIDUELL',
                   'INTELLEKTUELL', 'KARRIEREORIENTIERT', 'KOMPETITIV', 'KOOPERATIONSFÄHIG', 'LEIDENSCHAFTLICH',
                   'LEISTUNGSSTARK',
                   'LOGISCH', 'LÖSUNGSORIENTIERT', 'MEINUNGSSTARK', 'MUTIG', 'OBJEKTIV', 'OFFENSIV', 'PRAGMATISCH',
                   'RATIONAL',
                   'SELBSTÄNDIG', 'SELBSTBEWUSST', 'SELBSTSICHER', 'SELBSTÄNDIG', 'SYMPATHISCH', 'ÜBERDURCHSCHNITTLICH',
                   'ÜBERZEUGEND', 'UNABHÄNGIG', 'UNTERNEHMERISCH', 'VERHANDLUNGSSICHER', 'WETTBEWERBSORIENTIERT',
                   'WILLENSSTARK',
                   'ZIELSTREBIG'
    ]

    # nlp vs simple string analysis method
    files = ["C:\\Repos\\ProjektAnna\\res\Anzeige.txt", "C:\\Repos\\ProjektAnna\\res\Anzeige_nlp_modified.txt"]
    token_number = 0
    for file in files:
        token_number = nlp_vs_in_analyse(model=nlp, file_path=file)

    # Analyse time test
    start = time.time()
    for i in range(0,token_number):
        result = analyse_single_words_in_detail(model=nlp, word="Attraktive".upper(), lemma_liste=all_lemmata)
        if i % 50 ==0:
            print(f"Token {i} / {token_number}: Attraktive - {result}")

    end = time.time()

    print(f"Loop through {token_number} token in {end - start} s")

    # run advanced analysis
    print(f"\nrun advanced analysis on {files[0]} content")
    text = file_handler.read_txt_file(files[0])
    start = time.time()
    result = advanced_nlp_analysis(
        model=nlp,
        text=text,
        lemmata_info=all_lemmata
    )
    found_lemmata = []
    for token_text, lemmata in result:
        if len(lemmata) > 0:
            found_lemmata.append(lemmata)
    end = time.time()
    print(f"Found the following lemmata {found_lemmata} in {end - start} s")
