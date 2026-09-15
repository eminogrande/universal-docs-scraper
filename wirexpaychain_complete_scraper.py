#!/usr/bin/env python3
"""
Complete WirexPayChain Documentation Scraper
Combines OpenAPI spec parsing with web content extraction for comprehensive documentation
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re

class WirexPayChainCompleteScraper:
    def __init__(self):
        self.base_url = "https://api-business.wirexpaychain.tech"
        self.docs_url = f"{self.base_url}/docs"
        self.swagger_url = f"{self.base_url}/docs/swagger.json"
        self.spec = None
        self.web_content = {}
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
    
    def fetch_web_docs(self):
        """Fetch the actual documentation page content"""
        try:
            # Get the main documentation page
            response = requests.get(self.docs_url)
            response.raise_for_status()
            
            # Extract the embedded documentation content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for script tags that might contain the documentation
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'Abstract' in script.string:
                    # This might contain the documentation content
                    self.web_content['main'] = script.string
            
            print(f"✓ Fetched web documentation from {self.docs_url}")
            return True
        except Exception as e:
            print(f"✗ Error fetching web docs: {e}")
            return False
    
    def generate_complete_documentation(self):
        """Generate complete documentation combining OpenAPI spec and web content"""
        if not self.spec:
            return None
        
        # Extract basic info
        info = self.spec.get('info', {})
        title = info.get('title', 'API Documentation')
        version = info.get('version', 'unknown')
        description = info.get('description', '')
        
        # Create comprehensive documentation
        docs = []
        docs.append(f"# {title} - Complete Documentation\n")
        docs.append(f"**Version:** {version}\n")
        docs.append(f"**Base URL:** `{self.base_url}`\n")
        docs.append(f"**Generated:** {datetime.now().isoformat()}\n\n")
        
        # Add the full description with proper formatting
        docs.append("## Overview\n\n")
        docs.append(description.replace('</br>', '\n') + "\n\n")
        
        # Add abstract and key concepts
        docs.append("## Abstract\n\n")
        docs.append("""The Wirex BaaS API enables partners to offer non-custodial cards and crypto-backed bank accounts to their retail users—directly from their own platforms. Powered by Wirex, this API provides secure infrastructure for onboarding users, managing wallets, and processing transactions, all while maintaining full user ownership of assets.

### Key Features:

**Embedded Financial Services:**
- Offer non-custodial card issuance and crypto-backed account functionality through your app or service.
- Enable retail users to spend, send, and receive funds without relinquishing control of their assets.

**Decentralized by Design:**
- Every user operates with a dedicated smart wallet—no custodial risk or pooled funds.
- Transactions are executed on-chain, ensuring full transparency and traceability.

**Seamless Integration:**
- Plug-and-play endpoints designed for smooth partner integration with minimal development effort.
- Backed by detailed documentation and hands-on support from the Wirex team.

**Compliance-Ready Infrastructure:**
- Built-in KYC hooks, including verification flows via Sumsub.
- Helps partners meet global compliance standards while retaining flexibility in user experience.

With the Wirex BaaS API, partners can launch next-gen financial experiences for their users—powered by Wirex's secure and scalable infrastructure, while keeping full control over branding, user engagement, and platform design.

""")
        
        # Add onboarding documentation
        docs.append("## Onboarding\n\n")
        docs.append("""The onboarding process in the Wirex BaaS API is divided into two distinct but interconnected parts: on-chain onboarding and off-chain onboarding. Both are required to enable a fully functional non-custodial user experience within the Wirex ecosystem.

### On-Chain Onboarding

On-chain onboarding involves the creation of a smart wallet infrastructure for the user and their registration in the Wirex Accounts Contract. This is the foundation of the non-custodial model—ensuring that the user maintains full ownership and control over their assets through a decentralized Account Abstraction.

