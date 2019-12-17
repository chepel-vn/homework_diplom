import VKCommon


class Group:
    """

    Class describe group VK

    """

    # Initialization class
    def __init__(self, group_id):
        """

        (None, int) -> object Group or None

        Function of initialization of class Group

        """

        self.group_id = group_id
        self.members_count = 0
        self.group_name = ""

    # Detect a status of user
    def get_name(self):
        """

        (None) -> str

        Function gets name of group VK

        """

        if 'self.group_name' in locals():
            value = (0, "", self.group_name)
            return value

        params_here = VKCommon.params.copy()
        params_here["group_ids"] = self.group_id
        params_here["fields"] = "name,members_count"

        error, msg, response = VKCommon.request_get('https://api.vk.com/method/groups.getById', params_here)
        if error != 0:
            value = (error, msg, None)
            return value

        response_json = response.json()
        error, msg, info_json_list = VKCommon.get_field_of_response(response_json, 'response')
        if error != 0:
            value = (error, msg, None)
            return value

        info_json = info_json_list[0]

        error, msg, self.group_name = VKCommon.get_field_of_response(info_json, 'name')
        if error != 0:
            value = (error, msg, None)
            return value

        error, msg, self.members_count = VKCommon.get_field_of_response(info_json, 'members_count')
        if error != 0:
            value = (error, msg, None)
            return value

        value = (0, "", self.group_name)
        return value
