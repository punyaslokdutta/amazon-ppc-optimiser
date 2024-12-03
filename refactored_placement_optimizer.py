import pandas as pd

# Load data from CSV
def load_data(file_path):
    return pd.read_csv(file_path)

# Filter campaigns
def get_campaigns(data_sheet):
    return data_sheet[data_sheet["Entity"] == "Campaign"]

# Check if a campaign is enabled
def is_campaign_enabled(campaign):
    return campaign["Campaign State (Informational only)"] == "enabled"

# Filter campaigns based on orders
def filter_campaigns_by_orders(data_sheet, threshold=0):
    campaigns = get_campaigns(data_sheet)
    result = campaigns[campaigns["Orders"] > threshold]
    return result.sort_values(by=['Orders'], ascending=False)

# Filter campaigns based on ROAS
def filter_campaigns_by_roas(data_sheet, threshold=0):
    campaigns = get_campaigns(data_sheet)
    result = campaigns[campaigns["ROAS"] > threshold]
    return result.sort_values(by=['ROAS'], ascending=False)

# Filter campaigns based on name
def filter_campaigns_by_name(data_sheet, phrase):
    campaigns = get_campaigns(data_sheet)
    return campaigns[campaigns["Campaign Name"].str.contains(phrase, na=False)]

# Filter campaigns based on ACOS
def filter_campaigns_by_acos(data_sheet, threshold=0):
    campaigns = get_campaigns(data_sheet)
    result = campaigns[(campaigns["ACOS"] < threshold) & (campaigns["ACOS"] > 0)]
    return result.sort_values(by=['ACOS'], ascending=False)

# Adjust campaign bidding strategy
def adjust_campaigns(data_sheet, campaigns, strategy, adjust_first_page_factor=0, adjust_product_page_factor=0):
    bidding_strategies = {
        "dynamic": "Dynamic bids - up and down",
        "dynamic_down": "Dynamic bids - down only",
        "fixed": "Fixed bid"
    }

    # Set adjustment to 0 for fixed strategy
    if strategy == "fixed":
        adjust_first_page_factor = 0
        adjust_product_page_factor = 0

    # Adjust each row
    for index, row in data_sheet.iterrows():
        if is_campaign_enabled(row) and row["Entity"] == "Campaign":
            if row["Campaign Name (Informational only)"] in campaigns:
                row["Bidding Strategy"] = bidding_strategies[strategy]
                row["Operation"] = "update"
        
        if row["Entity"] == "Bidding Adjustment" and row["Campaign Name (Informational only)"] in campaigns:
            if row["Placement"] == "Placement Top":
                row["Percentage"] = adjust_first_page_factor
                row["Operation"] = "update"
            elif row["Placement"] == "Placement Product Page":
                row["Percentage"] = adjust_product_page_factor
                row["Operation"] = "update"

    return data_sheet

# Main function to run optimization
def run_placement_optimization(file_path, strategy, threshold_acos, adjust_first_page_factor, adjust_product_page_factor):
    data_sheet = load_data(file_path)

    # Filter campaigns based on ACOS
    filtered_campaigns = filter_campaigns_by_acos(data_sheet, threshold_acos)
    campaign_names = filtered_campaigns["Campaign Name (Informational only)"].unique()

    # Adjust campaigns based on strategy
    updated_data = adjust_campaigns(data_sheet, campaign_names, strategy, adjust_first_page_factor, adjust_product_page_factor)

    return updated_data

# Example usage
if __name__ == "__main__":
    file_path = "campaign_data.csv"
    strategy = "dynamic"
    threshold_acos = 0.3  # Example ACOS threshold
    adjust_first_page_factor = 20  # Example adjustment percentage
    adjust_product_page_factor = 15

    optimized_data = run_placement_optimization(file_path, strategy, threshold_acos, adjust_first_page_factor, adjust_product_page_factor)
    print(optimized_data.head())
