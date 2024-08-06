import spacy
import time
from typing import List, Union
from pandas import DataFrame

from FileHandler import FileHandler
from LemmataTable import LemmataTable


class TextAnalyserNLP:

    def __init__(self):

        self._nlp = None
        self.nlp_model_name = "de_core_news_sm"

    @property
    def nlp(self):
        if self._nlp is None:
            self._nlp = spacy.load(name=self.nlp_model_name)

        return self._nlp

    def _filter_list_by_word_length(self, word_list: List, lemma_table: LemmataTable):
        """
        reduces the list by filtering all word options, which are shorter,
        then the minimal lemma length or longer then the maximal length
        :param word_list:
        :param lemma_table:
        :return:
        """
        filtered_list_minimal = filter(lambda word: len(word)>= lemma_table.minimal_lemma_length, word_list)
        filtered_list_final = filter(lambda word: len(word) <= lemma_table.maximal_lemma_length, filtered_list_minimal)

        return filtered_list_final

    def build_lemmata_list_for_single_word(self, word: str, lemma_table: LemmataTable) -> List:
        """
        build a list of lemmata for a word by creating 'word' from all letters
        This is helpful for connect german words i.e. 'zusammengesetzt'
         to find the word 'zusammen' and 'gesetzt' as words for later analysis
        :param word: word basis
        :param lemma_table: table of all viable lemmata
        :return:
        """
        word_options = []
        # build all "word options" from the front and back
        for i, letter in enumerate(word):
            if i == 0:
                continue
            word_options.append(word[:i])
            word_options.append(word[i:])

        word_options_red = self._filter_list_by_word_length(word_options, lemma_table)

        all_options_str = " ".join(word_options_red)
        doc = self.nlp(text=all_options_str)
        token_lemma_list = [token.lemma_ for token in doc]

        return token_lemma_list

    def _tag_element_object(self, obj: Union[str, List], lemma_table: LemmataTable):

        found_words = {}
        for lemmata in lemma_table.all_lemmata:
            if lemmata in obj:
                print(f"Found {lemmata}")
                words = found_words.get(lemma_table.get_word_coding(lemmata), [])
                words.append(lemmata)
                found_words.update({lemma_table.get_word_coding(lemmata): words})

        return found_words

    def tag_coded_words__text(self, text, lemma_table: LemmataTable):

        text = text.upper()
        found_words = self._tag_element_object(obj=text, lemma_table=lemma_table)
        return found_words

    def tag_coded_words__nlp_simple(self, text, lemma_table: LemmataTable):

        doc = self.nlp(text)
        lemma_liste = [token.lemma_ for token in doc]
        found_words = self._tag_element_object(obj=lemma_liste, lemma_table=lemma_table)
        return found_words

    def tag_coded_words__nlp_advanced(self, text, lemma_table: LemmataTable):

        # build text modell, build all new word option and ad them to the text
        doc = self.nlp(text)
        token_text_list = [token.text.upper() for token in doc]

        new_words = []
        for idx, word in enumerate(token_text_list):
            if idx % 50 == 0:
                print(f"Token {idx} / {len(token_text_list)}: {word}")
            new_words.extend(
                self.build_lemmata_list_for_single_word(word=word, lemma_table=lemma_table)
            )
        new_words_string = " ".join(new_words)
        updated_text = f"{text} {new_words_string}"

        # build new text modellstring and run analysis
        doc_adv = self.nlp(updated_text)
        lemma_liste_updated = [token.lemma_ for token in doc_adv]

        found_words = self._tag_element_object(obj=lemma_liste_updated, lemma_table=lemma_table)
        return found_words


if __name__ == '__main__':

    start = time.time()
    table = LemmataTable(file_path="../res/german_gender_bias_word_list.CSV")
    handler = FileHandler()
    text = handler.read_txt_file(file_path="C:\\Repos\\ProjektAnna\\res\Anzeige.txt")
    analyser = TextAnalyserNLP()

    f = analyser.tag_coded_words__nlp_advanced(text=text, lemma_table=table)
    end = time.time()
    print(f"Found the following lemmata {f} in {end - start} s")