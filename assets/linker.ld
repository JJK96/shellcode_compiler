OUTPUT_FORMAT("binary")
SECTIONS {
    .text       (0x0): { *(.crtentry) *(.text) *(.data) *(.rdata*) *(.bss) }
    /DISCARD/ : { *(.eh_frame) *(.note.gnu.property) }
}
