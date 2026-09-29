# Module 1 Homework Submission

## TA Setup Guide — Complete These Steps Before Grading

> Fill in this section so TAs can reproduce your results. List any setup steps, dependencies, or commands needed to run your code.

**Environment:** _(e.g., Docker container `acal-curriculum`, local Python 3.10, etc.)_

**Setup commands:**
```bash
# List any install or setup commands needed
pip install ...
```

**How to run:**
```bash
# List commands to run your scripts and reproduce results
python3 hw1_1_convert.py
python3 hw1_1_analysis.py
python3 hw1_2_export.py
```

**Known issues or notes:**
_(Any issues TAs should be aware of — e.g., memory requirements, platform-specific notes, expected warnings)_

---

## Student Information

| Field | Value |
|-------|-------|
<<<<<<< Updated upstream
| **Name** | _(your full name)_ |
| **Student ID** | _(your student ID)_ |
| **Date** | _(submission date, YYYY-MM-DD)_ |
| **Email** | _(your email address)_ |
=======
| **Name** | 林名延|
| **Student ID** | 111062224 |
| **Date** | 3/4 |
| **Email** | linmingyan31@gmail.com |
>>>>>>> Stashed changes

## Git Repository

| Field | Value |
|-------|-------|
| **Repository URL** | _(link to your git repository)_ |
| **Branch** | _(branch name, e.g., `module1-submission`)_ |
| **Commit Hash** | _(commit hash of your final submission)_ |

---

## HW 1-1: Model Conversion & Visualization (40 points)

### Part 1: ResNet-50 Conversion (10 points)

**Code location:** `hw1_1_convert.py`

**Approach:**
_(Briefly describe how you loaded and exported the model. Note any issues encountered and how you resolved them.)_

**Verification result:**
```
(Paste the output of onnx.checker.check_model here, or confirm "verification passed")
```

### Part 2: Netron Visualization (10 points)

**Screenshot 1 -- Full Model Overview:**

_(Insert or attach `resnet50_overview.png`)_

**Observations:**
_(2--3 sentences describing the overall structure you observe.)_

**Screenshot 2 -- Residual Block Detail:**

_(Insert or attach `resnet50_block.png`)_

**Observations:**
_(2--3 sentences describing the residual block structure and skip connection.)_

### Part 3: Operator Analysis (20 points)

**Code location:** `hw1_1_analysis.py`

**Results:**

| Operator | Count |
|----------|-------|
| Conv | _(your count)_ |
| Gemm | _(your count)_ |
| BatchNormalization | _(your count)_ |
| Relu | _(your count)_ |
| Add | _(your count)_ |
| MaxPool | _(your count)_ |
| GlobalAveragePool | _(your count)_ |
| Flatten | _(your count)_ |
| **Total unique operator types** | _(your count)_ |

**Console output:**
```
(Paste the full console output of hw1_1_analysis.py here)
```

---

## HW 1-2: Architecture Comparison (60 points)

### Part 1: Model Export (10 points)

**Code location:** `hw1_2_export.py`

**Export results:**

| Model | File Size | ONNX Nodes | Parameters | Verified |
|-------|-----------|------------|------------|----------|
| AlexNet | _(size)_ MB | _(count)_ | _(count)_ | _(pass/fail)_ |
| ViT-B/16 | _(size)_ MB | _(count)_ | _(count)_ | _(pass/fail)_ |

### Part 2: Netron Visualizations (20 points)

**AlexNet -- Full Model:**
_(Insert or attach `alexnet_full.png`)_

**AlexNet -- Feature Extraction Detail:**
_(Insert or attach `alexnet_detail.png`)_

**ViT-B/16 -- Full Model:**
_(Insert or attach `vit_full.png`)_

**ViT-B/16 -- Encoder Block Detail:**
_(Insert or attach `vit_detail.png`)_

### Part 3: Written Analysis (30 points)

**Word count:** _(must be 400 or more)_

#### (a) Structural Differences

_(Your analysis here...)_

#### (b) Types of Operators Used

_(Your analysis here, with specific counts from your scripts...)_

#### (c) Data Flow

_(Your analysis here...)_

#### (d) Dominant Operations

_(Your analysis here...)_

#### (e) Implications for Hardware Accelerator Design

_(Your analysis here...)_

---

## File Checklist

Verify all files are included before submission:

| File | Included? |
|------|-----------|
| `hw1_1_convert.py` | [ ] |
| `resnet50_overview.png` | [ ] |
| `resnet50_block.png` | [ ] |
| `hw1_1_analysis.py` | [ ] |
| `hw1_2_export.py` | [ ] |
| `alexnet_full.png` | [ ] |
| `alexnet_detail.png` | [ ] |
| `vit_full.png` | [ ] |
| `vit_detail.png` | [ ] |
| `submission_template.md` (this file) | [ ] |

---

## Declaration of Originality

I declare that this submission is my own work. All code was written by me unless otherwise attributed. Any external resources, references, or AI tools used are listed below.

**External resources used:**
- _(list references, tutorials, documentation consulted)_

**AI tools used (if any):**
- _(list AI assistants used and describe how they were used)_

**Collaboration:**
- _(list classmates discussed with and nature of discussion)_

**Signature:** _(your name)_
**Date:** _(date)_
