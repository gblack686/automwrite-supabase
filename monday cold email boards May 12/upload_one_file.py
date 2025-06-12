import pandas as pd
import json
import requests

# Supabase credentials
SUPABASE_URL = "https://xaezrqaiswdplflbalxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZXpycWFpc3dkcGxmbGJhbHhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MTIwNjksImV4cCI6MjA2MjQ4ODA2OX0.JciLYAitkgL7jln9fTtipad7xR7TgcUJqKmCrzBopX0"

# Excel file path
EXCEL_FILE = "monday cold email boards May 12/Cold_Email_Out_Reach_Prospecting_Contacts_1747107836.xlsx"

def upload_to_supabase(data):
    url = f"{SUPABASE_URL}/rest/v1/monday_contacts"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    print(f"Uploading {len(data)} records...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"Data uploaded successfully")
        else:
            print(f"Error uploading: {response.status_code} - {response.text}")
            print(f"First record: {data[0]}")
    except Exception as e:
        print(f"Exception uploading: {str(e)}")

def main():
    print(f"Loading data from {EXCEL_FILE}...")
    
    try:
        # Read the Excel file
        raw_df = pd.read_excel(EXCEL_FILE, header=None)
        
        # Find the header row
        header_row = None
        for i in range(len(raw_df)):
            if raw_df.iloc[i, 0] == "Name":
                header_row = i
                break
        
        if header_row is None:
            print("Could not find header row with 'Name' column")
            return
        
        # Extract the group name from the previous rows
        group_name = "Unknown"
        for i in range(header_row):
            if pd.notna(raw_df.iloc[i, 0]) and "Cold Email Out Reach" not in str(raw_df.iloc[i, 0]):
                group_name = raw_df.iloc[i, 0]
                break
        
        # Read the Excel file with proper header
        df = pd.read_excel(EXCEL_FILE, header=header_row)
        
        # Clean up the column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Print the actual columns for verification
        print(f"Found columns: {df.columns.tolist()}")
        
        # Define all required fields that must be present in all records
        required_fields = [
            "source_file", "contact_group", "name", "email", "phone_number", 
            "website", "company_name", "status", "first_name", "last_name",
            "address", "location", "linkedin", "notes", "extra_data"
        ]
        
        # Records to upload
        records = []
        
        # Process each row
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row['Name']):
                continue
                
            # Create a record with ALL required fields (initialize with None)
            record = {field: None for field in required_fields}
            
            # Set the known fields
            record["source_file"] = EXCEL_FILE.split('/')[-1]
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
                if src_col in df.columns and pd.notna(row[src_col]):
                    record[dest_col] = str(row[src_col]).strip()
            
            # Store any additional fields as JSON
            extra_data = {}
            for col in df.columns:
                if col not in field_mapping.keys() and col not in ['Person', 'Phone #2']:
                    if pd.notna(row[col]):
                        extra_data[col] = str(row[col]).strip()
            
            # Add Phone #2 as separate field if available
            if 'Phone #2' in df.columns and pd.notna(row['Phone #2']):
                record['notes'] = f"Second phone: {row['Phone #2']}"
                
            record["extra_data"] = json.dumps(extra_data) if extra_data else None
            
            # Verify all required fields are present
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                print(f"Warning: Missing fields in record: {missing_fields}")
                
            records.append(record)
        
        if records:
            print(f"Processed {len(records)} records")
            print(f"Sample record keys: {list(records[0].keys())}")
            upload_to_supabase(records)
        else:
            print("No records to upload")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 