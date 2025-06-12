import pandas as pd
import requests
import time
import numpy as np

# Supabase credentials
SUPABASE_URL = "https://xaezrqaiswdplflbalxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZXpycWFpc3dkcGxmbGJhbHhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MTIwNjksImV4cCI6MjA2MjQ4ODA2OX0.JciLYAitkgL7jln9fTtipad7xR7TgcUJqKmCrzBopX0"

# File path
CSV_FILE_PATH = "sales_resources/Uk-Advisors-Csv-Default-view-export-1747116207819.csv"

# Function to upload data to Supabase
def upload_to_supabase(data):
    url = f"{SUPABASE_URL}/rest/v1/uk_advisors"
    
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

def clean_value(value):
    """Clean and standardize values"""
    if pd.isna(value) or value == "" or value is None:
        return None
    
    if isinstance(value, (int, float)):
        if np.isnan(value):
            return None
        return value
    
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    
    return value

def main():
    print(f"Reading data from CSV file: {CSV_FILE_PATH}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Exclude certain columns and rename for consistency 
        columns_to_keep = {
            'Company Name': 'company_name',
            'Total Advisers': 'total_advisers',
            'Website': 'website',
            'Employee Count': 'employee_count',
            'Size': 'size',
            'Industry': 'industry',
            'Description': 'description',
            'Domain': 'domain',
            'Type': 'type',
            'Founded': 'founded',
            'Revenue': 'revenue',
            'Site Traffic': 'site_traffic'
        }
        
        # Check if all required columns exist in the DataFrame
        missing_columns = [col for col in columns_to_keep.keys() if col not in df.columns]
        if missing_columns:
            print(f"Warning: The following columns are missing from the CSV: {missing_columns}")
            # Remove missing columns from our map
            for col in missing_columns:
                del columns_to_keep[col]
        
        # Prepare data for upload
        records = []
        for _, row in df.iterrows():
            record = {}
            
            for original_col, supabase_col in columns_to_keep.items():
                if original_col in df.columns:
                    record[supabase_col] = clean_value(row[original_col])
            
            # Skip records without a company name
            if 'company_name' in record and record['company_name'] is not None:
                records.append(record)
        
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