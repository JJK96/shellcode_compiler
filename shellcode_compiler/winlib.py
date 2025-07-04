from .config import settings
from . import hash_djb2
from functools import cache
from pathlib import Path
import logging
import json
import jinja2


class InvalidDefinition(Exception):
    pass

class Definition:
    def __init__(self, definition_str, dll=None):
        self.definition_str = definition_str
        self.dll = dll
        try:
            self.parse()
        except Exception as e:
            logging.error(f"Could not parse: {self.definition_str}")
            raise

    def parse(self):
        types, _, args = self.definition_str.partition('(')
        types = list(filter(lambda x:x and x != "WINBASEAPI", types.split(' ', )))
        self.function_name = types[-1]
        self.types = types[:-1]
        self.literal_args = args[:-2]
        self.variables = []
        if self.literal_args.lower() != "void":
            for arg in self.literal_args.split(", "):
                if not ' ' in arg:
                    continue
                self.variables.append(arg.split(' ')[1].lstrip('*'))

    def to_winlib_entry(self):
        if not self.dll:
            raise Exception("Cannot convert to winlib entry if the DLL is unknown")
        hash_name = self.dll[:-4]
        function_hash = hash_djb2(self.function_name)
        return f"""\
#define HASH_{self.function_name} {hex(function_hash)}
typedef {self.types[0]}({self.types[1]} *{self.function_name}_t) ({self.literal_args});
{' '.join(self.types)} {self.function_name} ({self.literal_args}) {{
    {self.function_name}_t _{self.function_name} = ({self.function_name}_t) getFunctionPtr(HASH_{hash_name}, HASH_{self.function_name});
    return _{self.function_name}({', '.join(self.variables)});
}}
"""

    def __str__(self):
        return self.definition_str

def lib_to_dll(lib):
    if lib.startswith('lib'):
        lib = lib[3:]
    return lib[:-2] + '.dll'

def dll_to_lib(dll):
    return "lib"+dll[:-3] + "a"

@cache
def create_database():
    res = {}
    win32_db = Path(__file__).parent.parent / "assets" / "win32-db"
    for dll in ["kernel32.dll", "ntdll.dll"]:
        db = win32_db / (dll + ".json")
        with open(db) as f:
            data = json.load(f)
        for function_name, definition in data.items():
            if function_name not in res:
                res[function_name] = Definition(definition, dll=dll)
    return res

def get_definition(function_name):
    db = create_database()
    return db[function_name]

def template_winlib(input, functions):
    env = jinja2.Environment()
    env.filters['hash'] = lambda x: hex(hash_djb2(x))
    with open(input) as f:
        template = env.from_string(f.read())
    definitions = [get_definition(f) for f in functions]
    dlls = {d.dll for d in definitions}
    return template.render({
        "dlls": dlls,
        "entries": [d.to_winlib_entry() for d in definitions]
    })

if __name__ == "__main__":
    # print(get_definition("WinExec"))
    # print(get_definition("VirtualAlloc"))
    # print(get_definition("CreateProcessA"))
    print(template_winlib("assets/winlib.j2.c", ["WinExec"]))
