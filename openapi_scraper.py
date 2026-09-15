#!/usr/bin/env python3
"""
OpenAPI/Swagger Documentation Scraper
Extracts complete API documentation from OpenAPI/Swagger JSON endpoints
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import yaml

class OpenAPIScraper:
    def __init__(self, swagger_url):
        self.swagger_url = swagger_url
        self.base_url = '/'.join(swagger_url.split('/')[:3])
        self.spec = None
        self.output_dir = None
        
    def fetch_spec(self):
        """Fetch the OpenAPI/Swagger specification"""
        try:
            response = requests.get(self.swagger_url)
            response.raise_for_status()
            self.spec = response.json()
            print(f"✓ Fetched OpenAPI spec from {self.swagger_url}")
            return True
        except Exception as e:
            print(f"✗ Error fetching spec: {e}")
            return False
    
    def parse_spec(self):
        """Parse the OpenAPI spec into structured markdown"""
        if not self.spec:
            return None
        
        # Extract basic info
        info = self.spec.get('info', {})
        title = info.get('title', 'API Documentation')
        version = info.get('version', 'unknown')
        description = info.get('description', '')
        
        # Create main documentation structure
        main_doc = []
        main_doc.append(f"# {title}\n")
        main_doc.append(f"**Version:** {version}\n")
        main_doc.append(f"**Base URL:** `{self.base_url}`\n")
        main_doc.append(f"**Generated:** {datetime.now().isoformat()}\n\n")
        
        if description:
            main_doc.append(f"## Description\n\n{description}\n\n")
        
        # Parse servers
        servers = self.spec.get('servers', [])
        if servers:
            main_doc.append("## Servers\n\n")
            for server in servers:
                url = server.get('url', '')
                desc = server.get('description', '')
                main_doc.append(f"- **{desc}:** `{url}`\n")
            main_doc.append("\n")
        
        # Parse authentication
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        if security_schemes:
            main_doc.append("## Authentication\n\n")
            for name, scheme in security_schemes.items():
                main_doc.append(f"### {name}\n\n")
                main_doc.append(f"- **Type:** {scheme.get('type', 'unknown')}\n")
                if 'scheme' in scheme:
                    main_doc.append(f"- **Scheme:** {scheme['scheme']}\n")
                if 'bearerFormat' in scheme:
                    main_doc.append(f"- **Bearer Format:** {scheme['bearerFormat']}\n")
                if 'description' in scheme:
                    main_doc.append(f"- **Description:** {scheme['description']}\n")
                main_doc.append("\n")
        
        # Group endpoints by tags
        paths = self.spec.get('paths', {})
        tags_dict = {}
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    tags = operation.get('tags', ['General'])
                    for tag in tags:
                        if tag not in tags_dict:
                            tags_dict[tag] = []
                        tags_dict[tag].append({
                            'path': path,
                            'method': method.upper(),
                            'operation': operation
                        })
        
        # Generate table of contents
        main_doc.append("## Table of Contents\n\n")
        for tag in sorted(tags_dict.keys()):
            main_doc.append(f"- [{tag}](#{tag.lower().replace(' ', '-')})\n")
        main_doc.append("\n")
        
        # Document each tag group
        chapters = {}
        for tag in sorted(tags_dict.keys()):
            chapter = []
            chapter.append(f"# {tag}\n\n")
            
            # Add tag description if available
            tag_info = next((t for t in self.spec.get('tags', []) if t['name'] == tag), None)
            if tag_info and 'description' in tag_info:
                chapter.append(f"{tag_info['description']}\n\n")
            
            main_doc.append(f"## {tag}\n\n")
            
            for endpoint in tags_dict[tag]:
                path = endpoint['path']
                method = endpoint['method']
                operation = endpoint['operation']
                
                # Create anchor-friendly ID
                operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
                
                # Add to main doc with link
                summary = operation.get('summary', 'No summary')
                main_doc.append(f"### {method} {path}\n\n")
                main_doc.append(f"**{summary}**\n\n")
                
                # Add to chapter with full details
                chapter.append(f"## {method} {path}\n\n")
                chapter.append(f"**Summary:** {summary}\n\n")
                
                if 'description' in operation:
                    desc = operation['description']
                    main_doc.append(f"{desc}\n\n")
                    chapter.append(f"**Description:** {desc}\n\n")
                
                # Parameters
                params = operation.get('parameters', [])
                if params:
                    chapter.append("### Parameters\n\n")
                    chapter.append("| Name | In | Type | Required | Description |\n")
                    chapter.append("|------|-----|------|----------|-------------|\n")
                    for param in params:
                        name = param.get('name', '')
                        location = param.get('in', '')
                        schema = param.get('schema', {})
                        param_type = schema.get('type', 'string')
                        required = '✓' if param.get('required', False) else ''
                        description = param.get('description', '').replace('\n', ' ')
                        chapter.append(f"| {name} | {location} | {param_type} | {required} | {description} |\n")
                    chapter.append("\n")
                
                # Request body
                request_body = operation.get('requestBody', {})
                if request_body:
                    chapter.append("### Request Body\n\n")
                    required = '**Required**' if request_body.get('required', False) else 'Optional'
                    chapter.append(f"{required}\n\n")
                    
                    content = request_body.get('content', {})
                    for content_type, schema_info in content.items():
                        chapter.append(f"**Content-Type:** `{content_type}`\n\n")
                        
                        schema = schema_info.get('schema', {})
                        if '$ref' in schema:
                            ref_name = schema['$ref'].split('/')[-1]
                            chapter.append(f"**Schema:** [{ref_name}](#schema-{ref_name.lower()})\n\n")
                        elif 'properties' in schema:
                            chapter.append("```json\n")
                            chapter.append(json.dumps(self._extract_schema_example(schema), indent=2))
                            chapter.append("\n```\n\n")
                
                # Responses
                responses = operation.get('responses', {})
                if responses:
                    chapter.append("### Responses\n\n")
                    for status_code, response in responses.items():
                        description = response.get('description', '')
                        chapter.append(f"#### {status_code}\n\n")
                        chapter.append(f"{description}\n\n")
                        
                        content = response.get('content', {})
                        for content_type, schema_info in content.items():
                            chapter.append(f"**Content-Type:** `{content_type}`\n\n")
                            
                            schema = schema_info.get('schema', {})
                            if '$ref' in schema:
                                ref_name = schema['$ref'].split('/')[-1]
                                chapter.append(f"**Schema:** [{ref_name}](#schema-{ref_name.lower()})\n\n")
                            elif 'properties' in schema or 'items' in schema:
                                chapter.append("```json\n")
                                chapter.append(json.dumps(self._extract_schema_example(schema), indent=2))
                                chapter.append("\n```\n\n")
                
                chapter.append("---\n\n")
                main_doc.append("---\n\n")
            
            chapters[tag] = ''.join(chapter)
        
        # Add schemas/models section
        schemas = self.spec.get('components', {}).get('schemas', {})
        if schemas:
            main_doc.append("## Schemas\n\n")
            schemas_chapter = ["# Schemas\n\n"]
            
            for schema_name, schema in schemas.items():
                main_doc.append(f"### {schema_name}\n\n")
                schemas_chapter.append(f"## {schema_name}\n\n")
                
                if 'description' in schema:
                    desc = schema['description']
                    main_doc.append(f"{desc}\n\n")
                    schemas_chapter.append(f"{desc}\n\n")
                
                main_doc.append("```json\n")
                main_doc.append(json.dumps(self._extract_schema_example(schema), indent=2))
                main_doc.append("\n```\n\n")
                
                schemas_chapter.append("```json\n")
                schemas_chapter.append(json.dumps(self._extract_schema_example(schema), indent=2))
                schemas_chapter.append("\n```\n\n")
                
                # Properties table
                if 'properties' in schema:
                    schemas_chapter.append("### Properties\n\n")
                    schemas_chapter.append("| Property | Type | Required | Description |\n")
                    schemas_chapter.append("|----------|------|----------|-------------|\n")
                    
                    required_props = schema.get('required', [])
                    for prop_name, prop_schema in schema['properties'].items():
                        prop_type = self._get_property_type(prop_schema)
                        required = '✓' if prop_name in required_props else ''
                        description = prop_schema.get('description', '').replace('\n', ' ')
                        schemas_chapter.append(f"| {prop_name} | {prop_type} | {required} | {description} |\n")
                    schemas_chapter.append("\n")
                
                schemas_chapter.append("---\n\n")
            
            chapters['Schemas'] = ''.join(schemas_chapter)
        
        return ''.join(main_doc), chapters
    
    def _extract_schema_example(self, schema):
        """Extract example from schema"""
        if 'example' in schema:
            return schema['example']
        elif 'properties' in schema:
            example = {}
            for prop_name, prop_schema in schema['properties'].items():
                example[prop_name] = self._get_example_value(prop_schema)
            return example
        elif 'items' in schema:
            return [self._extract_schema_example(schema['items'])]
        elif '$ref' in schema:
            ref_path = schema['$ref'].split('/')
            if ref_path[0] == '#':
                ref_schema = self.spec
                for part in ref_path[1:]:
                    ref_schema = ref_schema.get(part, {})
                return self._extract_schema_example(ref_schema)
        return self._get_example_value(schema)
    
    def _get_example_value(self, schema):
        """Get example value for a property"""
        if 'example' in schema:
            return schema['example']
        elif 'enum' in schema:
            return schema['enum'][0]
        elif '$ref' in schema:
            return f"<{schema['$ref'].split('/')[-1]}>"
        
        prop_type = schema.get('type', 'string')
        if prop_type == 'string':
            return schema.get('format', 'string')
        elif prop_type == 'integer':
            return 0
        elif prop_type == 'number':
            return 0.0
        elif prop_type == 'boolean':
            return True
        elif prop_type == 'array':
            if 'items' in schema:
                return [self._get_example_value(schema['items'])]
            return []
        elif prop_type == 'object':
            if 'properties' in schema:
                return self._extract_schema_example(schema)
            return {}
        return None
    
    def _get_property_type(self, schema):
        """Get readable property type"""
        if '$ref' in schema:
            return f"[{schema['$ref'].split('/')[-1]}]"
        
        prop_type = schema.get('type', 'any')
        if prop_type == 'array' and 'items' in schema:
            items_type = self._get_property_type(schema['items'])
            return f"{items_type}[]"
        
        if 'format' in schema:
            return f"{prop_type} ({schema['format']})"
        
        return prop_type
    
    def save_documentation(self, output_dir=None):
        """Save the parsed documentation"""
        if not self.spec:
            print("No specification loaded")
            return False
        
        # Parse the spec
        main_doc, chapters = self.parse_spec()
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain = self.swagger_url.split('/')[2].replace('www.', '').replace(':', '_')
        self.output_dir = Path(output_dir or f"wirexpaychain_api_docs_{timestamp}")
        self.output_dir.mkdir(exist_ok=True)
        
        # Save main complete documentation
        main_file = self.output_dir / "WIREXPAYCHAIN_API_COMPLETE.md"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_doc)
        print(f"✓ Saved complete documentation to {main_file}")
        
        # Save individual chapters
        chapters_dir = self.output_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        for tag, content in chapters.items():
            # Clean filename
            filename = f"{tag.lower().replace(' ', '_').replace('/', '_')}.md"
            chapter_file = chapters_dir / filename
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Saved chapter: {filename}")
        
        # Save the raw OpenAPI spec
        spec_file = self.output_dir / "openapi_spec.json"
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(self.spec, f, indent=2)
        print(f"✓ Saved raw OpenAPI spec to {spec_file}")
        
        # Create index file
        index_file = self.output_dir / "INDEX.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# WirexPayChain API Documentation Index\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("## Files\n\n")
            f.write("- `WIREXPAYCHAIN_API_COMPLETE.md` - Complete API documentation in a single file\n")
            f.write("- `openapi_spec.json` - Raw OpenAPI specification\n")
            f.write("- `chapters/` - Individual documentation chapters\n\n")
            f.write("## Chapters\n\n")
            for tag in sorted(chapters.keys()):
                filename = f"{tag.lower().replace(' ', '_').replace('/', '_')}.md"
                f.write(f"- [{tag}](chapters/{filename})\n")
        
        print(f"\n✅ Documentation saved to: {self.output_dir}")
        return True


def main():
    # WirexPayChain API swagger URL
    swagger_url = "https://api-business.wirexpaychain.tech/docs/swagger.json"
    
    print(f"🚀 Starting OpenAPI documentation extraction")
    print(f"📍 Target: {swagger_url}\n")
    
    scraper = OpenAPIScraper(swagger_url)
    
    if scraper.fetch_spec():
        if scraper.save_documentation():
            print("\n✨ Documentation extraction complete!")
        else:
            print("\n❌ Failed to save documentation")
    else:
        print("\n❌ Failed to fetch OpenAPI specification")


if __name__ == "__main__":
    main()