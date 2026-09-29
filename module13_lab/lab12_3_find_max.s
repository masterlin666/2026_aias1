# Lab 12-3: find_max function
# Arguments: a0 = pointer to int array, a1 = n (array size)
# Returns:   a0 = maximum value in the array

.data
test_array: .word 14, 7, 92, 3, 45, 28, 61, 5, 83, 17
test_n:     .word 10
msg_max:    .string "Maximum value: "

.text
.globl main

main:
    addi sp, sp, -16
    sw   ra, 12(sp)

    la   a0, test_array
    la   t0, test_n
    lw   a1, 0(t0)
    jal  ra, find_max

    mv   s0, a0              # save result
    la   a0, msg_max
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
# ============================================
find_max:
    # TODO: Implement find_max
    # Hint: This is a leaf function -- no need to save ra or use s-registers
    # 1. Load array[0] into a register (this is your initial max)
    # 2. Loop from i=1 to n-1
    # 3. Load array[i], compare with max, update if larger
    # 4. Return max in a0

    # --- Your code below ---




    # --- Your code above ---
    ret
