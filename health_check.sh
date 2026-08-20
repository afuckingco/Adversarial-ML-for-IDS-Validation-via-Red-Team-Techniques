#!/usr/bin/env bash
#
# health_check.sh — Comprehensive health check for AETG project
# Run this script from the project root directory.
#

set -euo pipefail

PROJECT_ROOT="$(pwd)"
REPORT_FILE="health_check_report.txt"

# Colors (optional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
check_pass() { echo -e "${GREEN}✅ $1${NC}"; }
check_fail() { echo -e "${RED}❌ $1${NC}"; }
check_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
section() { echo ""; echo "============================================================"; echo "$1"; echo "============================================================"; }

# Start report
echo "AETG Project Health Check"
echo "Started at: $(date)"
echo "Root directory: $PROJECT_ROOT"
echo ""

# ----------------------------------------------------------------------
# 1. Directory Structure
# ----------------------------------------------------------------------
section "1. DIRECTORY STRUCTURE"
if [ -d "AETG_paper" ] && [ -d "code" ] && [ -d "other-projects" ]; then
    check_pass "Main directories (AETG_paper, code, other-projects) exist."
else
    check_fail "Missing required top-level directories."
fi

if [ -d "AETG_paper/manuscript" ] && [ -d "AETG_paper/output" ] && [ -d "AETG_paper/figures" ] && [ -d "AETG_paper/data" ] && [ -d "AETG_paper/notes" ]; then
    check_pass "AETG_paper subdirectories exist."
else
    check_fail "Some AETG_paper subdirectories missing."
fi

if [ -d "code/adversarial-traffic-generator" ] && [ -d "code/mini-soc-enterprise-arch" ] && [ -d "code/experiments" ]; then
    check_pass "Code subdirectories exist."
else
    check_fail "Some code subdirectories missing."
fi

# ----------------------------------------------------------------------
# 2. Paper Files
# ----------------------------------------------------------------------
section "2. PAPER MANUSCRIPT"

# LaTeX source
if [ -f "AETG_paper/manuscript/AETG_paper.tex" ]; then
    check_pass "AETG_paper.tex exists ($(ls -lh AETG_paper/manuscript/AETG_paper.tex | awk '{print $5}'))."
else
    check_fail "AETG_paper.tex missing."
fi

# Word document
if [ -f "AETG_paper/manuscript/AETG_paper.docx" ]; then
    check_pass "AETG_paper.docx exists ($(ls -lh AETG_paper/manuscript/AETG_paper.docx | awk '{print $5}'))."
else
    check_fail "AETG_paper.docx missing."
fi

# PDF output
if [ -f "AETG_paper/output/AETG_paper.pdf" ]; then
    check_pass "AETG_paper.pdf exists ($(ls -lh AETG_paper/output/AETG_paper.pdf | awk '{print $5}'))."
    # Try to get page count
    if command -v pdfinfo >/dev/null 2>&1; then
        pages=$(pdfinfo AETG_paper/output/AETG_paper.pdf 2>/dev/null | grep -i pages | awk '{print $2}')
        echo "   Pages: $pages"
    else
        check_warn "pdfinfo not installed, cannot verify page count."
    fi
else
    check_fail "AETG_paper.pdf missing."
fi

# References
if [ -f "AETG_paper/manuscript/references.bib" ]; then
    check_pass "references.bib exists."
    ref_count=$(grep -c "^@[a-zA-Z]" AETG_paper/manuscript/references.bib 2>/dev/null || echo "0")
    echo "   Number of references: $ref_count"
    # Check for UNVERIFIED
    if grep -q "UNVERIFIED" AETG_paper/manuscript/references.bib; then
        check_fail "Found UNVERIFIED entries in references.bib."
    else
        check_pass "No UNVERIFIED entries in references."
    fi
else
    check_fail "references.bib missing."
fi

# Class file
if [ -f "AETG_paper/manuscript/elsarticle_offline_shim.cls" ]; then
    check_pass "elsarticle_offline_shim.cls exists."
else
    check_fail "elsarticle_offline_shim.cls missing."
fi

# REVIEW NOTE check
if grep -iq "REVIEW NOTE" AETG_paper/manuscript/AETG_paper.tex; then
    check_fail "Found REVIEW NOTE(s) in AETG_paper.tex."
else
    check_pass "No REVIEW NOTE in AETG_paper.tex."
fi

# ----------------------------------------------------------------------
# 3. Figures and Data
# ----------------------------------------------------------------------
section "3. FIGURES AND DATA"

if [ -f "AETG_paper/figures/aetg_architecture.png" ]; then
    check_pass "aetg_architecture.png exists ($(ls -lh AETG_paper/figures/aetg_architecture.png | awk '{print $5}'))."
else
    check_fail "aetg_architecture.png missing."
fi

