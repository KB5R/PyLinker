
import subprocess
import logging
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from toml_config import load_toml, add_entry_toml, del_entry_toml, toml_conf, output_host # Func from toml_conf.py


def inteactive_session_ssh(host, user, port, password):
    try:
# Данная команда cmd формирует как мы будем подключатся по ssh    
        cmd = [ 
            "sshpass", "-p", password, "ssh", f"{user}@{host}",
            "-p", str(port), "-o", "StrictHostKeyChecking=no" # Что бы не показывалось сообщение о обмене рукопажатиями
        ]



        subprocess.run(cmd, check=True) # Run 

        # Обработчики ошибок не понятно работают ли они 
        # Надо проверять !!!
        logging.info("Run ssh session...")
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
        button_main = radiolist_dialog(
            title="SSH Client Menu",
            text="Select action:",
            values=[
                ("ssh", "1. Connect to SSH"),
                ("toml", "2. Settings database (TOML)"),
                ("exit", "0. Exit"),
            ],
        ).run()

        if button_main == "ssh":
            connect_to_inteactive_session_ssh()
        elif button_main == "toml":
            toml_conf()
        elif button_main == "exit":
            break

if __name__ == "__main__":
    main()