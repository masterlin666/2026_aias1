# Lab 12-2: Recursive Factorial
# Computes factorial(n) and prints the result

.data
input_n:  .word 7                      # compute 7! = 5040
msg:      .string "factorial = "

.text
.globl main

main:
    # Save ra (main calls functions)
    addi sp, sp, -16
    sw   ra, 12(sp)

    # Load n and call factorial
    la   t0, input_n
    lw   a0, 0(t0)          # a0 = n
    jal  ra, factorial       # a0 = factorial(n)

    # Save result, print message
    mv   s0, a0              # save result
    la   a0, msg
    li   a7, 4               # print string
    ecall
    mv   a0, s0              # restore result
    li   a7, 1               # print integer
    ecall

    # Restore and exit
    lw   ra, 12(sp)
    addi sp, sp, 16
    li   a7, 10
    ecall

# ============================================
# factorial(n):
#   if n <= 1: return 1
#   else: return n * factorial(n - 1)
#
# Arguments:  a0 = n
# Returns:    a0 = n!
# ============================================
factorial:
    # TODO: Prologue -- allocate stack frame, save ra and s0
    addi sp, sp, -16
    sw   ra, 12(sp)
    sw   s0, 8(sp)

    # TODO: Save n into s0
    mv   s0, a0

    # TODO: Base case -- if n <= 1, return 1
    li   t0, 1
    bgt  s0, t0, fact_recurse
    li   a0, 1
    j    fact_epilogue

fact_recurse:
    # TODO: Set up argument (n-1) and make recursive call
    addi a0, s0, -1
    jal  ra, factorial

    # TODO: Multiply n * factorial(n-1)
    mul  a0, s0, a0

fact_epilogue:
    # TODO: Epilogue -- restore s0, ra, deallocate stack, return
    lw   s0, 8(sp)
    lw   ra, 12(sp)
    addi sp, sp, 16
    ret
