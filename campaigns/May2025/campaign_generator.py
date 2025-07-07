import os
import json
import csv
import openai
from typing import List, Dict, Optional
import math

def load_config(config_path: str) -> Dict:
    """Load the campaign configuration from a JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)

def load_companies_from_csv(csv_path: str) -> List[Dict]:
    """Load companies from a CSV file"""
    companies = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append({
                "name": row.get("Company", ""),
                "segment": row.get("Segment", "")
            })
    return companies

def assign_tiers(companies: List[Dict], tier_count: int, accounts_per_tier: int) -> List[Dict]:
    """Assign tiers to companies based on segment and position in list"""
    # Sort companies: Financial Advisers first, then Technology Providers, then Media/PR
    segment_priority = {
        "Financial Adviser": 0,
        "Technology Provider": 1,
        "Media/PR": 2
    }
    
    sorted_companies = sorted(companies, key=lambda x: segment_priority.get(x.get("segment", ""), 3))
    
    # Assign tiers based on position in the sorted list
    companies_with_tiers = []
    for i, company in enumerate(sorted_companies):
        if i < accounts_per_tier:
            tier = 1
        elif i < accounts_per_tier * 2:
            tier = 2
        elif i < accounts_per_tier * 3:
            tier = 3
        else:
            # If we have more companies than needed, assign them to tier 3
            tier = 3
        
        company_with_tier = company.copy()
        company_with_tier["tier"] = tier
        companies_with_tiers.append(company_with_tier)
    
    return companies_with_tiers[:tier_count * accounts_per_tier]

def generate_rep_assignments(companies: List[Dict], sales_team: List[Dict], 
                             leads_per_account: int, intertwined: bool,
                             role_distribution: Optional[Dict] = None,
                             workload_balancing: Optional[Dict] = None) -> Dict:
    """Generate rep assignments for each company based on sales team roles"""
    rep_assignments = {}
    
    # Extract roles from the sales team
    roles = [rep["role"] for rep in sales_team]
    
    # Track assigned accounts per role if workload balancing is enabled
    accounts_per_role = {role: 0 for role in roles}
    max_accounts = {}
    if workload_balancing and workload_balancing.get("enabled", False):
        max_accounts = workload_balancing.get("max_accounts_per_rep", {})
    
    for company in companies:
        tier = company.get("tier", 3)  # Default to tier 3 if not specified
        company_roles = []
        
        if role_distribution and f"tier_{tier}" in role_distribution:
            # Use the role distribution from the config
            tier_roles = role_distribution[f"tier_{tier}"]
            # Make sure we don't exceed leads_per_account
            candidate_roles = tier_roles[:leads_per_account]
            
            # Check workload balancing
            if workload_balancing and workload_balancing.get("enabled", False):
                filtered_roles = []
                for role in candidate_roles:
                    # Skip roles that have reached their account limit
                    if role in max_accounts and accounts_per_role[role] >= max_accounts[role]:
                        continue
                    filtered_roles.append(role)
                    accounts_per_role[role] += 1
                company_roles = filtered_roles
            else:
                company_roles = candidate_roles
        else:
            # Default assignment strategy based on tier and role rank
            # Find the primary role for this tier
            primary_role = None
            for role_info in sorted(sales_team, key=lambda x: -x.get("rank", 0)):  # Sort by rank descending
                if role_info.get("tier_focus") == tier:
                    role = role_info["role"]
                    # Check workload balancing
                    if workload_balancing and workload_balancing.get("enabled", False):
                        if role in max_accounts and accounts_per_role[role] >= max_accounts[role]:
                            continue
                    primary_role = role
                    break
            
            if primary_role:
                company_roles.append(primary_role)
                if workload_balancing and workload_balancing.get("enabled", False):
                    accounts_per_role[primary_role] += 1
            
            # Add SDR for all accounts if intertwined
            if intertwined:
                for role_info in sales_team:
                    role = role_info["role"]
                    if role not in company_roles and len(company_roles) < leads_per_account:
                        # Prioritize roles with matching tier focus or lower rank
                        if role_info.get("tier_focus") == tier or role_info.get("rank", 0) <= 2:
                            # Check workload balancing
                            if workload_balancing and workload_balancing.get("enabled", False):
                                if role in max_accounts and accounts_per_role[role] >= max_accounts[role]:
                                    continue
                            company_roles.append(role)
                            if workload_balancing and workload_balancing.get("enabled", False):
                                accounts_per_role[role] += 1
        
        # Ensure we have at least one role
        if not company_roles and roles:
            company_roles = [roles[0]]  # Assign first role as a fallback
            if workload_balancing and workload_balancing.get("enabled", False):
                accounts_per_role[roles[0]] += 1
        
        rep_assignments[company["name"]] = company_roles
    
    return rep_assignments

def calculate_messaging_workload(companies: List[Dict], rep_assignments: Dict, 
                               messaging_capacity: Dict, email_volume: Dict,
                               campaign_duration_weeks: int) -> Dict:
    """Calculate messaging workload for each role based on assignments and capacity"""
    workload = {}
    
    # Initialize workload dictionary for each role
    for role, capacity in messaging_capacity["daily_limits"].items():
        workload[role] = {
            "accounts": [],
            "total_accounts": 0,
            "daily_automated_emails": 0,
            "daily_custom_emails": 0,
            "daily_linkedin_messages": 0,
            "weekly_automated_emails": 0,
            "weekly_custom_emails": 0,
            "weekly_linkedin_messages": 0,
            "campaign_total_automated_emails": 0,
            "campaign_total_custom_emails": 0,
            "campaign_total_linkedin_messages": 0,
            "capacity_utilization_percentage": 0
        }
    
    # Assign accounts to roles
    for company in companies:
        company_name = company["name"]
        tier = company.get("tier", 3)
        tier_key = f"tier_{tier}"
        
        # Skip if the company doesn't have assigned roles
        if company_name not in rep_assignments:
            continue
        
        # Get email volume settings for this tier
        tier_email_settings = email_volume.get(tier_key, {
            "emails_per_week": 3,
            "max_automated_percentage": 80,
            "custom_touchpoint_requirement": False
        })
        
        # Calculate emails per role for this company
        assigned_roles = rep_assignments[company_name]
        for role in assigned_roles:
            # Skip if the role doesn't have capacity settings
            if role not in messaging_capacity["daily_limits"]:
                continue
            
            # Add company to role's account list
            workload[role]["accounts"].append({
                "name": company_name,
                "tier": tier,
                "weekly_emails": tier_email_settings["emails_per_week"]
            })
            workload[role]["total_accounts"] += 1
            
            # Calculate automated vs custom split
            automated_percentage = tier_email_settings["max_automated_percentage"] / 100.0
            weekly_emails = tier_email_settings["emails_per_week"]
            weekly_automated = math.floor(weekly_emails * automated_percentage)
            weekly_custom = weekly_emails - weekly_automated
            
            # Add to role's weekly totals
            workload[role]["weekly_automated_emails"] += weekly_automated
            workload[role]["weekly_custom_emails"] += weekly_custom
            
            # Add LinkedIn messages (1 per account per week as default)
            workload[role]["weekly_linkedin_messages"] += 1
    
    # Calculate daily averages (5 working days per week)
    for role in workload:
        workload[role]["daily_automated_emails"] = math.ceil(workload[role]["weekly_automated_emails"] / 5)
        workload[role]["daily_custom_emails"] = math.ceil(workload[role]["weekly_custom_emails"] / 5)
        workload[role]["daily_linkedin_messages"] = math.ceil(workload[role]["weekly_linkedin_messages"] / 5)
        
        # Calculate campaign totals
        workload[role]["campaign_total_automated_emails"] = workload[role]["weekly_automated_emails"] * campaign_duration_weeks
        workload[role]["campaign_total_custom_emails"] = workload[role]["weekly_custom_emails"] * campaign_duration_weeks
        workload[role]["campaign_total_linkedin_messages"] = workload[role]["weekly_linkedin_messages"] * campaign_duration_weeks
        
        # Calculate capacity utilization
        daily_capacity = messaging_capacity["daily_limits"][role]["automated_emails_per_day"]
        if daily_capacity > 0:
            utilization = (workload[role]["daily_automated_emails"] / daily_capacity) * 100
            workload[role]["capacity_utilization_percentage"] = round(utilization, 1)
    
    return workload

def generate_campaign_outline(config: Dict) -> str:
    """Generate a campaign outline based on configuration"""
    # Load settings from config
    api_key = config["api_settings"]["api_key"]
    model = config["api_settings"]["model"]
    campaign_name = config["campaign_details"]["campaign_name"]
    campaign_duration_weeks = config["campaign_details"]["campaign_duration_weeks"]
    sequence_length_days = config["campaign_details"]["sequence_length_days"]
    output_file = config["campaign_details"]["output_file"]
    
    tier_count = config["tiering_settings"]["tier_count"]
    accounts_per_tier = config["tiering_settings"]["accounts_per_tier"]
    leads_per_account = config["tiering_settings"]["leads_per_account"]
    email_volume = config.get("tiering_settings", {}).get("email_volume", {})
    
    sales_team = config["sales_team"]["sales_reps"]
    intertwined_reps = config["sales_team"]["intertwined_reps"]
    
    # Get messaging capacity and workload balancing settings
    messaging_capacity = config.get("messaging_capacity", {})
    workload_balancing = config.get("advanced_settings", {}).get("workload_balancing", None)
    
    temperature = config["advanced_settings"].get("temperature", 0.7)
    max_tokens = config["advanced_settings"].get("max_tokens", 4000)
    
    # Load companies
    if config["company_data"].get("company_file"):
        companies = load_companies_from_csv(config["company_data"]["company_file"])
    else:
        companies = []
    
    # Add manually specified companies
    if config["company_data"].get("manual_company_list"):
        manual_companies = config["company_data"]["manual_company_list"]
        # Remove duplicates between manual list and CSV
        existing_names = [c["name"] for c in manual_companies]
        companies = [c for c in companies if c["name"] not in existing_names]
        companies.extend(manual_companies)
    
    # Assign tiers if not already assigned
    if not config["advanced_settings"].get("use_custom_tiers", False):
        companies = assign_tiers(companies, tier_count, accounts_per_tier)
    
    # Generate rep assignments
    if config["sales_team"]["rep_assignments"]["enabled"] and config["sales_team"]["rep_assignments"].get("custom_assignments"):
        rep_assignments = config["sales_team"]["rep_assignments"]["custom_assignments"]
    else:
        # Check if we have role distribution
        role_distribution = None
        if config["sales_team"]["rep_assignments"].get("role_distribution"):
            role_distribution = config["sales_team"]["rep_assignments"]["role_distribution"]
        
        rep_assignments = generate_rep_assignments(
            companies, sales_team, leads_per_account, intertwined_reps, 
            role_distribution, workload_balancing
        )
    
    # Calculate messaging workload if messaging capacity is defined
    messaging_workload = None
    if messaging_capacity and "daily_limits" in messaging_capacity:
        messaging_workload = calculate_messaging_workload(
            companies, rep_assignments, messaging_capacity, email_volume, campaign_duration_weeks
        )
    
    # Sort companies by tier for the prompt
    companies_by_tier = {}
    for tier in range(1, tier_count + 1):
        companies_by_tier[tier] = [c for c in companies if c.get("tier") == tier][:accounts_per_tier]
    
    # Build prompt
    prompt = f"""
    Create a detailed markdown file for a tiered outbound sales campaign with the following specifications:
    
    CAMPAIGN DETAILS:
    - Campaign Name: {campaign_name}
    - Target List: {tier_count * accounts_per_tier} companies from provided list
    - Duration: {campaign_duration_weeks}-week campaign ({accounts_per_tier} companies per tier per week)
    - Channels: Email + LinkedIn
    - Sequence Length: {sequence_length_days} days per company
    - Contacts Per Company: {leads_per_account} key decision-makers
    
    TIERING:
    - {tier_count} tiers (High Priority, Medium Priority, Nurture)
    """
    
    # Add email volume information if available
    if email_volume:
        prompt += "\nEMAIL VOLUME BY TIER:\n"
        for tier_key, settings in email_volume.items():
            tier_number = tier_key.split('_')[1]  # Extract number from tier_1, tier_2, etc.
            prompt += f"- Tier {tier_number}: {settings['emails_per_week']} emails per week, "
            prompt += f"{settings['max_automated_percentage']}% automated, "
            prompt += f"Custom touchpoint required: {settings['custom_touchpoint_requirement']}\n"
    
    # Add companies by tier
    for tier in range(1, tier_count + 1):
        tier_companies = companies_by_tier.get(tier, [])
        prompt += f"\nTIER {tier} COMPANIES:\n"
        for company in tier_companies:
            prompt += f"- {company['name']} ({company['segment']})\n"
    
    # Add sales team information
    if sales_team:
        prompt += "\nSALES TEAM ROLES:\n"
        for rep in sales_team:
            prompt += f"- {rep['role']} (Rank: {rep.get('rank', 'N/A')})\n"
            prompt += f"  Target Personas: {', '.join(rep['target_personas'])}\n"
            prompt += f"  Strengths: {', '.join(rep['strengths'])}\n"
            prompt += f"  Tier Focus: {rep.get('tier_focus', 'All')}\n"
        
        prompt += "\nREP ASSIGNMENTS:\n"
        for company_name, assigned_roles in rep_assignments.items():
            prompt += f"- {company_name}: {', '.join(assigned_roles)}\n"
    
    # Add messaging capacity information if available
    if messaging_capacity and "daily_limits" in messaging_capacity:
        prompt += "\nMESSAGING CAPACITY BY ROLE:\n"
        for role, limits in messaging_capacity["daily_limits"].items():
            prompt += f"- {role}:\n"
            prompt += f"  Automated emails per day: {limits['automated_emails_per_day']}\n"
            prompt += f"  Custom emails per day: {limits['custom_emails_per_day']}\n"
            prompt += f"  LinkedIn messages per day: {limits['linkedin_messages_per_day']}\n"
    
    # Add messaging workload information if calculated
    if messaging_workload:
        prompt += "\nMESSAGING WORKLOAD:\n"
        for role, workload in messaging_workload.items():
            prompt += f"- {role}:\n"
            prompt += f"  Total accounts: {workload['total_accounts']}\n"
            prompt += f"  Daily automated emails: {workload['daily_automated_emails']}\n"
            prompt += f"  Daily custom emails: {workload['daily_custom_emails']}\n"
            prompt += f"  Daily LinkedIn messages: {workload['daily_linkedin_messages']}\n"
            prompt += f"  Capacity utilization: {workload['capacity_utilization_percentage']}%\n"
    
    prompt += """
    INCLUDE THE FOLLOWING SECTIONS:
    1. Campaign Overview
    2. Tiering Strategy
    3. Weekly Execution Plan (table format)
    4. Omni-Channel Sequence Structure (day-by-day)
    5. Tier-Specific Email Templates
    6. Target Contacts Per Company
    7. Success Metrics
    8. Initial Company Assignments (by tier)
    9. Sales Rep Role Assignments (who is responsible for each company/contact)
    10. Messaging Volume Strategy (email and LinkedIn messaging rates by role)
    11. Workload Distribution
    12. Next Steps
    
    FORMAT:
    - Use proper markdown formatting with headers, bullet points, tables
    - Make it visually organized and easy to read
    - Provide specific and actionable details
    - For the Sales Rep section, include specific guidance on which buyer personas each role should target
    - For the Messaging Volume Strategy, detail how many messages each role sends by tier
    
    Generate the complete markdown file that can be used as a comprehensive campaign outline.
    """
    
    # Set OpenAI API key
    openai.api_key = api_key
    
    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert sales operations strategist who creates detailed outbound campaign plans."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Extract markdown content
    markdown_content = response.choices[0].message.content
    
    # Write to file
    with open(output_file, "w") as file:
        file.write(markdown_content)
    
    return output_file

def generate_2_email_sequences(config: Dict) -> str:
    """Generate a markdown file with 2-email sequence examples for each tier/persona/role combination without using an API."""
    output_file = "campaigns/May2025/generated_2_email_sequences.md"
    sales_team = config["sales_team"]["sales_reps"]
    tier_count = config["tiering_settings"]["tier_count"]

    markdown_content = "# 2-Email Sequence Examples\n\nThis file contains example initial outreach and follow-up emails for different sales roles, target personas, and tiers.\n\n"

    tier_descriptions = {
        1: "High Priority (Enterprise focus, C-level, large accounts)",
        2: "Medium Priority (Growth, mid-market)",
        3: "Nurture (SMB, relationship building)"
    }

    # Email templates tailored by role
    email_templates = {
        "Enterprise Account Executive": {
            "email_1": {
                "subject": "Idea for scaling reporting at {company_name}",
                "body": """Hi {contact_name},

