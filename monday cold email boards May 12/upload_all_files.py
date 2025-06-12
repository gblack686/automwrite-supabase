import os
import pandas as pd
import json
import requests
import time

# Supabase credentials
SUPABASE_URL = "https://xaezrqaiswdplflbalxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZXpycWFpc3dkcGxmbGJhbHhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MTIwNjksImV4cCI6MjA2MjQ4ODA2OX0.JciLYAitkgL7jln9fTtipad7xR7TgcUJqKmCrzBopX0"

# Folder with Excel files
EXCEL_FOLDER = "monday cold email boards May 12"

# Define all required fields that must be present in all records
REQUIRED_FIELDS = [
    "source_file", "contact_group", "name", "email", "phone_number", 
    "website", "company_name", "status", "first_name", "last_name",
    "address", "location", "linkedin", "notes", "extra_data"
]

def upload_to_supabase(data):
    if not data:
        print("No data to upload")
        return
        
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
            
            # Sleep briefly to avoid rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Exception uploading batch {i+1}: {str(e)}")
    
    print("Upload complete!")

def process_file(file_path):
    print(f"\nProcessing file: {file_path}")
    
    try:
        # Read the Excel file
        raw_df = pd.read_excel(file_path, header=None)
        
        # Find the header row
        header_row = None
        for i in range(len(raw_df)):
            if raw_df.iloc[i, 0] == "Name":
                header_row = i
                break
        
        if header_row is None:
            print("Could not find header row with 'Name' column")
            return []
        
        # Extract the group name from the previous rows
        group_name = "Unknown"
        for i in range(header_row):
            if pd.notna(raw_df.iloc[i, 0]) and "Cold Email Out Reach" not in str(raw_df.iloc[i, 0]):
                group_name = raw_df.iloc[i, 0]
                break
        
        # Read the Excel file with proper header
        df = pd.read_excel(file_path, header=header_row)
        
        # Clean up the column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Records to upload
        records = []
        
        # Process each row
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('Name')):
                continue
                
            # Create a record with ALL required fields (initialize with None)
            record = {field: None for field in REQUIRED_FIELDS}
            
            # Set the known fields
            record["source_file"] = os.path.basename(file_path)
            record["contact_group"] = group_name
            
            # Map the standard fields
            field_mapping = {
                'Name': 'name',
                'First Name': 'first_name',
                'Last Name': 'last_name', 
                'Email': 'email',
                'Phone Number': 'phone_number',
                'Website': 'website',
                'Company Name': 'company_name',
                'Status': 'status',
                'Location': 'location',
                'LinkedIn': 'linkedin',
                'Physical Address': 'address'
            }
            
            # Add mapped fields when available
            for src_col, dest_col in field_mapping.items():
                if src_col in df.columns and pd.notna(row.get(src_col)):
                    record[dest_col] = str(row.get(src_col)).strip()
            
            # Store any additional fields as JSON
            extra_data = {}
            for col in df.columns:
                if col not in field_mapping.keys() and col not in ['Person', 'Phone #2']:
                    if pd.notna(row.get(col)):
                        extra_data[col] = str(row.get(col)).strip()
            
            # Add Phone #2 as separate field if available
            if 'Phone #2' in df.columns and pd.notna(row.get('Phone #2')):
                record['notes'] = f"Second phone: {row.get('Phone #2')}"
                
            record["extra_data"] = json.dumps(extra_data) if extra_data else None
            records.append(record)
        
        print(f"Extracted {len(records)} records from {os.path.basename(file_path)}")
        return records
            
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return []

def main():
    print(f"Processing Excel files from folder: {EXCEL_FOLDER}")
    
    all_records = []
    file_count = 0
    
    # Process each Excel file in the folder
    for filename in os.listdir(EXCEL_FOLDER):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(EXCEL_FOLDER, filename)
            records = process_file(file_path)
            all_records.extend(records)
            file_count += 1
    
    print(f"\nProcessed {file_count} files, found {len(all_records)} total records")
    
    if all_records:
        upload_to_supabase(all_records)
    else:
        print("No records to upload")

if __name__ == "__main__":
    main() 