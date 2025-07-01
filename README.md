# Shellcode Compiler

Compile C code to shellcode while allowing the use of Win32 APIs without changes to the source code. In addition, strings and other data can be used without special encoding like stack strings.

Currently, the Win32 APIs that you want to use need to be defined in `assets/winlib.c`. In the future, I'm planning to automatically generate this file based on the imported functions.

## Install

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
