#!/usr/bin/env python3
"""
Module 2 Auto-Grader: AI Model Analysis & Profiling
Grades student submissions for HW 2-1, HW 2-2, and HW 2-3.
"""

import argparse
import json
import math
import os
import sys
import re
import subprocess
import tempfile

import numpy as np


def load_test_cases(test_cases_path):
    """Load expected values from test_cases.json."""
    with open(test_cases_path, 'r') as f:
        return json.load(f)


# ============================================================
# HW 2-1: GoogleNet Full Analysis (30 points)
# ============================================================

def grade_hw2_1(submission_dir, test_cases):
    """
    Grade HW 2-1: GoogleNet Full Analysis (30 points)
    - 2-1-1: Parameter count (5 pts)
    - 2-1-2: Memory calculation (5 pts)
    - 2-1-3: torchinfo summary (5 pts)
    - 2-1-4: MACs calculation (10 pts)
    - 2-1-5: Forward hooks on Conv2d (5 pts)
    """
    results = {"hw2_1": {"total": 30, "earned": 0, "details": []}}
    expected = test_cases["hw2_1"]

    # --- 2-1-1: Parameter count (5 pts) ---
    param_score = 0
    param_script = _find_file(submission_dir, ["hw2_1_params.py", "hw2_1.py", "hw2_1_param.py"])

    if param_script:
        output = _run_script(param_script)
        if output:
            # Look for the parameter count in the output
            expected_params = expected["googlenet_params"]["expected"]
            tolerance = expected["googlenet_params"]["tolerance"]

            found_count = _extract_number_near_keyword(output, ["total param", "parameter"])
            if found_count is not None:
                if abs(found_count - expected_params) <= tolerance:
                    param_score = 5
                    results["hw2_1"]["details"].append(
                        f"2-1-1: Parameter count correct ({found_count:,} vs expected ~{expected_params:,}): +5"
                    )
                elif abs(found_count - expected_params) / expected_params < 0.01:
                    param_score = 3
                    results["hw2_1"]["details"].append(
                        f"2-1-1: Parameter count close ({found_count:,} vs expected ~{expected_params:,}): +3"
                    )
                else:
                    results["hw2_1"]["details"].append(
                        f"2-1-1: Parameter count incorrect ({found_count:,} vs expected ~{expected_params:,}): +0"
                    )
            else:
                results["hw2_1"]["details"].append("2-1-1: Could not parse parameter count from output: +0")
        else:
            results["hw2_1"]["details"].append("2-1-1: Script failed to run: +0")
    else:
        results["hw2_1"]["details"].append("2-1-1: Script not found: +0")

    results["hw2_1"]["earned"] += param_score

    # --- 2-1-2: Memory calculation (5 pts) ---
    mem_score = 0
    # Memory check can be in the same script or a separate report
    report_text = _find_and_read(submission_dir, [
        "hw2_1_params.py", "hw2_1_memory.py", "hw2_1_report.txt", "hw2_1.txt"
    ])
    if report_text is None and param_script:
        report_text = _run_script(param_script)

    if report_text:
        expected_fp32 = expected["googlenet_params"]["expected"] * 4
        # Look for FP32 memory value
        fp32_found = _extract_number_near_keyword(report_text, ["fp32", "float32", "233", "memory"])
        if fp32_found is not None and abs(fp32_found - expected_fp32) / expected_fp32 < 0.02:
            mem_score += 3
        # Look for multiple precision values
        has_fp16 = any(kw in report_text.lower() for kw in ["fp16", "float16", "half"])
        has_int8 = any(kw in report_text.lower() for kw in ["int8", "8-bit", "8 bit"])
        if has_fp16:
            mem_score += 1
        if has_int8:
            mem_score += 1
        mem_score = min(5, mem_score)
        results["hw2_1"]["details"].append(f"2-1-2: Memory calculation: +{mem_score}")
    else:
        results["hw2_1"]["details"].append("2-1-2: Memory output not found: +0")

    results["hw2_1"]["earned"] += mem_score

    # --- 2-1-3: torchinfo summary (5 pts) ---
    ti_score = 0
    # Look for torchinfo output in submission
    ti_text = _find_and_read(submission_dir, [
        "hw2_1_torchinfo.txt", "hw2_1_summary.txt", "torchinfo_output.txt"
    ])
    if ti_text is None:
        # Try running the params script and checking for torchinfo content
        if param_script:
            ti_text = _run_script(param_script)

    if ti_text and ("torchinfo" in ti_text.lower() or "mult_adds" in ti_text.lower()
                    or "num_params" in ti_text.lower() or "Total mult_adds" in ti_text):
        ti_score = 5
        results["hw2_1"]["details"].append("2-1-3: torchinfo summary present: +5")
    elif ti_text and "total params" in ti_text.lower():
        ti_score = 3
        results["hw2_1"]["details"].append("2-1-3: Summary present but may not be torchinfo: +3")
    else:
        results["hw2_1"]["details"].append("2-1-3: torchinfo summary not found: +0")

    results["hw2_1"]["earned"] += ti_score

    # --- 2-1-4: MACs calculation (10 pts) ---
    mac_score = 0
    mac_script = _find_file(submission_dir, ["hw2_1_macs.py", "hw2_1_mac.py", "hw2_1_flops.py"])

    if mac_script:
        output = _run_script(mac_script, timeout=120)
        if output:
            expected_macs = expected["googlenet_macs"]["expected"]
            tolerance_pct = expected["googlenet_macs"]["tolerance_percent"]

            found_macs = _extract_number_near_keyword(output, ["total mac", "total_mac", "macs"])
            if found_macs is not None:
                relative_error = abs(found_macs - expected_macs) / expected_macs
                if relative_error <= tolerance_pct / 100.0:
                    mac_score = 10
                    results["hw2_1"]["details"].append(
                        f"2-1-4: MACs correct ({found_macs:,.0f} vs expected ~{expected_macs:,.0f}): +10"
                    )
                elif relative_error <= 0.05:
                    mac_score = 7
                    results["hw2_1"]["details"].append(
                        f"2-1-4: MACs close ({found_macs:,.0f}, {relative_error*100:.1f}% off): +7"
                    )
                elif relative_error <= 0.10:
                    mac_score = 4
                    results["hw2_1"]["details"].append(
                        f"2-1-4: MACs somewhat off ({found_macs:,.0f}, {relative_error*100:.1f}% off): +4"
                    )
                else:
                    results["hw2_1"]["details"].append(
                        f"2-1-4: MACs significantly off ({found_macs:,.0f}, {relative_error*100:.1f}% off): +0"
                    )
            else:
                # Check if per-layer breakdown is present
                if "conv2d" in output.lower() and "linear" in output.lower():
                    mac_score = 4
                    results["hw2_1"]["details"].append(
                        "2-1-4: Per-layer breakdown present but total not parseable: +4"
                    )
                else:
                    results["hw2_1"]["details"].append("2-1-4: Could not parse MACs from output: +0")
        else:
            results["hw2_1"]["details"].append("2-1-4: MACs script failed to run: +0")
    else:
        results["hw2_1"]["details"].append("2-1-4: MACs script not found: +0")

    results["hw2_1"]["earned"] += mac_score

    # --- 2-1-5: Forward hooks (5 pts) ---
    hook_score = 0
    hook_script = _find_file(submission_dir, ["hw2_1_hooks.py", "hw2_1_hook.py", "hw2_1_activations.py"])

    if hook_script:
        output = _run_script(hook_script, timeout=120)
        if output:
            output_lower = output.lower()
            # Check for activation shapes being reported
            has_shapes = "shape" in output_lower or "activation" in output_lower
            has_conv2d = "conv" in output_lower
            has_memory = "kb" in output_lower or "byte" in output_lower or "memory" in output_lower

            if has_shapes and has_conv2d and has_memory:
                hook_score = 5
                results["hw2_1"]["details"].append("2-1-5: Forward hooks complete (shapes + memory): +5")
            elif has_shapes and has_conv2d:
                hook_score = 3
                results["hw2_1"]["details"].append("2-1-5: Forward hooks partial (shapes but no memory): +3")
            elif has_conv2d:
                hook_score = 1
                results["hw2_1"]["details"].append("2-1-5: Forward hooks minimal: +1")
            else:
                results["hw2_1"]["details"].append("2-1-5: Forward hooks output not recognized: +0")
        else:
            results["hw2_1"]["details"].append("2-1-5: Hook script failed to run: +0")
    else:
        results["hw2_1"]["details"].append("2-1-5: Hook script not found: +0")

    results["hw2_1"]["earned"] += hook_score

    return results


