import toml
import logging
import keyring
from getpass import getpass
from tabulate import tabulate
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.styles import Style
from pathlib import Path

config_dir = Path.home() / ".pylinker" # from pathlib import Path
config_file = config_dir / "config.toml"
log_file = config_dir / "pylinker.log"
    
    # Создаём директорию, если её нет
config_dir.mkdir(exist_ok=True)
    
    # Создаём config.toml (пустой), если его нет
if not config_file.exists():
    config_file.touch()  # Создаёт пустой файл
    logging.info(f"Created empty config file at {config_file}")
    
    # Создаём log-файл (пустой), если его нет
if not log_file.exists():
    log_file.touch()
    logging.info(f"Created empty log file at {log_file}")
    
logging.basicConfig(
    filename=log_file,            # Имя файла логов
    filemode='a',                         # Режим дозаписи (append)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
    
logging.info("File initialization completed")


with open(config_file) as f:
    config = toml.load(f)

table_data = []
host_entries = []  # Список для хранения данных по порядку (для выбора по индексу)


logging.basicConfig(
    filename=log_file,            # Имя файла логов
    filemode='a',                         # Режим дозаписи (append)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
            title="Ошибка",
            text="Конфигурация пуста."
        ).run()
        return None

    # 1. Выбор группы
    group = radiolist_dialog(
        title="Выбор группы",
        text="Выберите группу хостов:",
        values=[(g, g) for g in config.keys()]
    ).run()
    
    if group is None:
        return None

    hosts = config.get(group, {})
    if not hosts:
        message_dialog(
            title="Ошибка",
            text=f"Группа '{group}' не содержит хостов."
        ).run()
        return None

    # 2. Формирование списка для выбора хоста
    host_choices = []
    for host_name, details in hosts.items():
        ip = details.get("ip", "???")
        port = details.get("port", "22")
        user = details.get("user", "???")
        password_display = "[keyring]" if details.get("password_storage") == "keyring" else "[plain]"
        label = f"{host_name} ({ip}:{port}, {user}) {password_display}"
        host_choices.append(((group, host_name), label))

    # 3. Выбор хоста через TUI
    selected = radiolist_dialog(
        title="Выбор хоста",
        text="Выберите хост для подключения:",
        values=host_choices
    ).run()

    if selected is None:
        return None

    group, host_name = selected
    selected_host = hosts[host_name]
    ip = selected_host.get("ip")
    port = selected_host.get("port", 22)
    user = selected_host.get("user")

    # Получение пароля
    if selected_host.get("password_storage") == "keyring":
        service_name = f"pylinker_{group}_{host_name}"
        password = keyring.get_password(service_name, user)
        if password is None:
            message_dialog(title="Ошибка", text="Не удалось получить пароль из keyring!").run()
            return None
    else:
        password = selected_host.get("password")
        if password is None:
            message_dialog(title="Ошибка", text="Пароль не найден в конфигурации!").run()
            return None

    return ip, port, user, password

from prompt_toolkit.shortcuts import input_dialog


def add_entry_toml():
#    group = input("Введите имя существующей группы или новую для её создания: ").strip()
    group = input_dialog(
        title='Add entry toml',
        text='Введите имя существующей группы или новую для её создания:').run().strip()
    
#    name = input("Введите имя нового хоста (должно быть уникальным в пределах группы): ").strip()
    name = input_dialog(
        title='Add entry toml',
        text='Введите имя нового хоста (должно быть уникальным в пределах группы):').run().strip()
    
#    ip = input("Введите адрес хоста (example.com или 192.168.1.1): ").strip()
    ip = input_dialog(
        title='Add entry toml',
        text='Введите адрес хоста (example.com или 192.168.1.1):').run().strip()

#    port_input = input("Введите порт (по умолчанию 22): ").strip()
    port_input = input_dialog(
        title='Add entry toml',
        text='Введите порт (по умолчанию 22):').run().strip()
    port = int(port_input) if port_input else 22

#    user = input("Введите пользователя: ").strip()
    user = input_dialog(
        title='Add entry toml',
        text='Введите пользователя:').run().strip()

#    password = getpass("Введите пароль: ").strip()
    password = input_dialog(
        title='Add entry toml',
        text='Введите пароль:', password=True).run().strip()


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
    with open(config_file, "w") as f:
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

            #confirm = input(f"Удалить хост '{host_name}' из группы '{group}'? (y/n): ").strip().lower()

            confirm = yes_no_dialog(title='Yes/No dialog example',text='Do you want to confirm?').run()
            if confirm == True:
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
                with open(config_file, "w") as f:
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
            ]
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