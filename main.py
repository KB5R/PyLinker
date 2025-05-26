import subprocess
import sys
import logging
import signal

def inteactive_session_ssh():
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
    print("123")
if __name__ == "__main__":
    main()