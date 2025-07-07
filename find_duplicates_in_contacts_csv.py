import csv
from collections import defaultdict

input_file = 'combined_contacts.csv'
fieldnames = [
    'first_name', 'last_name', 'full_name', 'email', 'phone',
    'job_title', 'location', 'linkedin_url', 'company_name', 'source_table'
]

def main():
    duplicates = defaultdict(list)
    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['email'].strip().lower(), row['full_name'].strip().lower())
            duplicates[key].append(row)
    # Only keep keys with more than one entry
    dupes = {k: v for k, v in duplicates.items() if len(v) > 1 and k[0]}
    if not dupes:
        print('No duplicates found.')
        return
    for key, rows in dupes.items():
        print(f"\nDuplicate for email: {key[0]}, full_name: {key[1]}")
        for i, row in enumerate(rows, 1):
            print(f"  Record {i}:")
            for field in fieldnames:
                print(f"    {field}: {row[field]}")

if __name__ == '__main__':
    main() 