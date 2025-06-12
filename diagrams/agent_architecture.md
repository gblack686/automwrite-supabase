# FinGraph Multi-Agent Architecture

This document outlines a minimal yet effective multi-agent architecture for the FinGraph platform, leveraging FastAPI and Model Context Protocol (MCP) tools with a focus on Supabase integration.



## Architecture Components

### FastAPI Server

- **API Endpoints**: RESTful endpoints for client applications to interact with the agent system
- **Agent Orchestrator**: Central component managing agent interactions and workflow

### Agent System

1. **Data Agent**: Manages data operations using Supabase MCP tools
   - Handles CRUD operations on structured data
   - Manages database migrations and schema updates
   - Processes database queries
   
2. **Knowledge Agent**: Builds and maintains the knowledge graph
   - Processes vector embeddings for unstructured data
   - Manages knowledge retrieval and reasoning
   - Handles semantic search and similarity operations
   
3. **Validation Agent**: Implements human-in-the-loop validation
   - Routes validation tasks to human operators
   - Processes feedback and corrections
   - Updates data based on human validation
   
4. **Analytics Agent**: Generates insights and analytics
   - Creates visualizations and reports
   - Identifies trends and patterns
   - Performs predictive analytics

### MCP Tools Integration

```python
# Example code for integrating Supabase MCP tools with FastAPI

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from mcp.tools import SupabaseTool

app = FastAPI(title="FinGraph API")

# Initialize Supabase MCP tool
supabase_tool = SupabaseTool(
    project_id=os.getenv("SUPABASE_PROJECT_ID"),
    api_key=os.getenv("SUPABASE_API_KEY")
)

# Data models
class EntityBase(BaseModel):
    name: str
    type: str
    attributes: dict

class EntityCreate(EntityBase):
    pass

class Entity(EntityBase):
    id: str
    created_at: str
    
    class Config:
        orm_mode = True

# Data Agent endpoints
@app.post("/entities/", response_model=Entity)
async def create_entity(entity: EntityCreate):
    """Data Agent: Create a new entity in the knowledge base"""
    try:
        result = await supabase_tool.execute_sql(
            project_id=os.getenv("SUPABASE_PROJECT_ID"),
            query=f"""
            INSERT INTO entities (name, type, attributes)
            VALUES ('{entity.name}', '{entity.type}', '{entity.attributes}')
            RETURNING *;
            """
        )
        return result['data'][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entities/", response_model=List[Entity])
async def get_entities(entity_type: Optional[str] = None):
    """Data Agent: Retrieve entities from the knowledge base"""
    try:
        where_clause = f"WHERE type = '{entity_type}'" if entity_type else ""
        result = await supabase_tool.execute_sql(
            project_id=os.getenv("SUPABASE_PROJECT_ID"),
            query=f"SELECT * FROM entities {where_clause};"
        )
        return result['data']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Database Schema (Supabase)

The following migrations set up the core tables using Supabase MCP tools:

```python
# Example migration code using Supabase MCP tools

async def create_initial_schema():
    # Create entities table
    await supabase_tool.apply_migration(
        project_id=os.getenv("SUPABASE_PROJECT_ID"),
        name="create_entities_table",
        query="""
        CREATE TABLE entities (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            attributes JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_entities_type ON entities(type);
        """
    )
    
    # Create relationships table
    await supabase_tool.apply_migration(
        project_id=os.getenv("SUPABASE_PROJECT_ID"),
        name="create_relationships_table",
        query="""
        CREATE TABLE relationships (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            source_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
            target_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            attributes JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(source_id, target_id, type)
        );
        
        CREATE INDEX idx_relationships_source ON relationships(source_id);
        CREATE INDEX idx_relationships_target ON relationships(target_id);
        CREATE INDEX idx_relationships_type ON relationships(type);
        """
    )
    
    # Create vector embeddings table
    await supabase_tool.apply_migration(
        project_id=os.getenv("SUPABASE_PROJECT_ID"),
        name="create_embeddings_extension",
        query="""
        -- Enable the vector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Create embeddings table
        CREATE TABLE embeddings (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
            embedding vector(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_embeddings_entity ON embeddings(entity_id);
        """
    )
```

## Deployment Strategy

1. **Docker Containers**: Each component deployed as containerized service
2. **Environment Configuration**: All sensitive information stored in environment variables
3. **API Documentation**: FastAPI auto-generates OpenAPI specification

## Implementation Steps

1. Set up Supabase project and database schema
2. Implement FastAPI server with MCP tool integration
3. Develop agent components with clearly defined responsibilities
4. Configure environment and deployment pipeline
5. Implement minimal UI for human-in-the-loop validation

This architecture provides a solid foundation for the FinGraph platform while remaining minimal and focused on the core functionality required. 