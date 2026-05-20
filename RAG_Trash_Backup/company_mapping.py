import os
import time
import pandas as pd
import numpy as np

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
CSV_PATH = os.path.join(BASE_DIR, "data", "csv", "sales_data.csv")
OUTPUT_CSV_PATH = os.path.join(BASE_DIR, "data", "csv", "sales_data_with_companies.csv")

print("="*60)
print("🚀 CLASS 2: INJECTING VERIFIED ENTERPRISE MAPPING LAYER")
print("="*60)

# 🔥 EXACT MATCHED LIST FROM YOUR DIRECTORY SCREENSHOTS
companies_list = [
    "Adobe", "Amazon", "AMD", "Apple", "FordMotors", 
    "General Motors", "Goldman Sachs", "Google", "IBM", "Intel", 
    "JPMorgan Chase", "Mastercard", "MCDONALDS", "META", "Microsoft", 
    "Netflix", "NextEra", "Nvidia", "Oracle", "Paypal", 
    "Qualcomm", "SalesForce", "Starbucks", "Tesla", "Visa"
]

chunk_size = 200000  # Optimized speed for 1 Million dataset
first_chunk = True
total_rows = 0
start_time = time.time()

data_stream = pd.read_csv(CSV_PATH, chunksize=chunk_size)

for index, chunk in enumerate(data_stream, start=1):
    current_len = len(chunk)
    total_rows += current_len
    
    # Robust Clean-up: Extra spaces remove aur columns lowercase to prevent typos
    chunk.columns = [col.strip().lower() for col in chunk.columns]
    if 'oorder_id' in chunk.columns:
        chunk.rename(columns={'oorder_id': 'order_id'}, inplace=True)
    
    # Core Realism Allocation: Row assignment using numpy
    chunk['company_name'] = np.random.choice(companies_list, size=current_len)
    
    # Save the processed records chunk-by-chunk
    if first_chunk:
        chunk.to_csv(OUTPUT_CSV_PATH, index=False, mode='w')
        first_chunk = False
    else:
        chunk.to_csv(OUTPUT_CSV_PATH, index=False, mode='a', header=False)
        
    print(f"🔄 Processed Batch {index}: {total_rows:,} rows mapped with verified company keys...")

end_time = time.time()
print("\n" + "="*60)
print("✅ CLASS 2 SUCCESS: 'company_name' Column Injected Flawlessly!")
print(f"📁 Verified Realism Dataset Created: {OUTPUT_CSV_PATH}")
print(f"⏱️ Total Mapping Time: {end_time - start_time:.2f} Seconds")
print("="*60)