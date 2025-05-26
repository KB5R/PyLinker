import subprocess
import logging

def inteactive_session_ssh(host, user, port):
    try:
        cmd = ["ssh", f"{user}@{host}", "-p", str(port)]
        subprocess.run(cmd, check=True)
        logging.info("Run ssh session...")
    except subprocess.TimeoutExpired:
        logging.error("SSH session kill to timeout")
    except subprocess.CalledProcessError as e:
        logging.error(f"SSH failed with error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")

def main():
    host = input("Enter destination hosts:")
    user = input("Enter name users: ")
    port_input = input("Enter port [default 22]: ").strip()
    if port_input:
        port = int(port_input)
    else:
        port = 22
    print("Entered hosts", host)
    print("Entered user", user)
    print("Entered ports", port)
    inteactive_session_ssh(host, user, port)
if __name__ == "__main__":
    main()