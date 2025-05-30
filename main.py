
import subprocess
import logging


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

# Данная функция снизу не требуется больше пока оставлю ее что бы понимать более подробно работу
# def connect_to_inteactive_session_ssh():
#     host = input("Enter destination hosts:")
#     user = input("Enter name users: ")
#     port_input = input("Enter port [default 22]: ").strip()
#     if port_input:
#         port = int(port_input)
#     else:
#         port = 22
#     password = input("Enter password: ").strip()
#     output_host()

#     inteactive_session_ssh(host, user, port, password)

def connect_to_inteactive_session_ssh():
    result = output_host() # Получаем данные
    if result:# Распаковка в отдельные переменные
        host, port, user, password = result
        # Передвем данные дальше
        inteactive_session_ssh(host, user, port, password)

def main():
    while True:
        print("Выберите подключение")
        print("1. Connect to SSH")
        print("2. Working with the database")
        print("0. Exit")

        id = int(input())

        if id == 1:
            connect_to_inteactive_session_ssh()
        elif id == 2:
            toml_conf()
        elif id == 0:
            break


if __name__ == "__main__":
    main()