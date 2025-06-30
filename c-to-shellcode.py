#!/usr/bin/env python3
#
# Name  : c-to-shellcode.py
# Author: Print3M
# GitHub: https://github.com/Print3M
import subprocess


def args(arr: list[str]):
    return " ".join(arr)


def run_cmd(cmd: str):
    subprocess.run(cmd, text=True, check=True, shell=True)
    print(f"[+] {cmd}")


LOADER_PAYLOAD_STR = ":PAYLOAD:"

CC = "x86_64-w64-mingw32-gcc-win32"
LD = "x86_64-linux-gnu-ld"
EXE_PAYLOAD_CFLAGS = args(["-fPIC", "-mconsole", "-Os", "-e start", "-nostartfiles"])
BIN_PAYLOAD_CFLAGS = args(
    [
        "-Os",
        "-fPIC",
        "-nostdlib",
        "-nostartfiles",
        "-ffreestanding",
        "-fno-asynchronous-unwind-tables",
        "-fno-ident",
        "-e start",
        "-s",
    ]
)

if __name__ == "__main__":
    # Compile payload C code to object file
    run_cmd(f"{CC} -c payload.c -o bin/payload.o  {BIN_PAYLOAD_CFLAGS}")

    exe = False
    if exe:
        # Produce PE .exe with payload (WinAPI included)
        run_cmd(f"{CC} bin/payload.o -o bin/payload.exe {EXE_PAYLOAD_CFLAGS}")
        print("[+] bin/payload.exe is ready!")
    else:
        # Produce flat binary with payload
        run_cmd(
            f"{LD} -T assets/linker.ld bin/payload.o -o bin/payload.bin"
        )

        # Convert flat binary into C array of bytes
        with open("bin/payload.bin", "rb") as f:
            bytes = bytearray(f.read())

        size = len(bytes)
        print(f"[+] Binary payload size: {size} bytes")

        payload = ""
        for byte in bytes:
            payload += "\\" + hex(byte).lstrip("0")

        # Inject payload into loader source code
        with open("assets/loader.c", "r") as f:
            loader = f.read()

        loader = loader.replace(LOADER_PAYLOAD_STR, payload)

        with open("bin/loader.c", "w") as f:
            f.write(loader)

        # Compile loader
        run_cmd(f"{CC} bin/loader.c -o bin/loader.exe")

        print("[+] bin/loader.exe is ready!")
