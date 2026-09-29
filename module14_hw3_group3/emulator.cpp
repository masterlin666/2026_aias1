/* emulator.cpp -- RISC-V RV32I Text-Based Emulator */

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <cstdint>
#include <algorithm>
#include <climits>

/* ============================================================
 * Enumerations
 * ============================================================ */

enum class Opcode {
    // RV32I Base Integer
    ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, SLT, SLTU,
    ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI,
    LW, SW,
    BEQ, BNE, BLT, BGE, BLTU, BGEU,
    JAL, JALR,
    LUI, AUIPC,
    // Pseudo-instructions
    NOP, LI, MV, LA, J, CALL, RET,
    // M Extension
    MUL, MULHU, REM, REMU,
    // Zba - address generation
    SH1ADD,SH2ADD,SH3ADD,
    // Zbb - basic bit manipulation
    ANDN, CLZ, MAX, ROL,
    XNOR, MINU, SEXT_B, ZEXT_H, REV8,
    ORN, CTZ, MIN, ROR,
    CPOP, MAXU, SEXT_H, RORI, ORC_B, 
    // Zbc - carryless multiplication
    CLMUL, CLMULR, CLMULH,
    // Zbs - single-bit instructions
    BCLR, BCLRI, BEXT, BEXTI, BSET, BSETI,BINV, BINVI,
    UNKNOWN
};

enum class Format {
    R_TYPE, I_TYPE, S_TYPE, B_TYPE, U_TYPE, J_TYPE, PSEUDO, UNKNOWN
};

/* ============================================================
 * Instruction Structure
 * ============================================================ */

struct Instruction {
    Opcode opcode;
    Format format;
    int rd, rs1, rs2;
    int32_t imm;
    std::string label;
    std::string raw_text;
};

/* ============================================================
 * Utility Functions
 * ============================================================ */

std::string trim(const std::string &s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    size_t end = s.find_last_not_of(" \t\r\n");
    if (start == std::string::npos) return "";
    return s.substr(start, end - start + 1);
}

