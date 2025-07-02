from .config import settings
import re
import subprocess
from pathlib import Path
from . import hash_djb2
import logging

class InvalidDefinition(Exception):
    pass

class Definition:
    def __init__(self, definition_str, dll=None):
        self.definition_str = definition_str
        self.dll = dll
        if not self.is_valid():
            raise InvalidDefinition()
        try:
            self.parse()
        except Exception as e:
            logging.error(f"Could not parse: {self.definition_str}")
            raise

    def is_valid(self):
        return self.definition_str.count('(') == 1

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
        hash_name = self.dll[:-4].upper()
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

def get_definition(function_name):
    cmd = ["rg", "-IN", f"\\b{function_name}\\b *\\(", settings.get('mingw_headers_path')]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return Definition(p.stdout.decode().strip())

def get_library(function_name):
    cmd = ["rg", "-ali", f"\\b{function_name}\\b", settings.get('mingw_lib_path')]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if 'libkernel32.a' in p.stdout.decode():
        return "kernel32.dll"
    if 'libntdll.a' in p.stdout.decode():
        return "ntdll.dll"
    sizes = {}
    for line in p.stdout.decode().splitlines():
        lib = Path(line)
        size = lib.stat().st_size
        sizes[line] = size
    biggest, size = sorted(sizes.items(), key=lambda x:x[1])[0]
    return lib_to_dll(Path(biggest).name)

def get_symbols_for_dll(dll):
    lib = Path(settings.get('mingw_lib_path')) / dll_to_lib(dll)
    cmd = ["x86_64-w64-mingw32-objdump", "-t", lib]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout.decode().splitlines():
        # Cut to the symbol names
        line = line[67:]
        if not line or re.search(r"^[._\d]|\.c?$", line):
            continue
        yield line
    
def get_definitions_for_dll(dll):
    cmd = ["rg", "-IN", "WINAPI", settings.get('mingw_headers_path')]
    regex = r'\b\(' + '|'.join(get_symbols_for_dll(dll)) + r'\)\b'
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout.decode().splitlines():
        if "virtual" in line:
            continue
        if re.search(regex, line):
            try:
                yield Definition(line.strip(), dll=dll)
            except InvalidDefinition:
                continue

if __name__ == "__main__":
    # func = "WinExec"
    # dll = get_library(func)
    # definition = get_definition(func)
    # definition.dll = dll
    # print(definition.to_winlib_entry())
    for d in get_definitions_for_dll("kernel32.dll"):
        print(d.to_winlib_entry())

