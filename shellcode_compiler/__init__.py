from pathlib import Path
from enum import Enum
from contextlib import contextmanager
import logging
from .util import run_cmd
import jinja2
import shutil
from .config import settings

INPUT_FILE_NAME = "payload.c"
assets = Path(__file__).parent.parent / "assets"

@contextmanager
def error_handler():
    try:
        yield
    except Exception as e:
        logging.error(e)

class OutputFormat(Enum):
    BINARY = 1
    PE = 2

def compile(input_file=INPUT_FILE_NAME, output_dir="build", output_format=OutputFormat.BINARY, rebuild=False):
    output_dir = Path(output_dir)
    if rebuild and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)
    input_file = Path(input_file)
    main_file = (output_dir / INPUT_FILE_NAME)
    makefile = (output_dir / "Makefile")
    if not makefile.exists():
        content = template(assets / "Makefile.j2", {
            "CC": settings.get("CC"),
            "LD": settings.get("LD")
        })
        with open(makefile, 'w') as f:
            f.write(content)
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
    env = jinja2.Environment()

    # Inject payload into loader source code
    with open(input, "r") as f:
        template = env.from_string(f.read())

    context = {}
    for k,v in data.items():
        if isinstance(v, bytes):
            payload = ""
            for byte in v:
                payload += "\\" + hex(byte).lstrip("0")
            v = payload
        context[k] = v

    return template.render(context)

def hash_djb2(s):
    hash = 5381
    for x in s:
        hash = (( hash << 5) + hash) + ord(x)
        hash = hash & 0xFFFFFFFF
    return hash

