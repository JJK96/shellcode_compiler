# Credits to Michael Schrijver for the basis of this script
ENTRY(_start)
SECTIONS {
    .text       (0x0): { *(.start) *(.text*) *(.data) *(.rdata*) *(.xdata*) *(.pdata*) *(.bss) *(.end) }
    /DISCARD/ : { *(.eh_frame) *(.note.gnu.property) }
}
