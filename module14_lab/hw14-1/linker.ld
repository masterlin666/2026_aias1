/* linker.ld -- Baremetal linker script for QEMU virt (RV32) */

OUTPUT_ARCH("riscv")
ENTRY(_start)

MEMORY
{
    RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 4M
}

SECTIONS
{
    .text : {
        *(.text.init)
        *(.text*)
    } > RAM

    .rodata : {
        *(.rodata*)
    } > RAM

    .data : {
        *(.data*)
    } > RAM

    .bss : {
        __bss_start = .;
        *(.bss*)
        *(COMMON)
        __bss_end = .;
    } > RAM

    _stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
