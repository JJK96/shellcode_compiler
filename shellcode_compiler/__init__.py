import sys
from pathlib import Path
from enum import Enum
import subprocess
from contextlib import contextmanager
import logging

INPUT_FILE_NAME = "payload.c"
assets = Path(__file__).parent.parent / "assets"

@contextmanager
def error_handler():
    try:
        yield
    except Exception as e:
        logging.error(e)

def run_cmd(cmd: str):
    logging.info(f"[+] {cmd}")
    subprocess.run(cmd, text=True, check=True, shell=True)

class OutputFormat(Enum):
    BINARY = 1
    PE = 2

def compile(input_file=INPUT_FILE_NAME, output_dir="build", output_format=OutputFormat.BINARY):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    input_file = Path(input_file)
    main_file = (output_dir / INPUT_FILE_NAME)
    if not main_file.exists():
        main_file.symlink_to(input_file.absolute())
    for file in assets.glob("*"):
        output_file = (output_dir / file.name)
        if not output_file.exists():
            output_file.symlink_to(file.absolute())
    if output_format == OutputFormat.BINARY:
        with error_handler():
            run_cmd(f"make -C {output_dir}")
            logging.info(f"[+] {output_dir}/loader.exe and {output_dir}/payload.bin are ready!")
    else:
        with error_handler():
            run_cmd(f"make -C {output_dir} exe")
            logging.info(f"[+] {output_dir}/payload.exe is ready!")
    

def template(input, data):

    # Inject payload into loader source code
    with open(input, "r") as f:
        contents = f.read()

    for k,v in data.items():
        if isinstance(v, bytes):
            payload = ""
            for byte in v:
                payload += "\\" + hex(byte).lstrip("0")
            v = payload
        contents = contents.replace(f":{k}:", v)

    sys.stdout.write(contents)

def hash_djb2(s):
    hash = 5381
    for x in s:
        hash = (( hash << 5) + hash) + ord(x)
        hash = hash & 0xFFFFFFFF
    return hash

