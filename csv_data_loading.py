import os
import time
import pandas as pd

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
CSV_PATH = os.path.join(BASE_DIR, "data", "csv", "sales_data.csv")

print("="*60)
print("🚀 CLASS 1: STREAM-LOADING 1 MILLION ROWS DATASET (TYPO FIXED)")
print("="*60)

if not os.path.exists(CSV_PATH):
    print(f"❌ Error: File is path par nahi mili dost -> {CSV_PATH}")
    exit()

chunk_size = 100000
total_rows = 0
start_time = time.time()

data_stream = pd.read_csv(CSV_PATH, chunksize=chunk_size)

for index, chunk in enumerate(data_stream, start=1):
    current_chunk_len = len(chunk)
    total_rows += current_chunk_len
    
    # 1. Clean spaces and lower-case standard columns
    chunk.columns = [col.strip().lower() for col in chunk.columns]
    
    # 2. 🔥 AUTOMATED TYPO FIX: Agar pehle column mein 'oorder_id' ho, toh use 'order_id' kar do
    if 'oorder_id' in chunk.columns:
        chunk.rename(columns={'oorder_id': 'order_id'}, inplace=True)
    
    # Calculate memory consumption
    memory_mb = chunk.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"📦 Batch {index}: Loaded {current_chunk_len:,} rows | RAM Used: {memory_mb:.2f} MB")
    
    if index == 1:
        print(f"   🔹 Dataset Columns Count: {len(chunk.columns)}")
        print(f"   🔹 Sample Order ID Verified: {chunk['order_id'].iloc[0]}")
    print("-" * 40)

end_time = time.time()
print("\n" + "="*60)
print("✅ CLASS 1 SUCCESS: All rows verified smoothly")
print(f"⚡ Total Rows Processed: {total_rows:,}")
print(f"⏱️ Time Taken: {end_time - start_time:.2f} Seconds")
print("="*60)