#!/usr/bin/env python3
"""
API Explorer Pipeline - Enhanced OpenAPI Parser
A robust Python script to parse OpenAPI JSON and YAML files and manage API registry with duplicate prevention.

Features:
- Supports both JSON and YAML OpenAPI specs
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

# Import YAML support with fallback
try:
    import yaml
    YAML_SUPPORT = True
    print("[INIT] YAML support enabled")
except ImportError:
    YAML_SUPPORT = False
    print("[WARN] YAML support disabled - install PyYAML for YAML file support")

# Handle Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def load_openapi_file(file_path):
    """
    Load and validate an OpenAPI JSON or YAML file.
    
    Args:
        file_path (str): Path to the OpenAPI JSON/YAML file
        
    Returns:
        dict or None: OpenAPI data if successful, None if failed
    """
    try:
        print(f"[LOAD] Loading OpenAPI file: {file_path}")
        
        # Determine file type by extension
        file_ext = os.path.splitext(file_path)[1].lower()
        is_yaml = file_ext in ['.yaml', '.yml']
        
        if is_yaml and not YAML_SUPPORT:
            print("[ERROR] YAML file detected but PyYAML not installed")
            print("[FIX] Run: pip install PyYAML")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            if is_yaml:
                print("[LOAD] Parsing YAML format...")
                openapi_data = yaml.safe_load(file)
            else:
                print("[LOAD] Parsing JSON format...")
                openapi_data = json.load(file)
        
        print(f"[LOAD] Successfully loaded OpenAPI file ({file_ext[1:].upper()})")
        
        # Basic validation
        if not isinstance(openapi_data, dict):
            print("[ERROR] OpenAPI file must contain a valid object")
            return None
            
        if 'info' not in openapi_data:
            print("[ERROR] OpenAPI file missing 'info' section")
            return None
            
        # Check OpenAPI version (optional but good practice)
        openapi_version = openapi_data.get('openapi') or openapi_data.get('swagger')
        if openapi_version:
            print(f"[LOAD] OpenAPI version: {openapi_version}")
            
        return openapi_data
        
    except FileNotFoundError:
        print(f"[ERROR] File not found - {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON format - {e}")
        return None
    except yaml.YAMLError as e:
        print(f"[ERROR] Invalid YAML format - {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load OpenAPI file - {e}")
        return None


def extract_auth(openapi_data, endpoint_security=None):
    """
    Extract authentication information from OpenAPI specification with priority-based selection.
    
    Args:
        openapi_data (dict): Raw OpenAPI data
        endpoint_security (list, optional): Endpoint-specific security requirements
        
    Returns:
        dict: Authentication details with authType and authDetails
    """
    try:
        print("[AUTH] Extracting authentication information...")
        
        # Default: no authentication
        auth_result = {
            'authType': 'none',
            'authDetails': {}
        }
        
        # Check if components.securitySchemes exists
        components = openapi_data.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        
        if not security_schemes:
            print("[AUTH] No security schemes found")
            return auth_result
        
        # Priority-based selection: apiKey > http > oauth2 > first available
        selected_scheme = None
        selected_name = None
        
        # Priority 1: API Key
        for name, scheme in security_schemes.items():
            if scheme.get('type', '').lower() == 'apikey':
                selected_scheme = scheme
                selected_name = name
                break
        
        # Priority 2: HTTP (Bearer)
        if not selected_scheme:
            for name, scheme in security_schemes.items():
                if scheme.get('type', '').lower() == 'http':
                    selected_scheme = scheme
                    selected_name = name
                    break
        
        # Priority 3: OAuth2
        if not selected_scheme:
            for name, scheme in security_schemes.items():
                if scheme.get('type', '').lower() == 'oauth2':
                    selected_scheme = scheme
                    selected_name = name
                    break
        
        # Fallback: First available
        if not selected_scheme:
            selected_name = list(security_schemes.keys())[0]
            selected_scheme = security_schemes[selected_name]
        
        print(f"[AUTH] Selected security scheme: {selected_name} (type: {selected_scheme.get('type', 'unknown')})")
        
        # Extract authentication details based on type
        auth_type = selected_scheme.get('type', '').lower()
        
        if auth_type == 'apikey':
            # API Key authentication
            auth_result = {
                'authType': 'apiKey',
                'authDetails': {
                    'type': 'apiKey',
                    'name': selected_scheme.get('name', 'X-API-Key'),
                    'in': selected_scheme.get('in', 'header'),
                    'schemeName': selected_name
                }
            }
            print(f"[AUTH] API Key auth: {auth_result['authDetails']['name']} in {auth_result['authDetails']['in']}")
            
        elif auth_type == 'http':
            # HTTP authentication (Bearer, Basic, etc.)
            scheme = selected_scheme.get('scheme', 'bearer').lower()
            
            # NORMALIZE: http+bearer becomes "bearer" for consistency
            if scheme == 'bearer':
                normalized_auth_type = 'bearer'
            else:
                normalized_auth_type = 'http'
            
            auth_result = {
                'authType': normalized_auth_type,
                'authDetails': {
                    'type': 'http',
                    'scheme': scheme,
                    'schemeName': selected_name
                }
            }
            
            # Add bearer format if available
            if scheme == 'bearer' and 'bearerFormat' in selected_scheme:
                auth_result['authDetails']['bearerFormat'] = selected_scheme['bearerFormat']
            
            print(f"[AUTH] HTTP auth: {scheme} (normalized to: {normalized_auth_type})")
            
        elif auth_type == 'oauth2':
            # OAuth2 authentication (basic extraction)
            flows = selected_scheme.get('flows', {})
            flow_types = list(flows.keys())
            
            auth_result = {
                'authType': 'oauth2',
                'authDetails': {
                    'type': 'oauth2',
                    'flows': flow_types,
                    'schemeName': selected_name
                }
            }
            
            # Extract first flow details for simplicity
            if flow_types:
                first_flow = flows[flow_types[0]]
                if 'authorizationUrl' in first_flow:
                    auth_result['authDetails']['authorizationUrl'] = first_flow['authorizationUrl']
                if 'tokenUrl' in first_flow:
                    auth_result['authDetails']['tokenUrl'] = first_flow['tokenUrl']
            
            print(f"[AUTH] OAuth2 auth: flows {flow_types}")
            
        else:
            print(f"[AUTH] Unsupported auth type: {auth_type}, using 'none'")
        
        return auth_result
        
    except Exception as e:
        print(f"[WARN] Failed to extract authentication - {e}")
        return {
            'authType': 'none',
            'authDetails': {}
        }


def extract_endpoint_auth(openapi_data, endpoint_security):
    """
    Extract endpoint-specific authentication with proper normalization.
    
    Args:
        openapi_data (dict): Raw OpenAPI data
        endpoint_security (list): Endpoint security requirements
        
    Returns:
        str: Normalized auth type for this endpoint or None if should use global
    """
    try:
        # CRITICAL: Check if endpoint_security exists (not None)
        if endpoint_security is None:
            return None  # No endpoint security defined, inherit global
        
        # CRITICAL: If security is empty list [], it means NO AUTH (public endpoint)
        if isinstance(endpoint_security, list) and len(endpoint_security) == 0:
            return 'none'  # Explicitly public endpoint
        
        if not isinstance(endpoint_security, list) or len(endpoint_security) == 0:
            return None
        
        # Get security schemes for reference
        components = openapi_data.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        
        if not security_schemes:
            return None
        
        # Check first security requirement
        first_requirement = endpoint_security[0] if endpoint_security else {}
        
        if not first_requirement:
            return 'none'  # Empty requirement = no auth
        
        # Get the scheme name from the requirement
        scheme_name = list(first_requirement.keys())[0] if first_requirement else None
        
        if scheme_name and scheme_name in security_schemes:
            scheme_data = security_schemes[scheme_name]
            scheme_type = scheme_data.get('type', '').lower()
            
            # NORMALIZE auth types consistently with main extraction
            if scheme_type == 'apikey':
                return 'apiKey'
            elif scheme_type == 'http':
                # CRITICAL: Check if it's bearer specifically for normalization
                http_scheme = scheme_data.get('scheme', 'bearer').lower()
                if http_scheme == 'bearer':
                    return 'bearer'  # Normalize http+bearer to "bearer"
                else:
                    return 'http'    # Keep other http schemes as "http"
            elif scheme_type == 'oauth2':
                return 'oauth2'
        
        return None
        
    except Exception as e:
        print(f"[WARN] Failed to extract endpoint auth - {e}")
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
        
        # Extract authentication information FIRST (needed for endpoint inheritance)
        auth_info = extract_auth(openapi_data)
        global_auth_type = auth_info['authType']
        
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
                
                # Check for endpoint-specific authentication with proper logic order
                endpoint_security = method_data.get('security')
                endpoint_auth_type = extract_endpoint_auth(openapi_data, endpoint_security)
                
                # CRITICAL FIX: Apply correct logic order for auth inheritance
                if endpoint_security is not None and isinstance(endpoint_security, list) and len(endpoint_security) == 0:
                    # Case 1: security: [] → Public endpoint (NO AUTH)
                    final_auth_type = 'none'
                    print(f"[AUTH] Endpoint {method_upper} {path} is public (security: [])")
                elif endpoint_auth_type is not None:
                    # Case 2: Endpoint has specific security → Use extracted auth
                    final_auth_type = endpoint_auth_type
                    print(f"[AUTH] Endpoint {method_upper} {path} has specific auth: {endpoint_auth_type}")
                else:
                    # Case 3: No endpoint security defined → Inherit global auth
                    final_auth_type = global_auth_type
                    print(f"[AUTH] Endpoint {method_upper} {path} inherits global auth: {global_auth_type}")
                
                endpoint = {
                    'path': path.strip(),
                    'method': method_upper,
                    'summary': summary,
                    'authType': final_auth_type  # ALWAYS include normalized authType
                }
                
                endpoints.append(endpoint)
        
        # Create structured output (auth_info already extracted above)
        api_data = {
            'id': str(uuid.uuid4()),  # Unique ID for each API
            'name': api_name,
            'baseUrl': base_url,
            'authType': auth_info['authType'],
            'authDetails': auth_info['authDetails'],
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
    Clean and normalize API data, ensuring all required fields exist.
    
    Args:
        api_data (dict): Raw API data
        
    Returns:
        dict: Normalized API data with guaranteed auth fields
    """
    try:
        print("[NORM] Normalizing data...")
        
        # Ensure all required fields exist with proper defaults
        normalized = {
            'id': api_data.get('id', str(uuid.uuid4())),
            'name': str(api_data.get('name', 'Unknown API')).strip(),
            'baseUrl': str(api_data.get('baseUrl', '')).strip(),
            'authType': api_data.get('authType', 'none'),  # Always ensure authType exists
            'authDetails': api_data.get('authDetails', {}),  # Always ensure authDetails exists
            'endpoints': [],
            'lastUpdated': api_data.get('lastUpdated', datetime.now().isoformat())
        }
        
        # Validate authType - ensure it's a valid value
        valid_auth_types = ['none', 'apiKey', 'http', 'bearer', 'oauth2']
        if normalized['authType'] not in valid_auth_types:
            print(f"[NORM] Invalid authType '{normalized['authType']}', defaulting to 'none'")
            normalized['authType'] = 'none'
            normalized['authDetails'] = {}
        
        # Ensure authDetails is a dict
        if not isinstance(normalized['authDetails'], dict):
            print("[NORM] Invalid authDetails format, defaulting to empty dict")
            normalized['authDetails'] = {}
        
        # Normalize endpoints
        endpoints = api_data.get('endpoints', [])
        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue
                
            # CRITICAL FIX: Always include authType for every endpoint
            normalized_endpoint = {
                'path': str(endpoint.get('path', '')).strip(),
                'method': str(endpoint.get('method', 'GET')).upper(),
                'summary': str(endpoint.get('summary', '')).strip(),
                'authType': endpoint.get('authType', normalized['authType'])  # Inherit global if missing
            }
            
            # Validate endpoint authType
            if normalized_endpoint['authType'] not in valid_auth_types:
                print(f"[NORM] Invalid endpoint authType '{normalized_endpoint['authType']}', using global")
                normalized_endpoint['authType'] = normalized['authType']
            
            # Only add valid endpoints
            if normalized_endpoint['path'] and normalized_endpoint['method']:
                normalized['endpoints'].append(normalized_endpoint)
        
        # Sort endpoints alphabetically by path, then by method
        normalized['endpoints'].sort(key=lambda x: (x['path'], x['method']))
        
        print(f"[NORM] Normalized {len(normalized['endpoints'])} endpoint(s)")
        print(f"[NORM] Auth type: {normalized['authType']}")
        
        return normalized
        
    except Exception as e:
        print(f"[ERROR] Failed to normalize data - {e}")
        # Return safe defaults if normalization fails
        return {
            'id': str(uuid.uuid4()),
            'name': 'Unknown API',
            'baseUrl': '',
            'authType': 'none',
            'authDetails': {},
            'endpoints': [],
            'lastUpdated': datetime.now().isoformat()
        }


