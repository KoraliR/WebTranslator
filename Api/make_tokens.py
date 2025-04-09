import time
import jwt
import json
import requests
import os

def make_jwt_token(path_auth_key, jwt_key_name):
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

    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    with open(jwt_key_name, 'w') as j: #text-file
        j.write(encoded_token)


    return encoded_token
def make_aim_token(enc_jwt_key, aim_token_name):
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "jwt": enc_jwt_key
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
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

def delete_all_from_dir(dir_path):
    for file in os.listdir(dir_path):
        file_p = os.path.join(dir_path, file)
        try:
            if os.path.isfile(file_p):
                os.remove(file_p)
        except Exception as e:
            print(e)

def start_make_token(flag=False):
    DIR_PATH = os.path.join(os.getcwd(), "Api")
    if flag:
        path = os.path.join(os.getcwd(), "Api", "aim_tokens", "aim_token_trans.json")
        try:
            with open(path, "r") as f:
                obj = f.read()
                obj = json.loads(obj)
                aim_token = obj["iamToken"]
                delete_aim_token(aim_token)
        except Exception as e:
            print(e)
    delete_all_from_dir(os.path.join(DIR_PATH, "aim_tokens"))
    delete_all_from_dir(os.path.join(DIR_PATH, "jwt_tokens"))
    auth_path = os.path.join(DIR_PATH, "secret_keys_authr", "auth_key_trans.json")
    jwt_path = os.path.join(DIR_PATH, "jwt_tokens", "jwt_trans.txt")
    aim_path = os.path.join(DIR_PATH, "aim_tokens", "aim_token_trans.json")
    encoded_token = make_jwt_token(auth_path, jwt_path)
    make_aim_token(encoded_token, aim_path)
    try:
        with open(aim_path, "r") as f:
            obj = f.read()
            obj = json.loads(obj)
            expire_dateTime = obj["expiresAt"]
            return expire_dateTime
    except Exception as e:
        print(e)

