import csv

# Define input and output files
clay_file = 'clay_uk_advisors_contacts_rows.csv'
cold_file = 'cold_outreach_boards_rows.csv'
output_file = 'combined_contacts.csv'

# Define the target columns for the contacts table
fieldnames = [
    'first_name', 'last_name', 'full_name', 'email', 'phone',
    'job_title', 'location', 'linkedin_url', 'company_name', 'source_table'
]

def process_clay_row(row):
    return {
        'first_name': row.get('first_name', ''),
        'last_name': row.get('last_name', ''),
        'full_name': row.get('full_name', ''),
        'email': row.get('work_email', ''),
        'phone': '',
        'job_title': row.get('job_title', ''),
        'location': row.get('location', ''),
        'linkedin_url': row.get('linkedin_profile', ''),
        'company_name': row.get('company_domain', ''),
        'source_table': 'clay_uk_advisors_contacts',
    }

def process_cold_row(row):
    return {
        'first_name': row.get('first_name', ''),
        'last_name': row.get('last_name', ''),
        'full_name': row.get('name', ''),
        'email': row.get('email', ''),
        'phone': row.get('phone_number', ''),
        'job_title': row.get('contact_group', ''),
        'location': row.get('location', ''),
        'linkedin_url': row.get('linkedin', ''),
        'company_name': row.get('company_name', ''),
        'source_table': 'cold_outreach_boards',
    }

def main():
    combined_rows = []
    # Process clay_uk_advisors_contacts_rows.csv
    with open(clay_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            combined_rows.append(process_clay_row(row))
    # Process cold_outreach_boards_rows.csv
    with open(cold_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            combined_rows.append(process_cold_row(row))
    # Write combined output
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)

if __name__ == '__main__':
    main() 