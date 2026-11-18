# 🛡️ AI-Driven Credit Card Fraud Detection (SOC Scenario)

## 📖 The Scenario

An e-commerce platform (Arch Store) is facing an automated bot attack where stolen credit cards are being used to make fraudulent purchases. Traditional rule-based firewalls are failing, resulting in high false positives. In this SOC lab, a Machine Learning-based Detection Engine identifies suspicious transaction patterns.

## 🏗️ Technical Architecture

- **Algorithm:** Random Forest Classifier
- **Data Processing:** StandardScaler, Pandas
- **Imbalance Handling:** SMOTE (Synthetic Minority Over-sampling Technique) to handle the approximately 0.2% fraud ratio.
- **Evaluation:** Confusion Matrix (focusing on False Positives vs. False Negatives) and F1-Score.

## 🔍 SOC Metrics Addressed

- **False Positives (FP):** Normal transactions flagged as fraud, causing unnecessary review and potential customer friction.
- **False Negatives (FN):** Fraudulent transactions missed by the model, creating financial-loss risk. The model aims to minimize FN while keeping FP low.

## 🧠 Skills Demonstrated

- Machine Learning for Cybersecurity (AI in Sec)
- Detection Engineering
- Anomaly Detection & Data Analysis
- Python (Scikit-Learn, Pandas, Seaborn)

## 📸 Screenshots

- [Baseline traffic](screenshots/01-baseline-traffic.png)
- [SMOTE balancing](screenshots/02-smote-balancing.png)
- [Confusion matrix](screenshots/03-confusion-matrix.png)
- [Detection report](screenshots/04-detection-report.png)

All four images are real captures of JupyterLab on the PC.
