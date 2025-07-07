-- Create get_seniority function
CREATE OR REPLACE FUNCTION public.get_seniority(title text)
RETURNS text
LANGUAGE plpgsql
AS $function$
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
$function$;

-- Create TAM by Seniority View
-- Note: Requires a get_seniority(job_title) function or replace with your own logic
CREATE OR REPLACE VIEW tam_by_seniority_view AS
SELECT
    get_seniority(c.job_title) AS seniority_level,
    COUNT(c.id) AS contact_count
FROM contacts c
WHERE c.job_title IS NOT NULL AND c.job_title <> ''
GROUP BY get_seniority(c.job_title)
ORDER BY COUNT(c.id) DESC;

-- Create TAM by Firm Size View
CREATE OR REPLACE VIEW tam_by_firm_size_view AS
SELECT
    c.firm_size_category AS firm_size,
    COUNT(c.id) AS contact_count
FROM contacts c
WHERE c.firm_size_category IS NOT NULL AND c.firm_size_category <> ''
GROUP BY c.firm_size_category
ORDER BY COUNT(c.id) DESC;

-- Create TAM by Followers View
-- Note: Requires a followers column in contacts (integer or castable to int)
CREATE OR REPLACE VIEW tam_by_followers_view AS
SELECT
    CASE
        WHEN c.followers::int >= 10000 THEN '10000+ followers'
        WHEN c.followers::int >= 5000 THEN '5000-9999 followers'
        WHEN c.followers::int >= 1000 THEN '1000-4999 followers'
        WHEN c.followers::int >= 500 THEN '500-999 followers'
        ELSE '0-499 followers'
    END AS follower_segment,
    COUNT(c.id) AS contact_count
FROM contacts c
WHERE c.followers IS NOT NULL
GROUP BY
    CASE
        WHEN c.followers::int >= 10000 THEN '10000+ followers'
        WHEN c.followers::int >= 5000 THEN '5000-9999 followers'
        WHEN c.followers::int >= 1000 THEN '1000-4999 followers'
        WHEN c.followers::int >= 500 THEN '500-999 followers'
        ELSE '0-499 followers'
    END
ORDER BY MIN(c.followers::int) DESC;

-- Create TAM by Location View
CREATE OR REPLACE VIEW tam_by_location_view AS
SELECT
    c.location,
    COUNT(c.id) AS contact_count
FROM contacts c
WHERE c.location IS NOT NULL AND c.location <> ''
GROUP BY c.location
ORDER BY COUNT(c.id) DESC; 