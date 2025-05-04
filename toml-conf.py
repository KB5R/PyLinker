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

    headers = ["№", "Groups", "Name_hosts", "IP", "Port", "User", "Password"]
    
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
    # .strip() удаляет пробелы с левого края так же и с правого
    group = input("Введите имя существующей группы или новую для её создания: ").strip()
    name = input("Введите имя нового хоста (должно быть уникальным в пределах группы): ").strip()

    ip = input("Введите адрес хоста (example.com или 192.168.1.1): ").strip()
    port = input("Введите порт (например, 22): ").strip()
    user = input("Введите пользователя: ").strip()
    password = input("Введите пароль: ").strip()

    # Создаём группу, если её ещё нет
    if group not in config:
        config[group] = {}

    # Проверzка имени
    if name in config[group]:
        print(f"Ошибка: Хост с именем '{name}' уже существует в группе '{group}'!")
        return

    # Add host
    config[group][name] = {
        "ip": ip,
        "port": port,
        "user": user,
        "password": password
    }

    # Writ file
    with open("config.toml", "w") as f:
        toml.dump(config, f)

    print(f"Хост '{name}' успешно добавлен в группу '{group}' и сохранён.")


def main():
    add_entry_toml()
    print("Выберите что вы хотите сделать")
    print("Показать полный список:  [1]")
    try:
        id = int(input())
    except ValueError:
        print("Введите число!")
        return

    if id == 1:
        load_toml()
        choose_host()
    else:
        print("Вы вышли из программы")


if __name__ == "__main__":
    main()