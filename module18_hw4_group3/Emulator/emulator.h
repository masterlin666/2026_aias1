#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

#ifndef EMULATOR_H__
#define EMULATOR_H__

// 64 KB
#define MEM_BYTES 0x10000
#define TEXT_OFFSET 0
#define DATA_OFFSET 32768

#define MAX_LABEL_COUNT 128
#define MAX_LABEL_LEN 32
#define MAX_SRC_LEN (1024*1024)

#define VECTOR_LEN 512
#define ELEMENT_WIDTH 8
#define VLMAX VECTOR_LEN/ELEMENT_WIDTH

typedef struct {
	char* src;
	int offset;
} source;

/* Vector Struct for more than 64 bit */
typedef struct {
	uint8_t bytes[VLMAX];
} vector_reg;

typedef enum {
    UNIMPL = 0,

    // Instruction added (Lab/Project custom)
    MUL,
    VLE8_V,
    VSE8_V,
    VADD_VV,
    VMUL_VX,

    // RV32I Base Instruction Set
    ADD, ADDI, AND, ANDI, AUIPC,
    BEQ, BGE, BGEU, BLT, BLTU, BNE,
    JAL, JALR, LB, LBU, LH, LHU,
    LUI, LW, OR, ORI, SB, SH,
    SLL, SLLI, SLT, SLTI, SLTIU, SLTU,
    SRA, SRAI, SRL, SRLI, SUB, SW,
    XOR, XORI, HCF,

    // Zba: Address-generation shift/add operations.
    SH1ADD, SH2ADD, SH3ADD,

    // Zbb: Basic bit-manipulation operations.
    ANDN, ORN, XNOR,
    CLZ, CTZ, CPOP,
    MAX, MAXU, MIN, MINU,
    ROL, ROR, RORI,
    ORC_B, SEXT_H, SEXT_B, ZEXT_H, REV8,

    // Zbs: Single-bit operations.
    BCLR, BCLRI,
    BINV, BINVI,
    BSET, BSETI,
    BEXT, BEXTI
} instr_type;

typedef enum {
	OPTYPE_NONE, // more like "don't care"
	OPTYPE_REG,
	OPTYPE_IMM,
	OPTYPE_LABEL,
} operand_type;
typedef struct {
	operand_type type = OPTYPE_NONE;
	char label[MAX_LABEL_LEN];
	int reg;
	uint32_t imm;

} operand;
typedef struct {
	instr_type op;
	operand a1;
	operand a2;
	operand a3;
	char* psrc = NULL;
	int orig_line=-1;
	bool breakpoint = false;
} instr;

typedef struct {
	char label[MAX_LABEL_LEN];
	int loc = -1;
} label_loc;

uint32_t mem_read(uint8_t*, uint32_t, instr_type);

#endif