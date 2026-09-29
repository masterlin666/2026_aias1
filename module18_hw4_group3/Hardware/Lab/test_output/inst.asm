addi t0, zero, 0
lui x06, 0x00000008
addi x06, x06, 0x00000030
lw t1, 0(t1)
addi t1, t1, -1
add s10, t1, zero
addi a5, zero, -1
lui x18, 0x00000008
addi x18, x18, 0x00000034
lw s2, 0(s2)
lui x08, 0x00000008
addi x08, x08, 0x00000000
jal ra, binary_search
blt a5, zero, fail
j x0, exit
add a2, t0, t1
srli a2, a2, 1
blt s10, a2, fail
blt a2, zero, fail
add t2, a2, zero
slli t2, t2, 2
add t2, t2, s0
lw t2, 0(t2)
beq t2, s2, find
beq t0, t1, fail
blt s2, t2, less
addi t0, a2, 1
j x0, binary_search
addi t1, a2, -1
j x0, binary_search
addi a5, zero, -1
j x0, exit
add a5, a2, zero
j x0, exit
nop
nop
nop
nop
nop
hcf
