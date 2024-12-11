import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# File path
file_path = "IN_AMAZON_blackBoxProducts_1_2024-12-11_pet.csv"
data = pd.read_csv(file_path)

# Columns to normalize
columns_to_normalize = [
    "BSR",
    "Price Trend (90 days) (%)",
    "Monthly Sales",
    "Sales Trend (90 days) (%)",
    "Monthly Revenue",
    "Last Year Sales",
    "Sales Year Over Year (%)",
    "Age (Month)",
    "Number of Images",
]

# Convert columns to numeric and handle invalid values
for column in columns_to_normalize:
    data[column] = pd.to_numeric(data[column], errors='coerce')
data = data.dropna(subset=columns_to_normalize)

# Normalize columns
scaler = MinMaxScaler()
data[columns_to_normalize] = scaler.fit_transform(data[columns_to_normalize])

# Weights for MCDM score
weights = {
    "Monthly Revenue": 0.3,
    "Monthly Sales": 0.25,
    "Sales Trend (90 days) (%)": 0.2,
    "Price Trend (90 days) (%)": 0.05,
    "BSR": 0.1,
    "Last Year Sales": 0.05,
    "Sales Year Over Year (%)": 0.05,
    "Age (Month)": 0.05,
    "Number of Images": 0.05,
}

# Calculate MCDM Score
data["MCDM Score"] = sum(data[col] * weight for col, weight in weights.items())

# Sort and rank data
data = data.sort_values(by="MCDM Score", ascending=False)
data["Rank"] = range(1, len(data) + 1)

# Cumulative score and Pareto analysis
data["Cumulative Score"] = data["MCDM Score"].cumsum()
data["Cumulative Percentage"] = data["Cumulative Score"] / data["MCDM Score"].sum()

# Pareto threshold
pareto_threshold = 0.8
pareto_data = data[data["Cumulative Percentage"] <= pareto_threshold]

# Save output
# pareto_data[["ASIN", 'Title', "MCDM Score", "Rank", "Cumulative Percentage"]].to_csv(
#     "pareto_mcdm_results_BabyData_11_12_2024.csv", index=False
# )

pareto_data.to_csv(
    "pareto_mcdm_results_FullData_BabyData_11_12_2024_petSupplies.csv", index=False
)

print("Top Products Based on Pareto and MCDM:")
print(pareto_data[["ASIN", 'Title', "MCDM Score", "Rank", "Cumulative Percentage"]])
