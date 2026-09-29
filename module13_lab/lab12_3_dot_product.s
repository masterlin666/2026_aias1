# Lab 12-3 Part 3: Dot Product

.data
vec_a:   .word 1, 2, 3, 4, 5
vec_b:   .word 10, 20, 30, 40, 50
vec_n:   .word 5
msg_dot: .string "Dot product: "

.text
.globl main

main:
    addi sp, sp, -16
    sw   ra, 12(sp)

    la   a0, vec_a
    la   a1, vec_b
    la   t0, vec_n
    lw   a2, 0(t0)
    jal  ra, dot_product

    mv   s0, a0
    la   a0, msg_dot
    li   a7, 4
    ecall
    mv   a0, s0
    li   a7, 1
    ecall

    lw   ra, 12(sp)
    addi sp, sp, 16
    li   a7, 10
    ecall

# ============================================
# YOUR IMPLEMENTATION HERE
# Expected result: 1*10 + 2*20 + 3*30 + 4*40 + 5*50 = 550
# ============================================
dot_product:
    # TODO: Implement dot_product
    # Arguments: a0 = pointer to array a, a1 = pointer to array b, a2 = n
    # Returns:   a0 = dot product

    # --- Your code below ---




    # --- Your code above ---
    ret
