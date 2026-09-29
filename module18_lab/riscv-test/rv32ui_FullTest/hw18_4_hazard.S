# See LICENSE for license details.

#*****************************************************************************
# hw18_4_hazard.S
#-----------------------------------------------------------------------------
#
# HW 18-4 reference test — RAW data hazards involving Bitmanip instructions.
# Exercises the Controller hazard-detection signals (is_D_use_rs1 / is_D_use_rs2 /
# is_E_use_rd / is_M_use_rd / is_W_use_rd) for Bitmanip R-type and I-type variants.
#
# The program writes a checksum into a0 (x10). On a correctly extended pipelined
# CPU, a0 == 0x52  at termination. A pipeline that misses any of the 5 Bitmanip
# RAW chains will produce a different value, exposing the bug.
#
# Encoding: instructions are emitted via `.insn r` / `.insn i` to avoid relying
# on a toolchain configured with -march=rv32i_zba_zbb_zbs.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV32U
RVTEST_CODE_BEGIN

    # ----- Setup -----
    li      t0, 0x0000F000      # 4 leading zeros, 12 trailing zeros
    li      t1, 0x000000FF      # 8 set bits
    li      t2, 0xFF00FF00      # alternating bytes
    li      t3, 0xAAAAAAAA      # alternating bits

    # =====================================================================
    # Chain 1: clz writes t4, next instruction reads t4 at EXE distance
    #   clz t4, t0     ->  t4 = 16  (4 leading zeros + (28-16)? actually: x0000F000 has 16 leading zeros)
    #   addi t5, t4, 1 ->  t5 = 17  (EXE-to-ID RAW)
    # =====================================================================
    # clz t4, t0       (Zbb: funct7=0110000, rs2=0, funct3=001, opcode=0010011 [I-type variant])
    .insn r 0b0010011, 0b001, 0b0110000, t4, t0, x0
    addi    t5, t4, 1               # RAW on t4 (EXE-to-ID)

    # =====================================================================
    # Chain 2: cpop writes s0, next instruction reads s0 (MEM-to-ID after 1 bubble)
    #   cpop s0, t1    ->  s0 = 8
    #   nop
    #   xor s1, s0, t5 ->  s1 = 8 ^ 17 = 25 = 0x19
    # =====================================================================
    # cpop s0, t1      (Zbb: funct7=0110000, rs2=2, funct3=001, opcode=0010011)
    .insn r 0b0010011, 0b001, 0b0110000, s0, t1, x2
    nop
    xor     s1, s0, t5              # RAW on s0 (MEM-to-ID after one bubble)

    # =====================================================================
    # Chain 3: andn writes s2, immediate consumer reads s2 (EXE-to-ID)
    #   andn s2, t2, t3   -> s2 = 0xFF00FF00 & ~0xAAAAAAAA = 0xFF00FF00 & 0x55555555 = 0x55005500
    #   add s3, s2, t1    -> s3 = 0x55005500 + 0xFF = 0x550055FF
    # =====================================================================
    # andn s2, t2, t3   (Zbb: funct7=0100000, funct3=111, opcode=0110011 [R-type])
    .insn r 0b0110011, 0b111, 0b0100000, s2, t2, t3
    add     s3, s2, t1              # RAW on s2 (EXE-to-ID, R-type produced)

    # =====================================================================
    # Chain 4: rori (I-type Bitmanip) writes s4, next instruction reads s4
    #   rori s4, t0, 4    -> rotate 0x0000F000 right by 4 = 0x00000F00
    #   slli s5, s4, 4    -> s5 = 0x0000F000
    # =====================================================================
    # rori s4, t0, 4   (Zbb: funct7=0110000, shamt=4, funct3=101, opcode=0010011 [I-type])
    .insn i 0b0010011, 0b101, s4, t0, 0x604     # imm = (0110000 << 5) | 00100 = 0x604
    slli    s5, s4, 4               # RAW on s4 (EXE-to-ID, I-type produced)

    # =====================================================================
    # Chain 5: sh1add writes s6, consumer reads s6 (Zba R-type, EXE-to-ID)
    #   sh1add s6, t0, t1  -> s6 = (t0 << 1) + t1 = 0x0001E000 + 0xFF = 0x0001E0FF
    #   sub s7, s6, t1     -> s7 = 0x0001E000
    # =====================================================================
    # sh1add s6, t0, t1   (Zba: funct7=0010000, funct3=010, opcode=0110011)
    .insn r 0b0110011, 0b010, 0b0010000, s6, t0, t1
    sub     s7, s6, t1              # RAW on s6 (EXE-to-ID)

    # =====================================================================
    # Final checksum: low byte of (s1 xor s3 xor s5 xor s7) ought to be 0x52
    # if all 5 chains executed correctly.
    # =====================================================================
    xor     a0, s1, s3
    xor     a0, a0, s5
    xor     a0, a0, s7
    andi    a0, a0, 0xFF

    ecall                            # terminate

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
