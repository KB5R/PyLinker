import paramiko              # lib in SSH
import sys                   # stdin stdout and system function
import tty                   # Teletype
import termios               # управления параметрами терминала (например, echo)
import select                # одновременное чтения stdin и SSH
import logging               # logs


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def request_pty(channel):
    """Запрашивает TTY и запускает интерактивную оболочку."""
    try:
        channel.get_pty(term='xterm')
        channel.invoke_shell()
    except Exception as e:
        raise RuntimeError(f"Не удалось открыть интерактивный shell: {e}")

class RawTerminal:
    """Контекстный менеджер для установки raw-режима терминала и автоматического восстановления."""
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

def interactive_shell(channel):
    """Интерактивный input/output между users и SSH-connect."""
    try:
        with RawTerminal():
            while True:
                r, _, _ = select.select([sys.stdin, channel], [], [])

                if sys.stdin in r:
                    inp = sys.stdin.read(1)
                    if not inp:
                        break
                    channel.send(inp)

                if channel in r:
                    if channel.exit_status_ready():
                        break
                    while channel.recv_ready():
                        data = channel.recv(1024)
                        if not data:
                            break
                        sys.stdout.write(data.decode('utf-8', errors='ignore'))
                        sys.stdout.flush()
    except KeyboardInterrupt:
        logging.info("Прерывание пользователем (Ctrl+C)")

def ssh_interactive_session(host, port, user, password):
    """Основная функция подключения по SSH и запуска интерактивной сессии."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, port=port, username=user, password=password)
        transport = client.get_transport()
        channel = transport.open_session()

        request_pty(channel)
        logging.info("Интерактивная сессия открыта. Нажмите Ctrl+C для выхода.\n")
        interactive_shell(channel)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        client.close()
        logging.info("Соединение закрыто.")

def main():
    """ Главная функция — точка входа программы. """

    host = input("Введите хост: ")
    
    port = int(input("Введите порт [22]: ") or 22)
    
    user = input("Пользователь: ")
    
    password = input("Пароль: ")

    ssh_interactive_session(host, port, user, password)



    """ Вход """
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exit programm")

