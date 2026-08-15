#!/usr/bin/env python3
"""
Verification script for the Adversarial ML for IDS Validation via Red-Team Techniques repository.
Checks that key files exist and have valid Python syntax (without requiring dependencies).
"""

import os
import sys
import subprocess

def check_file_exists(path):
    """Check if a file exists."""
    if not os.path.exists(path):
        print(f"[FAIL] Missing file: {path}")
        return False
    print(f"[OK] Found file: {path}")
    return True

def check_directory_exists(path):
    """Check if a directory exists."""
    if not os.path.isdir(path):
        print(f"[FAIL] Missing directory: {path}")
        return False
    print(f"[OK] Found directory: {path}")
    return True

def check_python_syntax(file_path):
    """Check Python syntax of a file without executing it."""
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', file_path],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[OK] Syntax OK: {file_path}")
            return True
        else:
            print(f"[FAIL] Syntax error in {file_path}:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[FAIL] Failed to check syntax for {file_path}: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=== Verification of Adversarial ML for IDS Validation Repository ===\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_passed = True
    
    # Check that we are in the repository root
    if not os.path.exists(os.path.join(base_dir, "README.md")):
        print("[FAIL] Not in the repository root: README.md not found")
        return False
    
    # List of tasks and their key files to check
    tasks = {
        "adversarial-traffic-generator": [
            "src/traffic_gen.py",
            "README.md",
            "requirements.txt"
        ],
        "aksara-bali-ocr": [
            "src/train.py",
            "README.md",
            "requirements.txt"
        ],
        "dl-anomaly-detection-fundamentals": [
            "src/train.py",
            "README.md",
            "requirements.txt"
        ],
        "ids-architecture-comparison": [
            "src/train.py",
            "README.md",
            "requirements.txt",
            "xgb_model.json",
            "scaler_params.json"
        ],
        "ids-validation-saas-mvp": [
            "src/app.py",
            "src/templates/index.html",
            "README.md",
            "requirements.txt"
        ],
        "is-transformation-case-study": [
            "README.md"
        ],
        "mini-soc-enterprise-arch": [
            "docker-compose.yml",
            "README.md",
            "ids/Dockerfile",
            "ids/app.py",
            "shared/model/xgb_model.json",
            "shared/model/scaler_params.json"
        ],
        "network-traffic-analytics-pipeline": [
            "src/etl.py",
            "README.md",
            "requirements.txt",
            "data/processed/dataset.parquet"
        ],
        "paper-replication-ids-adversarial": [
            "src/replicate.py",
            "README.md",
            "requirements.txt"
        ],
        "thesis-research-design": [
            "README.md"
        ],
        "threat-intel-aggregator": [
            "src/aggregator.py",
            "README.md",
            "requirements.txt",
            "data/threat_intel_sample.json",
            "threat_intel.json"
        ]
    }
    
    # Check each task's files
    for task_name, files in tasks.items():
        print(f"\n--- Checking {task_name} ---")
        task_dir = os.path.join(base_dir, task_name)
        if not check_directory_exists(task_dir):
            all_passed = False
            continue
        for file_rel in files:
            file_path = os.path.join(task_dir, file_rel)
            if not check_file_exists(file_path):
                all_passed = False
                continue
            # If it's a Python file, check syntax
            if file_path.endswith('.py'):
                if not check_python_syntax(file_path):
                    all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED")
        print("The repository has been successfully created and verified.")
        return True
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please review the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)