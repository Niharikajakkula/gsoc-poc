#!/usr/bin/env python3
"""
API Explorer Pipeline - Enhanced OpenAPI Parser
A robust Python script to parse OpenAPI JSON files and manage API registry with duplicate prevention.

Features:
- Prevents duplicate APIs (same name + baseUrl)
- Normalizes data (uppercase methods, clean summaries)
- Handles missing fields gracefully
- Provides detailed console output
- Sorts endpoints alphabetically
"""

import json
import os
import sys
import uuid
from datetime import datetime

# Handle Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def load_openapi_file(file_path):
    """
    Load and validate an OpenAPI JSON file.
    
    Args:
        file_path (str): Path to the OpenAPI JSON file
        
    Returns:
        dict or None: OpenAPI data if successful, None if failed
    """
    try:
        print(f"[LOAD] Loading OpenAPI file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            openapi_data = json.load(file)
        
        print(f"[LOAD] Successfully loaded OpenAPI file")
        
        # Basic validation
        if not isinstance(openapi_data, dict):
            print("[ERROR] OpenAPI file must contain a JSON object")
            return None
            
        if 'info' not in openapi_data:
            print("[ERROR] OpenAPI file missing 'info' section")
            return None
            
        return openapi_data
        
    except FileNotFoundError:
        print(f"[ERROR] File not found - {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON format - {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load OpenAPI file - {e}")
        return None


def parse_openapi(openapi_data):
    """
    Parse OpenAPI data and extract structured API information.
    
    Args:
        openapi_data (dict): Raw OpenAPI data
        
    Returns:
        dict or None: Structured API data if successful, None if failed
    """
    try:
        # Extract API name from info.title
        info = openapi_data.get('info', {})
        api_name = info.get('title', 'Unknown API').strip()
        
        if not api_name or api_name == 'Unknown API':
            print("[WARN] API name is missing or empty")
        
        # Extract base URL from servers[0].url (handle missing servers)
        servers = openapi_data.get('servers', [])
        base_url = ''
        if servers and isinstance(servers, list) and len(servers) > 0:
            base_url = servers[0].get('url', '').strip()
        
        # Extract endpoints from paths
        paths = openapi_data.get('paths', {})
        if not paths:
            print("[WARN] No paths found in OpenAPI file")
            return None
        
        endpoints = []
        
        print(f"[PARSE] Processing {len(paths)} path(s)...")
        
        for path, path_data in paths.items():
            if not isinstance(path_data, dict):
                continue
                
            # Handle multiple HTTP methods under one path
            for method, method_data in path_data.items():
                # Skip non-HTTP method keys (like parameters, summary, etc.)
                method_upper = method.upper()
                if method_upper not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    continue
                
                if not isinstance(method_data, dict):
                    continue
                
                # Extract summary/description (handle missing summary)
                summary = method_data.get('summary', '').strip()
                if not summary:
                    summary = method_data.get('description', '').strip()
                
                # Ensure summary is a string (not None or other types)
                if not isinstance(summary, str):
                    summary = ''
                
                endpoint = {
                    'path': path.strip(),
                    'method': method_upper,
                    'summary': summary
                }
                
                endpoints.append(endpoint)
        
        # Create structured output
        api_data = {
            'id': str(uuid.uuid4()),  # Unique ID for each API
            'name': api_name,
            'baseUrl': base_url,
            'endpoints': endpoints,
            'lastUpdated': datetime.now().isoformat()
        }
        
        print(f"[PARSE] Parsed API: {api_name}")
        print(f"[PARSE] Base URL: {base_url or 'Not specified'}")
        print(f"[PARSE] Found {len(endpoints)} endpoint(s)")
        
        return api_data
        
    except Exception as e:
        print(f"[ERROR] Failed to parse OpenAPI data - {e}")
        return None


def normalize_data(api_data):
    """
    Clean and normalize API data.
    
    Args:
        api_data (dict): Raw API data
        
    Returns:
        dict: Normalized API data
    """
    try:
        print("[NORM] Normalizing data...")
        
        # Ensure all required fields exist
        normalized = {
            'id': api_data.get('id', str(uuid.uuid4())),
            'name': str(api_data.get('name', 'Unknown API')).strip(),
            'baseUrl': str(api_data.get('baseUrl', '')).strip(),
            'endpoints': [],
            'lastUpdated': api_data.get('lastUpdated', datetime.now().isoformat())
        }
        
        # Normalize endpoints
        endpoints = api_data.get('endpoints', [])
        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue
                
            normalized_endpoint = {
                'path': str(endpoint.get('path', '')).strip(),
                'method': str(endpoint.get('method', 'GET')).upper(),
                'summary': str(endpoint.get('summary', '')).strip()
            }
            
            # Only add valid endpoints
            if normalized_endpoint['path'] and normalized_endpoint['method']:
                normalized['endpoints'].append(normalized_endpoint)
        
        # Sort endpoints alphabetically by path, then by method
        normalized['endpoints'].sort(key=lambda x: (x['path'], x['method']))
        
        print(f"[NORM] Normalized {len(normalized['endpoints'])} endpoint(s)")
        
        return normalized
        
    except Exception as e:
        print(f"[ERROR] Failed to normalize data - {e}")
        return api_data  # Return original data if normalization fails


def load_registry(registry_path):
    """
    Load existing registry or create empty one.
    
    Args:
        registry_path (str): Path to registry file
        
    Returns:
        list: Registry data
    """
    try:
        if os.path.exists(registry_path):
            print(f"[REG] Loading existing registry: {registry_path}")
            with open(registry_path, 'r', encoding='utf-8') as file:
                registry = json.load(file)
            
            if not isinstance(registry, list):
                print("[WARN] Registry file format invalid, creating new registry")
                return []
            
            print(f"[REG] Found {len(registry)} existing API(s) in registry")
            return registry
        else:
            print(f"[REG] Creating new registry: {registry_path}")
            return []
            
    except json.JSONDecodeError as e:
        print(f"[WARN] Registry file corrupted ({e}), creating new registry")
        return []
    except Exception as e:
        print(f"[WARN] Failed to load registry ({e}), creating new registry")
        return []


def find_existing_api(registry, api_name, base_url):
    """
    Find existing API in registry by name and baseUrl.
    
    Args:
        registry (list): Current registry
        api_name (str): API name to search for
        base_url (str): Base URL to search for
        
    Returns:
        int or None: Index of existing API, None if not found
    """
    for i, existing_api in enumerate(registry):
        if not isinstance(existing_api, dict):
            continue
            
        existing_name = existing_api.get('name', '').strip()
        existing_base_url = existing_api.get('baseUrl', '').strip()
        
        if existing_name == api_name and existing_base_url == base_url:
            return i
    
    return None


def save_to_registry(api_data, registry_path):
    """
    Save API data to registry, handling duplicates intelligently.
    
    Args:
        api_data (dict): Normalized API data
        registry_path (str): Path to registry file
        
    Returns:
        tuple: (success: bool, operation: str)
    """
    try:
        # Create registry directory if it doesn't exist
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        
        # Load existing registry
        registry = load_registry(registry_path)
        
        # Check for existing API
        api_name = api_data['name']
        base_url = api_data['baseUrl']
        existing_index = find_existing_api(registry, api_name, base_url)
        
        if existing_index is not None:
            # Update existing API
            print(f"[UPDATE] Updating existing API: {api_name}")
            
            # Keep the original ID but update other fields
            original_id = registry[existing_index].get('id')
            if original_id:
                api_data['id'] = original_id
            
            registry[existing_index] = api_data
            operation = "Updated"
        else:
            # Add new API
            print(f"[ADD] Adding new API: {api_name}")
            registry.append(api_data)
            operation = "Added"
        
        # Save updated registry
        with open(registry_path, 'w', encoding='utf-8') as file:
            json.dump(registry, file, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] {operation} API in registry: {registry_path}")
        print(f"[SAVE] Total APIs in registry: {len(registry)}")
        
        return True, operation
        
    except Exception as e:
        print(f"[ERROR] Failed to save to registry - {e}")
        return False, "Failed"


def display_summary(api_data, operation_type):
    """
    Display a summary of the parsed API.
    
    Args:
        api_data (dict): API data
        operation_type (str): "Added" or "Updated"
    """
    print(f"\n[SUMMARY] API {operation_type} Successfully:")
    print(f"   ID: {api_data.get('id', 'N/A')}")
    print(f"   Name: {api_data['name']}")
    print(f"   Base URL: {api_data['baseUrl'] or 'Not specified'}")
    print(f"   Endpoints: {len(api_data['endpoints'])}")
    print(f"   Last Updated: {api_data.get('lastUpdated', 'N/A')}")
    
    if api_data['endpoints']:
        print(f"\n[ENDPOINTS] Showing first 5:")
        for i, endpoint in enumerate(api_data['endpoints'][:5]):
            summary_text = f" - {endpoint['summary']}" if endpoint['summary'] else ""
            print(f"   {i+1}. {endpoint['method']} {endpoint['path']}{summary_text}")
        
        if len(api_data['endpoints']) > 5:
            print(f"   ... and {len(api_data['endpoints']) - 5} more endpoint(s)")


def main():
    """
    Main function to run the enhanced OpenAPI parser.
    """
    print("API Explorer Pipeline - Enhanced OpenAPI Parser")
    print("=" * 60)
    print("Features: Duplicate prevention, data normalization, error handling")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("\n[ERROR] Usage Error:")
        print("   python parser.py <openapi_file.json>")
        print("\n[EXAMPLES]")
        print("   python parser.py data/sample_openapi.json")
        print("   python parser.py data/minimal_openapi.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = "registry/apis.json"
    
    print(f"\n[INPUT] Input file: {input_file}")
    print(f"[OUTPUT] Output file: {output_file}")
    print()
    
    # Step 1: Load OpenAPI file
    openapi_data = load_openapi_file(input_file)
    if not openapi_data:
        print("[FAIL] Pipeline failed at loading stage!")
        sys.exit(1)
    
    # Step 2: Parse OpenAPI data
    api_data = parse_openapi(openapi_data)
    if not api_data:
        print("[FAIL] Pipeline failed at parsing stage!")
        sys.exit(1)
    
    # Step 3: Normalize data
    normalized_data = normalize_data(api_data)
    
    # Step 4: Save to registry
    success, operation = save_to_registry(normalized_data, output_file)
    
    if success:
        print("\n[SUCCESS] Pipeline completed successfully!")
        
        # Display summary
        display_summary(normalized_data, operation)
    else:
        print("\n[FAIL] Pipeline failed at saving stage!")
        sys.exit(1)


if __name__ == "__main__":
    main()