My name is {sender_name} from Automwrite. Given your position as {persona} at {company_name}, I thought you might be interested in a more efficient way to handle client reporting.

For large advisory firms, ensuring consistency and quality in reporting at scale is a significant challenge. We specialize in automating this process, freeing up your team for more strategic, client-facing activities.

I have a few ideas on how we could help {company_name}. Would you be open to a brief introductory call next week?

Best regards,
{sender_name}
Enterprise Account Executive
"""
            },
            "email_2": {
                "subject": "Re: Idea for scaling reporting at {company_name}",
                "body": """Hi {contact_name},

Just a quick follow-up to my previous email.

A common pain point for firms of your size is the 'hidden' cost of manual, repetitive work in the reporting cycle. We recently helped a similar enterprise client reduce their report generation time by over 60% while improving compliance oversight.

Here is a brief case study outlining their success: [Link to Enterprise Case Study]

Is this a priority for you at the moment?

Best,
{sender_name}
"""
            }
        },
        "Mid-Market Account Executive": {
            "email_1": {
                "subject": "Growing {company_name} with better reporting",
                "body": """Hi {contact_name},

My name is {sender_name}, and I'm with Automwrite. I'm reaching out to growth-oriented firms like yours that attended the recent EATT event.

As you scale, manual processes like report writing can become a major bottleneck. We help mid-market firms automate this, allowing your advisors to focus on winning new business and serving clients.

