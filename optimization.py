import os
import time
import pandas as pd

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
INPUT_CSV = os.path.join(BASE_DIR, "data", "csv", "sales_data_final_realism.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "csv", "sales_data_cleaned_optimized.csv")

print("="*60)
print("🚀 CLASS 4: REMOVE NOISE, HANDLE NULLS & DATATYPE OPTIMIZATION")
print("="*60)

if not os.path.exists(INPUT_CSV):
    print(f"❌ Error: Class 3 wali file nahi mili dost! Pehle Class 3 run karo.")
    exit()

chunk_size = 200000
first_chunk = True
total_rows = 0
start_time = time.time()

data_stream = pd.read_csv(INPUT_CSV, chunksize=chunk_size)

for index, chunk in enumerate(data_stream, start=1):
    # 1. Clean Noisy/Null Rows: Agar critical financial columns mein kuch khali hai toh remove karo
    # Check if critical columns have nulls and drop them
    chunk = chunk.dropna(subset=['order_id', 'total_price_usd', 'company_name'])
    
    current_len = len(chunk)
    total_rows += current_len
    
    # 2. Datatype Optimization (Memory Downcasting)
    # Categorical Columns (Jo values baar baar repeat hoti hain unhein category banao)
    cat_cols = ['order_status', 'gender', 'customer_segment', 'country', 'currency', 
                'payment_method', 'payment_status', 'shipping_method', 'delivery_status', 
                'company_name', 'category', 'sub_category']
    
    for col in cat_cols:
        if col in chunk.columns:
            chunk[col] = chunk[col].astype('category')
            
    # Float Columns Downcasting (64-bit float takes too much RAM, shift to 32-bit)
    float_cols = chunk.select_dtypes(include=['float64']).columns
    for col in float_cols:
        chunk[col] = chunk[col].astype('float32')
        
    # Integer Columns Downcasting
    int_cols = chunk.select_dtypes(include=['int64']).columns
    for col in int_cols:
        chunk[col] = chunk[col].astype('int32')

    # Calculate current memory optimization score
    memory_mb = chunk.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # Save optimized chunk
    if first_chunk:
        chunk.to_csv(OUTPUT_CSV, index=False, mode='w')
        first_chunk = False
    else:
        chunk.to_csv(OUTPUT_CSV, index=False, mode='a', header=False)
        
    print(f"⚡ Batch {index}: Optimized {current_len:,} rows | Working Chunk RAM: {memory_mb:.2f} MB")

end_time = time.time()
print("\n" + "="*60)
print("✅ CLASS 4 SUCCESS: Phase 1 Data Cleaning & Optimization Complete!")
print(f"📁 Master Cleaned Dataset Saved: {OUTPUT_CSV}")
print(f"⏱️ Optimization Duration: {end_time - start_time:.2f} Seconds")
print("="*60)