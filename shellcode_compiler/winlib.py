from .config import settings
from . import hash_djb2
from functools import cache
from pathlib import Path
import logging
import json
import jinja2
from textwrap import indent


class InvalidDefinition(Exception):
    pass

class Definition:
    variable_args = False
    parsed = False
    def __init__(self, definition_str, dll=None):
        self.definition_str = definition_str
        self.dll = dll

    def _parse(self):
        types, _, args = self.definition_str.partition('(')
        types = list(filter(lambda x:x and x != "WINBASEAPI", types.split(' ', )))
        self.function_name = types[-1]
        self.types = types[:-1]
        self.retval_types = [t for t in self.types if t not in ["WINAPI", "__cdecl"]]
        self.literal_args = args[:-2]
        self.variables = []
        self.typedef_args = []
        if self.literal_args.lower() != "void":
            for arg in self.literal_args.split(","):
                arg = arg.strip()
                if arg == '...':
                    self.variable_args = True
                    self.typedef_args.append("__builtin_va_list __local_argv")
                else:
                    self.typedef_args.append(arg)
                if not ' ' in arg:
                    continue
                var = arg.split(' ')[-1].lstrip('*')
                self.variables.append(var)

    def parse(self):
        if self.parsed:
            return
        try:
            self._parse()
        except Exception as e:
            logging.error(f"Could not parse: {self.definition_str}")
            raise

    def to_winlib_entry(self):
        self.parse()
        if not self.dll:
            raise Exception("Cannot convert to winlib entry if the DLL is unknown")
        hash_name = self.dll[:-4]
        if self.variable_args:
            dynamic_function_name = "v" + self.function_name
            call = f"""\
__builtin_va_list __local_argv; __builtin_va_start( __local_argv, {', '.join(self.variables)} );
__retval = _{dynamic_function_name}({', '.join(self.variables)}, __local_argv );
__builtin_va_end( __local_argv );
"""
        else:
            dynamic_function_name = self.function_name
            call = f"__retval = _{dynamic_function_name}({', '.join(self.variables)});"
        function_hash = hash_djb2(dynamic_function_name)
        return f"""\
#define HASH_{dynamic_function_name} {hex(function_hash)}
typedef {self.types[0]}({self.types[1]} *{dynamic_function_name}_t) ({', '.join(self.typedef_args)});
{' '.join(self.types)} {self.function_name} ({self.literal_args}) {{
    {dynamic_function_name}_t _{dynamic_function_name} = ({dynamic_function_name}_t) getFunctionPtr(HASH_{hash_name}, HASH_{dynamic_function_name});
    {' '.join(self.retval_types)} __retval;
{indent(call, prefix="    ")}
    return __retval;
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
    for dll in ["kernel32.dll", "ntdll.dll", "msvcrt.dll"]:
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
