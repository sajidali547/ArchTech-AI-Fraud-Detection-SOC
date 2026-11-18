# SOC Detection Report: AI Fraud Engine

## Threat and rule limitations

In the Arch Store scenario, attackers automate payment attempts with stolen credit cards. A rule such as `Amount > $5000` can miss small card-testing attempts and can flag legitimate large orders. The scenario's attack and firewall failure are assumptions; this benchmark does not measure a real incident or a firewall comparison.

Automated validation of stolen card details matches [OWASP OAT-001 Carding](https://owasp.org/www-project-automated-threats-to-web-applications/assets/oats/EN/OAT-001_Carding.html). Credential stuffing is a separate login attack; this dataset contains no authentication logs to establish it.

## Model and data handling

The ULB/Worldline dataset contains 284,315 legitimate and 492 fraudulent transactions. The notebook removes 1,081 exact duplicates, leaving 283,726 unique transactions and 473 fraud cases. It creates a stratified 80/20 split with seed 42.

StandardScaler is fitted on training Amount and Time only. SMOTE balances the 226,980 training transactions into 453,204 training vectors. The test set stays unchanged. A 100-tree Random Forest learns from the supplied PCA features and scaled Amount and Time. This is supervised fraud classification.

## Triage results

The fixed fraud-score threshold is 0.50. Results on 56,746 held-out transactions:

| Actual class | Suppressed | HIGH review alert |
| --- | ---: | ---: |
| Legitimate | 56,644 TN | 7 FP |
| Fraud | 24 FN | 71 TP |

Fraud precision is **91.03%**, recall **74.74%**, and F1 **0.8208**. Legitimate suppression is **99.9876%**, exceeding the 99.8% target on this split. There are 78 HIGH alerts, including seven legitimate transactions. The model misses 24 fraud cases.

HIGH means analyst review, rather than a confirmed incident or a customer block. Analysts should correlate alerts with payment, device and session evidence. Validate chronologically on recent merchant data before deployment; this random historical split does not guarantee future performance.

## Evidence

All six notebook cells were executed successfully. `screenshots/00-import-libraries.png` is a real Windows capture of JupyterLab; its pixels were preserved when converting the capture to PNG. Remaining live screenshots are pending after Computer Use stopped at browser-URL verification during refresh. Generated output panels are no longer included.
