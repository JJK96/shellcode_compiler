#!/usr/bin/env bash
echo $@ > linker-args.txt
for arg in $@; do
    if [[ "$arg" = *.payload.*.o ]]; then
        echo "Saving $arg to payload.o"
        cp "$arg" "./payload.o"
    elif [[ "$arg" = *.o ]]; then
        cp "$arg" "./$(basename "$arg")_saved.o"
    fi
done > fake-linker.log
