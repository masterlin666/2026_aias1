.text
main:
    li x1, 0x0000f000
    li x2, 0x00000004
    li x3, 0x00000020
    li x4, 0x0f0f0707
    li x5, 0x00ff00ff
    li x6, 0x80000001

    # RAW dependency 1: sh1add writes x7, andn immediately reads x7.
    sh1add x7, x1, x2
    andn   x8, x7, x4

    # RAW dependency 2: andn writes x8, clz immediately reads x8.
    clz    x9, x8

    # RAW dependency 3: clz writes x9, max immediately reads x9.
    max    x10, x9, x3

    # RAW dependency 4: max writes x10, rol immediately reads x10.
    rol    x11, x10, x2

    # RAW dependency 5: rol writes x11, orc.b immediately reads x11.
    orc.b  x12, x11

    # xnor
    xnor   x17, x6, x5

    # minu (unsigned min)
    minu   x18, x17, x6

    # sext.b (sign extend byte)
    sext.b x19, x18

    # zext.h (zero extend halfword)
    zext.h x20, x19

    # rev8 (byte reverse)
    rev8   x21, x20

    #  bclr/bclri.
    bclr   x13, x12, x2
    bclri  x14, x13, 31

    # SH3ADD
    sh3add x17, x14, x2

    # maxu
    maxu   x18, x17, x6

    # binv
    binv   x19, x18, x2

    # binvi
    binvi  x20, x19, 31

    # cpop
    cpop   x21, x20

    # rori
    rori   x22, x21, 4
    
    # sext.h
    sext.h x24, x23
    
    # extract bit[4]
    bext   x22, x21, x2
    # extract bit0
    bexti  x23, x22, 0

    sh2add x24, x1, x2
    orn    x25, x24, x4
    ctz    x26, x25
    min    x27, x26, x3
    ror    x28, x27, x2
    bset   x29, x28, x2
    bseti  x30, x29, 31

    # Keep dependent results live in final register dump.
    add    x15, x14, x8
    add    x16, x15, x9

    hcf