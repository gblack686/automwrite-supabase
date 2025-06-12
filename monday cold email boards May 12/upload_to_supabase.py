import os
import pandas as pd
import json
import requests

# Supabase credentials
SUPABASE_URL = "https://xaezrqaiswdplflbalxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZXpycWFpc3dkcGxmbGJhbHhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MTIwNjksImV4cCI6MjA2MjQ4ODA2OX0.JciLYAitkgL7jln9fTtipad7xR7TgcUJqKmCrzBopX0"

# CSV data file path
CSV_FILE = "monday_raw_data.csv"

# Function to upload data to Supabase
def upload_to_supabase(data):
    url = f"{SUPABASE_URL}/rest/v1/monday_contacts"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Upload in batches to avoid request size limitations
    BATCH_SIZE = 100
    batches = [data[i:i + BATCH_SIZE] for i in range(0, len(data), BATCH_SIZE)]
    
    print(f"Uploading {len(data)} records in {len(batches)} batches...")
    
    for i, batch in enumerate(batches):
        try:
            response = requests.post(url, headers=headers, json=batch)
            if response.status_code == 201:
                print(f"Batch {i+1}/{len(batches)} uploaded successfully")
            else:
                print(f"Error uploading batch {i+1}: {response.status_code} - {response.text}")
                
                if i == 0:  # Debug first batch failure
                    print(f"First record in batch: {batch[0]}")
                    print(f"Keys: {list(batch[0].keys())}")
        except Exception as e:
            print(f"Exception uploading batch {i+1}: {str(e)}")
    
    print("Upload complete!")

# Main function
def main():
    print(f"Loading data from {CSV_FILE}...")
    try:
        # Read the CSV file
        df = pd.read_csv(CSV_FILE)
        print(f"Loaded {len(df)} records from CSV")
        
        # Define all fields in our schema to ensure consistent keys
        required_fields = [
            "source_file", "contact_group", "name", "email", "phone_number", 
            "website", "company_name", "status", "first_name", "last_name",
            "address", "location", "linkedin", "notes", "extra_data"
        ]
        
        # Processing data for upload
        records = []
        
        for _, row in df.iterrows():
            # Start with a basic record with all required keys
            record = {field: None for field in required_fields}
            
            # Set the known fields
            record["source_file"] = row["Source_File"]
            record["contact_group"] = row["Group"]
            
            # Try to map common columns based on position and content
            column_mapping = {
                # Common field positions based on analysis 
                "0": "name",
                "1": "first_name",  # Often first name is in column 1
                "2": "email",
                "3": "phone_number",
                "4": "website",
                "5": "company_name",
                "6": "last_name",   # Sometimes last name is in column 6
                "9": "status",
                "16": "location"
            }
            
            # Add mapped fields when they exist
            for col_num, field_name in column_mapping.items():
                if col_num in df.columns and pd.notna(row[col_num]) and row[col_num] != '':
                    record[field_name] = str(row[col_num])
            
            # Store remaining data as JSON
            extra_data = {}
            for col in df.columns:
                # Skip source and group columns
                if col not in ["Source_File", "Group"]:
                    col_key = str(col)
                    mapped_key = column_mapping.get(col_key)
                    
                    # If this column wasn't mapped to a standard field and has data
                    if not mapped_key and pd.notna(row[col]) and row[col] != '':
                        extra_data[col_key] = str(row[col])
            
            record["extra_data"] = json.dumps(extra_data) if extra_data else None
            records.append(record)
        
        print(f"Processed {len(records)} records for upload")
        
        # Upload the processed records
        upload_to_supabase(records)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 