# ============================================================
# HW 2-2: ONNX Analysis of MobileNetV2 (30 points)
# ============================================================

def grade_hw2_2(submission_dir, test_cases):
    """
    Grade HW 2-2: ONNX Analysis of MobileNetV2 (30 points)
    - 2-2-1: Operator statistics (10 pts)
    - 2-2-2: Data bandwidth requirement (10 pts)
    - 2-2-3: Activation memory requirement (10 pts)
    """
    results = {"hw2_2": {"total": 30, "earned": 0, "details": []}}
    expected = test_cases["hw2_2"]

    # --- 2-2-1: Operator statistics (10 pts) ---
    op_score = 0
    op_script = _find_file(submission_dir, ["hw2_2_operators.py", "hw2_2_ops.py", "hw2_2_1.py"])

    if op_script:
        output = _run_script(op_script, timeout=60)
        if output:
            output_lower = output.lower()

            # Check for operator listing
            has_op_list = any(op.lower() in output_lower for op in expected["operators"]["expected_types"])
            # Check for depthwise classification
            has_depthwise = "depthwise" in output_lower or "group" in output_lower
            # Check for kernel size analysis
            has_kernel = "kernel" in output_lower or "1x1" in output_lower or "3x3" in output_lower

            if has_op_list and has_depthwise and has_kernel:
                op_score = 10
                results["hw2_2"]["details"].append("2-2-1: Operator statistics complete: +10")
            elif has_op_list and has_depthwise:
                op_score = 7
                results["hw2_2"]["details"].append("2-2-1: Operators + depthwise but no kernel analysis: +7")
            elif has_op_list:
                op_score = 4
                results["hw2_2"]["details"].append("2-2-1: Operators listed but no depthwise classification: +4")
            else:
                results["hw2_2"]["details"].append("2-2-1: Operator output not recognized: +0")
        else:
            results["hw2_2"]["details"].append("2-2-1: Operator script failed to run: +0")
    else:
        results["hw2_2"]["details"].append("2-2-1: Operator script not found: +0")

    results["hw2_2"]["earned"] += op_score

    # --- 2-2-2: Data bandwidth requirement (10 pts) ---
    bw_score = 0
    bw_script = _find_file(submission_dir, ["hw2_2_bandwidth.py", "hw2_2_bw.py", "hw2_2_2.py"])

    if bw_script:
        output = _run_script(bw_script, timeout=60)
        if output:
            output_lower = output.lower()
            expected_weight_mb = expected["weight_data"]["expected_mb"]
            tolerance_mb = expected["weight_data"]["tolerance_mb"]

            # Try to extract total weight size
            weight_found = _extract_number_near_keyword(output, ["total weight", "weight data", "total.*mb"])

            # Check for bandwidth calculations
            has_ddr4 = "ddr4" in output_lower or "25.6" in output
            has_lpddr5 = "lpddr5" in output_lower or "51.2" in output
            has_hbm = "hbm" in output_lower or "460" in output

            bw_technologies = sum([has_ddr4, has_lpddr5, has_hbm])

            if weight_found is not None and abs(weight_found - expected_weight_mb) <= tolerance_mb:
                bw_score += 5
            elif weight_found is not None:
                bw_score += 2

            if bw_technologies >= 3:
                bw_score += 5
            elif bw_technologies >= 2:
                bw_score += 3
            elif bw_technologies >= 1:
                bw_score += 1

            bw_score = min(10, bw_score)
            results["hw2_2"]["details"].append(f"2-2-2: Bandwidth analysis: +{bw_score}")
        else:
            results["hw2_2"]["details"].append("2-2-2: Bandwidth script failed to run: +0")
    else:
        results["hw2_2"]["details"].append("2-2-2: Bandwidth script not found: +0")

    results["hw2_2"]["earned"] += bw_score

    # --- 2-2-3: Activation memory requirement (10 pts) ---
    act_score = 0
    act_script = _find_file(submission_dir, ["hw2_2_activations.py", "hw2_2_act.py", "hw2_2_3.py"])

    if act_script:
        output = _run_script(act_script, timeout=60)
        if output:
            output_lower = output.lower()

            has_shape_inference = "shape" in output_lower and ("infer" in output_lower or "intermediate" in output_lower)
            has_largest = "largest" in output_lower or "maximum" in output_lower or "biggest" in output_lower
            has_total = "total" in output_lower and ("activation" in output_lower or "memory" in output_lower)
            has_discussion = len(output) > 200 and ("sram" in output_lower or "dram" in output_lower
                                                     or "spill" in output_lower or "fit" in output_lower
                                                     or "on-chip" in output_lower)

            if has_shape_inference and has_largest and has_total:
                act_score += 7
            elif has_shape_inference and (has_largest or has_total):
                act_score += 4
            elif has_shape_inference:
                act_score += 2

            if has_discussion:
                act_score += 3

            act_score = min(10, act_score)
            results["hw2_2"]["details"].append(f"2-2-3: Activation analysis: +{act_score}")
        else:
            results["hw2_2"]["details"].append("2-2-3: Activation script failed to run: +0")
    else:
        results["hw2_2"]["details"].append("2-2-3: Activation script not found: +0")

    results["hw2_2"]["earned"] += act_score

    return results


