import csv
import os
import openai
from collections import defaultdict

# Mapping logic for firm size from contact_group
FIRM_SIZE_MAP = [
    (['single adviser'], 'individual'),
    (['5-9 adviser', '5-9 advisers', '5-9'], 'small_firm'),
    (['10-24 adviser', '10-24 advisers', '10-24'], 'medium_firm'),
    (['25', '25+', '25-39', '40-50', 'firm with 25', 'firm with 40', 'firm with 50', 'large'], 'large_firm'),
]

def infer_firm_size(contact_group):
    if not contact_group:
        return ''
    cg = contact_group.lower()
    for patterns, category in FIRM_SIZE_MAP:
        if any(p in cg for p in patterns):
            return category
    return ''

def load_cold_outreach(filename):
    cold_map = defaultdict(list)
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('email', '').strip().lower(), row.get('first_name', '').strip().lower(), row.get('last_name', '').strip().lower())
            cold_map[key].append(row)
    return cold_map

def get_openai_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input('Enter your OpenAI API key: ')
    return api_key

def classify_role_category(job_title, openai_client):
    if not job_title:
        return ''
    prompt = (
        "Classify the following job title as one of: direct_user (for planners, advisers, paraplanners, etc.), "
        "decision_maker (for executives, directors, etc.), or other.\n"
        f"Job title: {job_title}\n"
        "Category: "
    )
    response = openai_client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14", # 4.1-nano equivalent
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0
    )
    category = response.choices[0].message.content.strip().lower()
    if 'direct_user' in category:
        return 'direct_user'
    elif 'decision_maker' in category:
        return 'decision_maker'
    elif 'other' in category:
        return 'other'
    return ''

def main():
    contacts_file = 'contacts_rows.csv'
    cold_file = 'cold_outreach_boards_rows.csv'
    output_file = 'contacts_rows_processed.csv'

    cold_map = load_cold_outreach(cold_file)
    openai.api_key = get_openai_api_key()
    openai_client = openai

    with open(contacts_file, newline='', encoding='utf-8') as fin, \
         open(output_file, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            # Only update firm_size_category if blank
            if not row.get('firm_size_category'):
                key = (row.get('email', '').strip().lower(), row.get('first_name', '').strip().lower(), row.get('last_name', '').strip().lower())
                cold_rows = cold_map.get(key, [])
                firm_size = ''
                for cold_row in cold_rows:
                    firm_size = infer_firm_size(cold_row.get('contact_group', ''))
                    if firm_size:
                        break
                row['firm_size_category'] = firm_size
            # Only update role_category if blank
            if not row.get('role_category'):
                row['role_category'] = classify_role_category(row.get('job_title', ''), openai_client)
            writer.writerow(row)
    print(f"Processed contacts written to {output_file}")

if __name__ == '__main__':
    main() 