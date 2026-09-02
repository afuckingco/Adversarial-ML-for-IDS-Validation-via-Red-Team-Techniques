#!/bin/bash
# Quick fix script for GitHub profile cleanup
# Run this after manual edits to verify all changes

set -e

echo "🔍 GitHub Profile Cleanup Verification Script"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASS=0
FAIL=0

check_repo() {
    local repo=$1
    local description=$2
    
    if gh repo view afuckingco/$repo &> /dev/null; then
        echo -e "${GREEN}✅${NC} $repo exists"
        echo "   $description"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $repo not found"
        ((FAIL++))
    fi
}

check_archived() {
    local repo=$1
    
    if gh repo view afuckingco/$repo --json isArchived --jq '.isArchived' 2>/dev/null | grep -q true; then
        echo -e "${GREEN}✅${NC} $repo is ARCHIVED"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️${NC} $repo not archived yet"
        ((FAIL++))
    fi
}

echo "📊 ACTIVE REPOS (should exist and not be archived)"
echo "=================================================="
check_repo "Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques" "Thesis - IDS validation"
check_repo "sift" "Security tool - secret scanner"
check_repo "dockguard" "Security tool - Dockerfile linter"
check_repo "link-cleaner" "Privacy tool - browser extension"
check_repo "fraud-detection" "ML portfolio - fraud detection"
check_repo "signbridge-ai" "CV project - sign language translator"
check_repo "kopikita" "Data science - cafe analytics"
check_repo "log-anonymizer" "Privacy toolkit - log anonymization"

echo ""
echo "🗑️  DELETED REPOS (should NOT exist)"
echo "===================================="
if ! gh repo view afuckingco/dvwa-portfolio &>/dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} dvwa-portfolio DELETED"
    ((PASS++))
else
    echo -e "${RED}❌${NC} dvwa-portfolio still exists"
    ((FAIL++))
fi

if ! gh repo view afuckingco/tokokita &>/dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} tokokita DELETED"
    ((PASS++))
else
    echo -e "${RED}❌${NC} tokokita still exists"
    ((FAIL++))
fi

echo ""
echo "🔄 ARCHIVED REPOS (should be archived)"
echo "====================================="
check_archived "pilgrims" "Old project - archived"
check_archived "secradar" "Superseded by sift - archived"

echo ""
echo "📝 README CHECKS (sample)"
echo "========================"

# Check for common patterns
echo "Checking for URL fixes in link-cleaner..."
if gh repo view afuckingco/link-cleaner &>/dev/null 2>&1; then
    if gh api repos/afuckingco/link-cleaner/contents/README.md --jq '.content' 2>/dev/null | base64 -d | grep -q "afuckingco" && ! grep -q "afiqandico13" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} link-cleaner README has correct URLs"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️${NC} link-cleaner: check if URLs updated"
    fi
fi

echo ""
echo "✨ GitHub Actions Workflows"
echo "==========================="

check_workflow() {
    local repo=$1
    local workflow=$2
    
    if gh api repos/afuckingco/$repo/contents/.github/workflows/$workflow --jq '.name' &>/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $repo has $workflow"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️${NC} $repo missing $workflow"
    fi
}

check_workflow "Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques" "ci.yml"
check_workflow "dockguard" "lint-dockerfile.yml"
check_workflow "link-cleaner" "tests.yml"
check_workflow "fraud-detection" "train.yml"
check_workflow "log-anonymizer" "test.yml"

echo ""
echo "📊 SUMMARY"
echo "=========="
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"
echo "Total:  $((PASS + FAIL))"

if [ $FAIL -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL CHECKS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ SOME CHECKS FAILED${NC}"
    echo "Please complete remaining manual edits."
    exit 1
fi
