from urllib.parse import urlencode
import requests
import time

# Variables which need to work with API VK
token = "73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1"
params = {"access_token": token, "v": 5.103}

# Each api request prints symbol
process_show = False
symbol_process = '.'
count_symbol_process = 0

# Pause between api requests
dalay_in_sec = 1/3

# Max count of members of group which will be analized
max_count_members_group = 1000

# Max count of groups of user which will be analized
max_count_groups_by_user = 100

# Variable used for accumulate error statistics
error_stat = {}

msg_success = 'Успешное завершение'
msg_input_error = 'Ошибка входных данных'
msg_type_error = 'Ошибка типов'


def get_field_of_response(response_json, field_name):
  """

  (dict, string) -> tuple(int, string, object or None)

  Get value by key=field_name from dictionary

  """

  try:
    return (0, msg_success, response_json[field_name])
  except KeyError:
    try:
      error_info = response_json['error']
      return (error_info['error_code'], error_info['error_msg'], None)
    except KeyError:
      print(f"Не найден ключ \"{field_name}\" в ответе {response_json}")
      return (-1, 'Не найден ключ', None)
  except TypeError:
    print(f"Входные данные типа {type(response_json)}, а ожидается тип {type(dict())}")
    return (-1, msg_input_error, None)
  except Exception as e:
    try:
      error_info = response_json['error']
      return (error_info['error_code'], error_info['error_msg'], None)
    except KeyError:
      print(f"Не найден ключ \"error\" в ответе {response_json}")
      return (-1, 'Не найден ключ \"error\"', None)


def get_count_items_by_response(response):
  """

  (object response) -> tuple(int, string, int, list or None)

  Get fields count and items from response

  """

  response_json = response.json()

  error, msg, info_json = get_field_of_response(response_json, 'response')
  if error != 0:
    return (error, msg, 0, None)

  error, msg, count = get_field_of_response(info_json, 'count')
  if error != 0:
    return (error, msg, 0, None)

  error, msg, items = get_field_of_response(info_json, 'items')
  if error != 0:
    return (error, msg, 0, None)

  return (0, msg_success, count, items)

def request_get(method, params):
  """

  (string, dict) -> tuple(int, string, object response or None)

  Function execute request to API VK by method api vk and params and get response

  """
  global count_symbol_process

  try:
    response = requests.get(method, params)
    if process_show:
      if count_symbol_process >= 100:
        print('')
        count_symbol_process = 0
      print(symbol_process, end='')
      count_symbol_process += 1
    # because error appeared: many requests per second
    time.sleep(dalay_in_sec)
  except Exception as e:
    print(e)
    error_info = response['error']
    return (error_info['error_code'], error_info['error_msg'], None)

  return (0, msg_success, response)

# Function write list objects(groups) to json file
def write_groups_to_jsonfile(filename, groups):
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
        group_dict['name'] = group.name
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


