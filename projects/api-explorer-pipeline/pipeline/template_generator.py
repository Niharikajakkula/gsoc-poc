#!/usr/bin/env python3
"""
API Explorer Pipeline - Template Generator
Generates ready-to-use curl command templates for every API endpoint in the registry.

Features:
- Generates curl commands with proper authentication headers
- Handles path parameters (replaces {id} with sample values)
- Adds Content-Type headers for POST/PUT requests
- Includes sample request bodies for data methods
- Supports all authentication types: apiKey, bearer, oauth2, none
"""

import json
import os
import sys
import re
from datetime import datetime

# Handle Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def replace_path_parameters(path):
    """
    Replace path parameters with sample values.
    
    Args:
        path (str): API path with parameters like /pets/{petId}
        
    Returns:
        str: Path with sample values like /pets/123
    """
    # Common parameter replacements
    replacements = {
        'id': '123',
        'petId': '123', 
        'userId': '456',
        'orderId': '789',
        'productId': '101',
        'categoryId': '202',
        'itemId': '303',
        'accountId': '404',
        'customerId': '505'
    }
    
    # Replace {parameter} with sample values
    def replace_param(match):
        param_name = match.group(1)
        # Use specific replacement if available, otherwise use generic number
        return replacements.get(param_name, '123')
    
    # Pattern to match {parameterName}
    pattern = r'\{([^}]+)\}'
    result = re.sub(pattern, replace_param, path)
    
    return result


def generate_auth_header(auth_type, auth_details):
    """
    Generate authentication header based on auth type and details.
    
    Args:
        auth_type (str): Type of authentication
        auth_details (dict): Authentication details
        
    Returns:
        str: Authentication header string or empty string
    """
    try:
        if auth_type == 'apiKey':
            # API Key authentication
            key_name = auth_details.get('name', 'X-API-Key')
            key_location = auth_details.get('in', 'header')
            
            if key_location == 'header':
                return f'-H "{key_name}: YOUR_API_KEY"'
            elif key_location == 'query':
                # Note: Query params would be handled in URL, but we'll note it in header for clarity
                return f'# Add ?{key_name}=YOUR_API_KEY to URL'
            
        elif auth_type == 'bearer':
            # Bearer token authentication
            return '-H "Authorization: Bearer YOUR_TOKEN"'
            
        elif auth_type == 'http':
            # Generic HTTP authentication (fallback)
            scheme = auth_details.get('scheme', 'bearer')
            if scheme == 'bearer':
                return '-H "Authorization: Bearer YOUR_TOKEN"'
            else:
                return f'-H "Authorization: {scheme.title()} YOUR_CREDENTIALS"'
                
        elif auth_type == 'oauth2':
            # OAuth2 authentication (uses bearer token)
            return '-H "Authorization: Bearer YOUR_OAUTH_TOKEN"'
            
        elif auth_type == 'none':
            # No authentication required
            return ''
            
        else:
            # Unknown auth type
            return f'# Unknown auth type: {auth_type}'
            
    except Exception as e:
        print(f"[WARN] Failed to generate auth header for {auth_type}: {e}")
        return ''
    
    return ''


def generate_powershell_template(endpoint, api):
    """
    Generate a PowerShell Invoke-RestMethod command template for a single endpoint.
    
    Args:
        endpoint (dict): Endpoint information
        api (dict): API information
        
    Returns:
        str: Complete PowerShell command template
    """
    try:
        # Extract basic information
        method = endpoint.get('method', 'GET').upper()
        path = endpoint.get('path', '/')
        endpoint_auth_type = endpoint.get('authType', api.get('authType', 'none'))
        
        # Build full URL
        base_url = api.get('baseUrl', '').rstrip('/')
        if not base_url:
            base_url = 'https://api.example.com'  # Fallback URL
        
        # Replace path parameters with sample values
        processed_path = replace_path_parameters(path)
        full_url = f"{base_url}{processed_path}"
        
        # Start building PowerShell command
        ps_lines = []
        ps_lines.append(f'Invoke-RestMethod `')
        ps_lines.append(f'  -Uri "{full_url}" `')
        ps_lines.append(f'  -Method {method} `')
        
        # Build headers hashtable
        headers = []
        
        # Add Content-Type header for data methods
        if method in ['POST', 'PUT', 'PATCH']:
            headers.append('"Content-Type" = "application/json"')
        
        # Add authentication header
        auth_details = api.get('authDetails', {})
        if endpoint_auth_type == 'apiKey':
            key_name = auth_details.get('name', 'X-API-Key')
            headers.append(f'"{key_name}" = "YOUR_API_KEY"')
        elif endpoint_auth_type in ['bearer', 'http']:
            headers.append('"Authorization" = "Bearer YOUR_TOKEN"')
        elif endpoint_auth_type == 'oauth2':
            headers.append('"Authorization" = "Bearer YOUR_OAUTH_TOKEN"')
        
        # Add headers if any exist
        if headers:
            headers_str = '; '.join(headers)
            ps_lines.append(f'  -Headers @{{{headers_str}}} `')
        
        # Add request body for data methods
        if method in ['POST', 'PUT', 'PATCH']:
            realistic_body = generate_realistic_body(method, path)
            # Escape quotes for PowerShell
            escaped_body = realistic_body.replace('"', '""')
            ps_lines.append(f'  -Body \'{escaped_body}\'')
        else:
            # Remove trailing backtick for GET/DELETE requests
            if ps_lines[-1].endswith(' `'):
                ps_lines[-1] = ps_lines[-1][:-2]
        
        # Join all lines with newlines
        template = '\n'.join(ps_lines)
        
        return template
        
    except Exception as e:
        print(f"[ERROR] Failed to generate PowerShell template for {method} {path}: {e}")
        return f'Invoke-RestMethod -Uri "ERROR_GENERATING_TEMPLATE" -Method {method}'