std::string to_lower(const std::string &s) {
    std::string result = s;
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

std::vector<std::string> split_operands(const std::string &s) {
    std::vector<std::string> parts;
    std::stringstream ss(s);
    std::string token;
    while (std::getline(ss, token, ',')) {
        std::string t = trim(token);
        if (!t.empty()) parts.push_back(t);
    }
    return parts;
}

int parse_register(const std::string &s) {
    std::string t = trim(s);
    if (t.empty()) return -1;

    // x0..x31
    if (t[0] == 'x' || t[0] == 'X') {
        return std::stoi(t.substr(1));
    }

    // ABI names
    static const std::map<std::string, int> abi = {
        {"zero", 0}, {"ra", 1}, {"sp", 2}, {"gp", 3}, {"tp", 4},
        {"t0", 5}, {"t1", 6}, {"t2", 7},
        {"s0", 8}, {"fp", 8}, {"s1", 9},
        {"a0", 10}, {"a1", 11}, {"a2", 12}, {"a3", 13},
        {"a4", 14}, {"a5", 15}, {"a6", 16}, {"a7", 17},
        {"s2", 18}, {"s3", 19}, {"s4", 20}, {"s5", 21},
        {"s6", 22}, {"s7", 23}, {"s8", 24}, {"s9", 25},
        {"s10", 26}, {"s11", 27},
        {"t3", 28}, {"t4", 29}, {"t5", 30}, {"t6", 31}
    };

    auto it = abi.find(to_lower(t));
    if (it != abi.end()) return it->second;
    return -1;
}

int32_t parse_immediate(const std::string &s) {
    std::string t = trim(s);
    if (t.empty()) return 0;

    // Handle hex
    if (t.size() > 2 && t[0] == '0' && (t[1] == 'x' || t[1] == 'X')) {
        return (int32_t)std::stoul(t, nullptr, 16);
    }
    // Handle negative hex
    if (t.size() > 3 && t[0] == '-' && t[1] == '0' && (t[2] == 'x' || t[2] == 'X')) {
        return -(int32_t)std::stoul(t.substr(1), nullptr, 16);
    }
    return std::stoi(t);
}

/* ============================================================
 * Opcode Parsing
 * ============================================================ */

Opcode parse_opcode(const std::string &s) {
    static const std::map<std::string, Opcode> opcodes = {
        // R-type
        {"add", Opcode::ADD}, {"sub", Opcode::SUB},
        {"and", Opcode::AND}, {"or", Opcode::OR}, {"xor", Opcode::XOR},
        {"sll", Opcode::SLL}, {"srl", Opcode::SRL}, {"sra", Opcode::SRA},
        {"slt", Opcode::SLT}, {"sltu", Opcode::SLTU},
        // I-type
        {"addi", Opcode::ADDI}, {"andi", Opcode::ANDI},
        {"ori", Opcode::ORI}, {"xori", Opcode::XORI},
        {"slti", Opcode::SLTI}, {"sltiu", Opcode::SLTIU},
        {"slli", Opcode::SLLI}, {"srli", Opcode::SRLI}, {"srai", Opcode::SRAI},
        // Load/Store
        {"lw", Opcode::LW}, {"sw", Opcode::SW},
        // Branch
        {"beq", Opcode::BEQ}, {"bne", Opcode::BNE},
        {"blt", Opcode::BLT}, {"bge", Opcode::BGE},
        {"bltu", Opcode::BLTU}, {"bgeu", Opcode::BGEU},
        // Jump
        {"jal", Opcode::JAL}, {"jalr", Opcode::JALR},
        // Upper immediate
        {"lui", Opcode::LUI}, {"auipc", Opcode::AUIPC},
        // Pseudo
        {"nop", Opcode::NOP}, {"li", Opcode::LI}, {"mv", Opcode::MV},
        {"la", Opcode::LA}, {"j", Opcode::J}, {"call", Opcode::CALL},
        {"ret", Opcode::RET},
        // M Extension
        {"mul", Opcode::MUL}, {"mulhu", Opcode::MULHU},
        {"rem", Opcode::REM}, {"remu", Opcode::REMU},
        // Zba - address generation
        {"sh1add", Opcode::SH1ADD}, {"sh2add", Opcode::SH2ADD},{"sh3add", Opcode::SH3ADD},
        // Zbb - basic bit manipulation
        {"andn", Opcode::ANDN}, {"clz", Opcode::CLZ},
        {"max", Opcode::MAX}, {"rol", Opcode::ROL},
        {"xnor", Opcode::XNOR}, {"minu", Opcode::MINU}, {"sext.b", Opcode::SEXT_B}, {"zext.h", Opcode::ZEXT_H}, {"rev8", Opcode::REV8},
        {"orn", Opcode::ORN}, {"ctz", Opcode::CTZ}, {"min", Opcode::MIN}, {"ror", Opcode::ROR},{"cpop", Opcode::CPOP},
        {"maxu", Opcode::MAXU},
        {"sext.h", Opcode::SEXT_H},
        {"rori", Opcode::RORI},
        {"orc.b", Opcode::ORC_B},
        // Zbc - carryless multiplication
        {"clmul", Opcode::CLMUL}, {"clmulr", Opcode::CLMULR}, {"clmulh", Opcode::CLMULH},
        // Zbs - single-bit instructions
        {"bclr", Opcode::BCLR}, {"bclri", Opcode::BCLRI}, {"bext", Opcode::BEXT}, {"bexti", Opcode::BEXTI}, {"bset", Opcode::BSET}, {"bseti", Opcode::BSETI},{"binv", Opcode::BINV},
        {"binvi", Opcode::BINVI}
    };
    auto it = opcodes.find(to_lower(s));
    return (it != opcodes.end()) ? it->second : Opcode::UNKNOWN;
}

Format get_format(Opcode op) {
    switch (op) {
        case Opcode::ADD: case Opcode::SUB: case Opcode::AND:
        case Opcode::OR: case Opcode::XOR: case Opcode::SLL:
        case Opcode::SRL: case Opcode::SRA: case Opcode::SLT:
        case Opcode::SLTU:
        case Opcode::SH3ADD: case Opcode::MAXU: case Opcode::BINV:
            return Format::R_TYPE;
        case Opcode::ADDI: case Opcode::ANDI: case Opcode::ORI:
        case Opcode::XORI: case Opcode::SLTI: case Opcode::SLTIU:
        case Opcode::SLLI: case Opcode::SRLI: case Opcode::SRAI:
        case Opcode::JALR:
        case Opcode::CPOP: case Opcode::SEXT_H: case Opcode::RORI: 
        case Opcode::ORC_B: case Opcode::BINVI:
            return Format::I_TYPE;
        case Opcode::LW:
            return Format::I_TYPE;
        case Opcode::SW:
            return Format::S_TYPE;
        case Opcode::BEQ: case Opcode::BNE: case Opcode::BLT:
        case Opcode::BGE: case Opcode::BLTU: case Opcode::BGEU:
            return Format::B_TYPE;
        case Opcode::LUI: case Opcode::AUIPC:
            return Format::U_TYPE;
        case Opcode::JAL:
            return Format::J_TYPE;
        case Opcode::NOP: case Opcode::LI: case Opcode::MV:
        case Opcode::LA: case Opcode::J: case Opcode::CALL:
        case Opcode::RET:
            return Format::PSEUDO;
        // M Extension
        case Opcode::MUL: case Opcode::MULHU:
        case Opcode::REM: case Opcode::REMU:
        // Zba - address generation
        case Opcode::SH1ADD: case Opcode::SH2ADD:
        // Zbb - basic bit manipulation
        case Opcode::ANDN: case Opcode::MAX:
        case Opcode::ROL:
        case Opcode::XNOR: case Opcode::MINU: case Opcode::ZEXT_H:
        case Opcode::ORN: case Opcode::MIN: case Opcode::ROR:
        // Zbc - carryless multiplication
        case Opcode::CLMUL: case Opcode::CLMULR: case Opcode::CLMULH:
        // Zbs - single-bit instructions
        case Opcode::BCLR: case Opcode::BEXT: case Opcode::BSET:
            return Format::R_TYPE;
        // Zbb - basic bit manipulation
        case Opcode::CLZ: 
        case Opcode::SEXT_B: case Opcode::REV8:
        case Opcode::CTZ:
        // Zbs - single-bit instructions
        case Opcode::BCLRI: case Opcode::BEXTI: case Opcode::BSETI:
            return Format::I_TYPE;
        default:
            return Format::UNKNOWN;
    }
}

/* ============================================================
 * Emulator Class
 * ============================================================ */

class Emulator {
private:
    int32_t regs[32];
    int pc;
    std::vector<Instruction> program;
    std::map<std::string, int> labels;
    bool halted;
    int instruction_count;

    /* Memory for load/store (simple 64KB array) */
    static const int MEM_SIZE = 65536;
    int32_t memory[MEM_SIZE / 4];  /* Word-addressed */

public:
    Emulator() : pc(0), halted(false), instruction_count(0) {
        for (int i = 0; i < 32; i++) regs[i] = 0;
        for (int i = 0; i < MEM_SIZE / 4; i++) memory[i] = 0;
    }

    void set_reg(int rd, int32_t val) {
        if (rd != 0) regs[rd] = val;
    }

    int32_t get_reg(int rs) const {
        return regs[rs];
    }

    /* ---- Instruction Parsing ---- */

    Instruction parse_instruction(const std::string &line) {
        Instruction inst;
        inst.rd = inst.rs1 = inst.rs2 = 0;
        inst.imm = 0;
        inst.raw_text = line;

        // Strip inline comments
        std::string clean = line;
        size_t comment_pos = clean.find('#');
        if (comment_pos != std::string::npos) {
            clean = clean.substr(0, comment_pos);
        }
        clean = trim(clean);

        // Split into opcode and operands
        size_t space_pos = clean.find_first_of(" \t");
        std::string op_str;
        std::string operands_str;
        if (space_pos != std::string::npos) {
            op_str = trim(clean.substr(0, space_pos));
            operands_str = trim(clean.substr(space_pos));
        } else {
            op_str = clean;
        }

        inst.opcode = parse_opcode(op_str);
        inst.format = get_format(inst.opcode);

        if (operands_str.empty()) return inst;

        auto operands = split_operands(operands_str);

        static auto is_rd_rs1_instruction = [](Opcode op) -> bool {
            switch (op) {
                // Base & Zbb instructions that only use rd and rs1
                case Opcode::CLZ:
                case Opcode::CPOP:
                case Opcode::SEXT_B:
                case Opcode::SEXT_H:
                case Opcode::REV8:
                case Opcode::CTZ:
                case Opcode::ORC_B:
                    return true;
                default:
                    return false;
            }
        };

        switch (inst.format) {
            case Format::R_TYPE:
                if (operands.size() >= 3) {
                    inst.rd = parse_register(operands[0]);
                    inst.rs1 = parse_register(operands[1]);
                    inst.rs2 = parse_register(operands[2]);
                } else if (inst.opcode == Opcode::ZEXT_H) {
                    inst.rd = parse_register(operands[0]);
                    inst.rs1 = parse_register(operands[1]);
                    inst.rs2 = 0; // hardcoded into zero, same as `parse_register('zero')`
                }
                break;
            case Format::I_TYPE:
                if (inst.opcode == Opcode::LW && operands.size() >= 2) {
                    // lw rd, offset(rs1)
                    inst.rd = parse_register(operands[0]);
                    std::string mem_op = trim(operands[1]);
                    size_t paren = mem_op.find('(');
                    if (paren != std::string::npos) {
                        inst.imm = parse_immediate(mem_op.substr(0, paren));
                        std::string reg_part = mem_op.substr(paren + 1);
                        reg_part.erase(std::remove(reg_part.begin(), reg_part.end(), ')'), reg_part.end());
                        inst.rs1 = parse_register(reg_part);
                    }
                } 
                // 只要是只有兩個運算元的指令，統一在這裡處理
                else if (is_rd_rs1_instruction(inst.opcode) && operands.size() >= 2) {
                    inst.rd = parse_register(operands[0]);
                    inst.rs1 = parse_register(operands[1]);
                } 
                // 剩下的標準 I-type (rd, rs1, imm)
                else if (operands.size() >= 3) {
                    inst.rd = parse_register(operands[0]);
                    inst.rs1 = parse_register(operands[1]);
                    inst.imm = parse_immediate(operands[2]);
                }
                break;
            case Format::S_TYPE:
                if (operands.size() >= 2) {
                    // sw rs2, offset(rs1)
                    inst.rs2 = parse_register(operands[0]);
                    std::string mem_op = trim(operands[1]);
                    size_t paren = mem_op.find('(');
                    if (paren != std::string::npos) {
                        inst.imm = parse_immediate(mem_op.substr(0, paren));
                        std::string reg_part = mem_op.substr(paren + 1);
                        reg_part.erase(std::remove(reg_part.begin(), reg_part.end(), ')'), reg_part.end());
                        inst.rs1 = parse_register(reg_part);
                    }
                }
                break;
            case Format::B_TYPE:
                if (operands.size() >= 3) {
                    inst.rs1 = parse_register(operands[0]);
                    inst.rs2 = parse_register(operands[1]);
                    inst.label = trim(operands[2]);
                }
                break;
            case Format::U_TYPE:
                if (operands.size() >= 2) {
                    inst.rd = parse_register(operands[0]);
                    inst.imm = parse_immediate(operands[1]);
                }
                break;
            case Format::J_TYPE:
                if (operands.size() >= 2) {
                    inst.rd = parse_register(operands[0]);
                    inst.label = trim(operands[1]);
                } else if (operands.size() == 1) {
                    inst.rd = 1; // ra
                    inst.label = trim(operands[0]);
                }
                break;
            case Format::PSEUDO:
                switch (inst.opcode) {
                    case Opcode::LI:
                        if (operands.size() >= 2) {
                            inst.rd = parse_register(operands[0]);
                            inst.imm = parse_immediate(operands[1]);
                        }
                        break;
                    case Opcode::MV:
                        if (operands.size() >= 2) {
                            inst.rd = parse_register(operands[0]);
                            inst.rs1 = parse_register(operands[1]);
                        }
                        break;
                    case Opcode::J:
                        if (operands.size() >= 1) {
                            inst.label = trim(operands[0]);
                        }
                        break;
                    case Opcode::CALL:
                        if (operands.size() >= 1) {
                            inst.label = trim(operands[0]);
                        }
                        break;
                    case Opcode::LA:
                        if (operands.size() >= 2) {
                            inst.rd = parse_register(operands[0]);
                            inst.label = trim(operands[1]);
                        }
                        break;
                    default:
                        break;
                }
                break;
            default:
                break;
        }

        return inst;
    }

    /* ---- Program Loading ---- */

    void load_program(const std::string &filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "ERROR: Cannot open file: " << filename << std::endl;
            halted = true;
            return;
        }

        std::vector<std::string> lines;
        std::string line;
        while (std::getline(file, line)) {
            lines.push_back(line);
        }
        file.close();

        // Pass 1: Collect labels
        int inst_idx = 0;
        for (auto &l : lines) {
            std::string trimmed = l;
            size_t comment_pos = trimmed.find('#');
            if (comment_pos != std::string::npos) {
                trimmed = trimmed.substr(0, comment_pos);
            }
            trimmed = trim(trimmed);
            if (trimmed.empty() || trimmed[0] == '#') continue;

            size_t colon = trimmed.find(':');
            if (colon != std::string::npos) {
                std::string lbl = trim(trimmed.substr(0, colon));
                labels[lbl] = inst_idx;
                std::string remainder = trim(trimmed.substr(colon + 1));
                if (!remainder.empty() && remainder[0] != '#') {
                    inst_idx++;
                }
                continue;
            }
            inst_idx++;
        }

        // Pass 2: Parse instructions
        for (auto &l : lines) {
            std::string trimmed = l;
            size_t comment_pos = trimmed.find('#');
            if (comment_pos != std::string::npos) {
                trimmed = trimmed.substr(0, comment_pos);
            }
            trimmed = trim(trimmed);
            if (trimmed.empty() || trimmed[0] == '#') continue;

            size_t colon = trimmed.find(':');
            if (colon != std::string::npos) {
                trimmed = trim(trimmed.substr(colon + 1));
                if (trimmed.empty() || trimmed[0] == '#') continue;
            }

            Instruction inst = parse_instruction(trimmed);
            program.push_back(inst);
        }

        std::cout << "Loaded " << program.size() << " instructions, "
                  << labels.size() << " labels." << std::endl;
    }

    /* ---- Execution ---- */

    void execute(const Instruction &inst) {
        int next_pc = pc + 1;

        switch (inst.opcode) {
            /* --- R-type --- */
            case Opcode::ADD:
                set_reg(inst.rd, get_reg(inst.rs1) + get_reg(inst.rs2));
                break;
            case Opcode::SUB:
                set_reg(inst.rd, get_reg(inst.rs1) - get_reg(inst.rs2));
                break;
            case Opcode::AND:
                set_reg(inst.rd, get_reg(inst.rs1) & get_reg(inst.rs2));
                break;
            case Opcode::OR:
                set_reg(inst.rd, get_reg(inst.rs1) | get_reg(inst.rs2));
                break;
            case Opcode::XOR:
                set_reg(inst.rd, get_reg(inst.rs1) ^ get_reg(inst.rs2));
                break;
            case Opcode::SLL:
                set_reg(inst.rd, get_reg(inst.rs1) << (get_reg(inst.rs2) & 0x1F));
                break;
            case Opcode::SRL:
                set_reg(inst.rd,
                    (int32_t)((uint32_t)get_reg(inst.rs1) >> (get_reg(inst.rs2) & 0x1F)));
                break;
            case Opcode::SRA:
                set_reg(inst.rd, get_reg(inst.rs1) >> (get_reg(inst.rs2) & 0x1F));
                break;
            case Opcode::SLT:
                set_reg(inst.rd, (get_reg(inst.rs1) < get_reg(inst.rs2)) ? 1 : 0);
                break;
            case Opcode::SLTU:
                set_reg(inst.rd,
                    ((uint32_t)get_reg(inst.rs1) < (uint32_t)get_reg(inst.rs2)) ? 1 : 0);
                break;

            /* --- I-type arithmetic --- */
            case Opcode::ADDI:
                set_reg(inst.rd, get_reg(inst.rs1) + inst.imm);
                break;
            case Opcode::ANDI:
                set_reg(inst.rd, get_reg(inst.rs1) & inst.imm);
                break;
            case Opcode::ORI:
                set_reg(inst.rd, get_reg(inst.rs1) | inst.imm);
                break;
            case Opcode::XORI:
                set_reg(inst.rd, get_reg(inst.rs1) ^ inst.imm);
                break;
            case Opcode::SLTI:
                set_reg(inst.rd, (get_reg(inst.rs1) < inst.imm) ? 1 : 0);
                break;
            case Opcode::SLTIU:
                set_reg(inst.rd,
                    ((uint32_t)get_reg(inst.rs1) < (uint32_t)inst.imm) ? 1 : 0);
                break;
            case Opcode::SLLI:
                set_reg(inst.rd, get_reg(inst.rs1) << (inst.imm & 0x1F));
                break;
            case Opcode::SRLI:
                set_reg(inst.rd,
                    (int32_t)((uint32_t)get_reg(inst.rs1) >> (inst.imm & 0x1F)));
                break;
            case Opcode::SRAI:
                set_reg(inst.rd, get_reg(inst.rs1) >> (inst.imm & 0x1F));
                break;

            /* --- Load/Store --- */
            case Opcode::LW: {
                int32_t addr = get_reg(inst.rs1) + inst.imm;
                int word_idx = addr / 4;
                if (word_idx >= 0 && word_idx < MEM_SIZE / 4) {
                    set_reg(inst.rd, memory[word_idx]);
                } else {
                    std::cerr << "ERROR: Memory read out of bounds at addr="
                              << addr << std::endl;
                    halted = true;
                }
                break;
            }
            case Opcode::SW: {
                int32_t addr = get_reg(inst.rs1) + inst.imm;
                int word_idx = addr / 4;
                if (word_idx >= 0 && word_idx < MEM_SIZE / 4) {
                    memory[word_idx] = get_reg(inst.rs2);
                } else {
                    std::cerr << "ERROR: Memory write out of bounds at addr="
                              << addr << std::endl;
                    halted = true;
                }
                break;
            }
            //procat change5 new instructions
            // Zba: sh3add (rd = (rs1 << 3) + rs2)
            case Opcode::SH3ADD:
                set_reg(inst.rd, (int32_t)(((uint32_t)get_reg(inst.rs1) << 3) + (uint32_t)get_reg(inst.rs2)));
                break;

            // Zbb: cpop (Count population - count set bits)
            case Opcode::CPOP: {
                uint32_t v = (uint32_t)get_reg(inst.rs1);
                int count = 0;
                while (v) { v &= (v - 1); count++; }
                set_reg(inst.rd, count);
                break;
            }

            // Zbb: maxu (Unsigned maximum)
            case Opcode::MAXU: {
                uint32_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                set_reg(inst.rd, (int32_t)(a > b ? a : b));
                break;
            }

            // Zbb: sext.h (Sign-extend halfword)
            case Opcode::SEXT_H: {
                int16_t val = (int16_t)(get_reg(inst.rs1) & 0xFFFFU);
                set_reg(inst.rd, (int32_t)val);
                break;
            }

            // Zbb: rori (Rotate right immediate)
            case Opcode::RORI: {
                uint32_t v = (uint32_t)get_reg(inst.rs1);
                uint32_t sh = (uint32_t)inst.imm & 0x1F;
                set_reg(inst.rd, (int32_t)((v >> sh) | (v << ((32 - sh) & 0x1F))));
                break;
            }

            // Zbb: orc.b (Bitwise OR-combine, byte granule)
            case Opcode::ORC_B: {
                uint32_t v = (uint32_t)get_reg(inst.rs1);
                uint32_t res = 0;
                for (int i = 0; i < 4; ++i) {
                    if ((v >> (i * 8)) & 0xFFU) res |= (0xFFU << (i * 8));
                }
                set_reg(inst.rd, (int32_t)res);
                break;
            }

            // Zbs: binv (Bit invert - flip bit at index rs2)
            case Opcode::BINV: {
                uint32_t v = (uint32_t)get_reg(inst.rs1);
                uint32_t index = (uint32_t)get_reg(inst.rs2) & 0x1F;
                set_reg(inst.rd, (int32_t)(v ^ (1u << index)));
                break;
            }

            // Zbs: binvi (Bit invert immediate)
            case Opcode::BINVI: {
                uint32_t v = (uint32_t)get_reg(inst.rs1);
                uint32_t index = (uint32_t)inst.imm & 0x1F;
                set_reg(inst.rd, (int32_t)(v ^ (1u << index)));
                break;
            }

            /* --- Branches --- */
            case Opcode::BEQ:
                if (get_reg(inst.rs1) == get_reg(inst.rs2))
                    next_pc = labels[inst.label];
                break;
            case Opcode::BNE:
                if (get_reg(inst.rs1) != get_reg(inst.rs2))
                    next_pc = labels[inst.label];
                break;
            case Opcode::BLT:
                if (get_reg(inst.rs1) < get_reg(inst.rs2))
                    next_pc = labels[inst.label];
                break;
            case Opcode::BGE:
                if (get_reg(inst.rs1) >= get_reg(inst.rs2))
                    next_pc = labels[inst.label];
                break;
            case Opcode::BLTU:
                if ((uint32_t)get_reg(inst.rs1) < (uint32_t)get_reg(inst.rs2))
                    next_pc = labels[inst.label];
                break;
            case Opcode::BGEU:
                if ((uint32_t)get_reg(inst.rs1) >= (uint32_t)get_reg(inst.rs2))
                    next_pc = labels[inst.label];
                break;

            /* --- Jump --- */
            case Opcode::JAL:
                set_reg(inst.rd, pc + 1);
                next_pc = labels[inst.label];
                break;
            case Opcode::JALR:
                set_reg(inst.rd, pc + 1);
                next_pc = (get_reg(inst.rs1) + inst.imm);
                break;

            /* --- Upper Immediate --- */
            case Opcode::LUI:
                set_reg(inst.rd, inst.imm << 12);
                break;
            case Opcode::AUIPC:
                set_reg(inst.rd, pc + (inst.imm << 12));
                break;

            /* --- Pseudo-instructions --- */
            case Opcode::NOP:
                break;
            case Opcode::LI:
                set_reg(inst.rd, inst.imm);
                break;
            case Opcode::MV:
                set_reg(inst.rd, get_reg(inst.rs1));
                break;
            case Opcode::J:
                next_pc = labels[inst.label];
                break;
            case Opcode::CALL:
                set_reg(1, pc + 1);  // ra = return address
                next_pc = labels[inst.label];
                break;
            case Opcode::RET:
                next_pc = get_reg(1);  // jump to ra
                break;

            // M Extension
            case Opcode::MUL:
                set_reg(inst.rd, get_reg(inst.rs1) * get_reg(inst.rs2));
                break;
            case Opcode::MULHU: {
                uint64_t a = (uint64_t)(uint32_t)get_reg(inst.rs1);
                uint64_t b = (uint64_t)(uint32_t)get_reg(inst.rs2);
                uint64_t result = a * b;
                set_reg(inst.rd, (int32_t)(result >> 32));
                break;
            }
            case Opcode::REM: {
                int32_t a = get_reg(inst.rs1);
                int32_t b = get_reg(inst.rs2);
                if (b == 0) {
                    set_reg(inst.rd, a);
                } else if (a == INT32_MIN && b == -1) {
                    set_reg(inst.rd, 0);
                } else {
                    set_reg(inst.rd, a % b);
                }
                break;
            }
            case Opcode::REMU: {
                uint32_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                if (b == 0) {
                    set_reg(inst.rd, (int32_t)a);
                } else {
                    set_reg(inst.rd, (int32_t)(a % b));
                }
                break;
            }

            // Zba - address generation
            case Opcode::SH1ADD: {
                uint32_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                set_reg(inst.rd, (int32_t)((a << 1) + b));
                break;
            }

            case Opcode::SH2ADD: {
                uint32_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                set_reg(inst.rd, (int32_t)((a << 2) + b));
                break;
            }

            // Zbb - basic bit manipulation
            case Opcode::ANDN:
                set_reg(inst.rd, get_reg(inst.rs1) & ~get_reg(inst.rs2));
                break;
            case Opcode::CLZ: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                int count = 0;
                for (int bit = 31; bit >= 0; bit--) {
                    if ((value & (1u << bit)) != 0) break;
                    count++;
                }
                set_reg(inst.rd, count);
                break;
            }
            case Opcode::MAX: {
                int32_t a = get_reg(inst.rs1);
                int32_t b = get_reg(inst.rs2);
                set_reg(inst.rd, (a > b) ? a : b);
                break;
            }
            case Opcode::ROL: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                uint32_t shamt = (uint32_t)get_reg(inst.rs2) & 0x1F;
                set_reg(inst.rd, (int32_t)((value << shamt) | (value >> ((32 - shamt) & 0x1F))));
                break;
            }
            case Opcode::XNOR: {
                set_reg(inst.rd, ~(get_reg(inst.rs1) ^ get_reg(inst.rs2)));
                break;
            }
            case Opcode::MINU: {
                uint32_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                set_reg(inst.rd, (int32_t)(a < b ? a : b));
                break;
            }
            case Opcode::SEXT_B: {
                int32_t val = (int32_t)(int8_t)(get_reg(inst.rs1) & 0xFFU);
                set_reg(inst.rd, val);
                break;
            }
            case Opcode::ZEXT_H: {
                set_reg(inst.rd, (get_reg(inst.rs1) & 0xFFFFU));
                break;
            }
            case Opcode::REV8: {
                uint32_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t res = (a >> 24) | 
                            ((a >> 8) & 0x0000FF00) | 
                            ((a << 8) & 0x00FF0000) | 
                            (a << 24);
                set_reg(inst.rd, (int32_t)res);
                break;
            }
            case Opcode::ORN:
                set_reg(inst.rd, get_reg(inst.rs1) | ~get_reg(inst.rs2));
                break;
            case Opcode::CTZ: {
                uint32_t val = (uint32_t)get_reg(inst.rs1);
                int count = 0;
                if (val == 0) {
                    count = 32;
                } else {
                    while (!(val & 1)) {
                        count++;
                        val >>= 1;
                    }
                }
                set_reg(inst.rd, count);
                break;
            }
            case Opcode::MIN: {
                int32_t a = get_reg(inst.rs1);
                int32_t b = get_reg(inst.rs2);
                set_reg(inst.rd, (a < b) ? a : b);
                break;
            }
            case Opcode::ROR: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                uint32_t shamt = (uint32_t)get_reg(inst.rs2) & 0x1F;
                set_reg(inst.rd, (int32_t)((value >> shamt) | (value << ((32 - shamt) & 0x1F))));
                break;
            }
            // Zbc - carryless multiplication
            case Opcode::CLMUL: {
                uint64_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                uint64_t result = 0;
                for (int bit = 0; bit < 32; bit++) {
                    if ((b & (1u << bit)) != 0) {
                        result ^= a << bit;
                    }
                }
                set_reg(inst.rd, (int32_t)(uint32_t)result);
                break;
            }
            case Opcode::CLMULR: {
                uint64_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                uint64_t result = 0;
                for (int i = 0; i < 32; i++) {
                    if ((b >> i) & 1) {
                        result ^= (a >> (31 - i));
                    }
                }
                set_reg(inst.rd, (int32_t)(uint32_t)result);
                break;
            }
            case Opcode::CLMULH: {
                uint64_t a = (uint32_t)get_reg(inst.rs1);
                uint32_t b = (uint32_t)get_reg(inst.rs2);
                uint64_t result = 0;
                for (int i = 0; i < 32; i++) {
                    if ((b & (1u << i)) != 0) {
                        result ^= a << i;
                    }
                }
                set_reg(inst.rd, (int32_t)(uint32_t)(result >> 32));
                break;
            }
            
            // Zbs - single-bit instructions
            case Opcode::BCLR: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                uint32_t bit = (uint32_t)get_reg(inst.rs2) & 0x1F;
                set_reg(inst.rd, (int32_t)(value & ~(1u << bit)));
                break;
            }
            case Opcode::BCLRI: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                uint32_t bit = (uint32_t)inst.imm & 0x1F;
                set_reg(inst.rd, (int32_t)(value & ~(1u << bit)));
                break;
            }
            case Opcode::BEXT: {
                int i = get_reg(inst.rs2) & 0x1F;
                set_reg(inst.rd, ((get_reg(inst.rs1) >> i) & 1));
                break;
            }
            case Opcode::BEXTI: {
                int i = inst.imm & 0x1F;
                set_reg(inst.rd, ((get_reg(inst.rs1) >> i) & 1));
                break;
            }
            case Opcode::BSET: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                uint32_t index = (uint32_t)get_reg(inst.rs2) & 0x1F;
                set_reg(inst.rd, value | (1u << index));
                break;
            }
            case Opcode::BSETI: {
                uint32_t value = (uint32_t)get_reg(inst.rs1);
                int index = inst.imm & 0x1F;
                set_reg(inst.rd, value | (1u << index));
                break;
            }
            /* --- Unknown --- */
            default:
                std::cerr << "ERROR: Unknown/unsupported instruction at PC="
                          << pc << ": " << inst.raw_text << std::endl;
                halted = true;
                return;
        }

        pc = next_pc;
        instruction_count++;
    }

    /* ---- Main Run Loop ---- */

    void run() {
        while (!halted && pc >= 0 && pc < (int)program.size()) {
            Instruction &inst = program[pc];
            execute(inst);
            regs[0] = 0;  // x0 is always zero
        }

        if (!halted && pc >= (int)program.size()) {
            std::cout << "\n--- Program finished (fell off end) ---" << std::endl;
        }
    }

    /* ---- Register Dump ---- */

    void dump_registers() const {
        std::cout << "\n=== Register State ===" << std::endl;
        for (int i = 0; i < 32; i++) {
            if (regs[i] != 0) {
                std::cout << "  x" << i << " = " << regs[i]
                          << " (0x" << std::hex << (uint32_t)regs[i]
                          << std::dec << ")" << std::endl;
            }
        }
        std::cout << "  PC = " << pc << std::endl;
        std::cout << "  Instructions executed: " << instruction_count << std::endl;
    }
};

/* ============================================================
 * Main
 * ============================================================ */

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <assembly_file.txt>" << std::endl;
        return 1;
    }

    Emulator emu;
    emu.load_program(argv[1]);
    emu.run();
    emu.dump_registers();

    return 0;
}
