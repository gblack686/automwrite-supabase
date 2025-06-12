# LinkedIn Message Templates JSON Structure Documentation

This document explains the structure and usage patterns for the `copy samples.json` file.

## Structure Overview

The JSON file contains an array of LinkedIn message templates, each with the following structure:

```json
{
  "id": 1,
  "type": "business_page_viewer",
  "title": "Template title",
  "message": "Message content with {variables}",
  "target_personas": ["Persona 1", "Persona 2"],
  "metrics": {
    "character_count": 290,
    "acceptance_rate": "25-30%",
    "follow_up_required": "Low",
    "personalization_level": "Medium"
  },
  "use_cases": [
    "Use case 1",
    "Use case 2"
  ],
  "notes": "Additional guidance"
}
```

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique identifier for the template |
| `type` | String | Category/type of the template |
| `title` | String | Descriptive title of the template |
| `message` | String | The message content with variables |
| `target_personas` | Array of strings | Buyer personas this template is designed for |
| `metrics` | Object | Performance and classification metrics |
| `use_cases` | Array of strings | Recommended usage scenarios |
| `customization_notes` | Array of strings | (Optional) Guidance for personalizing the template |
| `notes` | String | Additional context and usage guidance |

### Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `character_count` | Integer | Length of the message in characters |
| `acceptance_rate` | String | Estimated connection acceptance percentage |
| `follow_up_required` | String | Level of follow-up needed ("Low", "Medium", "High") |
| `personalization_level` | String | Amount of customization needed ("Low", "Medium", "High") |

## Template Types

| Type | Description | Best For |
|------|-------------|----------|
| `business_page_viewer` | For people who visited your company page | Warm leads, passive interest |
| `industry_professional` | For financial advisers and directors | Direct prospects, decision makers |
| `regulatory_professional` | For non-adviser industry contacts | Strategic relationships, industry intelligence |

## Personalization Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Recipient's first name | "Sarah" |
| `[specific area]` | Bracketed text to replace with specific focus area | "AI Strategy in advice" |

## Programmatic Usage Examples

### Filtering by persona

```javascript
// Find messages suitable for a particular persona
function getMessagesForPersona(persona) {
  return templates.filter(template => 
    template.target_personas.includes(persona) || 
    template.target_personas.includes("All Personas")
  );
}
```

### Personalizing messages

```javascript
// Create personalized message for a prospect
function personalizeMessage(template, prospect) {
  let message = template.message;
  
  // Replace basic variables
  message = message.replace(/\{name\}/g, prospect.firstName);
  
  // Replace bracketed content if needed
  if (prospect.focusArea && message.includes('[')) {
    message = message.replace(/\[.*?\]/g, prospect.focusArea);
  }
  
  return message;
}
```

### Selecting by message length

```javascript
// Get short messages (under 250 characters)
const shortMessages = templates.filter(t => t.metrics.character_count < 250);

// Get messages by character count range
function getMessagesByLength(minChars, maxChars) {
  return templates.filter(t => 
    t.metrics.character_count >= minChars && 
    t.metrics.character_count <= maxChars
  );
}
```

## Integration with Buyer Personas

```javascript
// Get appropriate LinkedIn template based on persona level
function getTemplateForPersona(persona) {
  if (persona.level >= 4) {
    // For enterprise-level personas
    return templates.find(t => t.type === "regulatory_professional");
  } else if (persona.level === 3) {
    // For growth-oriented mid-level personas
    return templates.find(t => t.type === "industry_professional");
  } else {
    // For independent advisers and small practices
    return templates.find(t => t.type === "business_page_viewer");
  }
}
```

## Outreach Workflow Integration

```javascript
// Plan a complete outreach sequence
function createOutreachSequence(prospect, persona) {
  const initialTemplate = getTemplateForPersona(persona);
  const initialMessage = personalizeMessage(initialTemplate, prospect);
  
  return {
    prospect: prospect.name,
    persona: persona.persona_name,
    initialMessage: initialMessage,
    followUpLevel: initialTemplate.metrics.follow_up_required,
    estimatedAcceptanceRate: initialTemplate.metrics.acceptance_rate,
    notes: initialTemplate.notes
  };
}
``` 