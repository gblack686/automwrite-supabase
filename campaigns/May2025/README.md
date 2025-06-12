# Campaign Generator

This tool generates comprehensive outbound campaign outlines using the OpenAI API. It creates tiered campaigns with customizable parameters and supports role-based sales team assignments aligned with buyer personas and messaging capacity planning.

## Setup

1. Ensure you have Python 3.6+ installed
2. Install required packages:
   ```
   pip install openai
   ```
3. Set your OpenAI API key:
   - In the `campaign_config.json` file, or
   - As an environment variable: `OPENAI_API_KEY`

## Usage

1. Modify `campaign_config.json` with your desired settings:
   - Campaign details
   - Tiering strategy and email volume settings
   - Company information
   - Sales team roles and messaging capacities
   - Workload balancing parameters

2. Run the generator:
   ```
   python campaign_generator.py
   ```

3. The generated campaign outline will be saved to the location specified in your config file.

## Configuration Options

### API Settings
- `api_key`: Your OpenAI API key
- `model`: The model to use (e.g., "gpt-4")

### Campaign Details
- `campaign_name`: Name of the campaign
- `campaign_duration_weeks`: Duration in weeks
- `sequence_length_days`: Days in outreach sequence
- `output_file`: Where to save the generated markdown

### Tiering Settings
- `tier_count`: Number of priority tiers (typically 3)
- `accounts_per_tier`: How many accounts in each tier
- `leads_per_account`: Contacts per account
- `email_volume`: Tier-specific email volume settings:
  ```json
  "email_volume": {
    "tier_1": {
      "emails_per_week": 3,
      "max_automated_percentage": 60,
      "custom_touchpoint_requirement": true
    }
  }
  ```

### Messaging Capacity
- `daily_limits`: Maximum messaging volume by role:
  ```json
  "daily_limits": {
    "Enterprise Account Executive": {
      "automated_emails_per_day": 15,
      "custom_emails_per_day": 10,
      "linkedin_messages_per_day": 8
    }
  }
  ```
- `weekly_balance`: Distribution of messages across weekdays
- `time_of_day`: Distribution of messages by time of day

### Company Data
- `company_file`: CSV file with companies (must have "Company" and "Segment" columns)
- `manual_company_list`: Manually specify companies with their segments and tiers

### Sales Team
- `sales_reps`: List of sales team roles with the following structure:
  ```json
  {
    "role": "Enterprise Account Executive", 
    "rank": 4,
    "target_personas": ["Wealth-Delegator William", "Adviser Network Founder Alastair"],
    "strengths": ["C-level relationships", "Complex deal navigation"],
    "tier_focus": 1
  }
  ```
- `intertwined_reps`: Whether to assign multiple roles to each account
- `rep_assignments`: Role assignment configuration:
  - `enabled`: Whether to use custom assignments
  - `assignment_strategy`: Method for assigning roles ("by_tier_and_persona")
  - `role_distribution`: Mapping of tiers to roles (which roles handle which tiers)
  - `custom_assignments`: Manual assignments for specific companies

### Advanced Settings
- `use_custom_tiers`: Use tiers from manual list instead of auto-assigning
- `auto_distribute_accounts`: Whether to automatically distribute accounts
- `workload_balancing`: Settings to balance work across sales team:
  ```json
  "workload_balancing": {
    "enabled": true,
    "max_accounts_per_rep": {
      "Enterprise Account Executive": 15,
      "Sales Development Representative": 50
    }
  }
  ```
- `temperature`: Controls randomness (0-1)
- `max_tokens`: Maximum output size

## Messaging Rate Calculation

The system calculates messaging workload for each role based on:

1. **Tiered Email Volume**: Different tiers receive different email volumes
   - Tier 1 (high priority): Fewer, more personalized emails (lower automation %)
   - Tier 2 (medium priority): Moderate email volume with mixed automation
   - Tier 3 (nurture): Higher volume, mostly automated emails

2. **Role-Based Capacity**: Different roles have different messaging capacities
   - Enterprise Account Executives: Lower volume (15 automated emails/day)
   - Mid-Market Account Executives: Medium volume (25 automated emails/day)
   - SMB Account Executives: Higher volume (30 automated emails/day)
   - Sales Development Representatives: Highest volume (40 automated emails/day)

3. **Workload Distribution**: The system ensures no role is overloaded by:
   - Tracking account assignments per role
   - Respecting maximum account limits
   - Calculating capacity utilization percentages

## Buyer Persona Integration

The system integrates with your buyer personas by mapping sales roles to the appropriate personas they target best:

- **Enterprise Account Executive**: Targets high-level decision makers (Wealth-Delegator William, Adviser Network Founder Alastair)
- **Mid-Market Account Executive**: Targets growing firms (Scaling Firm Sam, Growth-Oriented Olivia)
- **SMB Account Executive**: Targets smaller businesses (Efficiency-Oriented Ethan, Cost-Conscious Chris)
- **Sales Development Representative**: Handles initial outreach (Independent Adviser Emma, initial qualification)

## Example Output

The generated markdown file includes:
- Campaign overview
- Tiering strategy
- Weekly execution plan
- Sequence structure
- Tier-specific email templates aligned with buyer personas
- Contact roles per company type
- Success metrics
- Company assignments
- Role-based sales team assignments
- **Messaging volume strategy by role and tier**
- **Workload distribution and capacity utilization**
- Next steps

## Customizing Templates

To influence the content and structure of your campaign outline, modify the prompt template in the `generate_campaign_outline` function. 