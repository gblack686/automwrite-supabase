import pandas as pd
import requests
import time

# Supabase credentials
SUPABASE_URL = "https://xaezrqaiswdplflbalxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZXpycWFpc3dkcGxmbGJhbHhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MTIwNjksImV4cCI6MjA2MjQ4ODA2OX0.JciLYAitkgL7jln9fTtipad7xR7TgcUJqKmCrzBopX0"

# File path
CSV_FILE_PATH = "lead qualification/EATT Delegate Lite List Post Event 20250307/all_unique_companies.csv"

# Function to upload data to Supabase
def upload_to_supabase(data):
    url = f"{SUPABASE_URL}/rest/v1/eatt_delegates"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Upload in batches to avoid request size limitations
    batch_size = 100
    total_records = len(data)
    batches = (total_records // batch_size) + (1 if total_records % batch_size > 0 else 0)
    
    for i in range(batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, total_records)
        batch = data[start_idx:end_idx]
        
        try:
            response = requests.post(url, headers=headers, json=batch)
            if response.status_code == 201:
                print(f"Batch {i+1}/{batches} uploaded successfully!")
            else:
                print(f"Error uploading batch {i+1}/{batches}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception uploading batch {i+1}/{batches}: {str(e)}")
        
        # Sleep briefly between batches to avoid rate limiting
        if i < batches - 1:
            time.sleep(0.5)

def main():
    print(f"Reading data from CSV file: {CSV_FILE_PATH}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Check if the file has the expected columns
        if 'Company' not in df.columns:
            print(f"Error: Expected 'Company' column not found in CSV. Found columns: {df.columns.tolist()}")
            return
        
        # Prepare data for upload
        records = []
        for _, row in df.iterrows():
            company_name = row['Company'].strip() if isinstance(row['Company'], str) else row['Company']
            
            # Skip empty company names
            if not company_name or pd.isna(company_name):
                continue
                
            records.append({
                "company_name": company_name
            })
        
        print(f"Processed {len(records)} companies from the CSV file")
        
        # Upload the data
        if records:
            upload_to_supabase(records)
            print(f"Upload complete!")
        else:
            print("No valid records found to upload")
            
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")

if __name__ == "__main__":
    main() 