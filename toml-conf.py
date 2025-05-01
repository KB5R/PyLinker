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
                "••••••"  # скрытый пароль
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

            print("\n✅ Вы выбрали:")
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


def main():
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