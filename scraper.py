import os
from dotenv import load_dotenv
from apify_client import ApifyClient
import pandas as pd

# 1. Load environment variables from .env file
load_dotenv()

# 2. Retrieve API token from .env or fallback
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "YOUR_APIFY_API_TOKEN")

if not APIFY_TOKEN or APIFY_TOKEN == "YOUR_APIFY_API_TOKEN":
    raise ValueError("Missing valid APIFY_API_TOKEN. Please set it in your .env file or script.")

client = ApifyClient(APIFY_TOKEN)

# 3. Configure search target parameters
run_input = {
    "startUrls": [
        {"url": "https://wellfound.com/role/r/technical-recruiter"}
    ],
    "max_items": 50,
}

print("Triggering Apify Wellfound scraper actor...")

try:
    # 4. Call the Apify actor
    actor_call = client.actor("radeance/wellfound-job-listings-scraper").call(run_input=run_input)

    print("Processing dataset results...")
    
    # 5. Safely extract dataset ID across apify-client versions
    dataset_id = actor_call.default_dataset_id if hasattr(actor_call, "default_dataset_id") else actor_call["defaultDatasetId"]
    
    dataset_items = client.dataset(dataset_id).iterate_items()
    df = pd.DataFrame(list(dataset_items))

    # 6. Save data to CSV
    if not df.empty:
        output_file = "wellfound_jobs.csv"
        df.to_csv(output_file, index=False)
        print(f"Success! Extracted {len(df)} jobs and saved to {output_file}.")
    else:
        print("The scraper ran, but returned 0 items. Check your target URL filters.")

except Exception as e:
    print(f"An error occurred during execution: {e}")