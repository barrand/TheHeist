#!/bin/bash

echo ""
echo "======================================================================"
echo "🎮 RUNNING E2E TESTS ON 3 SCENARIOS"
echo "======================================================================"
echo ""

cd /Users/bbarrand/Documents/Projects/TheHeist/backend

scenarios=(
    "experiences/generated_museum_heist_3players.md"
    "experiences/generated_bank_vault_3players.md"
    "experiences/generated_office_infiltration_2players.md"
)

pass_count=0
total=0

for scenario in "${scenarios[@]}"; do
    total=$((total + 1))
    scenario_name=$(basename "$scenario" .md)
    
    echo "[$total/3] Testing: $scenario_name"
    echo "----------------------------------------------------------------------"
    
    # Run test and capture exit code
    python3 scripts/test_gameplay_e2e.py \
        --scenario "$scenario" \
        --difficulty easy \
        --skip-npc \
        2>&1 | grep -E "(Status:|Per-Role Performance:|  hacker:|  mastermind:|  safe_cracker:|  insider:|  driver:|Test PASSED|Test ERROR|DEADLOCK|Issues Detected)" | tail -15
    
    exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        pass_count=$((pass_count + 1))
        echo "✅ PASSED"
    else
        echo "❌ FAILED (exit code: $exit_code)"
    fi
    
    echo ""
done

echo "======================================================================"
echo "📊 FINAL RESULTS: $pass_count/$total tests PASSED"
echo "======================================================================"
echo ""

exit $((total - pass_count))