def generate_realistic_body(method, path):
    """
    Generate realistic request body based on endpoint path and method.
    
    Args:
        method (str): HTTP method
        path (str): API endpoint path
        
    Returns:
        str: Realistic JSON body string
    """
    # Generate context-aware sample data based on path
    if 'user' in path.lower():
        return '{\n  "name": "John Doe",\n  "email": "john@example.com"\n}'
    elif 'pet' in path.lower():
        return '{\n  "name": "Fluffy",\n  "species": "cat",\n  "age": 3\n}'
    elif 'product' in path.lower():
        return '{\n  "name": "Sample Product",\n  "price": 29.99,\n  "category": "electronics"\n}'
    elif 'order' in path.lower():
        return '{\n  "quantity": 2,\n  "productId": "123",\n  "customerEmail": "customer@example.com"\n}'
    elif method == 'POST':
        return '{\n  "name": "Sample Name",\n  "description": "Sample description"\n}'
    else:
        return '{\n  "key": "value",\n  "data": "sample_data"\n}'


def generate_templates(endpoint, api):
    """
    Generate both curl and PowerShell command templates for a single endpoint.
    
    Args:
        endpoint (dict): Endpoint information
        api (dict): API information
        
    Returns:
        dict: Templates object with curl and powershell commands
    """
    try:
        # Generate curl template (existing function)
        curl_template = generate_template(endpoint, api)
        
        # Generate PowerShell template (new function)
        powershell_template = generate_powershell_template(endpoint, api)
        
        return {
            "curl": curl_template,
            "powershell": powershell_template
        }
        
    except Exception as e:
        method = endpoint.get('method', 'GET')
        path = endpoint.get('path', '/')
        print(f"[ERROR] Failed to generate templates for {method} {path}: {e}")
        return {
            "curl": f'curl -X {method} "ERROR_GENERATING_TEMPLATE"',
            "powershell": f'Invoke-RestMethod -Uri "ERROR_GENERATING_TEMPLATE" -Method {method}'
        }


def generate_template(endpoint, api):
    """
    Generate a multi-line, readable curl command template for a single endpoint.
    
    Args:
        endpoint (dict): Endpoint information
        api (dict): API information
        
    Returns:
        str: Complete multi-line curl command template
    """
    try:
        # Extract basic information
        method = endpoint.get('method', 'GET').upper()
        path = endpoint.get('path', '/')
        endpoint_auth_type = endpoint.get('authType', api.get('authType', 'none'))
        summary = endpoint.get('summary', '')
        
        # Build full URL
        base_url = api.get('baseUrl', '').rstrip('/')
        if not base_url:
            base_url = 'https://api.example.com'  # Fallback URL
        
        # Replace path parameters with sample values
        processed_path = replace_path_parameters(path)
        full_url = f"{base_url}{processed_path}"
        
        # Start building multi-line curl command
        curl_lines = []
        curl_lines.append(f'curl -X {method} \\')
        curl_lines.append(f'  "{full_url}" \\')
        
        # Add Content-Type header for data methods
        if method in ['POST', 'PUT', 'PATCH']:
            curl_lines.append('  -H "Content-Type: application/json" \\')
        
        # Add authentication header
        auth_details = api.get('authDetails', {})
        auth_header = generate_auth_header(endpoint_auth_type, auth_details)
        if auth_header and not auth_header.startswith('#'):
            # Extract just the header part (remove -H prefix for clean formatting)
            if auth_header.startswith('-H '):
                header_content = auth_header[3:]  # Remove '-H '
                curl_lines.append(f'  -H {header_content} \\')
        
        # Add sample request body for data methods
        if method in ['POST', 'PUT', 'PATCH']:
            realistic_body = generate_realistic_body(method, path)
            curl_lines.append(f"  -d '{realistic_body}'")
        else:
            # Remove trailing backslash for GET/DELETE requests
            if curl_lines[-1].endswith(' \\'):
                curl_lines[-1] = curl_lines[-1][:-2]
        
        # Join all lines with newlines for readable multi-line format
        template = '\n'.join(curl_lines)
        
        # Add auth comment if it's a query parameter
        if auth_header and auth_header.startswith('#'):
            template += f'\n{auth_header}'
        
        return template
        
    except Exception as e:
        print(f"[ERROR] Failed to generate template for {method} {path}: {e}")
        return f'curl -X {method} "ERROR_GENERATING_TEMPLATE"'


