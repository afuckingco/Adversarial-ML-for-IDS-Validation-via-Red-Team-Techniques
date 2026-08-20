# Audit Log

This document tracks the files and artifacts included in the AETG project, their status, and verification results.

## File Inventory

| File | Status | Verification |
|------|--------|--------------|
| `AETG_paper.tex` | ✅ Verified | LaTeX source compiles without errors |
| `AETG_paper.docx` | ✅ Verified | Word version, aligned with LaTeX |
| `AETG_paper.pdf` | ✅ Verified | Compiled from LaTeX (30 pages) |
| `references.bib` | ✅ Verified | 12 references, all cited in paper |
| `elsarticle_offline_shim.cls` | ✅ Present | Class file for Elsevier template |
| `aetg_architecture.png` | ✅ Present | Architecture diagram (text-based placeholder) |
| `eval_results.json` | ✅ Verified | Contains recall=1.0, evasion=0.0 |
| `adv_training_results.json` | ✅ Verified | Contains adversarial training results |
| `eval_ids.py` | ✅ Verified | Evaluation script, key-pattern mismatch identified |
| `push_alerts.py` | ✅ Verified | Alert ingestion script |
| `new_traffic_gen.py` | ✅ Verified | CLI entry point |

## Experiment Logs

| Log File | Status | Content |
|----------|--------|---------|
| `code/experiments/eval_results.json` | ✅ | Main evaluation (200 flows) |
| `code/experiments/adv_training_results.json` | ✅ | Adversarial training experiment |
| `AETG_paper/data/eval_results.json` | ✅ | Copy for paper |

## Known Issues

| Issue | Status | Resolution |
|-------|--------|------------|
| Key-pattern mismatch in `eval_ids.py` | ⚠️ Open | Uses `r.llen('alerts')` vs `r.set('alert:*')` |
| Figure `aetg_architecture.png` | ⚠️ Placeholder | Text-based diagram provided |
| Closed-loop feedback | ❌ Not completed | Future work |
| False Positive Impact | ❌ Not measured | Future work |

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-08-19 | v1.0 | Initial draft |
| 2026-08-19 | v1.1 | Added Section 5.9 (Mini-SOC status) |
| 2026-08-20 | v1.2 | Corrected alert_count interpretation, removed REVIEW NOTEs |

## Verification Commands

```bash
# Compile LaTeX
pdflatex AETG_paper.tex
bibtex AETG_paper
pdflatex AETG_paper.tex
pdflatex AETG_paper.tex

# Verify Python syntax
python3 verify.py

# Check for REVIEW NOTE
grep -i "REVIEW NOTE" AETG_paper.tex

# Check references
grep -n "UNVERIFIED" references.bib

Auditor

    Name: Afiq Andico Pangimpian

    Date: August 20, 2026

    Signature: (verified by author)

Next Steps

    Fix key-pattern mismatch in eval_ids.py

    Create proper aetg_architecture.png

    Complete closed-loop feedback integration

    Measure False Positive Impact

    Re-run experiments against Suricata with ML-derived rewards
    
    
