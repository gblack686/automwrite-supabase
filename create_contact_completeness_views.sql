-- View: contacts_with_email
CREATE OR REPLACE VIEW contacts_with_email AS
SELECT 
    COUNT(*) AS contacts_with_email,
    (SELECT COUNT(*) FROM contacts) AS total_contacts
FROM contacts
WHERE email IS NOT NULL AND email <> '';

-- View: contacts_with_linkedin_url
CREATE OR REPLACE VIEW contacts_with_linkedin_url AS
SELECT 
    COUNT(*) AS contacts_with_linkedin_url,
    (SELECT COUNT(*) FROM contacts) AS total_contacts
FROM contacts
WHERE linkedin_url IS NOT NULL AND linkedin_url <> '';

-- View: contacts_with_email_and_linkedin_url
CREATE OR REPLACE VIEW contacts_with_email_and_linkedin_url AS
SELECT 
    COUNT(*) AS contacts_with_email_and_linkedin_url,
    (SELECT COUNT(*) FROM contacts) AS total_contacts
FROM contacts
WHERE email IS NOT NULL AND email <> ''
  AND linkedin_url IS NOT NULL AND linkedin_url <> '';

-- Summary View: contact_completeness_summary
CREATE OR REPLACE VIEW contact_completeness_summary AS
SELECT
    (SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email <> '') AS contacts_with_email,
    (SELECT COUNT(*) FROM contacts WHERE linkedin_url IS NOT NULL AND linkedin_url <> '') AS contacts_with_linkedin_url,
    (SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email <> '' AND linkedin_url IS NOT NULL AND linkedin_url <> '') AS contacts_with_email_and_linkedin_url,
    (SELECT COUNT(*) FROM contacts) AS total_contacts;

-- View: contact_segment_summary_view
-- Groups by segment, firm size, seniority, and country
CREATE OR REPLACE VIEW contact_segment_summary_view AS
SELECT
    c.role_category AS segment,
    c.firm_size_category AS firm_size,
    get_seniority(c.job_title) AS seniority_level,
    c.country,
    COUNT(c.id) AS contact_count
FROM contacts c
GROUP BY c.role_category, c.firm_size_category, get_seniority(c.job_title), c.country;

-- View: contact_company_summary_view
-- Groups by company_name (from contacts)
CREATE OR REPLACE VIEW contact_company_summary_view AS
SELECT
    c.company_name,
    COUNT(c.id) AS contact_count
FROM contacts c
WHERE c.company_name IS NOT NULL AND c.company_name <> ''
GROUP BY c.company_name; 