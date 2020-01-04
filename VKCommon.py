from urllib.parse import urlencode
import requests
import time

# Variables which need to work with API VK
params = {"access_token": "", "v": 5.103, "timeout": 10}

COUNT_REQUESTS_EXECUTE = 25


def get_token(filename):
    """

    (string) -> string

    Get token - read from file filename

    """

    token = ""
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            token = file.readline().strip()
            if len(token) > 0:
                params["access_token"] = token
            else:
                print(f"Не удалось прочитать токен. Расместите токен в файле \"{filename}\" в папке с программой.")
    except FileNotFoundError:
        print(f"Файл \"{filename}\" не найден.")
    return token


def get_field_of_response(response_json, field_name):
    """

    (dict, string) -> tuple(int, string, object or None)

    Get value by key=field_name from dictionary

    """

    try:
        value = (0, "", response_json[field_name])
        return value
    except KeyError:
        try:
            error_info = response_json['error']
            value = (error_info['error_code'], error_info['error_msg'], None)
            return value
        except KeyError:
            # print(f"Не найден ключ \"{field_name}\" в ответе {response_json}")
            value = (-1, 'Не найден ключ', None)
            return value
    except TypeError:
        print(f"Входные данные типа {type(response_json)}, а ожидается тип {type(dict())}")
        value = (-1, "Ошибка входных данных", None)
        return value


def get_count_items_by_response(response):
    """

    (object response) -> tuple(int, string, int, list or None)

    Get fields count and items from response

    """

    response_json = response.json()

    error, msg, info_json = get_field_of_response(response_json, 'response')
    if error != 0:
        value = (error, msg, 0, None)
        return value

    error, msg, count = get_field_of_response(info_json, 'count')
    if error != 0:
        value = (error, msg, 0, None)
        return value

    error, msg, items = get_field_of_response(info_json, 'items')
    if error != 0:
        value = (error, msg, 0, None)
        return value
    value = (0, "", count, items)
    return value


def request_get(method, params_):
    """

    (string, dict) -> tuple(int, string, object response or None)

    Function execute request to API VK by method api vk and param and get response

    """
    response = None
    try:
        while True:
            response = requests.get(method, params_)
            response_json = response.json()
            error_info = response_json.get('error')
            if error_info is not None:
                if error_info['error_code'] != 6:
                    value = (error_info['error_code'], error_info['error_msg'], None)
                    return value
                else:
                    continue
            else:
                print('.', end='')
                # because error appeared: many requests per second
                time.sleep(1/10)
                break
    except requests.exceptions.ReadTimeout:
        time.sleep(1)
        request_get(method, params_)
    except Exception as e:
        value = (-1, e, None)
        return value

    value = (0, "", response)
    return value


# Function write list objects(groups) to json file
def write_groups_to_file(filename, groups):
    """

    (string, list of objects) -> None

    Function writes list of groups to json file

    """

    try:
        with open(filename, 'w', encoding="utf-8") as outfile:
            import json
            group_dict = dict()
            group_list = list()
            for group in groups:
                group_dict['name'] = group.get_name()
                group_dict['gid'] = group.group_id
                group_dict['members_count'] = group.members_count
                group_list.append(group_dict.copy())
            json.dump(group_list, outfile, ensure_ascii=False)

        return 0
    except FileNotFoundError:
        print(f"Файл \"{filename}\" не найден.")
    except PermissionError:
        print(f"Не хватает прав для создания файла \"{filename}\".")
    except Exception as e:
        print(f"Ошибка записи в файл \"{filename}\".")
        print(e)


def auth():
    """

    (None) -> None

    Function helps getting token for work with api VK

    """

    oauth_url = "https://oauth.vk.com/authorize"
    oauth_params = {
        "client_id": 7238600,
        "display": "page",
        "response_type": "token",
        "scope": "status, friends"
    }

    print("?".join(
      (oauth_url, urlencode(oauth_params)))
    )


# Print information about result list of groups
def print_groups(caption, groups):
    """

    (User, list(Group, Group, ..., Group)) -> None

    Function prints list objects-groups

    """

    print("")
    if len(groups) > 0:
        print(caption)
        for index, g in enumerate(groups, 1):
            print(f"{index}. \"{g.group_name}\"")


def test_id(sid):
    """

    (string) -> boolean

    Function test string = id or not

    """

    sid = sid.strip()
    if len(sid) == 0:
        return False

    if 'a' <= sid[0].lower() <= 'z' or sid[0] == '_':
        for i in range(1, len(sid)):
            if not ('a' <= sid[i].lower() <= 'z' or '0' <= sid[i].lower() <= '9' or sid[i].lower() == '_'):
                return False
        return True
    else:
        return False
