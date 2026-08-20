## 📄 **9. CONTRIBUTING.md**


# Contributing to AETG

We welcome contributions to the Adaptive Evasion Traffic Generator (AETG) project! This document outlines the guidelines for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

## How to Contribute

### 1. Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. Include:

- Clear description of the issue
- Steps to reproduce (if applicable)
- Expected vs. actual behavior
- Environment details (OS, Python version, dependencies)

### 2. Pull Requests

We follow the GitHub Flow:

1. **Fork the repository** and create your branch from `main`.
2. **Write code** with clear, descriptive commit messages.
3. **Test your changes** — run `python3 verify.py` to check syntax.
4. **Update documentation** if you change functionality.
5. **Open a pull request** with a clear description of what you changed and why.

### 3. Code Style

- **Python**: Follow PEP 8.
- **LaTeX**: Keep line width ≤ 80 characters.
- **Documentation**: Use clear, professional language.

### 4. Development Setup


# Clone the repository
git clone https://github.com/afuckingco/Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques.git
cd Adversarial-ML-for-IDS-Validation-via-Red-Team-Techniques

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r code/adversarial-traffic-generator/requirements.txt

Areas Needing Contribution
High Priority

    Fix key-pattern mismatch — eval_ids.py currently uses r.llen('alerts') but should use r.keys('alert:*').

    Create architecture diagram — Replace the text-based placeholder with a proper PNG/PDF diagram.

    Complete closed-loop feedback — Implement LinUCB training on live Suricata/ML-derived rewards.

Medium Priority

    Add more attack types — Extend beyond the current 6 attack templates.

    Measure False Positive Impact — Evaluate benign flow alert rate during tests.

    Improve ESM — Handle concept drift and dynamic baselines.

Low Priority

    Multi-IDS evasion — Support Zeek and Elastic SIEM alongside Suricata.

    Transfer learning — Reuse evasion strategies across different IDS models.

    Real-time rule adaptation — Adapt to dynamic signature updates.

Review Process

All contributions will be reviewed by the maintainer. We aim to provide feedback within 5 business days. Please be patient and open to suggestions.

License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.
Questions?

If you have any questions, please open an issue or contact the maintainer directly.

Thank you for contributing to AETG! 🚀
