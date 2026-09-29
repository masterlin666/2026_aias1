# Lab 12-1: Array Copy Program
# Copies elements from src array to dest array and prints results

.data
src:     .word 11, 22, 33, 44, 55, 66, 77, 88
dest:    .space 32                      # 8 words = 32 bytes (initialized to 0)
n:       .word 8
newline: .string "\n"

.text
.globl main

main:
    # Load addresses and count
    la   s0, src            # s0 = base address of src
    la   s1, dest           # s1 = base address of dest
    la   t0, n
    lw   s2, 0(t0)          # s2 = n (number of elements)
    li   s3, 0              # s3 = i (loop counter)

copy_loop:
    bge  s3, s2, print_setup   # if i >= n, done copying
    slli t1, s3, 2          # t1 = i * 4 (byte offset)
    add  t2, s0, t1         # t2 = &src[i]
    add  t3, s1, t1         # t3 = &dest[i]
    lw   t4, 0(t2)          # t4 = src[i]
    sw   t4, 0(t3)          # dest[i] = src[i]
    addi s3, s3, 1          # i++
    j    copy_loop

print_setup:
    # Print all elements of dest array
    li   s3, 0              # reset i = 0

print_loop:
    bge  s3, s2, exit       # if i >= n, done printing
    slli t1, s3, 2          # t1 = i * 4
    add  t2, s1, t1         # t2 = &dest[i]
    lw   a0, 0(t2)          # a0 = dest[i]
    li   a7, 1              # print integer
    ecall
    la   a0, newline        # print newline
    li   a7, 4              # print string
    ecall
    addi s3, s3, 1          # i++
    j    print_loop

exit:
    li   a7, 10             # exit
    ecall
