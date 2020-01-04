import VKCommon


class Users:
    """

    Class describe users VK

    """

    # Initialization class
    def __init__(self, user_ids):
        """

        (None, string) -> object User or None

        Function of initialization of class User

        """

        self.persons = list()
        person = dict()
        params_here = VKCommon.params.copy()
        params_here["user_ids"] = ",".join([str(i) for i in user_ids])

        error, msg, response = VKCommon.request_get("https://api.vk.com/method/users.get", params_here)
        if error != 0:
            self.error = {"error": error, "msg": msg}
            return

        error, msg, info_json_list = VKCommon.get_field_of_response(response.json(), "response")
        if error != 0:
            self.error = {"error": error, "msg": msg}
            return

        if len(info_json_list) <= 0:
            self.error = {"error": -1, "msg": "Пустой ответ"}
            return

        for user in info_json_list:
            person["user_id"] = user["id"]
            person["first_name"] = user["first_name"]
            person["last_name"] = user["last_name"]
            person["count_friends"] = 0
            self.persons.append(person.copy())

        self.error = {"error": 0, "msg": ""}