Given your role as {persona}, I believe our solution could be a key enabler for your next phase of growth. Do you have 15 minutes to see how it works next week?

Thanks,
{sender_name}
Mid-Market Account Executive
"""
            },
            "email_2": {
                "subject": "Re: Growing {company_name} with better reporting",
                "body": """Hi {contact_name},

Following up on my previous message.

Many firms in a growth phase don't realize how much time is lost to inefficient reporting until it's too late. Our clients typically save 5-10 hours per advisor, per week.

What could your team accomplish with that extra time?

Here's a quick video from one of our clients on how they've used that time to grow: [Link to Client Testimonial]

Worth a chat?

Best,
{sender_name}
"""
            }
        },
        "SMB Account Executive": {
            "email_1": {
                "subject": "Saving time on client reports",
                "body": """Hi {contact_name},

My name is {sender_name} from Automwrite. I saw you were at the EATT event and wanted to share a quick idea.

For busy firms like yours, time is money. We've built a straightforward tool that automates the tedious parts of client report writing, giving you more time to focus on what matters. It's easy to set up and very cost-effective.

As {persona}, I'm sure you're always looking for ways to improve efficiency. Can I show you a quick 10-minute demo?

Best,
{sender_name}
SMB Account Executive
"""
            },
            "email_2": {
                "subject": "Re: Saving time on client reports",
                "body": """Hi {contact_name},

