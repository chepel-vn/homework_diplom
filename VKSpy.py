import VKCommon
import VKUser


def main():
    """

    (None) -> None

    Main function describe main functionality

    """

    # Made it for getting token
    # auth()

    # Get token from file
    token = VKCommon.get_token("token.txt")
    if len(token) == 0:
        return

    # Input user id
    user = None
    while True:
        id_string = input("Введите id пользователя ВКонтакте (число=id пользователя или строка=nickname): ").strip()

        try:
            int(id_string)
            id_string = f"id{id_string}"
        except ValueError:
            pass

        # print(f"\"{id_string}\"")

        if VKCommon.test_id(id_string):
            user = VKUser.User(id_string)
            if user.error["error"] != 0:
                if user.error["error"] == 113:
                    print(f"Аккаунт ВК с id = \"{id_string}\" не определен в системе.")
                    continue
                else:
                    print(f"Возникла ошибка {user.error['error']}: {user.error['msg']}.")
                    return
            else:
                break
        else:
            print("Введенная строка не может быть идентификатором пользователя.")
            continue

    if user is None:
        return

    # Getting groups of user, members which not are friends of user
    error, msg, spy_groups = user.get_spy_groups()
    if error != 0:
        print(f"Ошибка {error}: {msg}.")
        return

    # Print information about result list of groups
    VKCommon.print_groups(user, spy_groups)

    # Write result list of groups to json file
    VKCommon.write_groups_to_file("groups.json", spy_groups)


# Point of enter to program
main()
