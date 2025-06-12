-- Simplified Schema V2: 3-Table Design
-- This migration creates a clean, simplified database structure with just 3 core tables

-- 1. COMPANIES TABLE
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    website TEXT,
    industry TEXT,
    size_employees INTEGER,
    size_advisors INTEGER,
    founded TEXT,
    location TEXT,
    country TEXT,
    linkedin_url TEXT,
    facebook_url TEXT,
    twitter_url TEXT,
    description TEXT,
    tier TEXT, -- Tier 1, Tier 2, etc.
    annual_revenue BIGINT,
    company_type TEXT, -- Advisory firm, Financial services, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. CONTACTS TABLE  
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    job_title TEXT,
    seniority_level TEXT, -- Senior, Mid-level, Junior, C-level, etc.
    department TEXT,
    location TEXT,
    country TEXT,
    linkedin_url TEXT,
    twitter_url TEXT,
    bio TEXT,
    
    -- Lead qualification fields
    lead_status TEXT DEFAULT 'new', -- new, qualified, contacted, converted, lost
    lead_source TEXT, -- clay, heyreach, manual, etc.
    lead_score INTEGER DEFAULT 0,
    tags TEXT[], -- Array of tags for flexible categorization
    
    -- Contact preferences
    email_opt_out BOOLEAN DEFAULT FALSE,
    linkedin_opt_out BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_contacted_at TIMESTAMPTZ
);

-- 3. EMAILS TABLE
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    
    -- Email metadata
    direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    email_type TEXT, -- cold_outreach, follow_up, reply, newsletter, etc.
    subject TEXT,
    body TEXT,
    
    -- Campaign tracking
    campaign_id TEXT, -- External campaign ID from tools like HeyReach
    campaign_name TEXT,
    sequence_step INTEGER,
    
    -- Email status
    status TEXT DEFAULT 'sent' CHECK (status IN ('draft', 'sent', 'delivered', 'opened', 'clicked', 'replied', 'bounced', 'failed')),
    
    -- Engagement tracking
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    
    -- External tool integration
    external_id TEXT, -- ID from external tools
    external_source TEXT, -- heyreach, clay, manual, etc.
    
    -- Timestamps
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_industry ON companies(industry);

CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_company_id ON contacts(company_id);
CREATE INDEX idx_contacts_full_name ON contacts(full_name);
CREATE INDEX idx_contacts_lead_status ON contacts(lead_status);
CREATE INDEX idx_contacts_lead_source ON contacts(lead_source);

CREATE INDEX idx_emails_contact_id ON emails(contact_id);
CREATE INDEX idx_emails_company_id ON emails(company_id);
CREATE INDEX idx_emails_direction ON emails(direction);
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_campaign_id ON emails(campaign_id);
CREATE INDEX idx_emails_sent_at ON emails(sent_at);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emails_updated_at BEFORE UPDATE ON emails
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;

-- Create basic RLS policies (adjust based on your auth requirements)
CREATE POLICY "Enable read access for all users" ON companies FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON companies FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON companies FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON companies FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON contacts FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON contacts FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON contacts FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON contacts FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON emails FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON emails FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON emails FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON emails FOR DELETE USING (true); 