#!/bin/bash
cd /workspace/module17_lab/Hardware/Lab

for instr in ADDI ADD LW SW BEQ JAL SLT SLTI SLLI SRAI; do
    echo "=== Testing $instr ==="
    bash load_test_data.sh -s "$instr" 2>/dev/null
    if [ $? -eq 0 ]; then
        sbt 'test:runMain acal_lab09.topTest' 2>&1 | grep -E '(RAN.*PASSED|Error|Exception)'
    else
        echo "Failed to load test data"
    fi
done
