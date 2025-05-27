
import subprocess
import logging


from toml_config import load_toml, choose_host, add_entry_toml, del_entry_toml, toml_conf # Func from toml_conf.py


def inteactive_session_ssh(host, user, port, password):
    try:
        cmd = [
            "sshpass", "-p", password,
            "ssh", f"{user}@{host}",
            "-p", str(port),
            "-o", "StrictHostKeyChecking=no"  # Отключаем подтверждение нового ключа хоста
        ]    
        subprocess.run(cmd, check=True)
        logging.info("Run ssh session...")
    except subprocess.TimeoutExpired:
        logging.error("SSH session kill to timeout")

    except subprocess.CalledProcessError as e:
        logging.error(f"SSH failed with error: {e}")
    
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")

def connect_to_inteactive_session_ssh():
    host = input("Enter destination hosts:")
    user = input("Enter name users: ")
    port_input = input("Enter port [default 22]: ").strip()
    if port_input:
        port = int(port_input)
    else:
        port = 22
    password = input("Enter password: ").strip()
    print("Entered hosts", host)
    print("Entered user", user)
    print("Entered ports", port)
    inteactive_session_ssh(host, user, port, password)

def main():
    connect_to_inteactive_session_ssh()

if __name__ == "__main__":
    main()