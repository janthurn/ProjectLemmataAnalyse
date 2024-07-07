import json
import logging
import os

from typing import Dict, List, Union
from pathlib import Path


class FileHandler:

    def __init__(self):
        pass

    def write_json_file(self, file_name: str, data: dict):
        with open(file_name, "w") as fp:
            json.dump(data, fp, indent=4)

    def read_json_file(self, file_name: Union[str, Path]) -> Dict:
        """
        get the
        :param file_name:
        :return:
        """
        json_file = open(str(file_name), "r")
        data = json.load(json_file)

        return data

    def _is_file_relevant(self, file_path: Union[str, Path]) -> bool:

        _path = None
        if isinstance(file_path, str):
            try:
                _path = Path(file_path)
            except ValueError as e:
                logging.info(f"The given path: {file_path} could not be transformed to a Path.\n {e}")
                return False

        if not _path.is_file():
            return False

        if _path.suffix not in [".txt"]:
            return False
        return True

    def find_relevant_files(self, base_path: str) -> List[Path]:
        """
        Suchen nach web crawling text-Dateien
        :param such_pfad:
        :return:
        """
        found_files = []
        for (root, dirs, files) in os.walk(base_path):
            for file in files:
                file_path = Path(f"{root}/{file}")
                if file_path.is_file() and Path(file).suffix in ['.txt']:
                    logging.info(f"{file_path} ist eine interessante Datei!!1111")
                    found_files.append(file_path)
                else:
                    logging.info(f"{Path(root) / Path(file)} Brauchen wir nicht")

        return found_files

    def convert_txt_to_json(self, file_name_txt, file_name_json):
        """
        web-crawling text-Dateien in Jsons umwandeln
        :return:
        """

        content_dict = {}
        with open(file_name_txt, encoding='utf-16-le') as f:
            content = f.read()
            for line in content.split("##"):
                s = line.strip()
                if len(s) == 0:
                    continue
                elemente = s.split("///")
                content_dict.update({elemente[1]: elemente[2]})

        self.write_json_file(file_name_json, content_dict)