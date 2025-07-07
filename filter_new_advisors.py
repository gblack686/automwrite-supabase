import csv

advisors_file = 'uk_advisors_flat.csv'
contacts_file = 'contacts_rows (2).csv'
output_file = 'uk_advisors_flat_new.csv'

def split_name(name):
    parts = name.strip().split()
    if len(parts) == 0:
        return '', ''
    elif len(parts) == 1:
        return parts[0].lower(), ''
    else:
        return parts[0].lower(), parts[-1].lower()

# Load contacts into a set of (first_name, last_name, company_name, website)
contacts = set()
with open(contacts_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        first = row.get('first_name', '').strip().lower()
        last = row.get('last_name', '').strip().lower()
        company = row.get('company_name', '').strip().lower()
        website = row.get('website', '').strip().lower() if 'website' in row else ''
        contacts.add((first, last, company))
        if website:
            contacts.add((first, last, website))

with open(advisors_file, newline='', encoding='utf-8') as fin, open(output_file, 'w', newline='', encoding='utf-8') as fout:
    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        adviser_name = row.get('adviser_name', '').strip()
        adviser_first, adviser_last = split_name(adviser_name)
        company = row.get('company_name', '').strip().lower()
        website = row.get('website', '').strip().lower()
        matched = (
            (adviser_first, adviser_last, company) in contacts or
            (adviser_first, adviser_last, website) in contacts
        )
        if not matched:
            writer.writerow(row) 