# ============================================================
# HW 2-3: ONNX Graph Transformation (40 points)
# ============================================================

def grade_hw2_3(submission_dir, test_cases):
    """
    Grade HW 2-3: ONNX Graph Transformation -- Tiling Linear Layers (40 points)
    - 2-3-1: Single Linear subgraph (10 pts)
    - 2-3-2: Tiled subgraph (10 pts)
    - 2-3-3: AlexNet transformation (10 pts)
    - 2-3-4: Equivalence verification (10 pts)
    """
    results = {"hw2_3": {"total": 40, "earned": 0, "details": []}}
    expected = test_cases["hw2_3"]

    # --- 2-3-1: Single Linear subgraph (10 pts) ---
    linear_score = 0
    linear_script = _find_file(submission_dir, ["hw2_3_linear.py", "hw2_3_1.py"])

    if linear_script:
        output = _run_script(linear_script, timeout=60)
        if output:
            output_lower = output.lower()
            has_verify = "verified" in output_lower or "passed" in output_lower or "pass" in output_lower
            has_error = "max error" in output_lower or "error:" in output_lower

            if has_verify and "fail" not in output_lower:
                linear_score = 10
                results["hw2_3"]["details"].append("2-3-1: Single Linear model verified: +10")
            elif has_error:
                linear_score = 7
                results["hw2_3"]["details"].append("2-3-1: Model created, error reported: +7")
            else:
                linear_score = 4
                results["hw2_3"]["details"].append("2-3-1: Script runs but verification unclear: +4")
        else:
            results["hw2_3"]["details"].append("2-3-1: Linear script failed to run: +0")
    else:
        results["hw2_3"]["details"].append("2-3-1: Linear script not found: +0")

    results["hw2_3"]["earned"] += linear_score

    # --- 2-3-2: Tiled subgraph (10 pts) ---
    tiled_score = 0
    tiled_script = _find_file(submission_dir, ["hw2_3_tiled.py", "hw2_3_2.py", "hw2_3_tile.py"])

    if tiled_script:
        output = _run_script(tiled_script, timeout=120)
        if output:
            output_lower = output.lower()
            has_tile = "tile" in output_lower or "matmul" in output_lower
            has_verify = "verified" in output_lower or "passed" in output_lower or "pass" in output_lower
            has_match = "match" in output_lower or "close" in output_lower or "error" in output_lower

            if has_tile and has_verify and "fail" not in output_lower:
                tiled_score = 10
                results["hw2_3"]["details"].append("2-3-2: Tiled subgraph verified: +10")
            elif has_tile and has_match:
                tiled_score = 7
                results["hw2_3"]["details"].append("2-3-2: Tiled subgraph created, partial verification: +7")
            elif has_tile:
                tiled_score = 4
                results["hw2_3"]["details"].append("2-3-2: Tiling logic present but verification unclear: +4")
            else:
                tiled_score = 2
                results["hw2_3"]["details"].append("2-3-2: Script runs but tiling not detected: +2")
        else:
            results["hw2_3"]["details"].append("2-3-2: Tiled script failed to run: +0")
    else:
        results["hw2_3"]["details"].append("2-3-2: Tiled script not found: +0")

    results["hw2_3"]["earned"] += tiled_score

    # --- 2-3-3: AlexNet transformation (10 pts) ---
    transform_score = 0
    transform_script = _find_file(submission_dir, ["hw2_3_transform.py", "hw2_3_3.py"])
    tiled_onnx = _find_file(submission_dir, ["alexnet_tiled.onnx", "alexnet_transformed.onnx"])

    if tiled_onnx:
        try:
            import onnx
            model = onnx.load(tiled_onnx)
            onnx.checker.check_model(model)

            # Count nodes
            num_nodes = len(model.graph.node)
            num_matmul = sum(1 for n in model.graph.node if n.op_type == "MatMul")
            num_gemm = sum(1 for n in model.graph.node if n.op_type == "Gemm")

            # AlexNet originally has 3 Gemm nodes. After tiling, Gemm should be 0
            # and there should be many MatMul nodes.
            expected_min_matmul = expected["alexnet_tiling"]["min_matmul_nodes"]

            if num_gemm == 0 and num_matmul >= expected_min_matmul:
                transform_score = 10
                results["hw2_3"]["details"].append(
                    f"2-3-3: Transformed model valid. Gemm={num_gemm}, MatMul={num_matmul}, "
                    f"total nodes={num_nodes}: +10"
                )
            elif num_gemm < 3 and num_matmul > 0:
                transform_score = 7
                results["hw2_3"]["details"].append(
                    f"2-3-3: Partial transformation. Gemm={num_gemm}, MatMul={num_matmul}: +7"
                )
            else:
                transform_score = 4
                results["hw2_3"]["details"].append(
                    f"2-3-3: Model valid but transformation incomplete. "
                    f"Gemm={num_gemm}, MatMul={num_matmul}: +4"
                )
        except ImportError:
            results["hw2_3"]["details"].append("2-3-3: onnx package not available for verification: +0")
        except Exception as e:
            transform_score = 2
            results["hw2_3"]["details"].append(f"2-3-3: Model exists but checker failed: {e}: +2")
    elif transform_script:
        output = _run_script(transform_script, timeout=120)
        if output and ("pass" in output.lower() or "saved" in output.lower()):
            transform_score = 4
            results["hw2_3"]["details"].append("2-3-3: Transform script runs but ONNX file not found: +4")
        else:
            results["hw2_3"]["details"].append("2-3-3: Transform script exists but ONNX not generated: +0")
    else:
        results["hw2_3"]["details"].append("2-3-3: Transform script and ONNX file not found: +0")

    results["hw2_3"]["earned"] += transform_score

    # --- 2-3-4: Equivalence verification (10 pts) ---
    verify_score = 0
    verify_script = _find_file(submission_dir, ["hw2_3_verify.py", "hw2_3_4.py", "hw2_3_verification.py"])

    if verify_script:
        output = _run_script(verify_script, timeout=300)
        if output:
            output_lower = output.lower()

            # Check for pass/fail results
            all_passed = ("all passed" in output_lower or "all pass" in output_lower
                          or "100/100" in output or "100 pass" in output_lower)
            has_results = "result" in output_lower or "test" in output_lower
            has_max_error = "max" in output_lower and "error" in output_lower

            # Try to extract pass count
            pass_match = re.search(r'(\d+)\s*/\s*100\s*pass', output_lower)
            if pass_match:
                num_passed = int(pass_match.group(1))
            elif all_passed:
                num_passed = 100
            else:
                num_passed = 0

            if all_passed or num_passed >= 100:
                verify_score = 10
                results["hw2_3"]["details"].append(
                    f"2-3-4: All {num_passed} tests passed: +10"
                )
            elif num_passed >= 95:
                verify_score = 7
                results["hw2_3"]["details"].append(
                    f"2-3-4: {num_passed}/100 tests passed: +7"
                )
            elif num_passed >= 80:
                verify_score = 4
                results["hw2_3"]["details"].append(
                    f"2-3-4: {num_passed}/100 tests passed: +4"
                )
            elif has_results:
                verify_score = 2
                results["hw2_3"]["details"].append(
                    f"2-3-4: Verification attempted, fewer than 80 passed: +2"
                )
            else:
                results["hw2_3"]["details"].append("2-3-4: Verification output not parseable: +0")
        else:
            results["hw2_3"]["details"].append("2-3-4: Verification script failed to run: +0")
    else:
        results["hw2_3"]["details"].append("2-3-4: Verification script not found: +0")

    results["hw2_3"]["earned"] += verify_score

    return results


