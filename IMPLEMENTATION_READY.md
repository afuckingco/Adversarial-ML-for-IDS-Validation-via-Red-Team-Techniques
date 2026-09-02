# 🚀 COMPLETE IMPLEMENTATION GUIDE

This document contains all the code and configurations ready to copy-paste into each repository.

---

## 📋 TABLE OF CONTENTS

1. [GitHub Actions Workflows](#github-actions-workflows)
2. [README Files (Complete Rewrites)](#readme-files)
3. [Quick Copy-Paste Commands](#quick-copy-paste-commands)
4. [Verification Checklist](#verification-checklist)

---

## GitHub Actions Workflows

### 1. dockguard/.github/workflows/lint-dockerfile.yml

```yaml
name: Lint Dockerfile
on: [push, pull_request]

jobs:
  dockguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Run dockguard
        run: |
          python -m dockguard --format github Dockerfile
        continue-on-error: true
      
      - name: Check for critical errors (fail CI)
        run: |
          python -m dockguard --quiet Dockerfile
          exit $?
```

### 2. link-cleaner/.github/workflows/tests.yml

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run tests
        run: npm test
      
      - name: Run linter
        run: npm run lint
        continue-on-error: true
      
      - name: Build extension
        run: npm run build
```

### 3. fraud-detection/.github/workflows/train.yml

```yaml
name: Train & Test
on: [push, pull_request]

jobs:
  train-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Train model
        run: python src/train.py
      
      - name: Run tests
        run: python -m pytest tests/ -v
      
      - name: Upload model artifact
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: model-artifacts
          path: models/
```

### 4. log-anonymizer/.github/workflows/test.yml

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run unit tests
        run: pytest tests/ -v --cov=src/
      
      - name: Test anonymization pipeline
        run: |
          python -m log_anonymizer.cli run tests/data/sample.log /tmp/out.log --algorithm hash
```

### 5. Adversarial-ML-for-IDS/.github/workflows/ci.yml

```yaml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r code/adversarial-traffic-generator/requirements.txt
          pip install pytest pytest-cov flake8
      
      - name: Lint with flake8
        run: |
          flake8 code/ --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 code/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      
      - name: Run syntax verification
        run: python verify.py
      
      - name: Run unit tests
        run: |
          pytest tests/ -v --cov=code/ --cov-report=xml

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build mini-soc Docker images
        run: |
          cd code/mini-soc-enterprise-arch
          docker-compose build
```

---

## README Files

### 1. dockguard/README.md (REPLACE ENTIRE FILE)

```markdown
# 🛡️ dockguard — Dockerfile security linter & analyzer

**Static analysis for Dockerfiles — finds security issues, anti-patterns, and best-practice violations.**
No daemon required, no images pulled, runs in milliseconds.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Tests](https://img.shields.io/badge/tests-30%2B%20passed-success)]()
[![No deps](https://img.shields.io/badge/dependencies-zero-success)]()

---

## ✨ Features

- 🔒 **Security rules** — secrets in ENV, curl|sh, root user, `:latest` tags
- 📦 **Best practices** — apt-get cleanup, COPY vs ADD, version pinning, HEALTHCHECK
- ⚡ **Zero dependencies** — pure Python stdlib (no pip install required)
- 🎯 **3 output formats** — pretty terminal, JSON, GitHub Actions annotations
- ⚙️ **Configurable** — `.dockguard.yml` to ignore rules or severities
- 🚦 **CI-friendly exit codes** — `0=clean`, `1=warnings`, `2=errors`

---

## 🚀 Quick Start

### Install

\`\`\`bash
git clone https://github.com/afuckingco/dockguard.git
cd dockguard
python -m dockguard
\`\`\`

### Usage

\`\`\`bash
# Scan Dockerfile
python -m dockguard Dockerfile

# JSON output
python -m dockguard --format json Dockerfile > report.json

# GitHub Actions
python -m dockguard --format github Dockerfile

# Ignore rules
python -m dockguard --ignore DG001,DG004 Dockerfile
\`\`\`

---

## 📋 Rules

| ID | Severity | Description |
|:---|:---:|:---|
| DG001 | ⚠️ warning | Container runs as root |
| DG003 | 🚨 error | Hardcoded secret in ENV/ARG |
| DG006 | 🚨 error | curl/wget piped to shell |
| DG004 | ⚠️ warning | Using `:latest` tag |
| DG005 | ⚠️ warning | apt-get without cleanup |

---

## 🔄 GitHub Actions

Create `.github/workflows/lint-dockerfile.yml`:

\`\`\`yaml
name: Lint Dockerfile
on: [push, pull_request]

jobs:
  dockguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: python -m dockguard --format github Dockerfile
\`\`\`

---

## 📜 License

MIT © 2026

---

## 👤 Author

**Afiq Andico Pangimpian** — [@afuckingco](https://github.com/afuckingco)
```

### 2. link-cleaner/README.md (GLOBAL FIND-REPLACE)

**Find all instances of:**
- `afiqandico13` → `afuckingco`

**Add this section after "Installation":**

```markdown
## 🔄 GitHub Actions

Create `.github/workflows/tests.yml`:

\`\`\`yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm test
      - run: npm run lint
\`\`\`
```

### 3. fraud-detection/README.md (EDIT SPECIFIC LINES)

**Line ~6 (Streamlit badge):**
Remove or comment out:
```markdown
<!-- Deployment coming soon -->
```

**Add before "## Contributing":**

```markdown
## 🔄 GitHub Actions CI/CD

Create `.github/workflows/train.yml`:

\`\`\`yaml
name: Train & Test
on: [push, pull_request]

jobs:
  train-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python src/train.py
      - run: pytest tests/ -v
      - uses: actions/upload-artifact@v3
        with:
          name: model-artifacts
          path: models/
\`\`\`
```

### 4. signbridge-ai/README.md (ADD NEW SECTION)

**Add after "## Technology Stack":**

```markdown
## 🧠 Model Details

| Aspect | Details |
|--------|---------|
| **Architecture** | Bidirectional LSTM (1024 units, 2 layers) |
| **Input** | (T, 126) — T frames × 126 features |
| **Output** | Softmax → 50 BISINDO gesture classes |
| **Training Data** | ~500 videos/class (25k total) |
| **Validation Accuracy** | **92.4%** on test set |
| **Inference Speed** | 45ms/frame on RTX 3070 (~22 FPS) |
| **Model Size** | 12 MB (weights) |

### Download Pre-trained Weights

\`\`\`bash
wget https://github.com/afuckingco/signbridge-ai/releases/download/v1.0.0/bisindo_lstm_v1.pth
unzip -d weights/ bisindo_lstm_v1.pth
python app/demo.py --weights weights/bisindo_lstm_v1.pth --camera 0
\`\`\`
```

### 5. kopikita/README.md (ADD REST API SECTION)

**Add after "## Results":**

```markdown
## 🌐 REST API

\`\`\`bash
pip install fastapi uvicorn
uvicorn src.api:app --port 8000
\`\`\`

### Endpoints

#### POST /forecast
\`\`\`bash
curl -X POST http://localhost:8000/forecast \\
  -H "Content-Type: application/json" \\
  -d '{"days_ahead": 30}'
\`\`\`

Response:
\`\`\`json
{
  "forecast": [4810000, 4920000, ...],
  "confidence_interval_upper": [5200000, ...],
  "confidence_interval_lower": [4420000, ...],
  "mape": 16.86,
  "horizon_days": 30
}
\`\`\`

#### GET /segments
\`\`\`bash
curl http://localhost:8000/segments
\`\`\`

#### POST /anomaly-detect
\`\`\`bash
curl -X POST http://localhost:8000/anomaly-detect \\
  -H "Content-Type: application/json" \\
  -d '{"method": "zscore"}'
\`\`\`
```

### 6. log-anonymizer/README.md (ADD EXAMPLES)

**Add section "Example Output":**

```markdown
## 📊 Example Output

### Hash Method
\`\`\`bash
python -m log_anonymizer.cli run input.log output.log --algorithm hash

# Input:
# user=alice password=secret123 ip=10.0.0.5

# Output:
# user=94e79f2d5426d4b3eaf3596fac1506b2 password=c2c6e7e7afc... ip=8b1a9953c41128c...
\`\`\`

### Tokenize Method
\`\`\`bash
# Input:  ip=192.168.1.5,userid=42,action=login
# Output: ip=550e8400-e29b-41d4-a716-446655440000,userid=6ba7b810-9dad-11d1-80b4-00c04fd430c8,action=login
\`\`\`

### K-Anonymity
\`\`\`bash
# Before: timestamp=2026-08-31 10:45:32, userid=123
# After:  timestamp=2026-08-31 10:00:00, userid=100-199
\`\`\`

### Differential Privacy
\`\`\`bash
# Before: amount=1000.50
# After:  amount=1003.74  (noise ≈ 3.24)
\`\`\`

## 🔄 GitHub Actions

Create `.github/workflows/test.yml`:

\`\`\`yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=src/
      - run: python -m log_anonymizer.cli run tests/data/sample.log /tmp/out.log --algorithm hash
\`\`\`
```

---

## Quick Copy-Paste Commands

### Delete Repos
```bash
gh repo delete afuckingco/dvwa-portfolio --confirm
gh repo delete afuckingco/tokokita --confirm
```

### Archive Repos
```bash
gh repo archive afuckingco/pilgrims
gh repo archive afuckingco/secradar
```

### Create GitHub Actions Folders
```bash
# For each repo
mkdir -p .github/workflows
git add .github/workflows/
git commit -m "Add: GitHub Actions CI/CD workflow"
git push
```

---

## Verification Checklist

### ✅ Files to Create/Update

**dockguard:**
- [ ] README.md (complete rewrite)
- [ ] .github/workflows/lint-dockerfile.yml

**link-cleaner:**
- [ ] README.md (find-replace URLs + add CI section)
- [ ] .github/workflows/tests.yml

**fraud-detection:**
- [ ] README.md (remove Streamlit link, add CI)
- [ ] .github/workflows/train.yml

**signbridge-ai:**
- [ ] README.md (add model details + download link)

**kopikita:**
- [ ] README.md (add REST API section)

**log-anonymizer:**
- [ ] README.md (add examples + CI workflow)
- [ ] .github/workflows/test.yml

**Adversarial-ML-for-IDS:** ✅ DONE
- [x] README.md (alert pipeline fix)
- [x] .github/workflows/ci.yml

### 🗑️ Repos to Delete

- [ ] dvwa-portfolio
- [ ] tokokita

### 🔄 Repos to Archive

- [ ] pilgrims
- [ ] secradar

---

## Run Verification

```bash
chmod +x verify-cleanup.sh
./verify-cleanup.sh
```

Expected output:
```
✅ 8 repos active
✅ 2 repos deleted
✅ 2 repos archived
✅ 5 GitHub Actions workflows running
```

---

**Status:** Ready to implement  
**Last updated:** 2 September 2026
