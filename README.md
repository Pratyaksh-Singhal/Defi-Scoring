# Wallet Credit Scoring Model

This repository contains a Python-based solution for calculating credit scores for cryptocurrency wallets based on their on-chain transaction history. The model processes raw transaction data, engineers relevant features, and assigns a credit score from 0 to 1000 to each wallet.

## Table of Contents

- [Introduction]
- [Methodology]
- [Architecture]
- [Processing Flow]
- [Features and Weights]
- [Getting Started]
  - [Prerequisites]
  - [Installation]
  - [Usage]
- [Analysis]
- [Contributing]
- [License]

## Introduction

In the decentralized finance (DeFi) ecosystem, assessing the creditworthiness of a wallet is crucial for various applications like lending protocols, undercollateralized loans, and risk management. This project aims to provide a transparent and quantifiable credit scoring mechanism by analyzing a wallet's historical on-chain activities.

## Methodology

The credit scoring model employs a feature-engineering approach combined with a weighted scoring mechanism.

1. **Install Requirements**: Install all the requirements file before running the main code. After cloning the repository run the following command to install all the dependencied "pip install -r requirements.txt".
2.  **Data Preprocessing**: Raw transaction data, typically in JSON format, is loaded and cleaned. This involves parsing complex `actionData` strings and standardizing transaction amounts into USD values.
3.  **Feature Engineering**: A comprehensive set of features is extracted for each unique wallet. These features capture various aspects of a wallet's financial behavior, activity levels, and risk indicators.
4.  **Normalization**: Each engineered feature is normalized using Min-Max scaling to bring them to a common scale (0 to 1). This ensures that features with larger numerical ranges do not disproportionately influence the final score.
5.  **Weighted Scoring**: A predefined set of weights is applied to the normalized features. Positive weights are assigned to desirable behaviors (e.g., repayment, deposits), while negative weights are assigned to undesirable behaviors (e.g., liquidations, net borrowing).
6.  **Score Calculation**: The weighted sum of normalized features is calculated for each wallet. This raw score is then scaled to a final credit score ranging from 0 to 1000.
7.  **Analysis and Visualization**: The distribution of credit scores is analyzed, and a histogram is generated to visualize the overall score landscape. Further analysis is performed on wallets in the extreme ends of the score spectrum to understand their characteristic behaviors.

## Architecture

The solution is structured into two main components:

-   **Scoring Module (`scoring.py`)**: Responsible for all data processing, feature engineering, and credit score calculation. It takes raw transaction data as input and outputs a JSON file containing the calculated wallet scores.
-   **Plotting Module (`plotting.py`)**: Responsible for loading the generated scores and visualizing their distribution.

├── data/ │ └── user-wallet-transactions.json # Input raw transaction data ├── output/ │ ├── wallet_scores.json # Output JSON with calculated scores │ └── score_distribution.png # Output plot of score distribution ├── scoring.py # Main script for scoring wallets ├── plotting.py # Script for plotting score distribution └── README.md # Project documentation └── analysis.md # Detailed analysis of wallet scores


## Processing Flow

1.  **Input Data**: The process begins with `data/user-wallet-transactions.json`, which contains a list of wallet transactions.
2.  **`scoring.py` Execution**:
    *   `load_and_preprocess_data()`: Reads the JSON, converts timestamps, parses `actionData`, and calculates `tx_value_usd` for each transaction.
    *   `engineer_features()`: Groups transactions by `userWallet` and computes various features (e.g., `total_repaid_usd`, `liquidation_count`, `activity_span_days`).
    *   `calculate_wallet_scores()`: Normalizes the engineered features using Min-Max scaling and applies `FEATURE_WEIGHTS` to compute a raw score. This raw score is then scaled to a 0-1000 range.
    *   The final scores are saved to `output/wallet_scores.json`.
3.  **`plotting.py` Execution**:
    *   `load_wallet_scores()`: Reads the `output/wallet_scores.json` file.
    *   `analyze_scores()`: Generates a histogram of the credit score distribution and saves it as `output/score_distribution.png`. It also prints descriptive statistics of the scores.

## Features and Weights

The following features are engineered and used in the credit score calculation, along with their respective weights. Positive weights indicate a positive contribution to the score, while negative weights indicate a negative contribution.

| Feature                       | Description                                                              | Weight |
| :---------------------------- | :----------------------------------------------------------------------- | :----- |
| `total_repaid_usd`            | Total USD value of repaid loans.                                         | 0.25   |
| `repay_to_borrow_ratio`       | Ratio of total repaid USD to total borrowed USD.                         | 0.30   |
| `total_deposited_usd`         | Total USD value of deposited assets.                                     | 0.15   |
| `activity_span_days`          | Number of days between the first and last transaction.                   | 0.10   |
| `avg_tx_per_day`              | Average number of transactions per active day.                           | 0.05   |
| `unique_actions`              | Number of distinct action types performed by the wallet.                 | 0.05   |
| `liquidation_count`           | Number of times the wallet has been liquidated. (Negative impact)        | -0.50  |
| `net_borrowed_usd`            | Total borrowed USD minus total repaid USD. (Negative impact)             | -0.10  |
| `borrow_to_deposit_ratio`     | Ratio of total borrowed USD to total deposited USD. (Negative impact)    | -0.05  |

**Note**: The `recency_score` feature mentioned in the previous context was part of an iterative debugging process and is not explicitly listed in the final `FEATURE_WEIGHTS` dictionary in `code_1.py`. The provided `code_1.py` uses the weights as defined in `FEATURE_WEIGHTS`.

## Getting Started

### Prerequisites

-   Python 3.8+
-   `pandas`
-   `numpy`
-   `matplotlib`
-   `seaborn`

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/wallet-credit-scoring.git
    cd wallet-credit-scoring
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  Place your `user-wallet-transactions.json` file in the `data/` directory.
2.  Run the scoring script:
    ```bash
    python scoring.py
    ```
    This will generate `wallet_scores.json` in the `output/` directory.
3.  Run the plotting script:
    ```bash
    python plotting.py
    ```
    This will generate `score_distribution.png` in the `output/` directory and display the plot.

## Analysis

For a detailed analysis of the wallet scores, including score distribution and behavior of wallets in different score ranges, please refer to `analysis.md`.

