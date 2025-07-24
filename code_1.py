import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import os

INPUT_JSON_PATH = 'data/user-wallet-transactions.json'
OUTPUT_DIR = 'output'
OUTPUT_JSON_FILE = os.path.join(OUTPUT_DIR, 'wallet_scores_2.json')

FEATURE_WEIGHTS = {
    'total_repaid_usd': 0.25,
    'repay_to_borrow_ratio': 0.30,
    'total_deposited_usd': 0.15,
    'activity_span_days': 0.10,
    'avg_tx_per_day': 0.05,
    'unique_actions': 0.05,

    'liquidation_count': 0.50, 
    'net_borrowed_usd': 0.10,
    'borrow_to_deposit_ratio': 0.05,
}

def parse_action_data(action_data_str):
    
    if pd.isna(action_data_str):
        return {}
    try:
        action_data_str = action_data_str.replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false')
        return json.loads(action_data_str)
    except json.JSONDecodeError:
 
        data = {}
        pairs = re.findall(r"'([^']+)':\s*'([^']+)'", action_data_str)
        for key, value in pairs:
            data[key] = value
        pairs_no_quotes = re.findall(r"(\w+):\s*([0-9.]+)", action_data_str)
        for key, value in pairs_no_quotes:
            data[key] = value
        return data

def calculate_score(wallet_features, min_max_values):
    score = 0
    normalized_features = {}
    for feature, weight in FEATURE_WEIGHTS.items():
        min_val = min_max_values[feature]['min']
        max_val = min_max_values[feature]['max']
        value = wallet_features.get(feature, 0)

        if max_val == min_val:
            normalized_value = 0
        else:
            normalized_value = (value - min_val) / (max_val - min_val)

        normalized_features[feature] = normalized_value

        if feature in ['liquidation_count', 'net_borrowed_usd', 'borrow_to_deposit_ratio']:
            score -= (normalized_value * weight)
        else:
            score += (normalized_value * weight)

    max_possible_score_component = sum(weight for feature, weight in FEATURE_WEIGHTS.items() 
                                       if feature not in ['liquidation_count', 'net_borrowed_usd', 'borrow_to_deposit_ratio'])

    min_possible_score_component = -sum(weight for feature, weight in FEATURE_WEIGHTS.items() 
                                        if feature in ['liquidation_count', 'net_borrowed_usd', 'borrow_to_deposit_ratio'])
    
    score_range = max_possible_score_component - min_possible_score_component
    if score_range == 0:
        final_score_0_1 = 0.5
    else:
        final_score_0_1 = (score - min_possible_score_component) / score_range
    
    final_score_0_1 = max(0.0, min(1.0, final_score_0_1))

    final_score = int(final_score_0_1 * 1000)
    return final_score

def convert_csv_to_json(input_json_path):
    df = pd.read_json(input_json_path)
    df.to_csv("data/converted.csv")
    return "data/converted.csv"

