# HW 14-3: RV32 Bit Manipulation Extension

Group project repository for **Module 14 HW 14-3: Bit Manipulation Extension**.

This project extends the Lab 13-4 / HW 14-2 RV32 emulator by adding the full RV32 Bit Manipulation Extension instructions from the Zba, Zbb, Zbc, and Zbs sub-extensions. The emulator keeps the RV32I base behavior and M extension support from HW 14-2.

## Group Members

| Role | Name | Student ID |
| --- | --- | --- |
| Leader | 吳明叡 | 114064523 |
| Member | 林庭佑 | 111020013 |
| Member | 林名延 | 111062224 |
| Member | 靳宇杰 | 111020035 |

## Repository

- GitLab repository: <https://course.playlab.tw/git/seer0208v2/module14_hw3_group3>
- Main source file: `emulator.cpp`
- Build file: `Makefile`
- Test files: `test_assembly/test_<instruction>.txt`

## Build and Run

Build the emulator:

```bash
make
```

Run the default tests from the `Makefile`:

```bash
make test
```

Run one assembly test manually:

```bash
./emulator test_assembly/test_andn.txt
```

Clean generated files:

```bash
make clean
```

## Implemented Extension Scope

The final merged emulator must support all 32 in-scope RV32 Bit Manipulation instructions:

- Zba: address generation
- Zbb: basic bit manipulation
- Zbc: carryless multiplication
- Zbs: single-bit instructions

Each instruction is implemented in `emulator.cpp` using the same 4-step methodology from Lab 13-4:

1. Add the opcode to the enum.
2. Add the mnemonic to the parser map.
3. Assign the correct instruction format.
4. Implement execution semantics.

## Owner Table

Each owner is responsible for implementing the instruction and adding `test_assembly/test_<instruction>.txt` with at least 3 distinct test cases, including edge cases and expected register values in comments.

| Sub-ext | Mnemonic | Description | Owner |
| --- | --- | --- | --- |
| Zba | `sh1add rd, rs1, rs2` | `rd = (rs1 << 1) + rs2` | 吳明叡 |
| Zba | `sh2add rd, rs1, rs2` | `rd = (rs1 << 2) + rs2` | 林庭佑 |
| Zba | `sh3add rd, rs1, rs2` | `rd = (rs1 << 3) + rs2` | 林名延 |
| Zbb | `andn rd, rs1, rs2` | `rd = rs1 & ~rs2` | 吳明叡 |
| Zbb | `orn rd, rs1, rs2` | <code>rd = rs1 &#124; ~rs2</code> | 林庭佑 |
| Zbb | `xnor rd, rs1, rs2` | `rd = ~(rs1 ^ rs2)` | 靳宇杰 |
| Zbb | `clz rd, rs` | Count leading zeros, from 0 to 32 | 吳明叡 |
| Zbb | `ctz rd, rs` | Count trailing zeros, from 0 to 32 | 林庭佑 |
| Zbb | `cpop rd, rs` | Population count, from 0 to 32 | 林名延 |
| Zbb | `max rd, rs1, rs2` | Signed maximum | 吳明叡 |
| Zbb | `maxu rd, rs1, rs2` | Unsigned maximum | 林名延 |
| Zbb | `min rd, rs1, rs2` | Signed minimum | 林庭佑 |
| Zbb | `minu rd, rs1, rs2` | Unsigned minimum | 靳宇杰 |
| Zbb | `sext.b rd, rs` | Sign-extend byte | 靳宇杰 |
| Zbb | `sext.h rd, rs` | Sign-extend halfword | 林名延 |
| Zbb | `zext.h rd, rs` | Zero-extend halfword | 靳宇杰 |
| Zbb | `rol rd, rs1, rs2` | Rotate left | 吳明叡 |
| Zbb | `ror rd, rs1, rs2` | Rotate right | 林庭佑 |
| Zbb | `rori rd, rs1, shamt` | Rotate right immediate | 林名延 |
| Zbb | `orc.b rd, rs` | Bitwise OR-combine, byte granule | 林名延 |
| Zbb | `rev8 rd, rs` | Byte-reverse register | 靳宇杰 |
| Zbc | `clmul rd, rs1, rs2` | Carry-less multiply, low | 吳明叡 |
| Zbc | `clmulh rd, rs1, rs2` | Carry-less multiply, high | 林庭佑 |
| Zbc | `clmulr rd, rs1, rs2` | Carry-less multiply, reversed | 靳宇杰 |
| Zbs | `bclr rd, rs1, rs2` | Single-bit clear | 吳明叡 |
| Zbs | `bclri rd, rs1, imm` | Single-bit clear immediate | 吳明叡 |
| Zbs | `bext rd, rs1, rs2` | Single-bit extract | 靳宇杰 |
| Zbs | `bexti rd, rs1, imm` | Single-bit extract immediate | 靳宇杰 |
| Zbs | `binv rd, rs1, rs2` | Single-bit invert | 林名延 |
| Zbs | `binvi rd, rs1, imm` | Single-bit invert immediate | 林名延 |
| Zbs | `bset rd, rs1, rs2` | Single-bit set | 林庭佑 |
| Zbs | `bseti rd, rs1, imm` | Single-bit set immediate | 林庭佑 |

## Test Requirements

The final submission should include:

- One test file per Bit Manipulation instruction under `test_assembly/`.
- At least 3 test cases per instruction.
- Expected register values commented next to each instruction.
- Passing regression tests for `test_m_ext.txt`.
- Passing regression tests for the basic Lab 13-3 test file, `test_basic.txt`, if included in the repository.

Suggested test command after all files are added:

```bash
make test
```

## Git Workflow

Each teammate works on a feature branch and opens a merge request into `main`.

Recommended branch names:

- `feature/<name>-zba`
- `feature/<name>-zbb`
- `feature/<name>-zbc`
- `feature/<name>-zbs`

Workflow rules:

- Do not push directly to `main`.
- Each merge request should be reviewed and approved by at least one teammate.
- Resolve conflicts inside the merge request.
- Keep each merge request focused on the assigned instructions and tests.
- Preserve other teammates' changes when resolving shared edits in `emulator.cpp`.

## Deliverables Checklist

- [ ] GitLab repository access granted to all teammates as Maintainer.
- [ ] TA and instructor access granted as Reporter.
- [ ] Group member list completed in this README.
- [ ] Owner table completed in this README.
- [ ] `emulator.cpp` supports all 32 RV32 Bit Manipulation instructions.
- [ ] M extension support from HW 14-2 still works.
- [ ] `test_assembly/` contains one test file per new instruction.
- [ ] Each instruction test file has at least 3 cases with expected values.
- [ ] Merge request history shows at least one reviewed MR per teammate.
