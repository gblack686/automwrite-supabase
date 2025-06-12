-- View to segment contacts by location
CREATE OR REPLACE VIEW tam_by_location_view AS
SELECT
    location,
    COUNT(id) AS contact_count
FROM
    public.cold_outreach_boards
WHERE
    location IS NOT NULL AND location != ''
GROUP BY
    location
ORDER BY
    contact_count DESC;

-- Function to determine seniority from a job title
CREATE OR REPLACE FUNCTION get_seniority(title TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN CASE
        WHEN title ILIKE '%c-level%' OR title ILIKE '%ceo%' OR title ILIKE '%cto%' OR title ILIKE '%cfo%' OR title ILIKE '%coo%' THEN 'C-Level'
        WHEN title ILIKE '%vp%' OR title ILIKE '%vice president%' THEN 'VP'
        WHEN title ILIKE '%director%' THEN 'Director'
        WHEN title ILIKE '%manager%' OR title ILIKE '%head of%' THEN 'Manager'
        WHEN title ILIKE '%senior%' OR title ILIKE '%sr.%' THEN 'Senior'
        WHEN title ILIKE '%junior%' OR title ILIKE '%jr.%' THEN 'Junior'
        ELSE 'Other'
    END;
END;
$$ LANGUAGE plpgsql;

-- View to segment contacts by seniority
CREATE OR REPLACE VIEW tam_by_seniority_view AS
SELECT
    get_seniority(c.job_title) AS seniority_level,
    COUNT(b.id) AS contact_count
FROM
    public.cold_outreach_boards b
JOIN
    public.clay_uk_advisors_contacts c ON b.email = c.work_email
WHERE
    c.job_title IS NOT NULL AND c.job_title != ''
GROUP BY
    seniority_level
ORDER BY
    contact_count DESC;

-- View to segment contacts by firm size
CREATE OR REPLACE VIEW tam_by_firm_size_view AS
SELECT
    ua.size AS firm_size,
    COUNT(cob.id) AS contact_count
FROM
    public.cold_outreach_boards cob
JOIN
    public.uk_advisors ua ON cob.company_name = ua.company_name
WHERE
    ua.size IS NOT NULL AND ua.size != ''
GROUP BY
    ua.size
ORDER BY
    contact_count DESC;

-- View to segment contacts by LinkedIn followers
CREATE OR REPLACE VIEW tam_by_followers_view AS
SELECT
    CASE
        WHEN lps.followers >= 10000 THEN '10000+ followers'
        WHEN lps.followers >= 5000 THEN '5000-9999 followers'
        WHEN lps.followers >= 1000 THEN '1000-4999 followers'
        WHEN lps.followers >= 500 THEN '500-999 followers'
        ELSE '0-499 followers'
    END AS follower_segment,
    COUNT(cob.id) AS contact_count
FROM
    public.cold_outreach_boards cob
JOIN
    public.leadmagic_people_search lps ON cob.linkedin = lps.profile_url
WHERE
    lps.followers IS NOT NULL
GROUP BY
    follower_segment
ORDER BY
    MIN(lps.followers) DESC; 