def generate_wallet_scores(input_csv_path, output_json_path):
    print(f"Loading data from {input_csv_path}...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv_path}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Preprocessing data...")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['parsed_action_data'] = df['actionData'].apply(parse_action_data)
    df['amount_numeric'] = df['parsed_action_data'].apply(lambda x: float(x.get('amount', 0)) if x.get('amount') else 0)
    df['asset_price_usd'] = df['parsed_action_data'].apply(lambda x: float(x.get('assetPriceUSD', 0)) if x.get('assetPriceUSD') else 0)
    df['tx_value_usd'] = df.apply(lambda row: row['amount_numeric'] * row['asset_price_usd'] if row['asset_price_usd'] > 0 else row['amount_numeric'], axis=1)

    df['assetSymbol'] = df['parsed_action_data'].apply(lambda x: x.get('assetSymbol'))
    df.loc[df['assetSymbol'].isin(['USDC', 'USDT']), 'tx_value_usd'] = \
        df.loc[df['assetSymbol'].isin(['USDC', 'USDT'])].apply(
            lambda row: row['amount_numeric'] / 1e6 * row['asset_price_usd'] if row['asset_price_usd'] > 0 else row['amount_numeric'] / 1e6, axis=1
        )
    df.loc[df['assetSymbol'].isin(['WMATIC', 'WETH', 'DAI']), 'tx_value_usd'] = \
        df.loc[df['assetSymbol'].isin(['WMATIC', 'WETH', 'DAI'])].apply(
            lambda row: row['amount_numeric'] / 1e18 * row['asset_price_usd'] if row['asset_price_usd'] > 0 else row['amount_numeric'] / 1e18, axis=1
        )
    df.loc[df['assetSymbol'] == 'WBTC', 'tx_value_usd'] = \
        df.loc[df['assetSymbol'] == 'WBTC'].apply(
            lambda row: row['amount_numeric'] / 1e8 * row['asset_price_usd'] if row['asset_price_usd'] > 0 else row['amount_numeric'] / 1e8, axis=1
        )
    print("Engineering features for each wallet...")
    wallet_features_list = []
    all_wallets = df['userWallet'].unique()

    for wallet in all_wallets:
        wallet_df = df[df['userWallet'] == wallet].copy()
        features = {
            'userWallet': wallet,
            'total_transactions': len(wallet_df),
            'unique_actions': wallet_df['action'].nunique(),
            'days_active': wallet_df['timestamp'].dt.date.nunique(),
            'first_tx_date': wallet_df['timestamp'].min(),
            'last_tx_date': wallet_df['timestamp'].max(),
            'total_deposited_usd': wallet_df[wallet_df['action'] == 'deposit']['tx_value_usd'].sum(),
            'total_borrowed_usd': wallet_df[wallet_df['action'] == 'borrow']['tx_value_usd'].sum(),
            'total_repaid_usd': wallet_df[wallet_df['action'] == 'repay']['tx_value_usd'].sum(),
            'total_redeemed_usd': wallet_df[wallet_df['action'] == 'redeemunderlying']['tx_value_usd'].sum(),
            'liquidation_count': wallet_df[wallet_df['action'] == 'liquidationcall'].shape[0],
        }

        features['activity_span_days'] = (features['last_tx_date'] - features['first_tx_date']).days
        if features['days_active'] > 0:
            features['avg_tx_per_day'] = features['total_transactions'] / features['days_active']
        else:
            features['avg_tx_per_day'] = 0

        features['net_borrowed_usd'] = features['total_borrowed_usd'] - features['total_repaid_usd']

        if features['total_deposited_usd'] > 0:
            features['borrow_to_deposit_ratio'] = features['total_borrowed_usd'] / features['total_deposited_usd']
        else:
            features['borrow_to_deposit_ratio'] = 0

        if features['total_borrowed_usd'] > 0:
            features['repay_to_borrow_ratio'] = features['total_repaid_usd'] / features['total_borrowed_usd']
        else:
            features['repay_to_borrow_ratio'] = 1.0 
        wallet_features_list.append(features)

    wallet_features_df = pd.DataFrame(wallet_features_list)
    min_max_values = {}
    for feature in FEATURE_WEIGHTS.keys():
        min_max_values[feature] = {
            'min': wallet_features_df[feature].min(),
            'max': wallet_features_df[feature].max()
        }
    if 'repay_to_borrow_ratio' in min_max_values:
        min_max_values['repay_to_borrow_ratio']['min'] = 0.0
        min_max_values['repay_to_borrow_ratio']['max'] = max(1.0, min_max_values['repay_to_borrow_ratio']['max'])
    if 'borrow_to_deposit_ratio' in min_max_values:
        min_max_values['borrow_to_deposit_ratio']['min'] = 0.0
    print("Calculating scores for each wallet...")
    scored_wallets = []
    for index, row in wallet_features_df.iterrows():
        score = calculate_score(row.to_dict(), min_max_values)
        scored_wallets.append({
            'userWallet': row['userWallet'],
            'credit_score': score
        })
    scored_wallets_sorted = sorted(scored_wallets, key=lambda x: x['credit_score'], reverse=True)
    print(f"Saving scores to {output_json_path}...")
    with open(output_json_path, 'w') as f:
        json.dump(scored_wallets_sorted, f, indent=4)
    print("Scoring complete.")
    print(f"Scores saved to {output_json_path}")

if __name__ == "__main__":
    INPUT_CSV_PATH = convert_csv_to_json(INPUT_JSON_PATH)
    generate_wallet_scores(INPUT_CSV_PATH, OUTPUT_JSON_FILE)