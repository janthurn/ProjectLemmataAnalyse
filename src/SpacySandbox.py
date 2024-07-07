import spacy

from FileHandler import FileHandler
from typing import Dict, List, Union, Optional


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


if __name__ == '__main__':

   files_content = get_content(search_dir= "C:\\Repos\\ProjektAnna\\res")
   nlp = spacy.load(name="de_core_news_sm")
   for content in files_content:
       for job_id, job_text in enumerate(content.values()):
            doc = nlp(text=job_text)
            if job_id ==0:
                token_list = [token for token in doc]
                print(token_list)
                for token in token_list:
                    if str(token) != str(token.lemma_):
                        print(f"{str(token):>20} : {str(token.lemma_)}")