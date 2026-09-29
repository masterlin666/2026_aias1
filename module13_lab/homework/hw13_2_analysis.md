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