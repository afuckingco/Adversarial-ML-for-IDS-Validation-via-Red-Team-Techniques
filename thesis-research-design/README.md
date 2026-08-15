# Thesis Research Design

## Title
Adversarial Machine Learning in Network Intrusion Detection Systems: Generation, Detection, and Mitigation

## Background
Network Intrusion Detection Systems (NIDS) are critical components of cybersecurity infrastructure. With the rise of machine learning-based NIDS, adversarial machine learning poses a significant threat by crafting inputs that evade detection. This thesis investigates the generation of adversarial traffic, its impact on NIDS, and potential mitigation strategies.

## Research Questions
1. **RQ1**: How can realistic adversarial network traffic be generated to test ML-based NIDS?
2. **RQ2**: What is the effectiveness of various adversarial attacks (e.g., FGSM, JSMA, CW) against different NIDS architectures (XGBoost, CatBoost, MLP)?
3. **RQ3**: How do feature importance and ablation studies reveal vulnerabilities in NIDS models?
4. **RQ4**: What mitigation strategies (e.g., adversarial training, feature sanitization) can improve the robustness of NIDS against adversarial examples?

## Hypotheses
- **H1**: Adversarial traffic generated with randomized JA3 fingerprints and timing jitter can evade signature-based and anomaly-based NIDS.
- **H2**: Gradient-based adversarial attacks (FGSM, JSMA, CW) will significantly reduce the F1-score of ML-based NIDS compared to benign traffic.
- **H3**: Features related to packet size and volume (e.g., total_packets, avg_packet_size) are more critical for NIDS model performance than JA3-based features.
- **H4**: Adversarial training will improve the robustness of NIDS models, increasing their F1-score on adversarial examples by at least 20%.

## Variables
### Independent Variables
- **Traffic Type**: Normal vs. Adversarial (generated via adversarial-traffic-generator)
- **Attack Method**: FGSM, JSMA, CW (for ML-based evasion) vs. None (benign)
- **NIDS Architecture**: XGBoost, CatBoost, MLP
- **Feature Set**: Full feature set vs. Ablated features (removing one feature at a time)
- **Mitigation Strategy**: None, Adversarial Training, Feature Sanitization

### Dependent Variables
- **Detection Rate**: True Positive Rate (Recall) of the NIDS
- **False Positive Rate**: False Positive Rate of the NIDS
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area Under the Receiver Operating Characteristic curve
- **Evasion Rate**: 1 - Detection Rate for adversarial traffic

## Methodology
### Phase 1: Adversarial Traffic Generation
- Use the `adversarial-traffic-generator` to create network packets with:
  - Random JA3 fingerprints from tls-client's supported list
  - Timing jitter (uniformly distributed between 0.1s and 0.5s)
  - HTTP requests to a target (e.g., localhost or a test server)
- Generate both benign and adversarial traffic for controlled experiments.

### Phase 2: Dataset Preparation
- Collect network traffic features (using Zeek/Suricata or similar) from generated traffic.
- Extract features: total packets, average packet size, packet size standard deviation, unique source IPs, unique destination IPs, JA3 fingerprints (hashed or categorical).
- Label each flow as normal (0) or adversarial (1).
- Split dataset into training (70%) and testing (30%) sets, stratified by label.

### Phase 3: Model Training and Evaluation
- Train three models: XGBoost, CatBoost, and MLP (using scikit-learn) on the training set.
- Evaluate each model on the benign test set to establish baseline performance.
- Generate adversarial examples using:
  - FGSM (for gradient-based attacks on ML models)
  - (Optional) JSMA and CW if resources permit
- Evaluate models on adversarial examples to compute evasion rates.
- Perform ablation study: remove one feature at a time and retrain to assess feature importance.
- Implement mitigation strategies:
  - Adversarial Training: retrain models on a mix of benign and adversarial examples.
  - Feature Sanitization: remove or smooth features found to be most sensitive in ablation.

### Phase 4: Analysis
- Compare detection rates, F1-scores, and AUC-ROC across models and attack methods.
- Statistical significance testing (e.g., t-test) to compare performance before and after mitigation.
- Visualize feature importance and ROC curves.

## Evaluation Metrics
- **Primary**: F1-Score (balances precision and recall, important for imbalanced security data)
- **Secondary**: 
  - Accuracy (overall correctness)
  - Precision (minimizing false alarms)
  - Recall (maximizing detection of actual intrusions)
  - AUC-ROC (threshold-independent performance)
  - Evasion Rate (specifically for adversarial robustness)

## Sampling Strategy
- **Traffic Generation**: 
  - For each experiment, generate 10,000 flows (5,000 normal, 5,000 adversarial) to ensure sufficient statistical power.
  - Use random seeding for reproducibility but vary seeds across experiments to capture variability.
- **Dataset Splitting**: 
  - Stratified sampling to maintain class distribution in train and test sets.
  - If using real-world datasets (e.g., UNSW-NB15), use the provided train/test splits or resample to match experimental conditions.
- **Cross-Validation**: 
  - Use 5-fold cross-validation on the training set for hyperparameter tuning (if computational resources allow).
  - Otherwise, use a fixed train/test split as described.

## Threats to Validity
### Internal Validity
- **Confounding Variables**: The synthetic nature of generated traffic may not capture all real-world variations. Mitigation: Use realistic parameters based on literature and validate with a small real-world capture if possible.
- **Implementation Bias**: Adversarial attack implementations (FGSM, JSMA, CW) may differ from the paper. Mitigation: Use well-tested libraries (e.g., Foolbox, CleverHans) or clearly document custom implementations.

### External Validity
- **Generalizability**: Results may not generalize to other NIDS or network environments. Mitigation: Test on multiple datasets (if available) and discuss limitations.

### Construct Validity
- **Metric Suitability**: F1-score may not capture all aspects of NIDS performance (e.g., latency). Mitigation: Supplement with domain-specific metrics like mean time to detect (MTTD) if feasible.

## Ethical Considerations
- All experiments are conducted in a controlled, isolated environment (localhost or virtual network).
- No traffic is sent to external systems without explicit permission.
- The adversarial traffic generator is intended for defensive security research only.

## Timeline
- **Month 1-2**: Literature review and setup of adversarial traffic generator.
- **Month 3-4**: Dataset generation and feature extraction.
- **Month 5-6**: Model training, baseline evaluation, and adversarial example generation.
- **Month 7**: Ablation studies and mitigation strategy implementation.
- **Month 8**: Analysis, validation, and thesis writing.

## Resources
- **Hardware**: Local machine (AMD Ryzen 7 5800H, 14GB RAM, 512GB NVMe)
- **Software**: Python 3.x, scikit-learn, XGBoost, CatBoost, tls-client, Zeek/Suricata (for feature extraction, if used)
- **Datasets**: Synthetic (generated) and optionally UNSW-NB15 for comparison.

## Expected Contributions
1. A framework for generating realistic adversarial network traffic with configurable JA3 and timing parameters.
2. Empirical evaluation of adversarial ML attacks on multiple NIDS architectures.
3. Insights into feature importance and robustness of ML-based NIDS.
4. Preliminary mitigation strategies to improve adversarial resilience.

## References
(To be filled with actual citations from the thesis)

\end{document}