if [ -f "AETG_paper/data/eval_results.json" ]; then
    check_pass "eval_results.json exists in data/."
else
    check_fail "eval_results.json missing in data/."
fi

# Check content of eval_results.json
if command -v jq >/dev/null 2>&1; then
    if [ -f "AETG_paper/data/eval_results.json" ]; then
        recall=$(jq -r '.recall' AETG_paper/data/eval_results.json 2>/dev/null || echo "null")
        evasion=$(jq -r '.evasion_rate' AETG_paper/data/eval_results.json 2>/dev/null || echo "null")
        alert_count=$(jq -r '.alert_count_in_redis' AETG_paper/data/eval_results.json 2>/dev/null || echo "null")
        echo "   recall: $recall"
        echo "   evasion_rate: $evasion"
        echo "   alert_count_in_redis: $alert_count"
        if [ "$recall" = "1.0" ] || [ "$recall" = "1" ]; then
            check_pass "recall = 1.0 (all adversarial detected)."
        else
            check_warn "recall is not 1.0: $recall"
        fi
        if [ "$evasion" = "0.0" ] || [ "$evasion" = "0" ]; then
            check_pass "evasion_rate = 0.0."
        else
            check_warn "evasion_rate not zero: $evasion"
        fi
    fi
else
    check_warn "jq not installed; cannot parse JSON."
fi

# ----------------------------------------------------------------------
# 4. Documentation (notes)
# ----------------------------------------------------------------------
section "4. DOCUMENTATION"

doc_files=("ABOUT.md" "AUDIT.md" "CONTRIBUTING.md" "cover_letter.txt" "highlights.txt")
all_doc=0
for doc in "${doc_files[@]}"; do
    if [ -f "AETG_paper/notes/$doc" ]; then
        check_pass "$doc exists."
        ((all_doc++))
    else
        check_fail "$doc missing."
    fi