# ============================================================
# Utility Functions
# ============================================================

def _find_file(directory, candidates):
    """Find the first existing file from a list of candidate filenames."""
    for name in candidates:
        path = os.path.join(directory, name)
        if os.path.exists(path):
            return path
    # Also search one level of subdirectories
    for subdir in os.listdir(directory):
        subpath = os.path.join(directory, subdir)
        if os.path.isdir(subpath):
            for name in candidates:
                path = os.path.join(subpath, name)
                if os.path.exists(path):
                    return path
    return None


def _find_and_read(directory, candidates):
    """Find and read the contents of the first matching file."""
    path = _find_file(directory, candidates)
    if path:
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception:
            return None
    return None


def _run_script(script_path, timeout=120):
    """Run a Python script and capture its stdout+stderr."""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(script_path),
        )
        return result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def _extract_number_near_keyword(text, keywords):
    """
    Search text for a number appearing near one of the given keywords.
    Returns the number as a float, or None if not found.
    Skips numbers that are part of precision format strings (FP32, INT8, etc.).
    """
    text_lower = text.lower()
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Find keyword occurrences
        idx = text_lower.find(keyword_lower)
        while idx != -1:
            # Look for a number within 100 characters after the keyword
            region = text[idx:idx + 150]
            # Match numbers with optional commas (e.g., 6,624,904 or 6624904 or 1.5e9)
            for m in re.finditer(r'[\d,]+(?:\.\d+)?(?:[eE][+-]?\d+)?', region):
                num_str = m.group()
                # Skip numbers that are part of precision/format tokens (FP32, INT8, BF16, etc.)
                start = m.start()
                if start > 0 and re.match(r'[a-zA-Z_]', region[start - 1]):
                    continue
                num_str_clean = num_str.replace(',', '')
                try:
                    val = float(num_str_clean)
                    if val > 0:
                        return val
                except ValueError:
                    continue
            idx = text_lower.find(keyword_lower, idx + 1)
    return None


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Module 2 Auto-Grader")
    parser.add_argument("submission_dir", help="Path to student submission directory")
    parser.add_argument("--test-cases", default=None,
                        help="Path to test_cases.json (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print expected values without grading")
    parser.add_argument("--output", default=None,
                        help="Output JSON report path")
    args = parser.parse_args()

    # Find test_cases.json
    if args.test_cases:
        test_cases_path = args.test_cases
    else:
        test_cases_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_cases.json")

    test_cases = load_test_cases(test_cases_path)

    if args.dry_run:
        print("=== DRY RUN: Expected Values ===")
        print(json.dumps(test_cases, indent=2))
        return

    # Grade all sections
    all_results = {}
    all_results.update(grade_hw2_1(args.submission_dir, test_cases))
    all_results.update(grade_hw2_2(args.submission_dir, test_cases))
    all_results.update(grade_hw2_3(args.submission_dir, test_cases))

    # Calculate total
    total_earned = sum(r["earned"] for r in all_results.values())
    total_possible = sum(r["total"] for r in all_results.values())

    report = {
        "module": "Module 2: AI Model Analysis & Profiling",
        "results": all_results,
        "total_earned": total_earned,
        "total_possible": total_possible,
        "percentage": round(100 * total_earned / total_possible, 1),
    }

    # Output
    report_json = json.dumps(report, indent=2)
    print(report_json)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report_json)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
