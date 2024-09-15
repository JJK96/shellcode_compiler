OUTPUT_FORMAT("binary");
/* ENTRY(start); */

BASE = 0x00;

SECTIONS
{
    . = BASE;
    .text : {
        . = BASE;
        /* *(.intro) */
        *(.text)
        *(.func)
    }
}
