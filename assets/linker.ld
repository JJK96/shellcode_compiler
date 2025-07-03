# Credits to Michael Schrijver for the basis of this script
OUTPUT_FORMAT("binary")
SECTIONS {
    .text       (0x0): { *(.start) *(.text*) *(.data) *(.rdata*) *(.bss) *(.end)}
    /DISCARD/ : { *(.eh_frame) *(.note.gnu.property) }
}