class User:
  """

  Class describe user VK

  """



  # Initialiazation class
  def __init__(self, userid_string):
    """

    (None, string) -> object User or None

    Function of initialization of class User

    """

    try:
      self.user_id = int(userid_string)
    except ValueError:
      #Convert from nickname to user_id
      error, msg, userid = self.get_id(userid_string)
      if error != 0:
        self.error = {'error': error, 'msg': msg}
        return

    self.count_friends = 0

    error, msg, fio = self.get_fio()
    if error != 0:
      print(f"Аккаунт ВК с id = {userid} не определен.")
      self.error = {'error': error, 'msg': msg}
      return

    self.error = {'error': 0, 'msg': msg_success}

  # Get list of friends of user if didn't it
  def get_friends_if_need(self):
    """

    (None) -> tuple(int, string, list or None)

    Function get list of user's friends

    """

    if self.count_friends <= 0:
      self.get_id_friends()

  # Override operation "&"
  def __and__(self, other):
    """

    (object User) -> tuple(int, string, list or None)

    Function overrides operation "&" between objects of User and gets common friends in list of objects of User

    """

    return self.get_common_friends(other)

  # Print instance of class
  def __str__(self):
    """

    (None) -> string

    Function overrides function "print" for object User

    """

    return f"https://vk.com/id{self.user_id}"

  # Get user_id by nickname of user VK
  def get_id(self, nickname):
    """

    (None) -> (int, string, int)

    Function gets id of user by nickname

    """

    params["user_ids"] = nickname
    error, msg, response = request_get("https://api.vk.com/method/users.get", params)
    if error != 0:
      return (error, msg, None)

    error, msg, info_json_list = get_field_of_response(response.json(), 'response')
    if error != 0:
      return (error, msg, None)

    if len(info_json_list) <= 0:
      return (-1, 'Пустой ответ', None)

    info_json = info_json_list[0]

    error, msg, self.user_id = get_field_of_response(info_json, 'id')
    if error != 0 or self.user_id == 'DELETED':
      return (error, msg, None)

    return (0, msg_success, self.user_id)

  # Get fio = "last_name first_name" of user
  def get_fio(self):
    """

    (None) -> str

    Function gets fio of user VK

    """

    if 'self.last_name' in locals() and 'self.first_name' in locals():
      return (0, msg_success, f"{self.last_name} {self.first_name}")

    params_here = params.copy()
    params_here["user_ids"] = self.user_id

    error, msg, response = request_get('https://api.vk.com/method/users.get', params_here)
    if error != 0:
      return (error, msg, None)

    response_json = response.json()
    error, msg, info_json_list = get_field_of_response(response_json, 'response')
    if error != 0:
      return (error, msg, None)

    if len(info_json_list) <= 0:
      return (-1, 'Пустой ответ', None)

    info_json = info_json_list[0]

    error, msg, self.last_name = get_field_of_response(info_json, 'last_name')
    if error != 0 or self.last_name == 'DELETED':
      return (error, msg, None)

    error, msg, self.first_name = get_field_of_response(info_json, 'first_name')
    if error != 0 or self.first_name == 'DELETED':
      return (error, msg, None)

    return (0, msg_success, f"{self.last_name} {self.first_name}")

  # Get status of user
  def get_status(self):
    """

    (None) -> string

    Function gets status of user VK

    """

    if 'self.status' in locals():
      return (0, msg_success, self.status)

    params_here = params.copy()
    params_here["user_id"] = self.user_id

    error, msg, response = request_get('https://api.vk.com/method/status.get', params_here)
    if error != 0:
      return (error, msg, None)

    error, msg, info_json = self.get_field_of_response(response.json(), 'response')
    if error != 0:
      return (error, msg, None)

    error, msg, self.status = self.get_field_of_response(info_json, 'text')
    if error != 0:
      return (error, msg, None)

    return (0, msg_success, self.status)

  # Get list of friends of user
  def get_id_friends(self):
    """

    (None) -> tuple(int, string, list or None)

    Function gets list of id friends of user VK: list(int, int, ..., int)

    """

    if 'self.friends' in locals():
      return (0, msg_success, self.friends)

    params_here = params.copy()
    params_here["user_id"] = self.user_id

    error, msg, response = request_get('https://api.vk.com/method/friends.get', params_here)
    if error != 0:
      return (error, msg, None)

    error, msg, count, items = get_count_items_by_response(response)
    if error != 0:
      return (error, msg, None)

    # self.count_friends = count_items[0]
    # self.friends = count_items[1]
    self.count_friends = count
    self.friends = items

    return (0, msg_success, self.friends)

  # Get list of groups of user
  def get_id_groups(self):
    """

    (None) -> list

    Function gets list of id groups of user VK: list(int, int, ..., int)

    """

    if 'self.groups' in locals():
      return (0, msg_success, self.groups)

    params_here = params.copy()
    params_here["user_id"] = self.user_id
    params_here["count"] = 1000

    error, msg, response = request_get('https://api.vk.com/method/groups.get', params_here)
    if error != 0:
      return (error, msg, None)

    error, msg, count, items = get_count_items_by_response(response)
    if error != 0:
      return (error, msg, None)

    # self.count_groups = count_items[0]
    # self.groups = count_items[1]
    self.count_groups = count
    self.groups = items

    return (0, msg_success, self.groups)

  # Get list of common friends of user=self and user=other
  def get_common_friends(self, other):
    """

    (object User) -> tuple(int, string, list or None)

    Function gets common friends in list of objects of User

    """

    if not isinstance(other, User):
      print(f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
      raise ValueError

    # Convertions to sets from lists
    error, msg, id_friends = self.get_id_friends()
    if error != 0:
      return (error, msg, None)

    error, msg, other_id_friends = other.get_id_friends()
    if error != 0:
      return (error, msg, None)

    self_friends = set(id_friends)
    other_friends = set(other_id_friends)

    # Getting common friends equals intersection of sets
    common_friends_list = list(self_friends.intersection(other_friends))

    common_friends = []
    for user_id in common_friends_list:
      user_friend = User(user_id)
      common_friends.append(user_friend)

    return (0, msg_success, common_friends)

  # Getting groups of user, members which not are friends of user
  def get_spy_groups(self):
    """

    (None) -> list(object Group, object Group, ..., object Group) or None

    Function gets groups of user, members which not are friends of user

    """

    global error_stat

    error, msg, id_groups = self.get_id_groups()
    if error != 0:
      add_error(error, msg)
      return

    spy_groups = []

    # Get list of friends
    error, msg, user_friends = self.get_id_friends()
    if error != 0:
      add_error(error, msg)
      return

    for index, group_id in enumerate(id_groups[:max_count_groups_by_user:1], 1):
      g = Group(group_id)
      error, msg, count_members, id_members = g.get_id_members()
      if error != 0:
        add_error(error, msg)
        continue

      error, msg, friends_members = g.get_userid_who_member(user_friends)
      if error != 0:
        add_error(error, msg)
        continue

      if len(friends_members) == 0:
        g.get_name()
        spy_groups.append(g)

    return spy_groups

class Group():
  """

  Class describe group VK

  """

  # Initialiazation class
  def __init__(self, group_id):
    """

    (None, int) -> object Group or None

    Function of initialization of class Group

    """

    self.group_id = group_id
    self.members_count = 0

  # Get list of members of group if didn't it
  def get_members_if_need(self):
    """

    (None) -> tuple(int, string, list(int, int, ..., int) or None)

    Function get list of group's members

    """

    if self.members_count <= 0:
      return self.get_id_members()
    else:
      return (0, msg_success, self.members_count, self.members)

  # Detect a status of user
  def get_name(self):
    """

    (None) -> str

    Function gets name of group VK

    """

    if 'self.name' in locals():
      return (0, msg_success, self.name)

    params_here = params.copy()
    params_here["group_ids"] = self.group_id
    params_here["fields"] = "name"

    error, msg, response = request_get('https://api.vk.com/method/groups.getById', params_here)
    if error != 0:
      return (error, msg, None)

    response_json = response.json()
    error, msg, info_json_list = get_field_of_response(response_json, 'response')
    if error != 0:
      return (error, msg, None)

    info_json = info_json_list[0]

    error, msg, self.name = get_field_of_response(info_json, 'name')
    if error != 0:
      return (error, msg, None)

    return (0, msg_success, self.name)

  # Get list of members of group
  def get_id_members(self):
    """

    (None) -> list(int, int, ..., int)

    Function gets list of id members of group VK

    """

    if 'self.members' in locals():
      return (0, msg_success, self.members_count, self.members)

    params_here = params.copy()
    params_here['group_id'] = self.group_id

    items_acumulate = []
    counter = 0
    while counter < max_count_members_group:
      params_here['offset'] = counter
      error, msg, response = request_get('https://api.vk.com/method/groups.getMembers', params_here)
      if error != 0:
        return (error, msg, 0, None)

      error, msg, count, items = get_count_items_by_response(response)
      if error != 0:
        return (error, msg, 0, None)

      items_acumulate += items
      counter += 1000

      if len(items) < 1000:
        break

    self.members_count = count
    self.members = items_acumulate
    error, msg, group_name = self.get_name()
    if error != 0:
      return (error, msg, 0, None)

    print(f" группа \"{group_name}\" обработано {len(items_acumulate)} участников группы.")
    count_symbol_process = 0

    return (0, msg_success, self.members_count, self.members)

  # Get list of users of user=self and list id of users
  def get_userid_who_member(self, user_ids):
    """

    (list(int, int, ..., int)) -> tuple(int, string, list(int, int, ..., int))

    Function gets list of user id who is member of group

    """

    error, msg, count, group_members_list = self.get_members_if_need()
    if error != 0:
      return (error, msg, None)

    # Convertions to sets from lists
    group_members = set(group_members_list)

    try:
      user_friends = set(user_ids)
    except TypeError:
      print(f"Входные данные типа {type(user_ids)}, а ожидается тип {type(list())}")
      return (-1, msg_input_error, None)

    # Getting common friends equals intersection of sets
    friends_members = list(group_members.intersection(user_friends))

    user_friends_who_member = []
    for user_id in friends_members:
      user_friends_who_member.append(user_id)

    return (0, msg_success, user_friends_who_member)

def auth():
  """

  (None) -> None

  Function helps getting token for work with api VK

  """

  OAUTH_URL = "https://oauth.vk.com/authorize"
  OAUTH_PARAMS = {
    "client_id": 7238600,
    "display": "page",
    "response_type": "token",
    "scope": "status, friends"
  }

  print("?".join(
    (OAUTH_URL, urlencode(OAUTH_PARAMS)))
  )

def add_error(error, msg):
  """

  (int, string, dict) -> None

  Function accumulates error to error statistic

  """

  if error_stat.get((error, msg)) == None:
    error_stat[(error, msg)] = 1
  else:
    error_stat[(error, msg)] += 1

def print_errors(error_stat):
  """

  (dict) -> None

  Function prints statistic of errors about process of analize groups of user

  """

  if len(error_stat) > 0:
    for key, item in error_stat.items():
      print(f"Количество ошибок под номером {key[0]} \"{key[1]}\": {item}")

# Print information about result list of groups
def print_groups(user, groups):
  """

  (User, list(Group, Group, ..., Group)) -> None

  Function prints list objects-groups

  """

  print("")
  if len(groups) > 0:
    print(f"Ни один из друзей пользователя c id = \"{user.user_id}\" не является участником групп из списка:")
    for index, g in enumerate(groups, 1):
      print(f"{index}. \"{g.name}\"")

def test_identificator(s):
  """

  (string) -> boolean

  Function test string = identificator or not

  """

  if 'a' <= s[0].lower() <= 'z' or s[0] == '_':
    for i in range(1, len(s)):
      if not ('a' <= s[i].lower() <= 'z' or '0' <= s[i].lower() <= '9' or s[i].lower() == '_'):
        return False
    return True
  else:
    return False

def main():
  """

  (None) -> None

  Main function describe main functionality

  """

  global process_show
  global error_stat

  # Made it for getting token
  # auth()

  # Input user id
  while True:
    id_string = input("Введите идентификатор пользователя ВКонтакте (число=id пользователя или строка=nickname): ").strip()
    # id_string = 'chepel_vn'
    try:
      uid = int(id_string)
    except ValueError:
      if test_identificator(id_string):
        user = User(id_string)
        if user.error['error'] != 0:
          if user.error['error'] == 113:
            print(f"Аккаунт ВК с id = \"{id_string}\" не определен в системе")
            continue
          else:
            print(f"Возникла ошибка {user.error['error']}: {user.error['msg']}.")
            return
        else:
          break
      else:
        print("Введенная строка не может быть идентификатором пользователя.")
        continue

  # Enable visualization of process analyze of groups
  process_show = True

  # Getting groups of user, members which not are friends of user
  spy_groups = user.get_spy_groups()

  # Print information about result list of groups
  print_groups(user, spy_groups)

  # Print information about errors
  print_errors(error_stat)

  # Write result list of groups to json file
  write_groups_to_jsonfile('groups.json', spy_groups)

# Point of enter to program
main()