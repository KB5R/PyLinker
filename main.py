
import subprocess
import logging
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from toml_config import load_toml, add_entry_toml, del_entry_toml, toml_conf, output_host # Func from toml_conf.py
from prompt_toolkit.styles import Style

# import loging
logging.basicConfig(
    filename='pylinker.log',            # Имя файла логов
    filemode='a',                         # Режим дозаписи (append)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def inteactive_session_ssh(host, user, port, password):
    try:
# Данная команда cmd формирует как мы будем подключатся по ssh    
        cmd = [ 
            "sshpass", "-p", password, "ssh", f"{user}@{host}",
            "-p", str(port), "-o", "StrictHostKeyChecking=no" # Что бы не показывалось сообщение о обмене рукопажатиями
        ]



        logging.info(f"Starting SSH session to {user}@{host}:{port}")
        subprocess.run(cmd, check=True)
        logging.info(f"SSH session to {user}@{host}:{port} finished successfully")


    except subprocess.TimeoutExpired:
        logging.error("SSH session killed due to timeout.")

    except subprocess.CalledProcessError as e:
        logging.error(f"SSH failed with error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")


def connect_to_inteactive_session_ssh():
    result = output_host() # Получаем данные
    if result:# Распаковка в отдельные переменные
        host, port, user, password = result
        # Передвем данные дальше
        inteactive_session_ssh(host, user, port, password)




def main():
    while True:
        custom_style = Style.from_dict({
    "dialog": "bg:#002b36",
    "dialog frame.label": "bg:#002b36 #00ff00",  # цвет заголовка
    "dialog.body": "bg:#002b36 #00ff00",         # фон и цвет текста
    "button": "bg:#002b36 #00ff00",
    "button.focused": "bg:#00ff00 #000000",       # активная кнопка
    "radiolist": "bg:#002b36 #00ff00",
    "radiolist focused": "bg:#00ff00 #000000",
})
        
        button_main = radiolist_dialog(
            title="SSH Client Menu",
            text="Select action:",
            values=[
                ("ssh_main",  "1. SSH"),
                ("sftp_main", "2. SFTP [OFF]"),
                ("vnc_main", "3. VNC [OFF]"),
                ("rdp_main", "4. RDP [OFF]"),
                ("exit", "0. Exit"),
            ],
            style=custom_style # Подключение themes
        ).run()

        if button_main == "ssh_main":
            ssh_menu()
        elif button_main == "sftp_mai": # Обртите внимание на комнду для обработаки так называемые заглушки
            ssh_menu() 
        elif button_main == "vnc_mai": # Обртите внимание на комнду для обработаки так называемые заглушки
            ssh_menu()
        elif button_main == "rdp_mai": # Обртите внимание на комнду для обработаки так называемые заглушки
            ssh_menu()
        elif button_main == "exit":
            break


def ssh_menu():
    while True:
        custom_style = Style.from_dict({
    "dialog": "bg:#002b36",
    "dialog frame.label": "bg:#002b36 #00ff00",  # цвет заголовка
    "dialog.body": "bg:#002b36 #00ff00",         # фон и цвет текста
    "button": "bg:#002b36 #00ff00",
    "button.focused": "bg:#00ff00 #000000",       # активная кнопка
    "radiolist": "bg:#002b36 #00ff00",
    "radiolist focused": "bg:#00ff00 #000000",
})
        
        button_main = radiolist_dialog(
            title="SSH Client Menu",
            text="Select action:",
            values=[
                ("ssh",  "1. Connect to SSH"),
                ("toml", "2. Settings database (TOML)"),
                ("exit", "0. Exit"),
            ],
            style=custom_style # Подключение themes
        ).run()

        if button_main == "ssh":
            connect_to_inteactive_session_ssh()
        elif button_main == "toml":
            toml_conf()
        elif button_main == "exit":
            break

if __name__ == "__main__":
    main()