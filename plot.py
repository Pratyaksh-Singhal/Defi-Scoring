import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import os

output_dir = 'output'
output_json_file = os.path.join(output_dir, 'wallet_scores_2.json')

if os.path.exists(output_json_file):
    with open(output_json_file, 'r') as f:
        scores_data = json.load(f)
    scores_df = pd.DataFrame(scores_data)

    sns.set(style="whitegrid")

    plt.figure(figsize=(12, 6))
    sns.histplot(scores_df, bins=30, kde=True, color='blue', alpha=0.6, edgecolor='black')
    plt.title('Distribution of Wallet Credit Scores (0-1000)', fontsize=16)
    plt.xlabel('Credit Score', fontsize=14)
    plt.ylabel('Number of Wallets', fontsize=14)
    plt.grid(axis='y', alpha=0.75)
    plt.show()

else:
    print(f"Score file not found: {output_json_file}. Please run `credit_score_model.py` first.")
