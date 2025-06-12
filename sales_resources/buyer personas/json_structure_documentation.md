/*
# Buyer Personas JSON Data

This file contains structured data about buyer personas for financial advisory software.

## Structure
- Each object represents a single buyer persona
- Personas are ranked by "level" (1-5) representing business size/complexity
- Demographics, pain points, goals, and characteristics are organized for easy filtering

## Usage Examples

### Filtering by level
```javascript
const enterprisePersonas = personas.filter(p => p.level >= 4);
const individualPersonas = personas.filter(p => p.level === 1);
```

### Finding personas by characteristic
```javascript
const techSavvyPersonas = personas.filter(p => 
  p.characteristics.some(c => c.toLowerCase().includes('tech savvy'))
);
```

### Sorting personas for targeting
```javascript
// Sort by business complexity/size
const sortedBySize = [...personas].sort((a, b) => b.level - a.level);

// Group personas by location
const personasByLocation = personas.reduce((acc, p) => {
  const location = p.demographics.location;
  acc[location] = acc[location] || [];
  acc[location].push(p);
  return acc;
}, {});
```

### Creating targeted messaging
```javascript
function createMessage(persona) {
  // For cost-conscious personas, emphasize ROI
  if (persona.level <= 2) {
    return `Hi ${persona.persona_name}, see how you can save costs with our solution...`;
  }
  
  // For enterprise personas, emphasize team benefits
  if (persona.level >= 4) {
    return `Hi ${persona.persona_name}, discover how your team can improve efficiency...`;
  }
  
  // Default for growth-oriented middle tier
  return `Hi ${persona.persona_name}, scale your business with our solution...`;
}
```
*/
