# Module 13 Homework Submission — 林名延（nthu cs)_111062224

## Student Information

| Field | Value |
|-------|-------|
| **Name** | 林名延（nthu cs) |
| **Student ID** | 111062224 |
| **Date** | 2026-04-22 |
| **Email** | _(your email address)_ |

## Git Repository

| Field | Value |
|-------|-------|
| **Repository URL** | _(link to your git repository)_ |
| **Branch** | _(branch name, e.g., `module13-submission`)_ |
| **Commit Hash** | _(commit hash of your final submission)_ |

---

## HW 13-1: Fibonacci Series (40 points)

### Assembly Code

**Code location:** `hw13_1_fibonacci.s`

**Approach:**
1.使用 s0 存儲當前的輸入值 n，使用 s1 存儲第一個遞迴分支 fibonacci(n-1) 的回傳結果。
2.針對 Venus 模擬器 的環境，將功能編號置於 a0，參數（如數值或字串位址）置於 a1。
3.基礎案例（Base Case）處理 $n=0$ 與 $n=1$。對於 $n \ge 2$，先呼叫 fib(n-1) 並將結果存入 s1，再呼叫 fib(n-2)，最後將兩者相加回傳。
4.每次函式呼叫分配 16 bytes 的空間
**Stack frame layout:**

  sp + 12: saved ra
  sp + 8:  saved s0
  sp + 4:  saved s1
  sp + 0:  (unused / padding for alignment)
  Frame size: 16 bytes


### Venus Output Screenshot

![](https://course.playlab.tw/md/uploads/6809e84d-21d7-49d3-9eb6-b23be523c2c6.png)

### Output Verification

| n | Expected F(n) | Your F(n) | Match? |
|---|--------------|-----------|--------|
| 0 | 0 | 0| [V ] |
| 1 | 1 | 1| [V ] |
| 2 | 1 | 1 | [V ] |
| 5 | 5 | 5| [V ] |
| 10 | 55 | 55| [V ] |
| 16 | 987 | 987| [ V] |

### Observations

遞迴版本的 Fibonacci 時間複雜度為 $O(2^n)$。在執行 F(16) 時，可以明顯感覺到 Venus 模擬器的運算速度比之前的 Factorial 慢得多，這是因為重複計算了大量相同的子問題，另外計算 F(n) 所需的遞迴呼叫次數為 $2 \cdot F(n+1) - 1$。對於 F(16) 來說，總共進行了 5167次

---

## HW 13-2: Assembly Program Analysis (40 points)

### Q1: Initial Setup (5 pts)

**s1 after Line 3:8
原因:line2 把count地位址放到t0，之後t0裡的.word 8被讀取

**s4 after Line 6:5
原因:line1 將values 陣列的頭地址放入s0，line6讀取陣列的第一個元素 values[0]，也就是5

### Q2: First Iteration, i=0 (5 pts)

**t3 at Line 10:5

**Branch at Line 11 (taken/not taken):taken
原因:5並不小於5，因此執行12-13

**s4 and s3 after iteration:** 5,0

### Q3: Iteration at i=4 (5 pts)

**t3 at Line 10:** 15

**Branch at Line 11 (taken/not taken):** not taken
原因:15<12(s4 為之前輪次的最高值 12)，也就是false，進入 mv

**s4 and s3 after iteration:** 15,4

### Q4: Complete Register Trace (5 pts)

| Iteration (i) | t3 (loaded value) | s4 (after iteration) | s3 (after iteration) | Branch at Line 11 |
|---|---|---|---|---|
| 0 | 5 | 5 | 0 | Not Taken |
| 1 | 12 | 12 | 1 | Not Taken |
| 2 | 8 | 12 | 1 | Taken |
| 3 | 3 | 12 | 1 | Taken |
| 4 | 15 | 15 | 4 | Not Taken |
| 5 | 7 | 15 | 4 | Taken |
| 6 | 10 | 15 | 4 | Taken |
| 7 | 1 | 15 | 4 | Taken |

### Q5: Final Output (5 pts)

**Printed value:**15

**What the program computes:** 遍歷array，並找出其MAX

### Q6: Meaning of s3 (5 pts)

**Value of s3: 4

**What it represents:** 最大值所在的索引，例如此題最大值 15 位於 values[4]
### Q7: Equivalent C Code (5 pts)

```c
#include <stdio.h>

int main() {
    int values[] = {5, 12, 8, 3, 15, 7, 10, 1};
    int count = 8;
    
    int max_val = values[0]; // s4
    int max_idx = 0;         // s3
    
    for (int i = 0; i < count; i++) { // i 為 s2
        int current = values[i];      // t3
        if (current >= max_val) {     // 對應 blt 的反向邏輯
            max_val = current;
            max_idx = i;
        }
    }
    
    printf("%d", max_val);
    return 0;
}
```

### Q8: Modified Program Behavior (5 pts)

**If Line 11 changed to `bgt t3, s4, skip`:**

**New output value:1

**What it computes instead:** 如果將 blt (if current < max) 改為 bgt (if current > max)，程式會變成尋找陣列中的 最小值 (Minimum Value)。

Final Output: 1。 (陣列中的最小值)

---

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


---

## Bonus: MaxPool1D (10 points)

**Code location:** `hw13_bonus_maxpool.s`

**Output screenshot:**
_(Insert or attach screenshot showing the 8 output values)_

**Expected output:** `7, 8, 8, 9, 9, 9, 6, 10`

**Your output matches?** [ ] Yes  [ ] No

---

## File Checklist

Verify all files are included before submission:

| File | Included? |
|------|-----------|
| `hw13_1_fibonacci.s` | [ V] |
| `hw13_2_analysis.md` | [ V] |
| `hw13_3_encoding.md` | [ V] |
| `hw13_bonus_maxpool.s` (optional) | [ ] |
| `submission_template.md` (this file) | [V ] |
| Venus output screenshots | [ V] |

---

## Declaration of Originality

I declare that this submission is my own work. All code was written by me unless otherwise attributed. Any external resources, references, or AI tools used are listed below.

**External resources used:**
- _(list references, tutorials, documentation consulted)_

**AI tools used (if any):**
google gemini

**Collaboration:**
- _(list classmates discussed with and nature of discussion)_

**Signature:** 林名延
**Date:** 4/27