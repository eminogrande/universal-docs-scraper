#!/usr/bin/env python3
"""
Smart Mermaid Diagram Generator with Enhanced Prompts
"""

import json
import requests
from typing import List, Dict, Optional

class SmartDiagramGenerator:
    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def generate_architecture_diagram(self, structure: Dict) -> str:
        """Generate a comprehensive architecture diagram."""
        prompt = f"""Create a Mermaid graph TD diagram showing the system architecture.

Based on this structure:
- Components: {json.dumps(structure.get('components', [])[:20])}
- APIs: {len(structure.get('api_groups', {}))} API groups
- Integrations: {json.dumps(structure.get('integrations', [])[:10])}

Requirements:
1. Use clear, hierarchical layout (TD or TB)
2. Group related components in subgraphs
3. Show data flow with arrows and labels
4. Use different shapes for different component types:
   - Databases: [(Database)]
   - Services: [Service]
   - APIs: {{API}}
   - External: ((External))
5. Keep labels concise (max 3 words)
6. Use --> for connections
7. Maximum 30 nodes total

Example structure:
graph TD
    subgraph "Core System"
        API[API Gateway]
        Auth[Auth Service]
        DB[(Database)]
    end
    
    subgraph "External"
        Ext((Payment))
    end
    
    API --> Auth
    Auth --> DB
    API --> Ext

Generate a complete, valid Mermaid diagram. Output ONLY the Mermaid code, no explanations."""
        
        return self._call_llm(prompt)
    
    def generate_flow_diagram(self, flows: List[Dict]) -> str:
        """Generate a sequence diagram for the main flow."""
        if not flows:
            return ""
        
        main_flow = flows[0]
        steps = main_flow.get('steps', [])[:15]
        
        prompt = f"""Create a Mermaid sequenceDiagram for this flow: {main_flow.get('name', 'Main Flow')}

Steps in order:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(steps))}

Requirements:
1. Identify 3-5 main participants/actors
2. Show interactions between participants
3. Use proper sequence diagram syntax:
   - participant declarations
   - arrows with labels: ->> or -->>
   - activation boxes: activate/deactivate
   - notes: Note over Actor: text
   - loops/alt blocks where appropriate
4. Keep message labels concise
5. Show error handling if mentioned

Example structure:
sequenceDiagram
    participant User
    participant API
    participant Database
    
    User->>API: Request
    activate API
    API->>Database: Query
    activate Database
    Database-->>API: Result
    deactivate Database
    API-->>User: Response
    deactivate API

Generate a complete, valid Mermaid sequence diagram. Output ONLY the Mermaid code."""
        
        return self._call_llm(prompt)
    
    def generate_api_hierarchy(self, api_groups: Dict) -> str:
        """Generate an API hierarchy diagram."""
        if not api_groups:
            return ""
        
        # Prepare API data
        api_summary = []
        for group, endpoints in list(api_groups.items())[:15]:
            api_summary.append(f"{group}: {len(endpoints)} endpoints")
            for ep in endpoints[:3]:
                api_summary.append(f"  - {ep.get('method', 'GET')} {ep.get('path', '/')}")
        
        prompt = f"""Create a Mermaid graph showing the API structure hierarchically.

API Groups and endpoints:
{chr(10).join(api_summary)}

Requirements:
1. Use graph TD or TB layout
2. Show hierarchy: API Root -> Groups -> Endpoints
3. Use different shapes:
   - Root: [API]
   - Groups: [Group Name]
   - Endpoints: (GET /path) or (POST /path) etc
4. Group similar endpoints
5. Use subgraphs for major API versions if applicable
6. Color code by HTTP method if possible using class definitions
7. Maximum 40 nodes

Example:
graph TB
    API[API Root]
    API --> Users[Users API]
    API --> Orders[Orders API]
    
    Users --> U1(GET /users)
    Users --> U2(POST /users)
    Users --> U3(GET /users/:id)
    
    Orders --> O1(GET /orders)
    Orders --> O2(POST /orders)

Generate a complete, valid Mermaid diagram. Output ONLY the Mermaid code."""
        
        return self._call_llm(prompt)
    
    def generate_state_diagram(self, content: Dict) -> str:
        """Generate a state diagram for entities or workflows."""
        # Extract potential states from content
        states_prompt = f"""Based on this documentation structure, identify the main entity or workflow that has states:

Sections: {json.dumps(list(content.get('sections', {}).keys())[:20])}
API groups: {json.dumps(list(content.get('api_groups', {}).keys())[:20])}

Create a Mermaid stateDiagram-v2 showing state transitions for the main entity.

Requirements:
1. Identify 5-10 meaningful states
2. Show transitions with labels
3. Include start [*] and end states [*] where appropriate
4. Use proper syntax:
   - state "Display Name" as StateName
   - StateName --> NextState : transition label
5. Group related states if needed
6. Include conditional transitions

Example:
stateDiagram-v2
    [*] --> Created
    Created --> Processing : submit
    Processing --> Approved : approve
    Processing --> Rejected : reject
    Approved --> Completed : complete
    Rejected --> [*]
    Completed --> [*]

Generate a complete, valid Mermaid state diagram. Output ONLY the Mermaid code."""
        
        return self._call_llm(states_prompt)
    
    def generate_er_diagram(self, data_models: List[Dict]) -> str:
        """Generate an entity relationship diagram."""
        if not data_models:
            return ""
        
        models_desc = []
        for model in data_models[:15]:
            models_desc.append(f"{model['name']}: {', '.join(model.get('fields', [])[:8])}")
        
        prompt = f"""Create a Mermaid erDiagram showing data model relationships.

Data Models:
{chr(10).join(models_desc)}

Requirements:
1. Show entities with their key attributes
2. Show relationships with proper cardinality
3. Use standard ER notation:
   - ||--|| : one to one
   - ||--o{ : one to many
   - }o--o{ : many to many
4. Include relationship labels
5. Limit to most important attributes (3-5 per entity)
6. Show primary keys and foreign keys

Example:
erDiagram
    User ||--o{ Order : places
    Order ||--|{ OrderItem : contains
    Product ||--o{ OrderItem : includes
    
    User {
        int id PK
        string email
        string name
    }
    
    Order {
        int id PK
        int user_id FK
        date created_at
        string status
    }

Generate a complete, valid Mermaid ER diagram. Output ONLY the Mermaid code."""
        
        return self._call_llm(prompt)
    
    def generate_all_diagrams(self, structured_content: Dict) -> List[str]:
        """Generate all applicable diagrams for the content."""
        diagrams = []
        
        # Architecture diagram
        if structured_content.get('components') or structured_content.get('sections'):
            arch = self.generate_architecture_diagram(structured_content)
            if arch:
                diagrams.append(arch)
        
        # Flow diagram
        if structured_content.get('flows'):
            flow = self.generate_flow_diagram(structured_content.get('flows', []))
            if flow:
                diagrams.append(flow)
        
        # API hierarchy
        if structured_content.get('api_groups'):
            api = self.generate_api_hierarchy(structured_content.get('api_groups', {}))
            if api:
                diagrams.append(api)
        
        # State diagram
        if len(diagrams) < 3:
            state = self.generate_state_diagram(structured_content)
            if state:
                diagrams.append(state)
        
        # ER diagram
        if structured_content.get('data_models') and len(diagrams) < 3:
            er = self.generate_er_diagram(structured_content.get('data_models', []))
            if er:
                diagrams.append(er)
        
        return diagrams[:3]  # Return maximum 3 diagrams
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM API call."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/docscraper",
                "X-Title": "Diagram Generation",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a Mermaid diagram expert. Generate only valid Mermaid v11 code. No explanations, just code."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"LLM API error: {response.status_code}")
                return ""
            
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            # Clean up response
            import re
            # Remove markdown fences if present
            content = re.sub(r'^```(?:mermaid)?\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
            
            return content.strip()
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""