def load_registry(registry_path):
    """
    Load the API registry from JSON file.
    
    Args:
        registry_path (str): Path to registry file
        
    Returns:
        list: Registry data or empty list if failed
    """
    try:
        if not os.path.exists(registry_path):
            print(f"[ERROR] Registry file not found: {registry_path}")
            return []
        
        print(f"[LOAD] Loading registry: {registry_path}")
        
        with open(registry_path, 'r', encoding='utf-8') as file:
            registry = json.load(file)
        
        if not isinstance(registry, list):
            print("[ERROR] Registry must be a list of APIs")
            return []
        
        print(f"[LOAD] Found {len(registry)} API(s) in registry")
        return registry
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in registry: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load registry: {e}")
        return []


def save_registry(registry, registry_path):
    """
    Save the updated registry with templates back to JSON file.
    
    Args:
        registry (list): Updated registry data
        registry_path (str): Path to registry file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"[SAVE] Saving updated registry: {registry_path}")
        
        # Create backup of original registry
        backup_path = f"{registry_path}.backup"
        if os.path.exists(registry_path):
            import shutil
            shutil.copy2(registry_path, backup_path)
            print(f"[SAVE] Created backup: {backup_path}")
        
        # Save updated registry
        with open(registry_path, 'w', encoding='utf-8') as file:
            json.dump(registry, file, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] Successfully saved registry with templates")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to save registry: {e}")
        return False


def generate_templates_for_registry(registry):
    """
    Generate templates for all endpoints in all APIs in the registry.
    
    Args:
        registry (list): List of API objects
        
    Returns:
        tuple: (updated_registry, total_templates_generated)
    """
    total_templates = 0
    
    print(f"\n[TEMPLATE] Starting template generation...")
    print("=" * 60)
    
    for api_index, api in enumerate(registry):
        if not isinstance(api, dict):
            continue
        
        api_name = api.get('name', f'API #{api_index + 1}')
        endpoints = api.get('endpoints', [])
        
        print(f"\n[API] Processing: {api_name}")
        print(f"[API] Endpoints to process: {len(endpoints)}")
        
        # Generate templates for each endpoint
        for endpoint_index, endpoint in enumerate(endpoints):
            if not isinstance(endpoint, dict):
                continue
            
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            
            # Generate both curl and PowerShell templates
            templates = generate_templates(endpoint, api)
            
            # Add templates and description to endpoint
            endpoint['templates'] = templates
            endpoint['description'] = endpoint.get('summary', 'No description available')
            total_templates += 1
            
            print(f"[TEMPLATE] Generated curl + PowerShell for {method} {path}")
    
    print(f"\n[SUMMARY] Generated {total_templates} template(s) total")
    return registry, total_templates


def main():
    """
    Main function to generate templates for all APIs in the registry.
    """
    print("API Explorer Pipeline - Template Generator")
    print("=" * 60)
    print("Generates curl command templates for all API endpoints")
    print("=" * 60)
    
    # Configuration
    registry_path = "registry/apis.json"
    
    print(f"\n[CONFIG] Registry file: {registry_path}")
    
    # Step 1: Load registry
    registry = load_registry(registry_path)
    if not registry:
        print("\n[FAIL] No APIs found in registry or failed to load!")
        sys.exit(1)
    
    # Step 2: Generate templates
    updated_registry, template_count = generate_templates_for_registry(registry)
    
    if template_count == 0:
        print("\n[WARN] No templates were generated!")
        sys.exit(1)
    
    # Step 3: Save updated registry
    success = save_registry(updated_registry, registry_path)
    
    if success:
        print(f"\n[SUCCESS] Cross-platform template generation completed!")
        print(f"[SUCCESS] Generated {template_count} template sets (curl + PowerShell)")
        print(f"[SUCCESS] Updated registry saved to: {registry_path}")
        
        # Show sample templates
        print(f"\n[SAMPLE] Example cross-platform templates:")
        sample_count = 0
        for api in updated_registry:
            if sample_count >= 2:  # Show max 2 samples for readability
                break
            for endpoint in api.get('endpoints', []):
                if sample_count >= 2:
                    break
                templates = endpoint.get('templates', {})
                if templates:
                    method = endpoint.get('method', 'GET')
                    path = endpoint.get('path', '/')
                    description = endpoint.get('description', 'No description')
                    print(f"   {method} {path} - {description}:")
                    
                    # Show curl template
                    curl_template = templates.get('curl', '')
                    if curl_template:
                        print(f"   [CURL]")
                        for line in curl_template.split('\n'):
                            print(f"   {line}")
                    
                    # Show PowerShell template
                    ps_template = templates.get('powershell', '')
                    if ps_template:
                        print(f"   [POWERSHELL]")
                        for line in ps_template.split('\n'):
                            print(f"   {line}")
                    
                    print()
                    sample_count += 1
    else:
        print("\n[FAIL] Failed to save updated registry!")
        sys.exit(1)


if __name__ == "__main__":
    main()