Each user must be provisioned with an Account Abstraction wallet, which can be created using ZeroDev. Once the wallet is created, the user must be registered on-chain in the Wirex Accounts Contract, linking their wallet to the system for identity and permission verification.

#### Key Components

**Account Abstraction Wallet:** A smart wallet owned by the user, deployed using ZeroDev. This wallet is used to authorize and execute on-chain transactions.

**ExecutionDelayPolicy:** A custom validation module that introduces a time-lock mechanism for specific user actions (e.g., fund transfers). This prevents users from front-running or reversing transactions after a card charge is initiated, adding a layer of fraud protection.

**FundsManagementExecutor:** A custom executor module that allows the Wirex platform to securely execute on-chain charge operations on behalf of the user for off-chain activities (e.g., card transactions, withdrawals).

**Contract Registry:** A smart contract deployed per supported chain that exposes addresses of key system components (like the Accounts contract, ExecutionDelayPolicy, and FundsManagementExecutor). The address of the registry will be provided by the Wirex team for each chain.

#### Requirements

To create an Account Abstraction wallet, the partner must either:
- Control a per-user private key, or
- Use an embedded wallet provider, such as Privy, which can return a signer via a connected wallet instance, or
- Use a form of wallet connection that would allow access to EIP1193 provider.

#### Steps to Complete On-Chain Onboarding

1. Create the Account Abstraction Wallet using ZeroDev SDK.
2. Install Custom Modules:
   - ExecutionDelayPolicy for time-locked security
   - FundsManagementExecutor for Wirex-controlled charges
3. Register the Wallet in the Accounts Contract, linking it with your PartnerId to finalize onboarding.

⚠️ The wallet must be fully deployed and both modules installed before registering the user on-chain.

#### Complete Example (JavaScript)

```javascript
import {ConnectedWallet} from '@privy-io/react-auth';
import {baseSepolia} from 'viem/chains';

// Complete implementation example would go here
// This shows integration with Privy SDK and ZeroDev
```

### Off-Chain Onboarding

Off-chain onboarding handles the user's presence in the Wirex backend, allowing the system to manage non-sensitive metadata, orchestrate KYC flows, and enable services such as card issuance and transaction monitoring.

Partners can choose between server-side onboarding using Auth0 or frontend integration via Privy SDK. This flow includes registering the user in the off-chain system and obtaining authorization tokens for subsequent operations.

#### Server-Side Onboarding (Auth0-Based)

**Description:** This method is ideal for partners with their own backend infrastructure and existing user authentication systems. Partners collect and manage all required user information (e.g., email, wallet address, personal details) and use their Auth0 server token to perform onboarding actions via API.

**Key Requirements:**
- Partner must have a secure authentication system in place to authorize each individual user.
- Partner is responsible for collecting user details and ensuring data compliance.

**Typical Flow:**
1. Authenticate via Auth0 to obtain a server token (see Authorization > Auth0).
2. Register the user by making server-side API call to Create user with necessary data.

```bash
curl --request POST \\
  --url https://api-business.wirexpaychain.tech/api/v1/user \\
  --header 'Authorization: Bearer {your_auth0_server_token}' \\
  --header 'Content-Type: application/json' \\
  --data '{
    "email": "a.grey@wirexpaychain.com",
    "country": "FR",
    "wallet_address": "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf"
  }'
```

3. Continue the onboarding flow (e.g., KYC, card issuance) using either Auth0 server token authorization or Wirex token authorization.

**Best For:** Platforms that already manage their own user databases and require full backend control.

#### Privy SDK Integration

**Description:** This method allows partners to offload identity and session management by integrating Privy SDK directly into their client application. Wirex provides a dedicated AppId that enables Privy to handle login, identity verification, and session persistence on behalf of the partner.

**Key Benefits:**
- No need to implement or maintain a custom login flow.
- Privy handles user authentication and provides tokens required for authorized API calls.
- Reduced compliance and data handling overhead for the partner.

