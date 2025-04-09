import requests
import base64
import json
import os


def get_aim_from_file():
    path = os.path.join(os.getcwd(), "Api", "aim_tokens", "aim_token_trans.json")
    try:
        with open(path, "r") as f:
            obj = f.read()
            obj = json.loads(obj)
            aim_token = obj["iamToken"]
        return aim_token
    except Exception as e:
        print(e)

def get_folderId_from_file():
    path = os.path.join(os.getcwd(), "Api", "secret_keys_authr", "folders_id.json")
    try:
        with open(path, "r") as f:
            obj = f.read()
            obj = json.loads(obj)
            folder_id = obj["translation"]
        return folder_id
    except Exception as e:
        print(e)

def make_request_translator(text): #Проверить работоспособность
    aim_token_trs = get_aim_from_file()
    translator_folder = get_folderId_from_file()
    body = {
        "targetLanguageCode": "ru",
        "texts": text,
        "folderId": translator_folder,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {aim_token_trs}"
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )
    translated_text = response.json()
    translated_text = translated_text.get("translations")[0]["text"]
    return translated_text

def make_request_vision(photo_base64, mime_type, aim_token_vsn, vision_folder, ): #на вход фото в байтах, выход - json еще надо обработать
    data = {"mimeType": mime_type,
            "languageCodes": "en", #проверить работоспособность!
            "content": photo_base64}
    url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer {:s}".format(aim_token_vsn),
               "x-folder-id": vision_folder,
               "x-data-logging-enabled": "true"}
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    result = response.json()
    return result