from sec_edgar_downloader import Downloader
import time

# Apna asli email aur project name likho
dl = Downloader("TechCorp-FYP", "hifza.riaz@example.com", "data/raw_pdfs")

# Jo companies reh gayi hain sirf unhe check karte hain
# Humne JPM ko nikal diya hai filhal error ki wajah se
remaining_tickers = ["GS", "V", "MA", "DIS", "PYPL"]

print("Starting Remaining Downloads... 🚀")

for ticker in remaining_tickers:
    try:
        print(f"Downloading 10-K for {ticker}...")
        dl.get("10-K", ticker, after="2004-01-01")
        print(f"✅ Finished {ticker}. Taking a short break...")
        time.sleep(5) # 5 second ka sakoon taake connection na toote
    except Exception as e:
        print(f"Could not download {ticker}: {e}")

print("\n🎉 All possible downloads are finished!")