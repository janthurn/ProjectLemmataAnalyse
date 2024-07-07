import re
import os
import requests
import time
import logging

from typing import List
from bs4 import BeautifulSoup

from Settings import (HEADERS, BASE_URL, CITIES, RADIUS, SEARCH_PAGES_UNTIL, STELLENANGEBOTE_REGEX)
from ExtractData import extract, extract_to_dict
from AnalyseKorpus import read_and_cleanup_file
from Jsonstyle import write_json_file


def search_stellenangebote(city: str, page: int):

    url = f"{BASE_URL}/in-{city}?radius={RADIUS}&page={page}"
    try:
        response = requests.get(url, headers=HEADERS)
        quelltext = response.text
    except Exception as e:
        quelltext = ""
        logging.error(f"Fehler beim request der url: {url}\n\n {e}")

    return re.findall(STELLENANGEBOTE_REGEX, quelltext)


def searching_matches() -> List:

    matches = []
    for city in CITIES:
        for page in range(1, SEARCH_PAGES_UNTIL+1):
            logging.info(f"Suche Stellenangebote in {city} auf Seite {page}")
            found_urls = search_stellenangebote(city=city, page=page)
            matches.extend(found_urls)
            time.sleep(10)
    return matches


def skim_matches(matches: List) -> List:
    logging.info(f"Starting with {len(matches)} matches.")
    skimmed_matches = list(set(matches))
    logging.info(f"Of these {len(skimmed_matches)} matches were unique.")
    return skimmed_matches


def analyse_offers(matches: List, file_name: str):
        
    for i, url in enumerate(matches):
        offer_url = "https://www.stepstone.de" + url
        sourcecode_offer = requests.get(offer_url, headers=HEADERS).text
        soup_offer = BeautifulSoup(sourcecode_offer, "lxml")
        extract(soup_offer, file_name=file_name)

        # als Zusatz für die Übersichtlichkeit (und weil es cool ist :) ) wird der Fortschritt der Quelltextextraktion aus den Anzeigen dargestellt
        print(str(i) + "/" + str(len(matches)) + "---" + format((i / len(matches)) * 100, '.2f') + "%")


def analyse_offers_alternativ(matches: List, file_name: str):

    all_offers = {}
    for i, url in enumerate(matches):
        offer_url = "https://www.stepstone.de" + url
        sourcecode_offer = requests.get(offer_url, headers=HEADERS).text
        soup_offer = BeautifulSoup(sourcecode_offer, "lxml")
        content = extract_to_dict(soup_offer_text=soup_offer)
        all_offers.update({offer_url: content})

    write_json_file(file_name=file_name, data=all_offers)


if __name__ == '__main__':

    all_matches = searching_matches()
    unique_matches = skim_matches(matches=all_matches)

    # open file for adding data later on
    file_name = "rohtext.txt"
    file_name_filtered = "Würzburg.txt"

    # Anna Style
    text = open(file_name, "w", encoding='utf-16-le')
    text.close()
    analyse_offers(unique_matches, file_name=file_name)
    read_and_cleanup_file(file_name_raw=file_name, file_name_filtered=file_name_filtered)

    # json-file
    json_file_name_roh = "rohtext.json"
    analyse_offers_alternativ(matches=unique_matches, file_name=json_file_name_roh)