Just a quick follow-up.

Wondering if you saw my previous email? The main benefit our clients see is a quick and clear ROI. For a small investment, they get hours back each week.

You can see a pricing overview and an ROI calculator on our site here: [Link to Pricing/ROI Page]

Let me know if it's of interest.

Best,
{sender_name}
"""
            }
        },
        "Sales Development Representative": {
             "email_1": {
                "subject": "Quick question from the EATT event",
                "body": """Hi {contact_name},

My name is {sender_name} with Automwrite. I'm following up with a few people from the EATT event.

We're helping financial advisors and firms automate their client reporting to save a ton of time.

Is this something you handle? If so, would you be open to learning more?

Thanks,
{sender_name}
Sales Development Representative
"""
            },
            "email_2": {
                "subject": "Re: Quick question from the EATT event",
                "body": """Hi {contact_name},

Just checking if you had a moment to consider my last email.

Our tool helps advisors like you get back hours every week. Here's a 2-minute video that shows how it works: [Link to Demo Video]

If you're interested, I can connect you with one of our specialists.

Best,
{sender_name}
"""
            }
        }
    }
    
    default_templates = email_templates['Sales Development Representative'] # Fallback

    for tier in range(1, tier_count + 1):
        for rep in sales_team:
            for persona in rep.get('target_personas', []):
                if "All personas" in persona:
                    continue

                markdown_content += f"## Tier {tier}: {tier_descriptions.get(tier, 'General')}\n\n"
                markdown_content += f"**Role:** {rep['role']}\n\n"
                markdown_content += f"**Target Persona:** {persona}\n\n"

                templates = email_templates.get(rep['role'], default_templates)
                
                # --- Email 1 ---
                email_1 = templates['email_1']
                markdown_content += "### Email 1: Initial Outreach\n\n"
                markdown_content += f"**Subject:** `{email_1['subject'].format(company_name='{Company Name}')}`\n\n"
                markdown_content += "```\n"
                markdown_content += email_1['body'].format(
                    company_name="{Company Name}",
                    contact_name="{Contact First Name}",
                    sender_name="{Sender Name}",
                    persona=persona
                ).strip()
                markdown_content += "\n```\n\n"
                
                # --- Email 2 ---
                email_2 = templates['email_2']
                markdown_content += "### Email 2: Follow-up\n\n"
                markdown_content += f"**Subject:** `{email_2['subject'].format(company_name='{Company Name}')}`\n\n"
                markdown_content += "```\n"
                markdown_content += email_2['body'].format(
                    contact_name="{Contact First Name}",
                    sender_name="{Sender Name}"
                ).strip()
                markdown_content += "\n```\n\n"
                markdown_content += "---\n\n"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(markdown_content)
    
    return output_file

if __name__ == "__main__":
    config_path = "campaigns/May2025/campaign_config.json"
    config = load_config(config_path)

    output_file = generate_2_email_sequences(config)
    print(f"2-email sequence examples generated and saved to {output_file}")
