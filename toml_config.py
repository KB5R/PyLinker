import toml
import logging
import keyring
from getpass import getpass
from tabulate import tabulate
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style
# Загрузка конфига
with open("config.toml") as f:
    config = toml.load(f)

table_data = []
host_entries = []  # Список для хранения данных по порядку (для выбора по индексу)


logging.basicConfig(
    filename='pylinker.log',            # Имя файла логов
    filemode='a',                         # Режим дозаписи (append)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

custom_style = Style.from_dict({ # Вынес что бы не дублировать (Черный фон, зеленые линии)
    "dialog": "bg:#002b36",
    "dialog frame.label": "bg:#002b36 #00ff00",  # цвет заголовка
    "dialog.body": "bg:#002b36 #00ff00",         # фон и цвет текста
    "button": "bg:#002b36 #00ff00",
    "button.focused": "bg:#00ff00 #000000",       # активная кнопка
    "radiolist": "bg:#002b36 #00ff00",
    "radiolist focused": "bg:#00ff00 #000000",
})


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
                "password_storage": details.get("password_storage")  # Добавляем это поле
            }
            host_entries.append(entry)
            
            # В таблице показываем откуда берётся пароль
            password_source = "[keyring]" if details.get("password_storage") == "keyring" else "[config]"
            table_data.append([
                group,
                host_name,
                details.get("ip"),
                details.get("port"),
                details.get("user"),
                password_source  # Изменяем отображение пароля
            ])

    headers = ["№", "Groups", "Hostname", "IP", "Port", "User", "Password Source"]
    numbered_table = [[i+1] + row for i, row in enumerate(table_data)]
    print(tabulate(numbered_table, headers=headers, tablefmt="grid"))

def output_host():
    if not config:
        message_dialog(
        title="Error",
        text="Конфигурация пуста.",
        style=custom_style
    ).run()
        return None

    # 1. Выбор группы
    group = radiolist_dialog(
        title="Выбор группы",
        text="Выберите группу хостов:",
        values=[(g, g) for g in config.keys()],
        style=custom_style
    ).run()
    
    if group is None:
        print("Группа не выбрана.")
        return None

    hosts = config.get(group, {})
    if not hosts:
        print(f"Группа '{group}' не содержит хостов.")
        return None

    # 2. Подготовка таблицы и выбора
    local_host_entries = []
    local_table = []

    for host_name, details in hosts.items():
        entry = {
            "group": group,
            "host_name": host_name,
            "ip": details.get("ip"),
            "port": details.get("port"),
            "user": details.get("user"),
            "password_storage": details.get("password_storage")  # Добавляем информацию о хранилище
        }
        local_host_entries.append(entry)
        
        # В таблице не показываем пароль, только отметку о его наличии
        password_display = "[keyring]" if details.get("password_storage") == "keyring" else "[plain]"
        local_table.append([
            host_name,
            details.get("ip", ""),
            details.get("port", ""),
            details.get("user", ""),
            password_display
        ])

    headers = ["№", "Hostname", "IP", "Port", "User", "Password Storage"]
    numbered_table = [[i + 1] + row for i, row in enumerate(local_table)]
    print(tabulate(numbered_table, headers=headers, tablefmt="grid"))

    # 3. Выбор хоста
    try:
        choice = int(input("\nВведите номер хоста для вывода: "))
        if 1 <= choice <= len(local_host_entries):
            selected = local_host_entries[choice - 1]
            ip = selected["ip"]
            port = selected["port"]
            user = selected["user"]
        
            # Получаем пароль из keyring или из конфига
            if selected.get("password_storage") == "keyring":
                service_name = f"pylinker_{group}_{selected['host_name']}"
                password = keyring.get_password(service_name, user)
                if password is None:
                    print("Ошибка: не удалось получить пароль из хранилища!")
                    return None
            else:
                # Для обратной совместимости с старыми записями
                password = hosts[selected["host_name"]].get("password")
                if password is None:
                    print("Ошибка: пароль не найден!")
                    return None

            print(f"\nInformation hosts:")
            print(f"Name host: {selected['host_name']}")
            print(f"IP: {ip}")
            print(f"Port: {port}")
            print(f"User: {user}")
            print(f"Password: [shadow]")

            return ip, port, user, password
        else:
            print("Неверный номер.")
            return None
    except ValueError:
        print("Введите корректное число!")
        return None


