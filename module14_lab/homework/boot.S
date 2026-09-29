# boot.S -- Baremetal startup for RV32 on QEMU virt machine

.section .text.init
.global _start

_start:
    # Set stack pointer to top of 4MB RAM
    # QEMU virt machine RAM starts at 0x80000000
    li sp, 0x80400000

    # Call C main
    call main

    # Halt after main returns
_halt:
    j _halt
