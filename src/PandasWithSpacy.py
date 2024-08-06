import pandas as pd
import numpy as np
import os
import spacy


from pathlib import Path
from pandas import DataFrame


from Jsonstyle import read_json_file, write_json_file

CODING_FILE_SETTINGS = {
    "female": "female-coded",
    "male": "male-coded",
    "word": "wordstem",
    "category": "coding"
}


def lemmata_einlesen(file_name) -> DataFrame:

    data = pd.read_csv(file_name)
    data.head()

    return data


def tag_coded_words(single_text, lemmata: DataFrame):
    single_text = single_text.upper()
    found_words = {}
    for idx, row in lemmata.iterrows():
        coded_word = row[CODING_FILE_SETTINGS.get("word")].upper()
        if coded_word in single_text:
            words = found_words.get(row[CODING_FILE_SETTINGS.get("category")], [])
            words.append(coded_word)
            found_words.update({row[CODING_FILE_SETTINGS.get("category")]: words})

    return found_words

 ######## NEW #####
def get_lemmata_by_spacy(single_text, nlp):
    """
    The nlp object creates a doc -object from a text, which can be analysed.
    The text split up be predefined rules (that can be changed) into a list of tokens (symbols and words)
    A doc object contains all tokens a gives the opportunity to analyse each token.
    The lemma_ attribute represents the natural lemma / wordstem of each word. i.e. zuverlässige -> zuverlässig
    :param single_text:
    :param nlp: natural language processing object
    :return:
    """
    doc = nlp(single_text)
    lemma_liste = [token.lemma_ for token in doc]
    lemma_string = "|".join(lemma_liste)

    return lemma_string

 ######## NEW #####
def tag_coded_lemmata(lemma_liste, lemmata: DataFrame):
    lemma_liste = lemma_liste.split("|")
    lemma_liste = [lemma.upper() for lemma in lemma_liste]
    found_words = {}
    for idx, row in lemmata.iterrows():
        coded_word = row[CODING_FILE_SETTINGS.get("word")].upper()
        if coded_word in lemma_liste:
            words = found_words.get(row[CODING_FILE_SETTINGS.get("category")], [])
            words.append(coded_word)
            found_words.update({row[CODING_FILE_SETTINGS.get("category")]: words})

    return found_words


def get_coded_words(data, coding: str):
    return data.get(CODING_FILE_SETTINGS.get(coding), [])


def count_coded_words(data, coding: str):
    return len(data.get(CODING_FILE_SETTINGS.get(coding), []))


def datei_format_umwandeln(file_name_txt, file_name_json):

    content_dict = {}
    with open(file_name_txt, encoding='utf-16-le') as f:
        content = f.read()
        for line in content.split("##"):
            s = line.strip()
            if len(s) == 0:
                continue
            elemente = s.split("///")
            content_dict.update({elemente[1]: elemente[2]})

    write_json_file(file_name_json, content_dict)


