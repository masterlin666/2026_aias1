# sum.S -- Array sum in RISC-V assembly
# int array_sum(int *arr, int n);
# Arguments: a0 = pointer to array, a1 = number of elements
# Return:    a0 = sum of all elements

.global array_sum
.type array_sum, @function

array_sum:
    li t0, 0            # t0 = accumulator = 0
    li t1, 0            # t1 = index i = 0

.sum_loop:
    bge t1, a1, .sum_done   # if i >= n, exit loop
    slli t2, t1, 2          # t2 = i * 4 (byte offset for int)
    add t2, a0, t2          # t2 = &arr[i]
    lw t3, 0(t2)            # t3 = arr[i]
    add t0, t0, t3          # accumulator += arr[i]
    addi t1, t1, 1          # i++
    j .sum_loop

.sum_done:
    mv a0, t0               # return accumulator in a0
    ret
