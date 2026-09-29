# HW 18-4: Bitmanip Extension on Pipelined CPU

Group project repository for extending a pipelined RV32I CPU with the RISC-V Bitmanip instructions from Zba, Zbb, and Zbs.

The base design is the HW 17-1 pipelined CPU. This project adds Bitmanip support across:

- Emulator execution in `Emulator/emulator.cpp`
- Machine-code translation in `Emulator/translate.cpp`
- Pipelined Chisel CPU decode, ALU execution, and hazard detection under `Hardware/Lab/src/main/scala/acal_lab09/PipelinedCPU`
- Assembly tests under `riscv-test`

## Group Members

| # | Name | Student ID | School | GitLab Username | Role |
|---:|---|---|---|---|---|
| 1 | 吳明叡 | 114064523 | NTHU | seer0208v2 | Group leader |
| 2 | 林庭佑 | 111020013 | NTHU | 12345 | Member |
| 3 | 林名延 | 111062224 | NTHU | procat | Member |
| 4 | 靳宇杰 | 111020035 | NTHU | yuchieh | Member |

## Instruction Ownership

| Num | Mnemonic | Category | Owner |
|---:|---|---|---|
| 1 | `clz rd, rs` | Zbb - Count leading zeros | 吳明叡 |
| 2 | `ctz rd, rs` | Zbb - Count trailing zeros | 林庭佑 |
| 3 | `cpop rd, rs` | Zbb - Population count | 林名延 |
| 4 | `andn rd, rs1, rs2` | Zbb - AND with complement | 吳明叡 |
| 5 | `orn rd, rs1, rs2` | Zbb - OR with complement | 林庭佑 |
| 6 | `xnor rd, rs1, rs2` | Zbb - Exclusive NOR | 靳宇杰 |
| 7 | `min rd, rs1, rs2` | Zbb - Minimum signed | 林庭佑 |
| 8 | `max rd, rs1, rs2` | Zbb - Maximum signed | 吳明叡 |
| 9 | `minu rd, rs1, rs2` | Zbb - Minimum unsigned | 靳宇杰 |
| 10 | `maxu rd, rs1, rs2` | Zbb - Maximum unsigned | 林名延 |
| 11 | `sext.b rd, rs` | Zbb - Sign-extend byte | 靳宇杰 |
| 12 | `sext.h rd, rs` | Zbb - Sign-extend halfword | 林名延 |
| 13 | `bset rd, rs1, rs2` | Zbs - Bit set | 林庭佑 |
| 14 | `bclr rd, rs1, rs2` | Zbs - Bit clear | 吳明叡 |
| 15 | `binv rd, rs1, rs2` | Zbs - Bit invert | 林名延 |
| 16 | `bext rd, rs1, rs2` | Zbs - Bit extract | 靳宇杰 |
| 17 | `bseti rd, rs1, imm` | Zbs - Bit set immediate | 林庭佑 |
| 18 | `bclri rd, rs1, imm` | Zbs - Bit clear immediate | 吳明叡 |
| 19 | `binvi rd, rs1, imm` | Zbs - Bit invert immediate | 林名延 |
| 20 | `bexti rd, rs1, imm` | Zbs - Bit extract immediate | 靳宇杰 |
| 21 | `ror rd, rs1, rs2` | Zbb - Rotate right | 林庭佑 |
| 22 | `rol rd, rs1, rs2` | Zbb - Rotate left | 吳明叡 |
| 23 | `rori rd, rs1, imm` | Zbb - Rotate right immediate | 林名延 |
| 24 | `sh1add rd, rs1, rs2` | Zba - Shift-and-add by 1 | 吳明叡 |
| 25 | `sh2add rd, rs1, rs2` | Zba - Shift-and-add by 2 | 林庭佑 |
| 26 | `sh3add rd, rs1, rs2` | Zba - Shift-and-add by 3 | 林名延 |
| 27 | `rev8 rd, rs` | Zbb - Byte-reverse | 靳宇杰 |
| 28 | `zext.h rd, rs` | Zbb - Zero-extend halfword | 靳宇杰 |
| 29 | `orc.b rd, rs` | Zbb - OR-combine bytes | 吳明叡 |

## Implementation Notes

### Emulator

The emulator layer should recognize all 29 Bitmanip mnemonics, translate them into RV32 machine code, and execute the corresponding behavior.

- Add execution behavior in `Emulator/emulator.cpp`
- Add instruction parsing and encoding in `Emulator/translate.cpp`
- Keep RV32 behavior explicit: shifts and bit indexes use the low 5 bits of `rs2` or immediate values

### Pipelined CPU

The Chisel hardware layer extends the existing HW 17-1 pipelined CPU.

- ALU operations are implemented in `Hardware/Lab/src/main/scala/acal_lab09/PipelinedCPU/DatapathModule/DatapathComponent/ALU.scala`
- Decode and ALU select generation are implemented in `Hardware/Lab/src/main/scala/acal_lab09/PipelinedCPU/Controller/Controller.scala`
- Bitmanip R-type and I-type encodings must produce unique `ALUSel` values using the instruction `funct7`, `funct3`, and immediate fields where needed

### Hazard Detection

The pipelined-track requirement is that Bitmanip instructions participate correctly in data-hazard detection.

When adding decode support, update the Controller signals so every new Bitmanip instruction reports the correct register usage:

- `is_D_use_rs1`
- `is_D_use_rs2`
- `is_E_use_rd`
- `is_M_use_rd`
- `is_W_use_rd`

R-type Bitmanip instructions use both `rs1` and `rs2`. I-type Bitmanip instructions use `rs1` and write `rd`, but do not use `rs2`. This is required so back-to-back RAW dependencies are detected or forwarded correctly.

## Required Tests

Create `hw18_4_hazard.asm` with at least five RAW dependencies involving Bitmanip instructions. The emulator and pipelined hardware register dumps must match exactly.

Run the new integration test:

```bash
cd Hardware/Lab
bash ./load_test_data.sh hw18_4_hazard
sbt 'Test/runMain acal_lab09.topTest'
```

Re-run existing pipeline hazard tests:

```bash
cd Hardware/Lab
bash ./load_test_data.sh -s TestDataHazard
sbt 'Test/runMain acal_lab09.topTest'

bash ./load_test_data.sh sum_negatives_data_hazard
sbt 'Test/runMain acal_lab09.topTest'
```

## Test Results

| Test | Status | Notes |
|---|---|---|
| `hw18_4_hazard.asm` | TBD | Emulator and hardware dumps should match |
| `TestDataHazard.S` | TBD | Existing data hazard test must still pass |
| `sum_negatives_data_hazard.S` | TBD | Existing full-test hazard program must still pass |

## Git Workflow

Each teammate works on a feature branch and opens a Merge Request against `main`.

Recommended branch names:

- `feature/<chinese_name>`

Before merging:

- At least one teammate reviews the Merge Request
- Conflicts in shared files are resolved in the MR
- The owner table above is updated for completed instructions
- Relevant emulator and hardware tests are run

