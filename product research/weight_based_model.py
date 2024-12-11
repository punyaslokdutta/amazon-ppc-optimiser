import csv
import requests
import time
from datetime import datetime

# Product class definition
class Product:
    def __init__(self, name, solving_need, recurring, price_range, competition, profit_margin, packaging_size, seasonal, customer_pricing, cross_selling, reviews, fragile, inventory_time, search_volume, sales_estimate, revenue_potential, bsr, trend, url=None):
        self.name = name
        self.solving_need = solving_need
        self.recurring = recurring
        self.price_range = price_range
        self.competition = competition
        self.profit_margin = profit_margin
        self.packaging_size = packaging_size
        self.seasonal = seasonal
        self.customer_pricing = customer_pricing
        self.cross_selling = cross_selling
        self.reviews = reviews
        self.fragile = fragile
        self.inventory_time = inventory_time
        self.search_volume = search_volume
        self.sales_estimate = sales_estimate
        self.revenue_potential = revenue_potential
        self.bsr = bsr
        self.trend = trend
        self.url = url

# Function to fetch Helium 10 data
def fetch_helium_10_data(product_name):
    api_url = 'https://api.helium10.com/v1/product'
    params = {'product_name': product_name, 'api_key': 'YOUR_API_KEY'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()  # Parse the JSON response to extract data
    return None

# Function to calculate score based on various product parameters
def calculate_score(product):
    weights = {
        'solving_need': 10,
        'recurring': 6,
        'price_range': {'<=300': 6, '>700': 10},
        'competition': 9,
        'profit_margin': 10,
        'packaging_size': 8,
        'seasonal': 8,
        'customer_pricing': 10,
        'cross_selling': 6,
        'reviews': {'<100': 5, '100-300': 10},
        'fragile': 8,
        'inventory_time': 9,
        'search_volume': 10,
        'sales_estimate': 10,
        'revenue_potential': 10,
        'BSR': 8,
        'trend': 7
    }

    score = 0
    score += weights['solving_need'] if product.solving_need else 0
    score += weights['recurring'] if product.recurring else 0
    score += weights['price_range'][product.price_range] if product.price_range in weights['price_range'] else 0
    score += weights['competition'] if product.competition == 'Low' else 0
    score += weights['profit_margin'] if product.profit_margin >= 300 else 5
    score += weights['packaging_size'] if product.packaging_size == 'Small' else 0
    score += weights['seasonal'] if not product.seasonal else 0
    score += weights['customer_pricing'] if product.customer_pricing == 'Flexible' else 0
    score += weights['cross_selling'] if product.cross_selling else 0
    score += weights['reviews'][calculate_reviews_range(product.reviews)] if calculate_reviews_range(product.reviews) in weights['reviews'] else 0
    score += weights['fragile'] if not product.fragile else 0
    score += weights['inventory_time'] if product.inventory_time == 'Less' else 0

    # Adding Helium 10 data
    score += weights['search_volume'] if product.search_volume > 1000 else 5
    score += weights['sales_estimate'] if product.sales_estimate > 1000 else 0
    score += weights['revenue_potential'] if product.revenue_potential > 10000 else 0
    score += weights['BSR'] if product.bsr < 10000 else 0
    score += weights['trend'] if product.trend == 'Rising' else 0

    return score

def calculate_reviews_range(reviews):
    if reviews < 100:
        return '<100'
    elif 100 <= reviews <= 300:
        return '100-300'
    else:
        return '>300'

# Function to rank products
def rank_products(products):
    ranked_products = sorted(products, key=lambda x: calculate_score(x), reverse=True)
    return ranked_products

# Function to read products from CSV and enrich with Helium 10 data
def read_products_from_csv(file_path):
    products = []

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            helium_data = fetch_helium_10_data(row['Title'])
            if helium_data:
                product = Product(
                    name=row['Title'],
                    solving_need=row['Solving need'] == 'True',
                    recurring=row['Recurring'] == 'True',
                    price_range=row['price_range'],
                    competition=row['Competition'],
                    profit_margin=float(row['profit_margin']),
                    packaging_size=row['packaging_size'],
                    seasonal=row['Seasonal'] == 'False',
                    customer_pricing=row['customer_pricing'],
                    cross_selling=row['Cross Selling'] == 'True',
                    reviews=float(row['Reviews']),
                    fragile=row['Fragile'] == 'False',
                    inventory_time=row['Inventory time'],
                    search_volume=helium_data['search_volume'],
                    sales_estimate=helium_data['sales_estimate'],
                    revenue_potential=helium_data['revenue_potential'],
                    bsr=helium_data['bsr'],
                    trend=helium_data['trend'],
                    url=row.get('URL', None)
                )
                products.append(product)

    return products

# Function to write the ranked products to a new CSV
def write_ranked_products_to_csv(ranked_products, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Score', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in ranked_products:
            writer.writerow({'Name': product.name, 'Score': calculate_score(product), 'URL': product.url})

# Main function to run the process
def run_product_analysis(file_path, output_file):
    products = read_products_from_csv(file_path)
    ranked_products = rank_products(products)[:20]
    write_ranked_products_to_csv(ranked_products, output_file)

# Schedule to run weekly
if __name__ == "__main__":
    file_path = 'prod_blackbox_8AUG.csv'  # Input file
    output_file = 'top_20_products_baby8AUG.csv'  # Output file

    while True:
        print(f"Running product analysis at {datetime.now()}")
        run_product_analysis(file_path, output_file)
        print(f"Analysis complete. Top products saved to {output_file}")
        time.sleep(7 * 24 * 60 * 60)  # Sleep for 1 week (7 days)
