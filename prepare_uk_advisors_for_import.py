import csv

input_file = 'contacts_rows (2).csv'
output_file = 'uk_advisors_flat_import.csv'

official_fields = [
    'id','company_id','first_name','last_name','full_name','email','phone','job_title','seniority_level','department','location','country','linkedin_url','twitter_url','bio','lead_status','lead_source','lead_score','tags','email_opt_out','linkedin_opt_out','created_at','updated_at','last_contacted_at','source_table','firm_size_category','role_category','company_name','followers'
]

output_fields = official_fields + ['financial_advisers_url']

def extract_last_name(full_name):
    parts = full_name.strip().split()
    if len(parts) > 1:
        return parts[-1]
    return ''

with open(input_file, newline='', encoding='utf-8') as fin, open(output_file, 'w', newline='', encoding='utf-8') as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=output_fields)
    writer.writeheader()
    for row in reader:
        last_name = row.get('last_name', '')
        linkedin_url = row.get('linkedin_url', '')
        # If last_name contains a LinkedIn URL, move it to linkedin_url (if linkedin_url is blank)
        if 'linkedin.com' in last_name:
            if not linkedin_url:
                linkedin_url = last_name
            # Try to recover last name from full_name
            last_name = extract_last_name(row.get('full_name', ''))
        # Now handle the linkedin_url and financial_advisers_url logic
        if 'linkedin.com' in linkedin_url:
            financial_advisers_url = ''
        elif 'financialadvisers.co.uk' in linkedin_url:
            financial_advisers_url = linkedin_url
            linkedin_url = ''
        else:
            financial_advisers_url = ''
            linkedin_url = linkedin_url if linkedin_url else ''
        out_row = {k: row.get(k, '') for k in official_fields}
        out_row['last_name'] = last_name
        out_row['linkedin_url'] = linkedin_url
        out_row['financial_advisers_url'] = financial_advisers_url
        writer.writerow(out_row) 