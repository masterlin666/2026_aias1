# See LICENSE for license details.

#*****************************************************************************
# sum_negatives_data_hazard.S
#-----------------------------------------------------------------------------
#
# Test data hazard when summing negative numbers.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV32U
RVTEST_CODE_BEGIN






    # Initialize the stack pointer
    addi  sp, sp, -32       # Allocate stack space

    # Load the array address and size
    la    t0, array         # t0 = @array
    lw    t1, size          # t1 = size of the array (10)

    # Initialize the index and result
    li    t2, 0             # t2 = i (index)
    li    t3, 0             # t3 = accumulator (sum)

loop:
    # Check if the loop should terminate
    bge   t2, t1, loop_end  # If i >= size, exit the loop

    # Read the current element of the array (Data Hazard: lw -> add)
    slli  t4, t2, 2         # t4 = i * 4 (calculate array offset)
    add   t4, t4, t0        # t4 = @array[i] (calculate element address)
    lw    t5, 0(t4)         # t5 = array[i] (load current element)

    # Add the element to the result (Data Hazard: use t5)
    add   t3, t3, t5        # sum += array[i]

    # Jump back to the loop
    addi  t2, t2, 1         # i++

    # Jump back to the loop
    j     loop

loop_end:
    # Store the final result in register a0
    mv    a0, t3            # a0 = sum

    ecall






RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA
  

array:  .word -412, -474, -443, -171, -23, -247, -221, -7, -40, -221
size:   .word 10

RVTEST_DATA_END