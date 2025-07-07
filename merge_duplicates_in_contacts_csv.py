import csv
from collections import defaultdict

input_file = 'combined_contacts.csv'
output_file = 'combined_contacts_merged.csv'
fieldnames = [
    'first_name', 'last_name', 'full_name', 'email', 'phone',
    'job_title', 'location', 'linkedin_url', 'company_name', 'source_table'
]

def merge_records(records):
    merged = {}
    for field in fieldnames:
        # Prefer the first non-empty value found
        merged[field] = next((r[field] for r in records if r[field].strip()), '')
    # If there are multiple source_tables, join them
    sources = set(r['source_table'] for r in records if r['source_table'].strip())
    merged['source_table'] = ','.join(sorted(sources))
    return merged

def main():
    by_key = defaultdict(list)
    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['email'].strip().lower(), row['full_name'].strip().lower())
            by_key[key].append(row)
    merged_rows = [merge_records(records) for records in by_key.values()]
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)
    print(f"Merged contacts written to {output_file}")

if __name__ == '__main__':
    main() 