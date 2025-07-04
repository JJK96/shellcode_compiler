CC = x86_64-w64-mingw32-gcc-win32
LD = x86_64-linux-gnu-ld
EXE_PAYLOAD_CFLAGS = -fPIC -mconsole -Os
BIN_PAYLOAD_CFLAGS = \
 -Os\
 -fPIC\
 -nostdlib\
 -nostartfiles\
 -ffreestanding\
 -fno-asynchronous-unwind-tables\
 -fno-ident\
 -Wl,--no-seh\
 -fno-optimize-sibling-calls\
 -ffunction-sections\
 -DWINBASEAPI= #Do not import from DLLs, but statically

loader.exe: loader.c
	${CC} $^ -o $@

loader.c: loader.template.c payload.bin
	shellcode_compiler template $< PAYLOAD=@payload.bin > $@

payload.bin: linker.ld payload.o winlib.o AdjustStack.o
	${LD} -T $^ -o $@ --gc-sections

payload.o: payload.c
	# Compile payload C code to object file
	${CC} -c $^ -o $@ ${BIN_PAYLOAD_CFLAGS}

functions.txt: linker.ld payload.o AdjustStack.o
	# Determine undefined references based on linking errors
	${LD} -T $^ -o /dev/null --gc-sections 2>&1 | awk -F\` '/undefined reference/{print substr($$(NF), 1, length($$(NF))-1)}' > $@

winlib.c: winlib.j2.c functions.txt
	shellcode_compiler winlib $^ > $@

winlib.o: winlib.c
	${CC} -c $^ -o $@ ${BIN_PAYLOAD_CFLAGS}

AdjustStack.o: AdjustStack.s
	${CC} -c $^ -o $@ ${BIN_PAYLOAD_CFLAGS}

exe: payload.exe

payload.exe: winlib.o payload.o
	${CC} $^ -o $@ ${EXE_PAYLOAD_CFLAGS}

