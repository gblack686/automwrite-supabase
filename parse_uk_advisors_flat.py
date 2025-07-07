import csv
import ast

input_file = 'uk_advisors_data 21(in).csv'
output_file = 'uk_advisors_flat.csv'

with open(input_file, newline='', encoding='utf-8') as fin, open(output_file, 'w', newline='', encoding='utf-8') as fout:
    reader = csv.DictReader(fin)
    fieldnames = [
        'company_name', 'total_advisers', 'location', 'address', 'website', 'adviser_name', 'adviser_profile_url'
    ]
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        advisers_str = row.get('Individual Advisers', '').strip()
        if advisers_str:
            try:
                advisers = ast.literal_eval(advisers_str)
            except Exception:
                advisers = []
        else:
            advisers = []
        for adviser in advisers:
            writer.writerow({
                'company_name': row.get('Company Name', ''),
                'total_advisers': row.get('Total Advisers', ''),
                'location': row.get('Location', ''),
                'address': row.get('Address', ''),
                'website': row.get('Website', ''),
                'adviser_name': adviser.get('name', ''),
                'adviser_profile_url': adviser.get('profile_url', '')
            }) 