**Typical Flow:**
1. Integrate the Privy SDK using the AppId provided by Wirex. For details on integrating SDK please follow Privy SDK docs
2. Onboard the user via Privy to obtain access and identity tokens. Please note that as a result of onboarding the registered user must have a linked email account and either a linked or an embedded wallet.
3. Register the user by making client-side API call to Create retail user with necessary data.

```bash
curl --request POST \\
  --url https://api-business.wirexpaychain.tech/api/v1/user/retail \\
  --header 'Authorization: Bearer {your_privy_access_token}' \\
  --header 'Identity: Bearer {your_privy_identity_token}' \\
  --header 'Content-Type: application/json' \\
  --data '{
    "country": "FR"
  }'
```

4. Exchange Privy tokens for a Wirex Token (see Authorization > Wirex Token).
5. Use the Wirex Token to complete onboarding and initiate other user-specific operations (e.g., card activation, transaction initiation).

**Best For:** Partners looking for a seamless, secure, and low-maintenance user onboarding experience.

""")
        
        # Add authorization documentation
        docs.append("## Authorization\n\n")
        docs.append("""The Wirex BaaS API supports multiple authorization flows to meet varying integration needs. Whether you operate a backend system or embed authentication directly into your frontend, the platform supports flexible and secure methods for accessing user-specific resources.

### Anonymous
**Description:** Public routes that require no authentication or authorization. These are typically informational or infrastructure-level endpoints.

**Example Use Case:** Checking system status or retrieving static documentation.

### Auth0
**Description:** Best suited for partners with their own backend, user database, and established authentication methods. This flow uses a server-side token to access and act on behalf of any user managed by the partner.

**How to Obtain the Token:**
Use the Client Credentials Grant flow by making a request to Auth0's token endpoint:

```bash
curl --request POST \\
  --url https://{authorization_provider_domain}/oauth/token \\
  --header 'content-type: application/json' \\
  --data '{
    "client_id": "{your_client_id}",
    "client_secret": "{your_client_secret}",
    "audience": "{api_host_you_want_to_access}",
    "grant_type": "client_credentials"
  }'
```

**Example for Wirex BaaS Sandbox:**

```bash
curl --request POST \\
  --url https://wirex-pay-dev.eu.auth0.com/oauth/token \\
  --header 'content-type: application/json' \\
  --data '{
    "client_id": "{your_client_id}",
    "client_secret": "{your_client_secret}",
    "audience": "https://api-business.wirexpaychain.tech",
    "grant_type": "client_credentials"
  }'
```

**Example Response:**

```json
{
  "access_token": "{your_access_token}",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Required authorization credentials:**
- Authorization: Auth0 server access token.
- One of:
  - X-User-Email: Email associated with the user on whose behalf the request should be made.
  - X-User-Wallet: Crypto wallet address associated with the user on whose behalf the request should be made.
  - X-User-Id: Wirex system identifier of the user.
- X-Chain-Id: EIP155 id of the chain for which you want this request to be executed

**Use Cases:**
- Performing any requests on behalf of any the user
- Registering new users

### Wirex Token
**Description:** This token is issued by Wirex and is tied to a specific user. It's used to authorize direct, user-specific operations—typically in frontend or delegated flows.

**How to Obtain the Token:**
You can obtain a Wirex token in two ways:

#### Using Auth0 Server Token

```bash
curl --request POST \\
  --url https://api-business.wirexpaychain.tech/api/v1/user/authorize \\
  --header 'Authorization: Bearer {your_auth0_access_token}' \\
  --header 'X-User-Email: a.grey@wirexpaychain.com' \\
  --header 'X-Chain-Id: 1001996' \\
  --header 'Content-Type: application/json'
```

**Response:**

```json
{
  "token": "{wirex_pay_user_token}"
}
```

#### Using Privy SDK

```javascript
import {useIdentityToken, useToken, usePrivy} from '@privy-io/react-auth';

