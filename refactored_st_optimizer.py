import pandas as pd
from amz_ppc_optimizer import AmzSheetHandler  # Assuming necessary handler functions are imported

# Load data (replace 'data.csv' with your actual file)
def load_data(file_path):
    return pd.read_csv(file_path)

# Filter profitable search terms
def filter_profitable_search_terms(data_sheet, desired_acos):
    search_terms = data_sheet[data_sheet["Match Type"].isin(["Exact", "Phrase", "Broad"])]
    result = search_terms[(search_terms["ACOS"] < desired_acos) & (search_terms["ACOS"] > 0)]
    return result.sort_values(by=["ACOS"], ascending=False)

# Filter unprofitable search terms
def filter_unprofitable_search_terms(data_sheet, desired_acos):
    search_terms = data_sheet[data_sheet["Match Type"].isin(["Exact", "Phrase", "Broad"])]
    result = search_terms[(search_terms["ACOS"] > desired_acos)]
    return result.sort_values(by=["ACOS"], ascending=False)

# Add search terms to campaigns based on match type
def add_search_terms(datagram, search_terms, bid_factor, products_portfolio, match_type):
    for _, row in search_terms.iterrows():
        customer_st = AmzSheetHandler.get_customer_search_term(row)
        st_product = AmzSheetHandler.get_search_term_targeting_portfolio(row)
        st_bid = float(AmzSheetHandler.get_search_term_cpc(row))

        add_campaign_id = products_portfolio[st_product]["search_terms_campaign_id"]
        add_ad_group_id = products_portfolio[st_product]["search_terms_ad_group_id"]

        if not AmzSheetHandler.is_keyword_exists(datagram, customer_st, match_type):
            datagram = AmzSheetHandler.add_keyword(datagram, add_campaign_id, add_ad_group_id,
                                                   customer_st, st_bid * bid_factor, match_type)
    return datagram

# Parameterized function to add all match types
def add_all_match_types(datagram, search_terms, bid_factor, products_portfolio):
    for match_type in ["Exact", "Phrase", "Broad"]:
        datagram = add_search_terms(datagram, search_terms, bid_factor, products_portfolio, match_type)
    return datagram

# Main function to orchestrate optimization
def optimize_search_terms(file_path, desired_acos, bid_factor, products_portfolio):
    data_sheet = load_data(file_path)

    # Filtering search terms
    profitable_terms = filter_profitable_search_terms(data_sheet, desired_acos)
    unprofitable_terms = filter_unprofitable_search_terms(data_sheet, desired_acos)

    # Create an empty datagram or load existing campaign data
    datagram = pd.DataFrame()  # Initialize or load existing data

    # Add profitable search terms to campaigns
    datagram = add_all_match_types(datagram, profitable_terms, bid_factor, products_portfolio)

    return datagram  # Return or save the updated datagram

# Example usage
if __name__ == "__main__":
    file_path = "search_terms.csv"
    desired_acos = 20.0  # Example ACOS threshold
    bid_factor = 1.1  # Example bid increase factor
    products_portfolio = {
        "Product1": {
            "search_terms_campaign_id": 101,
            "search_terms_ad_group_id": 201
        }
    }

    optimized_data = optimize_search_terms(file_path, desired_acos, bid_factor, products_portfolio)
    print(optimized_data.head())
