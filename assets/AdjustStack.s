# Based on: https://github.com/mattifestation/PIC_Bindshell/blob/master/PIC_Bindshell/AdjustStack.asm
    .global _start
    .section .start
_start:
    pushq   %rsi                 # Preserve RSI
    movq    %rsp, %rsi           # Save RSP
    andq    $-16, %rsp           # Align RSP to 16 bytes (0xFFFFFFFFFFFFFFF0)
    subq    $32, %rsp            # Allocate homing space (0x20 bytes)
    call    main                 # Call the payload entry point
    movq    %rsi, %rsp           # Restore original RSP
    popq    %rsi                 # Restore RSI
    jmp     end

    .global  __main
__main:
    ret                          #Dummy definition of main because this is required by gcc

    .global end
    .section .end
end:
	ret
