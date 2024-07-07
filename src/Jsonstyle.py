import json
import requests

from typing import Dict, List


def write_json_file(file_name: str, data: dict):

    with open(file_name, "w") as fp:
        json.dump(data, fp, indent=4)


def read_json_file(file_name: str) -> Dict:

    json_file = open(file_name, "r")
    data = json.load(json_file)

    return data

