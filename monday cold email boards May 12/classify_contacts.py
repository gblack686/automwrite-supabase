import requests
import re
import json
import time

# Supabase credentials
SUPABASE_URL = "https://xaezrqaiswdplflbalxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZXpycWFpc3dkcGxmbGJhbHhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MTIwNjksImV4cCI6MjA2MjQ4ODA2OX0.JciLYAitkgL7jln9fTtipad7xR7TgcUJqKmCrzBopX0"

# Fetch contacts from Supabase
def fetch_contacts(limit=1000, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/monday_contacts?select=id,name,email,first_name,last_name,company_name,extra_data&limit={limit}&offset={offset}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching contacts: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception fetching contacts: {str(e)}")
        return []

# Update entity_type for a contact
def update_entity_type(contact_id, entity_type):
    url = f"{SUPABASE_URL}/rest/v1/monday_contacts?id=eq.{contact_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    data = {"entity_type": entity_type}
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 204:
            return True
        else:
            print(f"Error updating contact {contact_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception updating contact {contact_id}: {str(e)}")
        return False

# Determine if a contact represents a company or person
def classify_contact(contact):
    # Common company email prefixes
    company_email_prefixes = [
        'info', 'contact', 'hello', 'mail', 'enquiry', 'enquiries', 'sales',
        'support', 'admin', 'office', 'help', 'service', 'general', 'directors',
        'accounts', 'finance', 'marketing', 'compliance', 'hr', 'careers'
    ]
    
    # Company name indicators in the name field
    company_name_indicators = [
        'ltd', 'limited', 'llc', 'inc', 'incorporated', 'plc', 'corporation',
        'corp', 'group', 'holdings', 'associates', 'partners', 'consultants',
        'services', 'solutions', 'advisers', 'advisors', 'wealth', 'financial',
        'management', 'investments', 'consulting', 'international', 'uk', 'bank'
    ]
    
    # Decision making logic
    is_company = False
    reasons = []
    
    # Check email pattern
    if contact.get('email'):
        email = contact['email'].lower()
        username = email.split('@')[0]
        
        # Check for company email patterns
        if any(username.startswith(prefix) for prefix in company_email_prefixes):
            is_company = True
            reasons.append(f"Email starts with company prefix: {username}")
        
        # Check for team/role emails
        if '@' in email and any(prefix in username for prefix in company_email_prefixes):
            is_company = True
            reasons.append(f"Email contains company term: {username}")
    
    # Check name for company indicators
    if contact.get('name') and not is_company:
        name = contact['name'].lower()
        
        # Check for common company name patterns
        if any(indicator in name for indicator in company_name_indicators):
            is_company = True
            reasons.append(f"Name contains company indicator: {contact['name']}")
    
    # Look for presence of both first and last name as strong person indicator
    if contact.get('first_name') and contact.get('last_name') and not is_company:
        # If a contact has both first and last name populated, likely a person
        if len(contact['first_name']) > 1 and len(contact['last_name']) > 1:
            is_company = False
            reasons.append("Has distinct first and last name")
    
    # Look at company_name field
    if contact.get('company_name') and not contact.get('first_name') and not contact.get('last_name'):
        is_company = True
        reasons.append(f"Has company name but no person name: {contact['company_name']}")
    
    # Check extra_data for additional clues
    if contact.get('extra_data') and not is_company:
        try:
            extra_data = json.loads(contact['extra_data']) if contact['extra_data'] else {}
            
            # If Decision Maker field has company terms like "Head Office"
            decision_maker = extra_data.get('Decision Maker', '')
            if isinstance(decision_maker, str) and 'office' in decision_maker.lower():
                is_company = True
                reasons.append(f"Decision Maker indicates company: {decision_maker}")
                
        except (json.JSONDecodeError, TypeError):
            pass
    
    return 'company' if is_company else 'person', reasons

def main():
    print("Starting contact classification...")
    
    # Process contacts in batches to handle large datasets
    batch_size = 500
    offset = 0
    total_processed = 0
    companies_found = 0
    
    while True:
        # Fetch a batch of contacts
        contacts = fetch_contacts(batch_size, offset)
        
        if not contacts:
            break
            
        print(f"Processing batch of {len(contacts)} contacts (offset {offset})...")
        
        # Process each contact
        for contact in contacts:
            entity_type, reasons = classify_contact(contact)
            
            if entity_type == 'company':
                companies_found += 1
                print(f"Classified as COMPANY: {contact.get('name')} ({contact.get('email')}) - {'; '.join(reasons)}")
            else:
                print(f"Classified as PERSON: {contact.get('name')} ({contact.get('email')})")
                
            # Update the contact in Supabase
            success = update_entity_type(contact['id'], entity_type)
            if not success:
                print(f"Failed to update contact {contact['id']}")
            
            total_processed += 1
            
            # Sleep briefly between requests to avoid rate limiting
            if total_processed % 50 == 0:
                time.sleep(0.5)
        
        # Move to the next batch
        offset += batch_size
        
        # If we got fewer contacts than the batch size, we've reached the end
        if len(contacts) < batch_size:
            break
    
    print(f"\nClassification complete!")
    print(f"Total contacts processed: {total_processed}")
    print(f"Companies identified: {companies_found}")
    print(f"Persons identified: {total_processed - companies_found}")

if __name__ == "__main__":
    main() 