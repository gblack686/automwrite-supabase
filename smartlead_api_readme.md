# SmartLead API Documentation

## Overview
SmartLead is a powerful API for email outbound automation that provides comprehensive tools for campaign management, lead management, email account management, and analytics. This documentation covers all essential endpoints and features for integrating with SmartLead.

## Base URL
```
https://api.smartlead.ai
```

## Authentication
SmartLead API uses API key authentication. Include your API key in the request headers:

```http
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits
- Standard rate limits apply (check the API documentation for current limits)
- Monitor rate limit headers in responses

## Core API Sections

### 1. Campaign Management

#### List All Campaigns
- **Endpoint**: `GET /campaigns`
- **Description**: Retrieve all campaigns associated with your account
- **Response**: Array of campaign objects with details

#### Get Campaign by ID
- **Endpoint**: `GET /campaigns/{id}`
- **Description**: Retrieve specific campaign details
- **Parameters**: Campaign ID

#### Create Campaign
- **Endpoint**: `POST /campaigns`
- **Description**: Create a new email campaign
- **Required Fields**: Campaign name, email sequences

#### Update Campaign Schedule
- **Endpoint**: `POST /campaigns/{id}/schedule`
- **Description**: Update campaign schedule settings

#### Update Campaign General Settings
- **Endpoint**: `POST /campaigns/{id}/settings`
- **Description**: Update general campaign configurations

#### Patch Campaign Status
- **Endpoint**: `PATCH /campaigns/{id}/status`
- **Description**: Start, pause, or stop campaigns

#### Delete Campaign
- **Endpoint**: `DELETE /campaigns/{id}`
- **Description**: Delete a campaign

### 2. Lead Management

#### List All Leads by Campaign ID
- **Endpoint**: `GET /campaigns/{id}/leads`
- **Description**: Get all leads in a specific campaign
- **Parameters**: Campaign ID, optional filters

#### Fetch Lead Categories
- **Endpoint**: `GET /leads/categories`
- **Description**: Get available lead categories/statuses

#### Fetch Lead by Email Address
- **Endpoint**: `GET /leads/email/{email}`
- **Description**: Search for a lead by email address

#### Add Leads to Campaign
- **Endpoint**: `POST /campaigns/{id}/leads`
- **Description**: Add new leads to a campaign
- **Body**: Array of lead objects with email and other data

#### Update Lead
- **Endpoint**: `PUT /leads/{id}`
- **Description**: Update lead information
- **Parameters**: Lead ID, updated lead data

#### Resume/Pause Lead
- **Endpoint**: `POST /campaigns/{campaign_id}/leads/{lead_id}/resume`
- **Endpoint**: `POST /campaigns/{campaign_id}/leads/{lead_id}/pause`
- **Description**: Control lead status in campaigns

#### Delete Lead
- **Endpoint**: `DELETE /campaigns/{campaign_id}/leads/{lead_id}`
- **Description**: Remove lead from campaign

#### Fetch All Leads From Entire Account
- **Endpoint**: `GET /leads`
- **Description**: Get all leads across all campaigns

#### Global Block List Management
- **Endpoint**: `POST /leads/block-list`
- **Endpoint**: `GET /leads/block-list`
- **Description**: Manage globally blocked leads/domains

### 3. Email Account Management

#### List Email Accounts per Campaign
- **Endpoint**: `GET /campaigns/{id}/email-accounts`
- **Description**: Get email accounts associated with a campaign

#### Add Email Account to Campaign
- **Endpoint**: `POST /campaigns/{id}/email-accounts`
- **Description**: Associate email account with campaign

#### Remove Email Account from Campaign
- **Endpoint**: `DELETE /campaigns/{id}/email-accounts/{account_id}`
- **Description**: Remove email account from campaign

#### Fetch All Email Accounts
- **Endpoint**: `GET /email-accounts`
- **Description**: Get all email accounts for user

#### Create Email Account
- **Endpoint**: `POST /email-accounts`
- **Description**: Add new email account
- **Required**: Email, SMTP settings, provider details

#### Update Email Account
- **Endpoint**: `PUT /email-accounts/{id}`
- **Description**: Update email account settings

#### Fetch Email Account by ID
- **Endpoint**: `GET /email-accounts/{id}`
- **Description**: Get specific email account details

#### Email Warmup Management
- **Endpoint**: `POST /email-accounts/{id}/warmup`
- **Description**: Configure email warmup settings

### 4. Campaign Statistics & Analytics

#### Fetch Campaign Statistics
- **Endpoint**: `GET /campaigns/{id}/stats`
- **Description**: Get campaign performance metrics

#### Fetch Campaign Analytics by Date Range
- **Endpoint**: `GET /campaigns/{id}/analytics`
- **Parameters**: Start date, end date
- **Description**: Get detailed analytics for specific period

#### Fetch Campaign Top Level Analytics
- **Endpoint**: `GET /campaigns/{id}/analytics/summary`
- **Description**: Get high-level campaign metrics

#### Fetch Campaign Lead Statistics
- **Endpoint**: `GET /campaigns/{id}/leads/stats`
- **Description**: Get lead-specific statistics

#### Fetch Campaign Mailbox Statistics
- **Endpoint**: `GET /campaigns/{id}/mailboxes/stats`
- **Description**: Get mailbox performance metrics

#### Fetch Warmup Stats
- **Endpoint**: `GET /email-accounts/{id}/warmup/stats`
- **Description**: Get email warmup statistics

### 5. Smart Delivery

#### Spam Testing
- **Endpoint**: `POST /smart-delivery/spam-test`
- **Description**: Test email deliverability

#### Provider Performance
- **Endpoint**: `GET /smart-delivery/providers/report`
- **Description**: Get provider-wise performance data

#### Geographic Reports
- **Endpoint**: `GET /smart-delivery/geo/report`
- **Description**: Get geographic delivery performance

#### Blacklist Monitoring
- **Endpoint**: `GET /smart-delivery/blacklists`
- **Description**: Monitor domain/IP blacklist status

### 6. Webhooks

#### Fetch Webhooks by Campaign ID
- **Endpoint**: `GET /campaigns/{id}/webhooks`
- **Description**: Get configured webhooks for campaign

#### Add/Update Campaign Webhook
- **Endpoint**: `POST /campaigns/{id}/webhooks`
- **Description**: Configure webhook for campaign events

#### Delete Campaign Webhook
- **Endpoint**: `DELETE /campaigns/{id}/webhooks/{webhook_id}`
- **Description**: Remove webhook configuration

### 7. Client Management (Whitelabel)

#### Add Client to System
- **Endpoint**: `POST /clients`
- **Description**: Add new client (whitelabel feature)

#### Fetch All Clients
- **Endpoint**: `GET /clients`
- **Description**: Get all clients

#### Client API Key Management
- **Endpoint**: `POST /clients/{id}/api-keys`
- **Endpoint**: `GET /clients/{id}/api-keys`
- **Endpoint**: `DELETE /clients/{id}/api-keys/{key_id}`
- **Description**: Manage client API keys

### 8. Global Analytics

#### Overall Statistics
- **Endpoint**: `GET /analytics/overall`
- **Description**: Get account-wide statistics

#### Day-wise Analytics
- **Endpoint**: `GET /analytics/daily`
- **Description**: Get daily performance metrics

#### Lead Response Analytics
- **Endpoint**: `GET /analytics/leads/response`
- **Description**: Get lead response analytics

#### Reply Rate Analytics
- **Endpoint**: `GET /analytics/reply-rate`
- **Description**: Get reply rate statistics

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_count": 100
    }
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Detailed error message",
    "details": {}
  }
}
```

