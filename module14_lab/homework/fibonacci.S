.section .text
.global fibonacci_asm

fibonacci_asm:
    # a0 = n
    li   t0, 1
    ble  a0, t0, .Lfinish  # n <= 1, 直接回傳 n (a0)

    li   t2, 1             # F(i-1)
    li   t3, 0             # F(i-2)
    
.Lloop:
    add  t1, t2, t3        # F(i) = F(i-1) + F(i-2)
    mv   t3, t2            # 更新 F(i-2)
    mv   t2, t1            # 更新 F(i-1)
    addi a0, a0, -1
    li   t0, 1
    bgt  a0, t0, .Lloop    # if n > 1 loop

    mv   a0, t1            # 返回結果
.Lfinish:
    ret