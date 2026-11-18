# SOC Detection Report: AI Fraud Engine

## 1. Threat Overview

The Arch Store scenario involves automated card testing and fraudulent purchases using stolen card details. Credential stuffing, when stolen account logins are also used, is a separate authentication technique covered by MITRE ATT&CK T1110.004. The transaction dataset does not establish a live bot incident.

## 2. Why Traditional SIEM Rules Failed

A traditional rule such as `IF Amount > $5000 THEN ALERT` can miss small, distributed card-testing transactions, such as $10 attempts. This is the scenario's motivation; a measured SIEM comparison is outside the supplied experiment.

## 3. The ML Solution

A Random Forest Classifier is trained on historical fraud labels using the supplied V1-V28 PCA components and scaled Amount and Time. It classifies transactions as normal or suspected fraud for SOC review.

## 4. Imbalance Resolution

The baseline dataset contains 284,315 legitimate transactions and only 492 frauds. Training-only SMOTE expands the training set from 227,845 to 454,902 feature vectors. The test set remains untouched at 56,962 transactions.

## 5. Triage & Evaluation

- **True Positives:** 79 fraud cases correctly flagged.
- **False Negatives:** 19 fraud cases missed.
- **False Positives:** 18 legitimate transactions incorrectly flagged.
- **True Negatives:** 56,846 legitimate transactions correctly classified.

Fraud precision: **81.44%**. Recall: **80.61%**. F1-score: **0.8103**. Legitimate suppression: **99.9683%**.

These are results from the supplied random-split workflow. Scaling before splitting and repeated records can make benchmark performance optimistic; training-only scaling and chronological validation are needed for a stronger evaluation. A flag is a review signal, not evidence that a payment was blocked.