## Key Data Objects

### Campaign Object
```json
{
  "id": 123,
  "name": "Campaign Name",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "settings": {
    "daily_limit": 50,
    "time_zone": "UTC"
  }
}
```

### Lead Object
```json
{
  "id": 456,
  "email": "lead@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Example Corp",
  "status": "active",
  "campaign_id": 123,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Email Account Object
```json
{
  "id": 789,
  "email": "sender@example.com",
  "provider": "gmail",
  "status": "active",
  "warmup_enabled": true,
  "daily_limit": 50
}
```

## Best Practices

1. **Rate Limiting**: Respect API rate limits and implement exponential backoff
2. **Error Handling**: Always check response status and handle errors gracefully
3. **Pagination**: Use pagination for large datasets
4. **Webhooks**: Use webhooks for real-time updates instead of constant polling
5. **Lead Management**: Regularly clean and update lead lists
6. **Email Warmup**: Always warm up new email accounts before high-volume sending
7. **Monitoring**: Monitor deliverability and campaign performance regularly

## Common Use Cases

### 1. Setting Up a New Campaign
1. Create campaign
2. Add email accounts
3. Upload leads
4. Configure sequences
5. Set schedule
6. Start campaign

### 2. Lead List Management
1. Upload new leads
2. Check for duplicates
3. Segment leads
4. Update lead status
5. Remove unresponsive leads

### 3. Performance Monitoring
1. Fetch campaign statistics
2. Monitor email deliverability
3. Track reply rates
4. Analyze open rates
5. Review bounce rates

### 4. Account Health Monitoring
1. Check email account status
2. Monitor warmup progress
3. Review blacklist status
4. Track sender reputation

## Security Considerations

1. **API Key Security**: Store API keys securely and rotate regularly
2. **HTTPS Only**: Always use HTTPS for API requests
3. **Input Validation**: Validate all input data before sending to API
4. **Rate Limiting**: Implement client-side rate limiting
5. **Logging**: Log API interactions for debugging and audit purposes

## Support and Resources

- API Documentation: https://api.smartlead.ai/docs
- Support: Contact SmartLead support team
- Status Page: Monitor API status and uptime
- Community: SmartLead developer community

---

*Last Updated: January 2025*
*For the latest API changes, always refer to the official SmartLead API documentation*