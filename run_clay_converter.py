from clay_api_converter import clay_http_api_json_converter
import sys

# The columns from the uk_advisors_clay table (excluding id and created_at)
columns = [
    "company_name",
    "total_advisers",
    "website",
    "enrich_company",
    "name",
    "website_2",
    "employee_count",
    "size",
    "industry",
    "description",
    "url",
    "follower_count",
    "domain",
    "type",
    "founded",
    "revenue",
    "revenue_data_provider",
    "site_traffic",
    "add_lead_to_heyreach"
]

# Convert to Clay API format with the default company_ prefix
output = clay_http_api_json_converter(columns)

# Print without line breaks (avoid automatic line wrapping in terminal)
sys.stdout.write(output)
# Optional: Write to a file for easier copying
with open("clay_output.txt", "w") as f:
    f.write(output)

print("\nOutput saved to clay_output.txt")

# Also generate output with contact_ prefix for comparison
contact_output = clay_http_api_json_converter(columns, prefix="contact_")
# Write to a separate file
with open("clay_output_contact.txt", "w") as f:
    f.write(contact_output) 