## HW 13-3: Instruction Encoding (20 points)

### Instruction 1: `sub x10, x11, x12` (4 pts)

**Format:** R-type

Field | Value | Bits |
|-------|-------|------|
| funct7 | 0x20 | 0100000 |
| rs2 | x12 | 01100 |
| rs1 | x11 | 01011 |
| funct3 | 0x0 | 000 |
| rd | x10 | 01010 |
| opcode | 0x33 | 0110011 |

**Binary:** `01000000110001011000010100110011`
**Hex:** `0x40C58533`

### Instruction 2: `lw x15, 12(x8)` (4 pts)

**Format:** I-type

## Instruction 2: `lw x15, 12(x8)` (4 pts)

**Format:** I-type

| Field | Value | Bits |
|-------|-------|------|
| imm[11:0] | 12 | 000000001100 |
| rs1 | x8 | 01000 |
| funct3 | 0x2 | 010 |
| rd | x15 | 01111 |
| opcode | 0x03 | 0000011 |

**Binary:** `00000000110001000010011110000011`
**Hex:** `0x00C42783`

### Instruction 3: `sw x14, -8(x2)` (4 pts)

**Format:** S-type

| Field | Value | Bits |
|-------|-------|------|
| imm[11:5] | 0x7F | 1111111 |
| rs2 | x14 | 01110 |
| rs1 | x2 | 00010 |
| funct3 | 0x2 | 010 |
| imm[4:0] | 0x18 | 11000 |
| opcode | 0x23 | 0100011 |

**Binary:** `11111110111000010010110000100011`
**Hex:** `0xFEE12C23`
### Instruction 4: `bne x5, x6, +16` (4 pts)

**Format:** B-type

| Field | Value | Bits |
|-------|-------|------|
| imm[12] | 0 | 0 |
| imm[10:5] | 0 | 000000 |
| rs2 | x6 | 00110 |
| rs1 | x5 | 00101 |
| funct3 | 0x1 | 001 |
| imm[4:1] | 8 | 1000 |
| imm[11] | 0 | 0 |
| opcode | 0x63 | 1100011 |

**Binary:** `00000000011000101001100001100011`
**Hex:** `0x00629863`

### Instruction 5: `addi x9, x0, -1` (4 pts)

**Format:** I-type

|Field | Value | Bits |
|-------|-------|------|
| imm[11:0] | -1 | 111111111111 |
| rs1 | x0 | 00000 |
| funct3 | 0x0 | 000 |
| rd | x9 | 01001 |
| opcode | 0x13 | 0010011 |

**Binary:** `11111111111100000000010010010011`
**Hex:** `0xFFF00493`

### Verification
將待驗證的五條指令編寫為 .s 彙編檔案，並載入 Venus Editor
點擊 "Assemble" 將彙編原始碼轉換為 RISC-V 機器二進位碼。
![](https://course.playlab.tw/md/uploads/06775bf9-685c-4910-b950-e014b56e3101.png)