def add_entry_toml():
    group = input("Введите имя существующей группы или новую для её создания: ").strip()
    name = input("Введите имя нового хоста (должно быть уникальным в пределах группы): ").strip()

    ip = input("Введите адрес хоста (example.com или 192.168.1.1): ").strip()
    port_input = input("Введите порт (по умолчанию 22): ").strip()
    port = int(port_input) if port_input else 22
    user = input("Введите пользователя: ").strip()
    password = getpass("Введите пароль: ").strip()

    # Создаём группу, если её ещё нет
    if group not in config:
        config[group] = {}

    if name in config[group]:
        print(f"Ошибка: Хост с именем '{name}' уже существует в группе '{group}'!")
        return

    # Сохраняем пароль в keyring
    service_name = f"pylinker_{group}_{name}"
    keyring.set_password(service_name, user, password)

    # Добавляем запись без пароля
    config[group][name] = {
        "ip": ip,
        "port": port,
        "user": user,
        "password_storage": "keyring"  # Флаг, что пароль хранится в keyring
    }

    # Сохраняем конфиг
    with open("config.toml", "w") as f:
        for group_name, hosts in config.items():
            f.write(f"[{group_name}]\n")
            for host_name, details in hosts.items():
                inline = ", ".join([f'{k} = "{v}"' for k, v in details.items() if k != 'password'])
                f.write(f'{host_name} = {{ {inline} }}\n')
            f.write("\n")

    print(f"Хост '{name}' успешно добавлен в группу '{group}' и сохранён.")
    logging.info(f"Хост '{name}' успешно добавлен в группу '{group}' и сохранён.")


def del_entry_toml():
    print("Выберите какой host вы хотите удалить")
    load_toml()

    try:
        choice = int(input("\nВведите номер хоста для удаления: "))
        if 1 <= choice <= len(host_entries):
            selected = host_entries[choice - 1]
            group = selected["group"]
            host_name = selected["host_name"]
            user = selected["user"]

            confirm = input(f"Удалить хост '{host_name}' из группы '{group}'? (y/n): ").strip().lower()
            if confirm == 'y':
                # Удаляем пароль из keyring
                if selected.get("password_storage") == "keyring":
                    service_name = f"pylinker_{group}_{host_name}"
                    try:
                        keyring.delete_password(service_name, user)
                    except keyring.errors.PasswordDeleteError:
                        pass  # Пароль уже удален или не существует

                # Удаляем запись из конфига
                del config[group][host_name]

                # Если группа пуста — удалить и её
                if not config[group]:
                    del config[group]

                # Сохраняем изменения
                with open("config.toml", "w") as f:
                    for group_name, hosts in config.items():
                        f.write(f"[{group_name}]\n")
                        for host_name, details in hosts.items():
                            inline = ", ".join([f'{k} = "{v}"' for k, v in details.items() if k != 'password'])
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
        button_toml = radiolist_dialog(
            title="SSH Client Menu",
            text="Select a task for toml",
            values=[
                ("Add",  "1. Add entry toml"),
                ("Dell", "2. Del entry toml"),
                ("Output", "3. Output entry toml"),
                ("Exit", "0. Exit")
            ],
            style=custom_style
        ).run()
        

        if button_toml == "Add":
            add_entry_toml()
        elif button_toml == "Dell":
            del_entry_toml()
        elif button_toml == "Output":
            output_host()
        elif button_toml == "Exit":
            break
        else:
            print("Unknown sig.")