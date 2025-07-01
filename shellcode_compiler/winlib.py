from .config import settings
import subprocess
from pathlib import Path
from . import hash_djb2

def lib_to_dll(lib):
    if lib.startswith('lib'):
        lib = lib[3:]
    return lib[:-2] + '.dll'

def definition_to_winlib_entry(dll, definition):
    # Parse definition
    types, _, args = definition.partition('(')
    types = list(filter(lambda x:x and x != "WINBASEAPI", types.split(' ', )))
    function_name = types[-1]
    types = types[:-1]
    literal_args = args[:-2]
    variables = []
    for arg in literal_args.split(", "):
        variables.append(arg.split(' ')[1])

    # Assemble winlib entry
    hash_name = dll[:-4].upper()
    function_hash = hash_djb2(function_name)
    return f"""\
#define HASH_{function_name} {hex(function_hash)}
typedef {types[0]}({types[1]} *{function_name}_t) ({literal_args});
{' '.join(types)} {function_name} ({literal_args}) {{
    {function_name}_t _{function_name} = ({function_name}_t) getFunctionPtr(HASH_{hash_name}, HASH_{function_name});
    return _{function_name}({', '.join(variables)});
}}
"""

def get_definition(function_name):
    cmd = ["rg", "-IN", f"\\b{function_name}\\b *\\(", settings.get('mingw_headers_path')]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode().strip()

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

if __name__ == "__main__":
    func = "WinExec"
    dll = get_library(func)
    definition = get_definition(func)
    print(definition_to_winlib_entry(dll, definition))

