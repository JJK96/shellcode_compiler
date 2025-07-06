# Shellcode Compiler

Compile C code to shellcode while allowing the use of Win32 APIs without changes to the source code. In addition, strings and other data can be used without special encoding like stack strings.

The Win32 APIs and standard library functions that you use are automatically detected at link time, after which a `winlib.c` file is generated containing definitions for these functions. Currently only functions in `kernel32.dll`, `ntdll.dll` and `msvcrt.dll` are supported, because these DLLs can reasonably be expected in every process. However, if you need other DLLs, you need to load your required DLL using `LoadLibrary`, change `shellcode_compiler/winlib.py` to include functions from your required DLL and extend [win32-db] to generate a function definition database for your DLL.

## Install

```
git clone --recurse-submodules https://github.com/jjk96/shellcode_compiler
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

## Caveats

I have to be honest, I have not tested every edge-case and I might have taken some shortcuts here and there. Below follows a list of caveats that I can think of at the moment:

* The shellcode (mainly the loader in `winlib.c`) assumes that all used DLLs are already loaded in the process. If your DLL is not loaded, you can load it manually using `LoadLibrary`. You can also resolve this generally by including the logic for loading missing DLLs from [BOF2Shellcode]. The reason I did not do that here is that I want to avoid storing unnecessary strings in the shellcode.
* My parsing logic for C headers is very ad-hoc, it might parse some function headers incorrectly, resulting in incorrect code in `winlib.c`. This might be fixed in the future by including an actual C parser.
* I only tested a very limited set of Windows API and Standard library functions (`WinExec`, `CreateProcessA`, `ExpandEnvironmentStringsA`, `VirtualAlloc`, `VirtualProtect` and `printf`). I'm assuming my code works for any other Windows API function, but I might be wrong. If you encounter anything, it should not be too hard to fix.
* The library uses Windows API functions in a trivial way. For more OPSEC, you probably want to use indirect syscalls or something else. It should not be hard to fork and modify the project to support this.
* I use `Mingw` headers and libraries. These might have subtle differences with Windows SDK headers. If you run into such issues, you can adapt the [win32-db] project to use the Windows SDK headers or generate similar JSON output yourself.

## Tests

Not implemented yet. Test your shellcode before deloyment!

```
make tests
```

## Credits

* [c-to-shellcode](https://github.com/Print3M/c-to-shellcode) for the initial idea and framework.
* Michael Schrijver for providing me with a nice linker script that enabled me to use normal strings and data in shellcode.
* [BOF2Shellcode] for the implementation of hash-based dynamic API resolving.

[BOF2Shellcode]: https://github.com/FalconForceTeam/BOF2shellcode
[win32-db]: https://github.com/JJK96/win32-db
