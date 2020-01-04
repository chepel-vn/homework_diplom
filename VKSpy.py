import VKCommon
import VKUser


def main():
    """

    (None) -> None

    Main function describe main functionality

    """

    # Made it for getting token
    # VKCommon.auth()

    # Get token from file
    token = VKCommon.get_token("token.txt")
    if len(token) == 0:
        return

    # Input user id
    user = None
    while True:
        id_string = input("Введите id пользователя ВКонтакте (число=id пользователя или строка=nickname): ").strip()
        # id_string = '171691064'

        try:
            int(id_string)
            id_string = f"id{id_string}"
        except ValueError:
            pass

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

    while True:
        try:
            count_friends_limit = int(input("Введите ограничение на количество общих друзей в группах (N=число):"))
            break
        except ValueError:
            print("Необходимо ввести число.")
    # count_friends_limit = 7

    # Getting groups of user, members which not are friends of user
    error, msg, spy_groups = user.get_spy_groups2(count_friends_limit)
    if error != 0:
        print(f"Ошибка {error}: {msg}.")
        return

    # Print information about result list of groups
    VKCommon.print_groups(f"Ни один из друзей пользователя c id = \"{user.user_id}\" {user.last_name} "
                          f"{user.first_name} не является участником групп из списка:", spy_groups[0])

    VKCommon.print_groups(f"Группы, имеющие в участниках не более {count_friends_limit} друзей пользователя "
                          f"c id = \"{user.user_id}\" {user.last_name} {user.first_name}:", spy_groups[1])

    # Write result list of groups to json file
    VKCommon.write_groups_to_file("groups.json", spy_groups[0])


if __name__ == "__main__":
    main()


