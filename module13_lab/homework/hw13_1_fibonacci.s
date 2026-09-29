# hw13_1_fibonacci.s
# Fibonacci Series -- Recursive Implementation

.data
newline: .string "\n"

.text
.globl main

main:
    addi sp, sp, -16
    sw   ra, 12(sp)
    li   s0, 0       # n = 0
    li   s1, 16      # limit = 16

loop:
    bgt  s0, s1, end_main

    # 呼叫 fibonacci
    mv   a0, s0
    jal  ra, fibonacci
    mv   s2, a0      # 將結果暫存到 s2 (或是 t 暫存器)

    # Venus 印出整數: a0=1, a1=數值
    li   a0, 1
    mv   a1, s2
    ecall
    
    # Venus 印出換行: a0=4, a1=地址
    li   a0, 4
    la   a1, newline
    ecall

    addi s0, s0, 1
    j    loop

end_main:
    lw   ra, 12(sp)
    addi sp, sp, 16
    li   a0, 10      # Venus 退出: a0=10
    ecall

# ========================================================
# fibonacci(n)
# Argument: a0 = n
# Return:   a0 = F(n)
# ========================================================
fibonacci:
    # --- Prologue ---
    # 分配 16 bytes 保持對齊，並保存必要暫存器
    addi sp, sp, -16
    sw   ra, 12(sp)
    sw   s0, 8(sp)   # 用來存當前的 n
    sw   s1, 4(sp)   # 用來存第一次遞迴的結果 F(n-1)

    mv   s0, a0      # s0 = n

    # --- Base Case: F(0) = 0 ---
    li   t0, 0
    beq  s0, t0, finish

    # --- Base Case: F(1) = 1 ---
    li   t0, 1
    beq  s0, t0, finish

    # --- Recursive Step 1: F(n-1) ---
    addi a0, s0, -1  # a0 = n - 1
    jal  ra, fibonacci
    mv   s1, a0      # s1 = F(n-1)

    # --- Recursive Step 2: F(n-2) ---
    addi a0, s0, -2  # a0 = n - 2
    jal  ra, fibonacci
    # 此時 a0 = F(n-2)

    # --- 相加: F(n) = F(n-1) + F(n-2) ---
    add  a0, s1, a0  # a0 = F(n-1) + F(n-2)
    j    epilogue

finish:
    # 針對 Base Case 直接回傳 n (因為 0->0, 1->1)
    mv   a0, s0

epilogue:
    # --- Epilogue ---
    lw   s1, 4(sp)
    lw   s0, 8(sp)
    lw   ra, 12(sp)
    addi sp, sp, 16
    ret