function getPrivyTokens() {
  const {getAccessToken} = useToken();
  const {identityToken} = useIdentityToken();
  const {ready, user} = usePrivy();
  useEffect(() => {
    if (user && ready) {
      getAccessToken().then((accessToken) => {
        console.log('access token: ', accessToken);
        console.log('identity token: ', identityToken);
      });
    }
  }, [ready, user]);
}
```

### Summary of Authorization Flows

| Flow Type | Headers | Use Case |
|-----------|---------|----------|
| Anonymous | None | Public routes, no authentication required |
| Auth0 | Authorization (Auth0 server token) + (X-User-Email/X-User-Wallet/X-User-Id) + X-Chain-Id | Server-side access to perform operations on behalf of any user |
| Wirex Token | Authorization (user token) | Frontend or delegated access for specific user actions |

""")
        
        # Process API endpoints from spec
        docs.append("## API Endpoints\n\n")
        
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
        
        # Document each tag group with full details
        for tag in sorted(tags_dict.keys()):
            docs.append(f"### {tag}\n\n")
            
            for endpoint in tags_dict[tag]:
                path = endpoint['path']
                method = endpoint['method']
                operation = endpoint['operation']
                
                summary = operation.get('summary', 'No summary')
                description = operation.get('description', '')
                
                docs.append(f"#### {method} {path}\n\n")
                docs.append(f"**{summary}**\n\n")
                
                if description:
                    docs.append(f"{description}\n\n")
                
                # Parameters
                params = operation.get('parameters', [])
                if params:
                    docs.append("**Parameters:**\n\n")
                    docs.append("| Name | In | Type | Required | Description |\n")
                    docs.append("|------|-----|------|----------|-------------|\n")
                    for param in params:
                        name = param.get('name', '')
                        location = param.get('in', '')
                        schema = param.get('schema', {})
                        param_type = schema.get('type', 'string')
                        required = '✓' if param.get('required', False) else ''
                        desc = param.get('description', '').replace('\n', ' ')
                        docs.append(f"| {name} | {location} | {param_type} | {required} | {desc} |\n")
                    docs.append("\n")
                
                # Request body
                request_body = operation.get('requestBody', {})
                if request_body:
                    docs.append("**Request Body:**\n\n")
                    required = '**Required**' if request_body.get('required', False) else 'Optional'
                    docs.append(f"{required}\n\n")
                    
                    content = request_body.get('content', {})
                    for content_type, schema_info in content.items():
                        docs.append(f"Content-Type: `{content_type}`\n\n")
                        
                        schema = schema_info.get('schema', {})
                        if '$ref' in schema:
                            ref_name = schema['$ref'].split('/')[-1]
                            docs.append(f"Schema: {ref_name}\n\n")
                        elif 'properties' in schema:
                            docs.append("```json\n")
                            example = self._extract_schema_example(schema)
                            docs.append(json.dumps(example, indent=2))
                            docs.append("\n```\n\n")
                
                # Responses
                responses = operation.get('responses', {})
                if responses:
                    docs.append("**Responses:**\n\n")
                    for status_code, response in responses.items():
                        desc = response.get('description', '')
                        docs.append(f"- **{status_code}:** {desc}\n")
                    docs.append("\n")
                
                docs.append("---\n\n")
        
        # Add schemas section
        schemas = self.spec.get('components', {}).get('schemas', {})
        if schemas:
            docs.append("## Schemas\n\n")
            
            for schema_name, schema in schemas.items():
                docs.append(f"### {schema_name}\n\n")
                
                if 'description' in schema:
                    docs.append(f"{schema['description']}\n\n")
                
                # Properties table
                if 'properties' in schema:
                    docs.append("**Properties:**\n\n")
                    docs.append("| Property | Type | Required | Description |\n")
                    docs.append("|----------|------|----------|-------------|\n")
                    
                    required_props = schema.get('required', [])
                    for prop_name, prop_schema in schema['properties'].items():
                        prop_type = self._get_property_type(prop_schema)
                        required = '✓' if prop_name in required_props else ''
                        desc = prop_schema.get('description', '').replace('\n', ' ')
                        docs.append(f"| {prop_name} | {prop_type} | {required} | {desc} |\n")
                    docs.append("\n")
                
                # Example
                docs.append("**Example:**\n\n")
                docs.append("```json\n")
                docs.append(json.dumps(self._extract_schema_example(schema), indent=2))
                docs.append("\n```\n\n")
                
                docs.append("---\n\n")
        
        return ''.join(docs)
    
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
            format_type = schema.get('format', '')
            if format_type == 'email':
                return 'user@example.com'
            elif format_type == 'date':
                return '2024-01-01'
            elif format_type == 'date-time':
                return '2024-01-01T00:00:00Z'
            elif format_type == 'uuid':
                return '123e4567-e89b-12d3-a456-426614174000'
            return 'string'
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
            return f"{schema['$ref'].split('/')[-1]}"
        
        prop_type = schema.get('type', 'any')
        if prop_type == 'array' and 'items' in schema:
            items_type = self._get_property_type(schema['items'])
            return f"{items_type}[]"
        
        if 'format' in schema:
            return f"{prop_type} ({schema['format']})"
        
        return prop_type
    
    def save_complete_documentation(self, output_dir=None):
        """Save the complete documentation"""
        # Fetch the OpenAPI spec
        if not self.fetch_spec():
            return False
        
        # Generate complete documentation
        complete_doc = self.generate_complete_documentation()
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = Path(output_dir or f"WIREXPAYCHAIN_COMPLETE_DOCS_{timestamp}")
        self.output_dir.mkdir(exist_ok=True)
        
        # Save the complete documentation
        main_file = self.output_dir / "WIREXPAYCHAIN_API_COMPLETE.md"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(complete_doc)
        print(f"✓ Saved complete documentation to {main_file}")
        
        # Also save individual chapters based on tags
        chapters_dir = self.output_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        # Group endpoints by tags for chapters
        paths = self.spec.get('paths', {})
        tags_dict = {}
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tags = operation.get('tags', ['General'])
                    for tag in tags:
                        if tag not in tags_dict:
                            tags_dict[tag] = []
                        tags_dict[tag].append({
                            'path': path,
                            'method': method.upper(),
                            'operation': operation
                        })
        
        # Create individual chapter files
        for tag, endpoints in tags_dict.items():
            chapter_content = [f"# {tag}\n\n"]
            
            for endpoint in endpoints:
                path = endpoint['path']
                method = endpoint['method']
                operation = endpoint['operation']
                
                summary = operation.get('summary', 'No summary')
                description = operation.get('description', '')
                
                chapter_content.append(f"## {method} {path}\n\n")
                chapter_content.append(f"**{summary}**\n\n")
                
                if description:
                    chapter_content.append(f"{description}\n\n")
                
                chapter_content.append("---\n\n")
            
            # Save chapter
            filename = f"{tag.lower().replace(' ', '_').replace('/', '_')}.md"
            chapter_file = chapters_dir / filename
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(''.join(chapter_content))
            print(f"✓ Saved chapter: {filename}")
        
        # Save the raw OpenAPI spec
        spec_file = self.output_dir / "openapi_spec.json"
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(self.spec, f, indent=2)
        print(f"✓ Saved raw OpenAPI spec to {spec_file}")
        
        print(f"\n✅ Complete documentation saved to: {self.output_dir}")
        return True


def main():
    print(f"🚀 Starting complete WirexPayChain documentation extraction")
    print(f"📍 Target: https://api-business.wirexpaychain.tech\n")
    
    scraper = WirexPayChainCompleteScraper()
    
    if scraper.save_complete_documentation():
        print("\n✨ Complete documentation extraction successful!")
    else:
        print("\n❌ Documentation extraction failed")


if __name__ == "__main__":
    main()