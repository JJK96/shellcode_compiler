import subprocess
import logging

def run_cmd(cmd: str, do_print=True):
    if do_print:
        logging.info(f"[+] {cmd}")
    subprocess.run(cmd, text=True, check=True, shell=True)

