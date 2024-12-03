import pandas as pd

# Configuration parameters
config = {
    "desired_acos": 0.4,
    "increase_by": 1.2,
    "decrease_by": 0.9,
    "min_bid": 0.2,
    "max_bid": 4.0,
    "high_acos_thr": 0.3,
    "mid_acos_thr": 0.25,
    "click_thr": 11,
    "impression_thr": 1000,
    "step_up": 0.04,
    "no_data_bid": 0.31,
    "low_impression_max_value": 0.35
}

# Core optimization functions
def optimize_bid(row, suggested_bid, config):
    if row['Orders'] == 0 and row['Clicks'] >= config['click_thr']:
        row['Bid'] = max(config['min_bid'], row['Bid'] * config['decrease_by'])
    elif row['Orders'] == 0 and row['Impressions'] <= config['impression_thr']:
        row['Bid'] = min(config['low_impression_max_value'], row['Bid'] + config['step_up'])
    elif row['ACOS'] > config['high_acos_thr']:
        row['Bid'] = max(config['min_bid'], min(config['desired_acos'] / row['ACOS'] * row['CPC'], suggested_bid))
    elif row['ACOS'] < config['mid_acos_thr']:
        row['Bid'] = min(config['max_bid'], min(row['CPC'] * config['increase_by'], suggested_bid))
    return row

# Load and process the data
def process_campaign_data(data_sheet, target_sheet, config):
    for index, row in data_sheet.iterrows():
        suggested_bid = get_suggested_bid(row, target_sheet, config['no_data_bid'])
        data_sheet.loc[index] = optimize_bid(row, suggested_bid, config)
    return data_sheet

# Placeholder for suggested bid logic
def get_suggested_bid(row, target_sheet, no_data_bid):
    # Simplified lookup or default value if no data
    return no_data_bid  # Replace with actual lookup logic

# Example usage with a sample data frame
if __name__ == "__main__":
    # Load data from CSV or any source
    data = pd.read_csv('campaign_data.csv')
    targets = pd.read_csv('targets_data.csv')
    
    optimized_data = process_campaign_data(data, targets, config)
    optimized_data.to_csv('optimized_campaign_data.csv', index=False)
