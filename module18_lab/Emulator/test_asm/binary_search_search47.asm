# s0: base address of array, s1: array size, s2: the search element
# return index at a5, if not found put -1 in a5
.data
array:          .word 2, 5, 8, 11, 16, 21, 23, 29, 34, 38, 41, 47
array_size:     .word 12
search_element: .word 47
.text
main:
    addi t0, zero, 0
    la   t1, array_size
    lw   t1, 0(t1)
    addi t1, t1, -1
    add  s10, t1, zero
    addi a5, zero, -1
    la   s2, search_element
    lw   s2, 0(s2)
    la   s0, array
    jal  ra, binary_search
    blt  a5, zero, Fail
    j exit
binary_search:
    add  a2, t0, t1
    srli a2, a2, 1
    blt  s10, a2, Fail
    blt  a2, zero, Fail
    add  t2, a2, zero
    slli t2, t2, 2
    add  t2, t2, s0
    lw   t2, 0(t2)
    beq  t2, s2, Find
    beq  t0, t1, Fail
    blt  s2, t2, less
greater:
    addi t0, a2, 1
    j binary_search
less:
    addi t1, a2, -1
    j binary_search
Fail:
    addi a5, zero, -1
    j exit
Find:
    add  a5, a2, zero
    j exit
exit:
    hcf
