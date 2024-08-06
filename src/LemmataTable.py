import pandas

from typing import List, Union, Optional
from pandas import DataFrame
from pathlib import Path


class LemmataTable:

    SEX_CODING_SETTINGS = {
        "female": "female-coded",
        "male": "male-coded",
    }
    TABLE_HEADER = {
        "word": "wordstem",
        "category": "coding",
        "lemmata_header": "Lemmata"
    }

    def __init__(self, file_path: Union[str, Path]):

        self._file_path = file_path
        self._data = None
        self._min_length = None
        self._max_length = None

    def _lemmata_transformation(self, value):
        return value.upper()

    @property
    def data(self) -> Optional[DataFrame]:
        if self._data is None:
            try:
                if Path(self._file_path).suffix in [".csv", ".CSV"]:
                    self._data = pandas.read_csv(self._file_path)
                    self._data[self.TABLE_HEADER.get("lemmata_header")] = self._data.wordstem.apply(
                        self._lemmata_transformation
                    )
            except Exception as e:
                print(f"Error while reading lemma file {self._file_path}: \n\n{e}\n\n")

        return self._data

    @property
    def minimal_lemma_length(self):
        if self._min_length is None:
            self._min_length = len(min(self.all_lemmata, key=len))

        return self._min_length

    @property
    def maximal_lemma_length(self):
        if self._max_length is None:
            self._max_length = len(max(self.all_lemmata, key=len))

        return self._max_length

    def _get_data_row(self, search_word: str, search_column: str = TABLE_HEADER.get("lemmata_header")):
        for idx, row in self.data.iterrows():
            if row[search_column] == search_word:
                return row
        return None

    @property
    def all_lemmata(self):
        for idx, row in self.data.iterrows():
            yield row[self.TABLE_HEADER.get("lemmata_header")]

    def is_lemmata_in_table(self, word: str, capslock: bool = True) -> bool:

        if capslock:
            word = word.upper()
        rows = self._get_data_row(search_word=word)
        if rows is None:
            return False
        return True

    def get_word_coding(self, word: str, capslock: bool = True) -> Optional[str]:

        if capslock:
            word = word.upper()
        rows = self._get_data_row(search_word=word)
        if rows is None:
            return None

        return rows[self.TABLE_HEADER.get("category")]



if __name__ == '__main__':

    table = LemmataTable(file_path="../res/german_gender_bias_word_list.CSV")
    row = table._get_data_row(search_word="herausfordernd")

    print(table.is_lemmata_in_table("herausfordernd"))
    print(table.get_word_coding("herausfordernd"))
    print(table.is_lemmata_in_table("Papa"))
    print(table.minimal_lemma_length)
    print(table.maximal_lemma_length)