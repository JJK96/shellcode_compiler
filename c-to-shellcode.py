#!/usr/bin/env python3
# Based on: https://github.com/Print3M
import subprocess

def args(arr: list[str]):
    return " ".join(arr)


def run_cmd(cmd: str):
    subprocess.run(cmd, text=True, check=True, shell=True)
    print(f"[+] {cmd}")


CC = "x86_64-w64-mingw32-gcc-win32"
LD = "x86_64-linux-gnu-ld"
EXE_PAYLOAD_CFLAGS = args(["-fPIC", "-mconsole", "-Os"])
BIN_PAYLOAD_CFLAGS = args(
    [
        "-Os",
        "-fPIC",
        "-nostdlib",
        "-nostartfiles",
        "-ffreestanding",
        "-fno-asynchronous-unwind-tables",
        "-fno-ident",
        "-Wl,--no-seh",
        "-fno-optimize-sibling-calls",
        "-ffunction-sections",
        "-DWINBASEAPI=", #Do not import from DLLs, but statically
    ]
)

def template(input, output, data):

    # Inject payload into loader source code
    with open(input, "r") as f:
        contents = f.read()

    for k,v in data.items():
        if isinstance(v, bytearray):
            payload = ""
            for byte in v:
                payload += "\\" + hex(byte).lstrip("0")
            v = payload
        contents = contents.replace(f":{k}:", v)

    with open(output, "w") as f:
        f.write(contents)

if __name__ == "__main__":
    # Compile payload C code to object file
    run_cmd(f"{CC} -c payload.c -o bin/payload.o  {BIN_PAYLOAD_CFLAGS}")

    exe = False
    if exe:
        # Produce PE .exe with payload (WinAPI included)
        run_cmd(f"{CC} -c assets/winlib.c -o bin/winlib.o {BIN_PAYLOAD_CFLAGS}")
        run_cmd(f"{CC} bin/payload.o bin/winlib.o -o bin/payload.exe {EXE_PAYLOAD_CFLAGS}")
        print("[+] bin/payload.exe is ready!")
    else:
        run_cmd(f"{CC} -c assets/AdjustStack.s -o bin/AdjustStack.o  {BIN_PAYLOAD_CFLAGS}")
        run_cmd(f"{CC} -c assets/winlib.c -o bin/winlib.o {BIN_PAYLOAD_CFLAGS}")
        # Produce flat binary with payload
        run_cmd(
            f"{LD} -T assets/linker.ld bin/payload.o bin/winlib.o bin/AdjustStack.o -o bin/payload.bin --gc-sections"
        )

        # Convert flat binary into C array of bytes
        with open("bin/payload.bin", "rb") as f:
            bytes = bytearray(f.read())

        size = len(bytes)
        print(f"[+] Binary payload size: {size} bytes")

        template("assets/loader.c", "bin/loader.c", {
            "PAYLOAD": bytes
        })

        # Compile loader
        run_cmd(f"{CC} bin/loader.c -o bin/loader.exe")

        print("[+] bin/loader.exe is ready!")
