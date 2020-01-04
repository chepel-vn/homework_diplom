import VKCommon
import VKGroup
import VKUsers


class User:
    """

    Class describe user VK

    """

    # Initialization class
    def __init__(self, user_id_string):
        """

        (None, string) -> object User or None

        Function of initialization of class User

        """

        self.last_name = ""
        self.first_name = ""
        self.status = ""
        self.friends = list()
        self.count_groups = 0
        self.groups = list()

        try:
            self.user_id = int(user_id_string)
        except ValueError:
            # Convert from nickname to user_id
            error, msg, user_id = self.get_id(user_id_string)
            if error != 0:
                self.error = {"error": error, "msg": msg}
                return

        self.count_friends = 0

        error, msg, fio = self.get_fio()
        if error != 0:
            self.error = {"error": error, "msg": msg}
            return

        self.error = {"error": 0, "msg": ""}

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

        value = f"https://vk.com/id{self.user_id}"
        return value

    # Get user_id by nickname of user VK
    def get_id(self, nickname):
        """

        (None) -> (int, string, int)

        Function gets id of user by nickname

        """

        params_here = VKCommon.params.copy()
        params_here["user_ids"] = nickname
        error, msg, response = VKCommon.request_get("https://api.vk.com/method/users.get", params_here)
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, info_json_list = VKCommon.get_field_of_response(response.json(), "response")
        if error != 0:
            value = (error, msg, None)
            return value

        if len(info_json_list) <= 0:
            value = (-1, "Пустой ответ", None)
            return value

        info_json = info_json_list[0]

        error, msg, self.user_id = VKCommon.get_field_of_response(info_json, "id")
        if error != 0 or self.user_id == "DELETED":
            value = (error, msg, None)
            return value

        error, msg, deactivated = VKCommon.get_field_of_response(info_json, "deactivated")
        if deactivated == "deleted":
            value = (-1, "Аккаунт удален", None)
            return value

        value = (0, "", self.user_id)
        return value

    # Get fio = "last_name first_name" of user
    def get_fio(self):
        """

        (None) -> str

        Function gets fio of user VK

        """

        if "self.last_name" in locals() and "self.first_name" in locals():
            value = (0, "", f"{self.last_name} {self.first_name}")
            return value

        params_here = VKCommon.params.copy()
        params_here["user_ids"] = self.user_id

        error, msg, response = VKCommon.request_get("https://api.vk.com/method/users.get", params_here)
        if error != 0:
            value = (error, msg, None)
            return value

        response_json = response.json()
        error, msg, info_json_list = VKCommon.get_field_of_response(response_json, "response")
        if error != 0:
            value = (error, msg, None)
            return value

        if len(info_json_list) <= 0:
            value = (-1, "Пустой ответ", None)
            return value

        info_json = info_json_list[0]

        error, msg, self.last_name = VKCommon.get_field_of_response(info_json, "last_name")
        if error != 0 or self.last_name == "DELETED":
            value = (error, msg, None)
            return value

        error, msg, self.first_name = VKCommon.get_field_of_response(info_json, "first_name")
        if error != 0 or self.first_name == "DELETED":
            value = (error, msg, None)
            return value

        value = (0, "", f"{self.last_name} {self.first_name}")
        return value

    # Get status of user
    def get_status(self):
        """

        (None) -> string

        Function gets status of user VK

        """

        if "self.status" in locals():
            value = (0, "", self.status)
            return value

        params_here = VKCommon.params.copy()
        params_here["user_id"] = self.user_id

        error, msg, response = VKCommon.request_get("https://api.vk.com/method/status.get", params_here)
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, info_json = VKCommon.get_field_of_response(response.json(), "response")
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, self.status = VKCommon.get_field_of_response(info_json, "text")
        if error != 0:
            value = (error, msg, None)
            return value

        value = (0, "", self.status)
        return value

    # Get list of friends of user
    def get_id_friends(self):
        """

        (None) -> tuple(int, string, list or None)

        Function gets list of id friends of user VK: list(int, int, ..., int)

        """

        if "self.friends" in locals():
            value = (0, "", self.friends)
            return value

        params_here = VKCommon.params.copy()
        params_here["user_id"] = self.user_id

        error, msg, response = VKCommon.request_get("https://api.vk.com/method/friends.get", params_here)
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, count, items = VKCommon.get_count_items_by_response(response)
        if error != 0:
            value = (error, msg, None)
            return value

        # self.count_friends = count_items[0]
        # self.friends = count_items[1]
        self.count_friends = count
        self.friends = items

        value = (0, "", self.friends)
        return value

    # Get list of groups of user
    def get_id_groups(self):
        """

        (None) -> list

        Function gets list of id groups of user VK: list(int, int, ..., int)

        """

        if "self.groups" in locals():
            value = (0, "", self.groups)
            return value

        params_here = VKCommon.params.copy()
        params_here["user_id"] = self.user_id
        params_here["count"] = 1000

        error, msg, response = VKCommon.request_get("https://api.vk.com/method/groups.get", params_here)
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, count, items = VKCommon.get_count_items_by_response(response)
        if error != 0:
            value = (error, msg, None)
            return value

        # self.count_groups = count_items[0]
        # self.groups = count_items[1]
        self.count_groups = count
        self.groups = items

        value = (0, "", self.groups)
        return value

    # Get list of common friends of user=self and user=other
    def get_common_friends(self, other):
        """

        (object User) -> tuple(int, string, list or None)

        Function gets common friends in list of objects of User

        """

        if not isinstance(other, User):
            print(f"Входные данные типа {type(other)}, а ожидается тип {type(self)}")
            raise ValueError

        # Conversions to sets from lists
        error, msg, id_friends = self.get_id_friends()
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, other_id_friends = other.get_id_friends()
        if error != 0:
            value = (error, msg, None)
            return value

        self_friends = set(id_friends)
        other_friends = set(other_id_friends)

        # Getting common friends equals intersection of sets
        common_friends_list = list(self_friends.intersection(other_friends))

        common_friends = []
        for user_id in common_friends_list:
            user_friend = User(user_id)
            common_friends.append(user_friend)

        value = (0, "", common_friends)
        return value

    # Getting groups of user, members which not are friends of user
    def get_spy_groups(self):
        """

        (None) -> list(object Group, object Group, ..., object Group) or None

        Function gets groups of user, members which not are friends of user

        """

        spy_groups = []

        error, msg, id_groups = self.get_id_groups()
        if error != 0:
            value = (error, msg, None)
            return value
        id_groups_set = set(id_groups)

        # Get list of friends
        error, msg, user_friends = self.get_id_friends()
        if error != 0:
            value = (error, msg, None)
            return value

        for user_id in user_friends:
            user = User(user_id)

            error, msg, id_groups_user = user.get_id_groups()
            if error != 0:
                print(f" аккаунт id = {user_id}: \"{user.last_name} {user.first_name}\": ошибка \"{msg}\".")
                continue

            id_groups_user_set = set(id_groups_user)

            id_groups_set = id_groups_set - id_groups_user_set

            print(f" аккаунт id = {user_id}: \"{user.last_name} {user.first_name}\" обработан.")

        if len(id_groups_set) > 0:
            for id_spy_group in id_groups_set:
                g = VKGroup.Group(id_spy_group)
                g.get_name()
                spy_groups.append(g)

        value = (0, "", spy_groups)
        return value

    # Getting groups of user, members which not are friends of user
    def get_spy_groups2(self, count_friends_limit):
        """

        (None) -> list(object Group, object Group, ..., object Group) or None

        Function gets groups of user, members which not are friends of user (use method "execute" for more speed)

        """

        spy_groups = []
        spy2_groups = []

        error, msg, id_groups = self.get_id_groups()
        if error != 0:
            value = (error, msg, None)
            return value
        id_groups_set = set(id_groups)

        # Get list of friends
        error, msg, user_friends = self.get_id_friends()
        if error != 0:
            value = (error, msg, None)
            return value

        params_here = dict()
        params_here["count"] = 1000
        params_code = VKCommon.params.copy()
        start = 0
        count_remain_accounts = len(user_friends)
        while True:
            if start > len(user_friends):
                break

            script = ""
            users = VKUsers.Users(user_friends)
            for user in users.persons[start:start + VKCommon.COUNT_REQUESTS_EXECUTE:1]:
                params_here["user_id"] = user["user_id"]
                script += f"API.groups.get({params_here}),"

            params_code["code"] = f"return [{script}];"
            error, msg, response = VKCommon.request_get('https://api.vk.com/method/execute', params_code)
            if error != 0:
                value = (error, msg, None)
                return value
            response_json = response.json()
            response_json_ = response_json["response"]
            for response_item in response_json_:
                if response_item:
                    id_groups_user = response_item["items"]
                    id_groups_user_set = set(id_groups_user)
                    id_groups_set = id_groups_set - id_groups_user_set

            start = start + VKCommon.COUNT_REQUESTS_EXECUTE

            count_remain_accounts -= VKCommon.COUNT_REQUESTS_EXECUTE
            if count_remain_accounts > 0:
                print(f"осталось обработать {count_remain_accounts} аккаунтов")

        if len(id_groups_set) > 0:
            for id_spy_group in id_groups_set:
                g = VKGroup.Group(id_spy_group)
                g.get_name()
                spy_groups.append(g)

        error, msg, id_groups_common_friends_n = VKGroup.get_groups_with_common_friends(id_groups, count_friends_limit)
        if error != 0:
            value = (error, msg, None)
            return value

        if len(id_groups_common_friends_n) > 0:
            for group_id in id_groups_common_friends_n:
                g = VKGroup.Group(group_id)
                g.get_name()
                spy2_groups.append(g)

        value = (0, "", (spy_groups, spy2_groups))
        return value