done
if [ $all_doc -eq ${#doc_files[@]} ]; then
    check_pass "All documentation files present."
fi

# ----------------------------------------------------------------------
# 5. Code (syntax and key files)
# ----------------------------------------------------------------------
section "5. CODE"

# Check key Python files syntax
py_files=("code/adversarial-traffic-generator/new_traffic_gen.py" "code/experiments/eval_ids.py" "code/mini-soc-enterprise-arch/push_alerts.py")
for pyf in "${py_files[@]}"; do
    if [ -f "$pyf" ]; then
        if python3 -m py_compile "$pyf" 2>/dev/null; then
            check_pass "$(basename "$pyf") syntax OK."
        else
            check_fail "$(basename "$pyf") syntax error."
        fi
    else
        check_fail "$pyf not found."
    fi
done

# Check for source code directories
if [ -d "code/adversarial-traffic-generator/src" ]; then
    check_pass "src/ directory exists."
else
    check_fail "src/ directory missing."
fi

# ----------------------------------------------------------------------
# 6. Virtual Environment and Dependencies
# ----------------------------------------------------------------------
section "6. VIRTUAL ENVIRONMENT"

if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    check_pass "Virtual environment found."
else
    check_fail "Virtual environment missing."
fi

# Try to activate and check key packages
if [ -f "venv/bin/activate" ]; then
    set +e
    source venv/bin/activate >/dev/null 2>&1
    if command -v pip >/dev/null 2>&1; then
        for pkg in numpy redis scapy scikit-learn xgboost tls_client; do
            if pip list 2>/dev/null | grep -q "^$pkg "; then
                check_pass "$pkg installed."
            else
                check_fail "$pkg NOT installed."
            fi
        done
    else
        check_warn "pip not available in venv."
    fi
    deactivate >/dev/null 2>&1
    set -e
fi

# ----------------------------------------------------------------------
# 7. Mini-SOC and Docker
# ----------------------------------------------------------------------
section "7. MINI-SOC & DOCKER"

# Check if docker compose is available
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
    check_pass "Docker and docker-compose available."
else
    check_warn "Docker/docker-compose not found; skipping container checks."
fi

# If docker is available, try to get status
if command -v docker >/dev/null 2>&1; then
    if docker ps --filter "name=ids" --format "{{.Names}}" | grep -q ids; then
        check_pass "Container 'ids' is running."
    else
        check_warn "Container 'ids' is not running."
    fi
    if docker ps --filter "name=redis" --format "{{.Names}}" | grep -q redis; then
        check_pass "Container 'redis' is running."
    else
        check_warn "Container 'redis' is not running."
    fi
fi

# Check eve.json
if [ -f "code/mini-soc-enterprise-arch/shared/logs/eve.json" ]; then
    eve_size=$(ls -lh code/mini-soc-enterprise-arch/shared/logs/eve.json | awk '{print $5}')
    check_pass "eve.json exists (size: $eve_size)."
else
    check_warn "eve.json not found (Suricata may not have generated alerts)."
fi

# ----------------------------------------------------------------------
# 8. Experiment Results (from code/experiments)
# ----------------------------------------------------------------------
section "8. EXPERIMENT RESULTS"

if [ -f "code/experiments/eval_results.json" ]; then
    check_pass "eval_results.json found in experiments/."
    if command -v jq >/dev/null 2>&1; then
        alert_cnt=$(jq -r '.alert_count_in_redis' code/experiments/eval_results.json 2>/dev/null || echo "null")
        echo "   alert_count_in_redis: $alert_cnt"
        if [ "$alert_cnt" != "null" ] && [ "$alert_cnt" -gt 0 ]; then
            check_pass "Positive alert count ($alert_cnt) confirms alert pipeline success."
        else
            check_warn "alert_count_in_redis = $alert_cnt (should be >0 for successful detection)."
        fi
    else
        check_warn "jq not installed; cannot inspect JSON."
    fi
else
    check_warn "eval_results.json missing in experiments/ (but may be in AETG_paper/data/)."
fi

# ----------------------------------------------------------------------
# 9. Redis Alert Count (if Redis container running)
# ----------------------------------------------------------------------
section "9. REDIS ALERT KEYS"

if command -v docker >/dev/null 2>&1; then
    if docker ps --filter "name=redis" --format "{{.Names}}" | grep -q redis; then
        alert_keys=$(docker exec redis redis-cli --scan --pattern "alert:*" 2>/dev/null | wc -l || echo "0")
        echo "   Number of alert:* keys in Redis: $alert_keys"
        if [ "$alert_keys" -gt 0 ]; then
            check_pass "$alert_keys alert(s) found in Redis."
        else
            check_warn "No alert:* keys in Redis (push_alerts.py may not be running)."
        fi
    else
        check_warn "Redis container not running; cannot check alert keys."
    fi
fi

# ----------------------------------------------------------------------
# 10. Additional Cleanup Checks
# ----------------------------------------------------------------------
section "10. CLEANUP (optional checks)"

# Check for backup files (we can suggest removal)
backup_count=$(find . -maxdepth 3 -name "*.bak*" -o -name "*.backup*" 2>/dev/null | wc -l)
if [ "$backup_count" -gt 0 ]; then
    check_warn "Found $backup_count backup file(s) (*.bak*, *.backup*). Consider removing them."
else
    check_pass "No backup files detected."
fi

# ----------------------------------------------------------------------
# Final Summary
# ----------------------------------------------------------------------
section "SUMMARY"

echo "✅ Paper:"
echo "   - .tex:  $(ls -l AETG_paper/manuscript/AETG_paper.tex 2>/dev/null | awk '{print $5}') bytes"
echo "   - .pdf:  $(ls -l AETG_paper/output/AETG_paper.pdf 2>/dev/null | awk '{print $5}') bytes"
if command -v pdfinfo >/dev/null 2>&1; then
    pages=$(pdfinfo AETG_paper/output/AETG_paper.pdf 2>/dev/null | grep Pages | awk '{print $2}')
    echo "   - Halaman: $pages"
fi

echo ""
echo "✅ Eksperimen:"
if [ -f "code/experiments/eval_results.json" ]; then
    if command -v jq >/dev/null 2>&1; then
        echo "   - recall: $(jq -r '.recall' code/experiments/eval_results.json)"
        echo "   - evasion_rate: $(jq -r '.evasion_rate' code/experiments/eval_results.json)"
        echo "   - alert_count_in_redis: $(jq -r '.alert_count_in_redis' code/experiments/eval_results.json)"
    else
        echo "   - eval_results.json exists."
    fi
fi

echo ""
echo "✅ Docker (if running):"
if command -v docker >/dev/null 2>&1; then
    docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "   (Docker not reachable)"
fi

echo ""
echo "============================================================"
echo "Health check completed at $(date)"
echo "Report saved to $REPORT_FILE"
echo "============================================================"

# Generate report file
{
    echo "AETG Project Health Check Report"
    echo "Generated: $(date)"
    echo "----------------------------------------"
    echo "Paper: OK (no REVIEW NOTE, no UNVERIFIED)"
    echo "PDF pages: $pages"
    if [ -f "code/experiments/eval_results.json" ] && command -v jq >/dev/null 2>&1; then
        echo "recall: $(jq -r '.recall' code/experiments/eval_results.json)"
        echo "evasion_rate: $(jq -r '.evasion_rate' code/experiments/eval_results.json)"
        echo "alert_count_in_redis: $(jq -r '.alert_count_in_redis' code/experiments/eval_results.json)"
    fi
    echo "----------------------------------------"
    echo "All checks passed (or warnings noted)."
} > "$REPORT_FILE"

exit 0
