from typing import List, Optional, Dict
from bs4 import BeautifulSoup

from Settings import VALUES
import typeguard


def _extract_from_offer(soup_offer_text, attr_name: str = "data-at", attr_value: str = "") -> Optional[str]:

    result = soup_offer_text.find(attrs={attr_name: attr_value})

    if result is None:
        return None
    elif result.span is None:
        return None
    else:
        return str(result.contents[0])

@typeguard.typechecked()
def _extract_content(soup_offer_text) -> Optional[List[str], Dict]:

    texts = []
    content_dict = {}
    for value, key_word in VALUES.items():
        content = _extract_from_offer(soup_offer_text=soup_offer_text, attr_value=key_word)
        if content is None:
            content = ""
        texts.append(content)
        content_dict.update({value, content})

    return texts, content_dict


def extract(soup_offer_text, file_name: str):

    title = _extract_from_offer(soup_offer_text=soup_offer_text, attr_value="header-job-title" )
    if title is None:
        return

    texts,_ = _extract_content(soup_offer_text)

    text = open(file_name, "a", encoding='utf-16-le')
    text.write("\n" + "## ")
    text.write("///" + title + "///" + "\n")
    for x in texts:

        text.write(x + "\n")
    text.close()


def extract_to_dict(soup_offer_text) -> Optional[Dict]:

    title = _extract_from_offer(soup_offer_text=soup_offer_text, attr_value="header-job-title" )
    if title is None:
        return

    _, content = _extract_content(soup_offer_text)
    return content