def analyse_with_dataframe(nlp, data: dict, lemmata: DataFrame, Ort: str, Zeitpunkt: str):

    # create and fill data frame
    df = pd.DataFrame([], columns=["Titel", "Text", "Form", "Ort", "Datum","Lemmata"])
    i = 0
    for title, text in data.items():
        df.loc[i] = [title, text, "", Ort, Zeitpunkt, []]
        i += 1
    #print(df)
    # filter and sort dataframe bei Job titel gender decriptor
    x = df.Titel
    if_list = [
        x.str.contains('.\*(\s|\))'),
        x.str.contains('\w*(\*|:|_)\s*in'),
        x.str.contains('\SIn'),
        x.str.contains('(\(|\s)(\w(\/|\||,)\s*\w(\/|\||,)\s*\w)|(\w(\/|\||,)\s*\w)(\)|\s)')
    ]
    then_list = [
        "Sternchen",
        "in-Form",
        "Binnenmajuskel",
        "MWD"
    ]
    df["Form"] = np.select(if_list, then_list, "Rest")
    df["Lemmata"] = df.Text.apply(tag_coded_words, lemmata=lemmata)
    df["Female_coded_words"] = df.Lemmata.apply(get_coded_words, coding="female")
    df["Male_coded_words"] = df.Lemmata.apply(get_coded_words, coding="male")
    df["Number_Female_coded_words"] = df.Lemmata.apply(count_coded_words, coding="female")
    df["Number_Male_coded_words"] = df.Lemmata.apply(count_coded_words, coding="male")

    ######## NEW #####
    df["LemmataSpaCy"] = df.Text.apply(get_lemmata_by_spacy, nlp=nlp)
    df["CodedLemmata_spaCy"] = df.LemmataSpaCy.apply(tag_coded_lemmata, lemmata=lemmata)
    df["Female_coded_words_spaCy"] = df.CodedLemmata_spaCy.apply(get_coded_words, coding="female")
    df["Male_coded_words_spaCy"] = df.CodedLemmata_spaCy.apply(get_coded_words, coding="male")
    df["Number_Female_coded_words_spaCy"] = df.CodedLemmata_spaCy.apply(count_coded_words, coding="female")
    df["Number_Male_coded_words_spaCy"] = df.CodedLemmata_spaCy.apply(count_coded_words, coding="male")

    #print(df)

    #df.Form.value_counts()

    #Gruppieren und Verteilung berechnen
    df.sort_values(by="Number_Female_coded_words")
    print(df.groupby("Form").Number_Female_coded_words.value_counts())
    print(df.groupby("Form").Number_Female_coded_words_spaCy.value_counts())
    #print(df.groupby("Form").Number_Male_coded_words.value_counts())

    return df


def texte_einlesen(such_pfad: str) -> list[Path]:
    """
    Suchen nach web crawling text-Dateien
    :param such_pfad:
    :return:
    """
    found_files = []
    for (root,dirs,files) in os.walk(such_pfad):
        for file in files:
            file_path = Path(f"{root}/{file}")
            if file_path.is_file() and Path(file).suffix in ['.txt']:
                print(f"{file_path} ist eine interessante Datei!!1111")
                found_files.append(file_path)
            else:
                print(f"{Path(root) /Path(file)} Brauchen wir nicht")

    return found_files


def analysiere_zeitpunkt(stadt_name:str):

    conversion = {"2": "Ende April", "3": "Ende Mai"}

    if "_" not in stadt_name:
        return "Ende März"

    zeitpunkt = stadt_name.split("_")[1]
    return conversion.get(zeitpunkt)


if __name__ == '__main__':

    # Files
    #alle_wichtigen_dateien = texte_einlesen("\\Users\\icq-k\\Desktop\\Masterarbeit\\Skriptteil\\Korpusdateien")
    alle_wichtigen_dateien = texte_einlesen("C:\\Repos\\ProjektAnna\\res")
    problem_dateien = []
    ######## NEW #####
    nlp = spacy.load(name="de_core_news_sm")

    for datei in alle_wichtigen_dateien:

        file_json_new = str(datei).replace(".txt", ".json")
        stadt_name = datei.stem

        zeitpunkt = analysiere_zeitpunkt(stadt_name)

        print(f"\n ------ Wir analysieren nun die Stellenanzeigen für die Stadt {stadt_name} ------\n")
        try:
            # read in data
            datei_format_umwandeln(
                file_name_txt=str(datei),
                file_name_json=file_json_new
            )
            data_dict = read_json_file(file_json_new)
            lemmata_file = "../res/german_gender_bias_word_list.CSV"
            info = lemmata_einlesen(lemmata_file)


            # run analysis
            ######## NEW #####
            data_frame = analyse_with_dataframe(
                nlp=nlp, data=data_dict, lemmata=info, Ort=stadt_name, Zeitpunkt=zeitpunkt
            )

            result_path = Path(f"{datei.parent}/{stadt_name}_result.csv")
            data_frame.to_csv(result_path, sep=",")
        except Exception as e:
            print(e)
            problem_dateien.append(datei)

    print("Folgende Dateien hatten ein Problem:")
    for d in problem_dateien:
        print(d)
