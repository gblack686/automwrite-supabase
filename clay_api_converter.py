import json

def clay_http_api_json_converter(columns, prefix="company_"):
    """
    Convert a list of column names to a JSON format expected by Clay HTTP API.
    
    This function takes a list of column names and transforms them into a JSON structure 
    suitable for Clay HTTP API. It converts column names to a consistent format with the
    specified prefix, and formats values with double curly braces for template substitution
    without quotes around them.
    
    Args:
        columns (list): List of column names to convert
        prefix (str, optional): Prefix to add to each key in the output. Defaults to "company_".
    
    Returns:
        str: JSON string with the formatted data (single line, no spaces)
    
    Example:
        >>> clay_http_api_json_converter(["Name", "Website"], prefix="contact_")
        '{"contact_full_name":{{Name}},"contact_website":{{Website}}}'
    """
    # Define mapping of column names to Clay API keys and template values
    # The first part of each tuple will have the prefix applied
    base_mapping = {
        # Basic profile info
        "Name": ("full_name", "Name"),
        "LinkedIn Profile": ("url", "LinkedInProfile"),
        "Title": ("title", "Title"),
        "Org": ("org", "Org"),
        "Slug": ("slug", "Slug"),
        "Connections": ("connections", "Connections"),
        "Num Followers": ("followers", "NumFollowers"),
        "Headline": ("headline", "Headline"),
        "Summary": ("summary", "Summary"),
        "First Name": ("first_name", "FirstName"),
        "Last Name": ("last_name", "LastName"),
        "Country": ("country", "Country"),
        "Location Name": ("location_name", "LocationName"),
        "Dob": ("date_of_birth", "Dob"),
        "Jobs Count": ("jobs_count", "JobsCount"),
        "Last Refresh": ("last_refresh_date", "LastRefresh"),
        "Picture Url Copy": ("picture_url_copy", "PictureUrlCopy"),
        "Picture Url Orig": ("picture_url_original", "PictureUrlOrig"),
        "Workflow Id": ("workflow_id", "WorkflowId"),
        
        # Experience fields
        "Title - Experience": ("experience_title", "Title-Experience"),
        "Org Id - Experience": ("experience_org_id", "OrgId-Experience"),
        "Company - Experience": ("experience_company", "Company-Experience"),
        "Summary - Experience": ("experience_summary", "Summary-Experience"),
        "Locality - Experience": ("experience_locality", "Locality-Experience"),
        "Company Id - Experience": ("experience_company_id", "CompanyId-Experience"),
        "End Date - Experience": ("experience_end_date", "EndDate-Experience"),
        "Is Current - Experience": ("experience_is_current", "IsCurrent-Experience"),
        "Start Date - Experience": ("experience_start_date", "StartDate-Experience"),
        "Company Domain - Experience": ("experience_company_domain", "CompanyDomain-Experience"),
        
        # Latest Experience fields
        "Url - Latest Experience": ("latest_experience_url", "Url-LatestExperience"),
        "Title - Latest Experience": ("latest_experience_title", "Title-LatestExperience"),
        "Company - Latest Experience": ("latest_experience_company", "Company-LatestExperience"),
        "Start Date - Latest Experience": ("latest_experience_start_date", "StartDate-LatestExperience"),
        "Is Current - Latest Experience": ("latest_experience_is_current", "IsCurrent-LatestExperience"),
        "Company Domain Source": ("latest_experience_company_domain", "CompanyDomainSource"),
        
        # Education fields
        "Grade - Education": ("education_grade", "Grade-Education"),
        "Degree - Education": ("education_degree", "Degree-Education"),
        "End Date - Education": ("education_end_date", "EndDate-Education"),
        "Start Date - Education": ("education_start_date", "StartDate-Education"),
        "Activities - Education": ("education_activities", "Activities-Education"),
        "School Name - Education": ("education_school_name", "SchoolName-Education"),
        "Field Of Study - Education": ("education_field_of_study", "FieldOfStudy-Education"),
        
        # Projects fields
        "Title - Projects": ("projects_title", "Title-Projects"),
        "Summary - Projects": ("projects_summary", "Summary-Projects"),
        
        # Languages fields
        "Language - Languages": ("languages_language", "Language-Languages"),
        "Proficiency - Languages": ("languages_proficiency", "Proficiency-Languages"),
        
        # Publications fields
        "Title - Publications": ("publications_title", "Title-Publications"),
        "Summary - Publications": ("publications_summary", "Summary-Publications"),
        "Publisher - Publications": ("publications_publisher", "Publisher-Publications"),
        "Date - Publications": ("publications_date", "Date-Publications"),
        "Url - Publications": ("publications_url", "Url-Publications"),
        "Num Recommenders": ("publications_num_recommenders", "NumRecommenders"),
        
        # Certifications fields
        "Company Name - Certifications": ("certifications_company_name", "CompanyName-Certifications"),
        "Title - Certifications": ("certifications_title", "Title-Certifications"),
        "Date - Certifications": ("certifications_date", "Date-Certifications"),
        "Verify Url - Certifications": ("certifications_verify_url", "VerifyUrl-Certifications"),
    }
    
    # Apply the prefix to each key in the mapping
    column_mapping = {}
    for key, (base_key, value) in base_mapping.items():
        # Special case for workflow_id - don't add prefix
        if base_key == "workflow_id":
            column_mapping[key] = (base_key, value)
        else:
            column_mapping[key] = (f"{prefix}{base_key}", value)
    
    # Create a list to build parts of the JSON string manually
    json_parts = []
    
    # Process each column
    for i, column in enumerate(columns):
        if column in column_mapping:
            key, value = column_mapping[column]
            # Format as "key":{{value}} without quotes around the template
            json_parts.append(f'"{key}":{{{{%s}}}}' % value)
        else:
            # If column not in mapping, use a default naming convention
            sanitized_key = column.lower().replace(" ", "_")
            # Create a CamelCase version of the column name without spaces
            camelcase_value = ''.join(word if i == 0 else word.capitalize() 
                                     for i, word in enumerate(column.split(' ')))
            key = f"{prefix}{sanitized_key}"
            # Format as "key":{{value}} without quotes around the template
            json_parts.append(f'"{key}":{{{{%s}}}}' % camelcase_value)
    
    # Join parts with commas and wrap in curly braces
    result = '{' + ','.join(json_parts) + '}'
    
    return result


# Example usage
if __name__ == "__main__":
    # Example columns
    sample_columns = [
        "Name", 
        "LinkedIn Profile", 
        "Title", 
        "Org", 
        "Country",
        "First Name",
        "Last Name",
        "Workflow Id"
    ]
    
    # Convert to Clay API format with default company_ prefix
    output1 = clay_http_api_json_converter(sample_columns)
    print("With company_ prefix:")
    print(output1)
    
    # Convert to Clay API format with contact_ prefix
    output2 = clay_http_api_json_converter(sample_columns, prefix="contact_")
    print("\nWith contact_ prefix:")
    print(output2)
    
    # Example of how you might use this in practice
    print("\nExample of how to use in your code:")
    print("-----------------------------------")
    print("from clay_api_converter import clay_http_api_json_converter")
    print("columns = ['Name', 'LinkedIn Profile', 'Title', 'Org']")
    print("payload = clay_http_api_json_converter(columns)")
    print("# Now you can use this payload in your HTTP request to Clay API") 