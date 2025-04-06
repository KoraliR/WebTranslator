import time
import jwt
import json
import requests

def make_jwt_token(path_auth_key, jwt_key_name):
# Чтение закрытого ключа из JSON-файла
    with open(path_auth_key, 'r') as f: #json-file
        obj = f.read()
        obj = json.loads(obj)
        private_key = obj['private_key']
        key_id = obj['id']
        service_account_id = obj['service_account_id']

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600
    }

# Формирование JWT.
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

# Запись ключа в файл
    with open(jwt_key_name, 'w') as j: #text-file
        j.write(encoded_token)


# Вывод в консоль
    print(encoded_token)
    return encoded_token
def make_aim_token(enc_jwt_key, aim_token_name):
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "jwt": enc_jwt_key
    }

    # Выполняем POST-запрос
    response = requests.post(url, headers=headers, json=data)

    # Проверяем статус и выводим результат
    if response.status_code == 200:
        print("Ответ от сервера:", response.json())
        with open(aim_token_name, "w", encoding="utf-8") as json_file: #json file
            json.dump(response.json(), json_file, ensure_ascii=False, indent=4)
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")

# t = start_key() Выполняются последовательно
# make_req(t)
def delete_aim_token(aim_token):
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens:revoke"
    headers={
        'Content-Type': 'application/json',
        "Authorization": f'Bearer {aim_token}'
    }
    data = {
        "iamToken": f"{aim_token}"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")

