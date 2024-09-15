# C-to-shellcode

## Usage

1. Edit `payload.c`
2. Execute: `python c-to-shellcode.py`
3. Look to the `bin/` directory:
    - `payload.bin` - raw flat binary with compiled `payload.c`
    - `payload.exe` - compiled `payload.c` as a standalone EXE
    - `loader.exe` - compiled `loader.c` with the payload injected

## Caveats

- Use `ALIGN_STACK()` macro before WinAPI call.
- 