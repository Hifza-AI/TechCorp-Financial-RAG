import os
import time
import pandas as pd

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
INPUT_CSV = os.path.join(BASE_DIR, "data", "csv", "sales_data_with_companies.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "csv", "sales_data_final_realism.csv")

print("="*60)
print("🚀 CLASS 3: INJECTING REAL ENTERPRISE REALISM LAYER (100% MATCHED)")
print("="*60)

if not os.path.exists(INPUT_CSV):
    print(f"❌ Error: Class 2 wali file nahi mili dost! Pehle Class 2 run karo.")
    exit()

# Business Realism Rules Dictionary - Exact 25 Companies from your Folders
realism_rules = {
    # Tech & AI Hardware
    "Apple": {"category": "Electronics", "sub_category": "Smartphones & Tablets", "brand": "Apple iPhone"},
    "Nvidia": {"category": "Computing", "sub_category": "AI Hardware & GPUs", "brand": "Nvidia RTX/H100"},
    "AMD": {"category": "Computing", "sub_category": "Processors & Graphics", "brand": "AMD Ryzen"},
    "Intel": {"category": "Computing", "sub_category": "Semiconductors", "brand": "Intel Core i9"},
    "Qualcomm": {"category": "Electronics", "sub_category": "Mobile Chips", "brand": "Snapdragon"},
    "IBM": {"category": "Computing", "sub_category": "Enterprise Systems", "brand": "IBM ThinkSystem"},
    
    # Software & Cloud
    "Microsoft": {"category": "Cloud Services", "sub_category": "Cloud Infrastructure", "brand": "Microsoft Azure"},
    "Adobe": {"category": "Software", "sub_category": "Creative Tools", "brand": "Adobe Creative Cloud"},
    "Oracle": {"category": "Software", "sub_category": "Database Software", "brand": "Oracle Autonomous DB"},
    "SalesForce": {"category": "Software", "sub_category": "Enterprise CRM", "brand": "SalesForce Cloud"},
    "Google": {"category": "Digital Services", "sub_category": "Search & Cloud Ads", "brand": "Google AdSense"},
    "META": {"category": "Digital Services", "sub_category": "Social Media Ads", "brand": "Meta Business Suite"},
    
    # Retail & Entertainment
    "Amazon": {"category": "Retail", "sub_category": "E-Commerce Goods", "brand": "AmazonBasics"},
    "Netflix": {"category": "Entertainment", "sub_category": "Digital Subscriptions", "brand": "Netflix Premium"},
    
    # Automotive
    "Tesla": {"category": "Automotive", "sub_category": "Electric Vehicles", "brand": "Tesla Model Y"},
    "FordMotors": {"category": "Automotive", "sub_category": "Commercial Vehicles", "brand": "Ford Mustang Mach-E"},
    "General Motors": {"category": "Automotive", "sub_category": "Passenger Cars", "brand": "Chevrolet EV"},
    
    # Finance, Banking & Payments
    "JPMorgan Chase": {"category": "Financial Services", "sub_category": "Investment Banking", "brand": "Chase Wealth Mgmt"},
    "Goldman Sachs": {"category": "Financial Services", "sub_category": "Asset Management", "brand": "Marcus by Goldman"},
    "Visa": {"category": "Payments", "sub_category": "Credit Networks", "brand": "Visa Network"},
    "Mastercard": {"category": "Payments", "sub_category": "Transaction Networks", "brand": "Mastercard Core"},
    "Paypal": {"category": "Payments", "sub_category": "Digital Wallets", "brand": "PayPal Express"},
    
    # Food & Energy/Utilities
    "MCDONALDS": {"category": "Food & Beverages", "sub_category": "Fast Food Sales", "brand": "McDonalds Big Mac"},
    "Starbucks": {"category": "Food & Beverages", "sub_category": "Coffee & Retail", "brand": "Starbucks Espresso"},
    "NextEra": {"category": "Energy", "sub_category": "Clean Utilities", "brand": "NextEra Wind Power"}
}

chunk_size = 200000
first_chunk = True
total_rows = 0
start_time = time.time()

data_stream = pd.read_csv(INPUT_CSV, chunksize=chunk_size)

for index, chunk in enumerate(data_stream, start=1):
    current_len = len(chunk)
    total_rows += current_len
    
    # Loop through our 25 verified rules and overwrite rows
    for company, mapping in realism_rules.items():
        mask = chunk['company_name'] == company
        chunk.loc[mask, 'category'] = mapping['category']
        chunk.loc[mask, 'sub_category'] = mapping['sub_category']
        chunk.loc[mask, 'brand'] = mapping['brand']
        
    # Save processed chunk
    if first_chunk:
        chunk.to_csv(OUTPUT_CSV, index=False, mode='w')
        first_chunk = False
    else:
        chunk.to_csv(OUTPUT_CSV, index=False, mode='a', header=False)
        
    print(f"🛠️ Realism Applied to Batch {index}: Adjusted rules for {total_rows:,} rows...")

end_time = time.time()
print("\n" + "="*60)
print("✅ CLASS 3 SUCCESS: Synthetic Anomalies Fixed Permanently!")
print(f"📁 Final Production-Ready CSV: {OUTPUT_CSV}")
print(f"⏱️ Alignment Duration: {end_time - start_time:.2f} Seconds")
print("="*60)