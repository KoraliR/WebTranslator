import requests
import base64
import json


def make_request_translator(text, aim_token_trs, translator_folder): #Проверить работоспособность
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