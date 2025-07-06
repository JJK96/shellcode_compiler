# Shellcode Compiler

Compile C code to shellcode while allowing the use of Win32 APIs without changes to the source code. In addition, strings and other data can be used without special encoding like stack strings.

The Win32 APIs and standard library functions that you use are automatically detected at link time, after which a `winlib.c` file is generated containing definitions for these functions. Currently only functions in `kernel32.dll`, `ntdll.dll` and `msvcrt.dll` are supported, because these DLLs can reasonably be expected in every process. However, if you need other DLLs, you need to load your required DLL using `LoadLibrary`, change `shellcode_compiler/winlib.py` to include functions from your required DLL and extend [win32-db](https://github.com/JJK96/win32-db) to generate a function definition database for your DLL.

## Install

```
git clone --recurse-submodules https://github.com/jjk96/c-to-shellcode
cd c-to-shellcode
```

```
pip install -e .
```

or 

```
make install
```

Copy `settings.example.toml` to `settings.toml` and fill the necessary values.
You can also install a settings file in ~/.config/shellcode_compiler/settings.toml

## Usage

```
shellcode_compiler compile payload.c
```

This will compile the payload in the `build` directory. The resulting files are:
* `payload.bin`: The shellcode.
* `loader.exe`: A trivial loader to test the shellcode.

## Tests

```
make tests
```

## Credits

* [c-to-shellcode](https://github.com/Print3M/c-to-shellcode) for the initial idea and framework.
* Michael Schrijver for providing me with a nice linker script that enabled me to use normal strings and data in shellcode.
* [BOF2Shellcode](https://github.com/FalconForceTeam/BOF2shellcode) for the implementation of hash-based dynamic API resolving.