def load_registry(registry_path):
    """
    Load existing registry or create empty one, ensuring all APIs have auth fields.
    
    Args:
        registry_path (str): Path to registry file
        
    Returns:
        list: Registry data with normalized auth fields
    """
    try:
        if os.path.exists(registry_path):
            print(f"[REG] Loading existing registry: {registry_path}")
            with open(registry_path, 'r', encoding='utf-8') as file:
                registry = json.load(file)
            
            if not isinstance(registry, list):
                print("[WARN] Registry file format invalid, creating new registry")
                return []
            
            # CRITICAL FIX: Ensure ALL APIs have auth fields before any processing
            fixed_count = 0
            for api in registry:
                if isinstance(api, dict):
                    # Force auth fields to exist with safe defaults
                    if 'authType' not in api or api['authType'] is None:
                        api['authType'] = 'none'
                        fixed_count += 1
                    if 'authDetails' not in api or not isinstance(api['authDetails'], dict):
                        api['authDetails'] = {}
                        fixed_count += 1
                    
                    # Fix endpoints missing authType (inherit from global)
                    global_auth = api.get('authType', 'none')
                    endpoints = api.get('endpoints', [])
                    for endpoint in endpoints:
                        if isinstance(endpoint, dict) and 'authType' not in endpoint:
                            endpoint['authType'] = global_auth
                            fixed_count += 1
            
            if fixed_count > 0:
                print(f"[REG] Fixed {fixed_count} missing auth field(s) in existing APIs")
                # Save the fixed registry immediately
                try:
                    with open(registry_path, 'w', encoding='utf-8') as file:
                        json.dump(registry, file, indent=2, ensure_ascii=False)
                    print(f"[REG] Saved fixed registry to {registry_path}")
                except Exception as e:
                    print(f"[WARN] Could not save fixed registry: {e}")
            
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
    print(f"   Auth Type: {api_data.get('authType', 'none')}")
    
    # Display auth details if present
    auth_details = api_data.get('authDetails', {})
    if auth_details:
        if api_data.get('authType') == 'apiKey':
            print(f"   Auth Details: {auth_details.get('name', 'N/A')} in {auth_details.get('in', 'N/A')}")
        elif api_data.get('authType') == 'http':
            print(f"   Auth Details: {auth_details.get('scheme', 'N/A')} scheme")
        elif api_data.get('authType') == 'oauth2':
            flows = auth_details.get('flows', [])
            print(f"   Auth Details: OAuth2 flows {flows}")
    
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
    print("Features: JSON/YAML support, duplicate prevention, data normalization")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("\n[ERROR] Usage Error:")
        print("   python parser.py <openapi_file>")
        print("\n[SUPPORTED FORMATS]")
        print("   JSON: .json files")
        print("   YAML: .yaml, .yml files")
        print("\n[EXAMPLES]")
        print("   python parser.py data/sample_openapi.json")
        print("   python parser.py data/petstore.yaml")
        print("   python parser.py data/minimal_openapi.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = "registry/apis.json"
    
    # Validate file extension
    file_ext = os.path.splitext(input_file)[1].lower()
    supported_extensions = ['.json', '.yaml', '.yml']
    
    if file_ext not in supported_extensions:
        print(f"\n[ERROR] Unsupported file format: {file_ext}")
        print(f"[SUPPORTED] {', '.join(supported_extensions)}")
        sys.exit(1)
    
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