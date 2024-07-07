import re
from typing import Dict, List

def _replace_html_tags(korpus: str) -> str:

    html_free_korpus = ""
    tags_to_remove = [
        "<p>", "</p>", "<strong>", "</strong>", "<ul>", "</ul>", "<li>", "</li>", "<em>", "</em>", "<br/>", "</a>",
        "<b>", "</b>", "<u>", "</u>", "<i>", "</i>"
    ]
    for html_tag in tags_to_remove:
        html_free_korpus = korpus.replace(html_tag, " ")
    html_free_korpus = re.sub(r'<a href=".*">', "", html_free_korpus)

    # Zwischenüberschriften-Tags entfernen
    html_free_korpus = re.sub(r'<h1>.*</h1>', "", html_free_korpus)

    return html_free_korpus


def _replace_special_characters(korpus: str):

    korpus_final = korpus.replace("   ", " ")
    while "  " in korpus:
        korpus_final = korpus_final.replace("  ", " ")

    replace_dict = {
        "\n": " ",
        "„": "\"",
        "“": "\"",
        "·": "-",
        "‑": "-",
        "’": "'",
        "…": "...",
        "\t": " "
        }
    for orig, replace_to in replace_dict.items():
        korpus_final = korpus_final.replace(orig, replace_to)

    korpus_final = re.sub(r'[^a-zA-Z0-9äöü.,;ß/()\[\]\-#\|&\*\+:ÖÄÜ?"!§$%&\\²³€\'\s]', "", korpus_final)
    return korpus_final


def read_and_cleanup_file(file_name_raw: str, file_name_filtered: str):

    text = open(file_name_raw, "r", encoding='utf-16-le')
    lines = text.readlines()

    korpus = "".join(lines)

    korpus = _replace_html_tags(korpus=korpus)
    korpus = _replace_special_characters(korpus)

    text = open(file_name_filtered, "w", encoding='utf-16-le')
    text.write(korpus)
    text.close()


class QualitivAnalysis:

    def __init__(self, file_name):

        self.file_name = file_name
        self.job_offers = {}        #type: Dict

    def _read_file(self):

        text = open(self.file_name, "r", encoding='utf-16-le')
        lines = text.readlines()
        full_text = "".join(lines).strip()
        job_list = full_text.split("##")
