import toml
from tabulate import tabulate

# Загрузка конфига
with open("config.toml") as f:
    config = toml.load(f)

table_data = []
host_entries = []  # Список для хранения данных по порядку (для выбора по индексу)


def load_toml():
    table_data.clear()
    host_entries.clear()

    for group, hosts in config.items():
        for host_name, details in hosts.items():
            entry = {
                "group": group,
                "host_name": host_name,
                "ip": details.get("ip"),
                "port": details.get("port"),
                "user": details.get("user"),
                "password": details.get("password")
            }
            host_entries.append(entry)
            table_data.append([
                group,
                host_name,
                details.get("ip"),
                details.get("port"),
                details.get("user"),
                details.get("password")
            ])

    headers = ["№", "Groups", "Hostname", "IP", "Port", "User", "Password"]
    
    # Добавляем нумерацию строк
    numbered_table = [[i+1] + row for i, row in enumerate(table_data)]
    
    print(tabulate(numbered_table, headers=headers, tablefmt="grid"))


def choose_host():
    try:
        choice = int(input("\nВыберите номер хоста: "))
        if 1 <= choice <= len(host_entries):
            selected = host_entries[choice - 1]

            # Сохраняем в переменные

            ip = selected["ip"]
            port = selected["port"]
            user = selected["user"]
            password = selected["password"]

            print(f"Имя хоста: {selected['host_name']}")
            print(f"IP: {ip}")
            print(f"Порт: {port}")
            print(f"Пользователь: {user}")
            print(f"Пароль: {password}")

            return ip, port, user, password
        else:
            print("Неверный номер.")
            return None
    except ValueError:
        print("Введите число!")
        return None



def add_entry_toml():
    group = input("Введите имя существующей группы или новую для её создания: ").strip()
    name = input("Введите имя нового хоста (должно быть уникальным в пределах группы): ").strip()

    ip = input("Введите адрес хоста (example.com или 192.168.1.1): ").strip()
    port = input("Введите порт (например, 22): ").strip()
    user = input("Введите пользователя: ").strip()
    password = input("Введите пароль: ").strip()

    # Создаём группу, если её ещё нет
    if group not in config:
        config[group] = {}

    if name in config[group]:
        print(f"Ошибка: Хост с именем '{name}' уже существует в группе '{group}'!")
        return

    # Добавляем запись
    config[group][name] = {
        "ip": ip,
        "port": port,
        "user": user,
        "password": password
    }

    # Генерируем строку вручную для inline table
    with open("config.toml", "w") as f:
        for group_name, hosts in config.items():
            f.write(f"[{group_name}]\n")
            for host_name, details in hosts.items():
                inline = ", ".join([f'{k} = "{v}"' for k, v in details.items()])
                f.write(f'{host_name} = {{ {inline} }}\n')
            f.write("\n")

    print(f"Хост '{name}' успешно добавлен в группу '{group}' и сохранён.")

def del_entry_toml():
    print("Выберите какой host вы хотите удалить")
    load_toml()

    try:
        choice = int(input("\nВведите номер хоста для удаления: "))
        if 1 <= choice <= len(host_entries):
            selected = host_entries[choice - 1]
            group = selected["group"]
            host_name = selected["host_name"]

            confirm = input(f"Удалить хост '{host_name}' из группы '{group}'? (y/n): ").strip().lower()
            if confirm == 'y':
                del config[group][host_name]

                # Если группа пуста — удалить и её
                if not config[group]:
                    del config[group]

                # Сохраняем изменения
                with open("config.toml", "w") as f:
                    for group_name, hosts in config.items():
                        f.write(f"[{group_name}]\n")
                        for host_name, details in hosts.items():
                            inline = ", ".join([f'{k} = "{v}"' for k, v in details.items()])
                            f.write(f'{host_name} = {{ {inline} }}\n')
                        f.write("\n")

                print(f"Хост '{host_name}' успешно удалён.")
            else:
                print("Удаление отменено.")
        else:
            print("Неверный номер.")
    except ValueError:
        print("Введите корректное число.")



def toml_conf():
    while True:
        load_toml()
        print("Select a task for toml")
        print("1. Add entry toml")
        print("2. Dell entry toml")
        print("0. Exit")
        number = int(input())
        if number == 1:
            add_entry_toml()
        elif number == 2:
            del_entry_toml()
        elif number == 0:
            break
    


if __name__ == "__main__":
    toml_conf()
