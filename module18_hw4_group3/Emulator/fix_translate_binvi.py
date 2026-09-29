from pathlib import Path
import re
path = Path('translate.cpp')
text = path.read_text(encoding='utf-8')
pattern = re.compile(r'''(            case BINVI:\n                binary = \(0x04 << 2\) \+ 0x03; // opcode = 0010011 \(OP-IMM\)\n                binary \+= i\.a1\.reg << 7;     // rd\n                binary \+= 0b001 << 12;       // funct3\n                binary \+= i\.a2\.reg << 15;    // rs1\n                binary \+= \(i\.a3\.imm & 0x1F\) << 20; // shamt \(要反轉的 bit 位置\)\n                binary \+= 0b0110100 << 25;   // funct7\n)[ \t\n]*break;\n''', re.MULTILINE)
new_text, count = pattern.subn(r"\1            break;\n", text)
if count != 1:
    raise SystemExit(f'pattern count={count}')
path.write_text(new_text, encoding='utf-8')
print('fixed BINVI block')
