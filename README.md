# Shellcode Compiler

Compile C code to shellcode while allowing the use of Win32 APIs without changes to the source code. In addition, strings and other data can be used without special encoding like stack strings.

## Install

```
pip install .
```

or 

```
make install
```

Copy `settings.example.toml` to `settings.toml` and fill the necessary values.
You can also install a settings file in ~/.config/shellcode_compiler/settings.toml

## Usage

```
shellcode_compiler --help
```

## Tests

```
make tests
```
