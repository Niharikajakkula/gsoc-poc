#!/usr/bin/env python3
"""
API Explorer Pipeline - Registry Manager
Handles modular registry storage, versioning, and template management.

Features:
- Modular file storage (global_index, current, search index)
- Template separation per API
- API versioning system
- Deduplication logic
- Search index generation
"""

import json
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
import shutil

class RegistryManager:
    """Manages the modular API registry system."""
    
    def __init__(self, base_path=".", registry_path="registry"):
        self.base_path = Path(base_path)
        self.registry_path = self.base_path / registry_path
        self.apis_path = self.base_path / "apis"
        self.templates_path = self.base_path / "api_templates"
        
        # Ensure directories exist
        self.registry_path.mkdir(exist_ok=True)
        self.apis_path.mkdir(exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)
    
    def generate_api_id(self, api_name, base_url):
        """Generate unique API ID from name and base URL."""
        content = f"{api_name}:{base_url}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def load_global_index(self):
        """Load the global API index."""
        index_file = self.registry_path / "global_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "metadata": {
                "version": "1.0.0",
                "lastUpdated": datetime.now().isoformat(),
                "totalAPIs": 0,
                "totalEndpoints": 0,
                "generatedBy": "API Explorer Pipeline v1.0"
            },
            "apis": []
        }
    
    def save_global_index(self, index_data):
        """Save the global API index."""
        index_file = self.registry_path / "global_index.json"
        index_data["metadata"]["lastUpdated"] = datetime.now().isoformat()
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def find_existing_api(self, api_name, base_url):
        """Find existing API by name and base URL."""
        index = self.load_global_index()
        
        for api in index["apis"]:
            if api["name"] == api_name and api["baseUrl"] == base_url:
                return api["id"]
        
        return None
    
    def save_api_spec(self, api_id, openapi_data):
        """Save OpenAPI specification for an API."""
        api_dir = self.apis_path / api_id
        api_dir.mkdir(exist_ok=True)
        
        # Save current version
        spec_file = api_dir / "openapi.json"
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_data, f, indent=2, ensure_ascii=False)
        
        # Create versioned copy
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_file = api_dir / f"v_{version}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_data, f, indent=2, ensure_ascii=False)
        
        print(f"[REGISTRY] Saved API spec: {api_id}")

    def save_api_metadata(self, api_id, api_data):
        """Save API metadata to dedicated metadata.json file."""
        api_dir = self.apis_path / api_id
        api_dir.mkdir(exist_ok=True)
        
        # Calculate endpoint count from endpoints array if not set
        endpoint_count = api_data.get("endpointCount", len(api_data.get("endpoints", [])))
        
        metadata = {
            "id": api_data.get("id"),
            "name": api_data.get("name"),
            "description": api_data.get("description", ""),
            "category": api_data.get("category", "General"),
            "tags": api_data.get("tags", []),
            "authType": api_data.get("authType", "none"),
            "authDetails": api_data.get("authDetails", {}),
            "baseUrl": api_data.get("baseUrl", ""),
            "version": api_data.get("version", "1.0.0"),
            "rating": api_data.get("rating", 4.0),
            "reviews": api_data.get("reviews", []),
            "endpointCount": endpoint_count,
            "lastUpdated": api_data.get("lastUpdated"),
            "documentation": {
                "hasExamples": True,
                "hasSchemas": True,
                "completeness": "high"
            },
            "usage": {
                "difficulty": "beginner" if api_data.get("authType") == "none" else "intermediate",
                "popularity": "high" if endpoint_count > 3 else "medium",
                "maintenance": "active"
            }
        }
        
        # Debug: Print what we're saving to metadata
        print(f"[REGISTRY] Saving metadata: category={metadata['category']}, tags={metadata['tags']}, endpoints={endpoint_count}")
        
        metadata_file = api_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"[REGISTRY] Saved API metadata: {api_id}")
    
    def save_api_templates(self, api_id, endpoints_with_templates):
        """Save templates separately for an API."""
        templates_dir = self.templates_path / api_id
        templates_dir.mkdir(exist_ok=True)
        
        templates_data = {
            "metadata": {
                "apiId": api_id,
                "generatedAt": datetime.now().isoformat(),
                "endpointCount": len(endpoints_with_templates)
            },
            "endpoints": []
        }
        
        for endpoint in endpoints_with_templates:
            if "templates" in endpoint:
                templates_data["endpoints"].append({
                    "path": endpoint["path"],
                    "method": endpoint["method"],
                    "authType": endpoint.get("authType"),
                    "templates": endpoint["templates"]
                })
        
        templates_file = templates_dir / "templates.json"
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, indent=2, ensure_ascii=False)
        
        print(f"[REGISTRY] Saved templates: {api_id} ({len(templates_data['endpoints'])} endpoints)")
    
    def add_or_update_api(self, api_data, openapi_data=None):
        """Add new API or update existing one."""
        api_name = api_data["name"]
        base_url = api_data.get("baseUrl", "")
        
        # Check for existing API
        existing_id = self.find_existing_api(api_name, base_url)
        
        if existing_id:
            api_id = existing_id
            operation = "UPDATE"
            print(f"[REGISTRY] Updating existing API: {api_name}")
        else:
            api_id = self.generate_api_id(api_name, base_url)
            operation = "ADD"
            print(f"[REGISTRY] Adding new API: {api_name} (ID: {api_id})")
        
        # Update API data with ID
        api_data["id"] = api_id
        
        # Extract and calculate endpoint count
        endpoints_with_templates = api_data.get("endpoints", [])
        endpoint_count = len(endpoints_with_templates)
        
        # Add endpoint count to api_data for metadata consistency
        api_data["endpointCount"] = endpoint_count
        
        # Save OpenAPI spec if provided
        if openapi_data:
            self.save_api_spec(api_id, openapi_data)
        
        # Save API metadata (now with correct endpointCount)
        self.save_api_metadata(api_id, api_data)
        
        # Save templates separately
        if endpoints_with_templates:
            self.save_api_templates(api_id, endpoints_with_templates)
        
        # Create clean API metadata for global registry
        clean_api_data = {
            "id": api_id,
            "name": api_data["name"],
            "baseUrl": api_data.get("baseUrl", ""),
            "authType": api_data.get("authType", "none"),
            "authDetails": api_data.get("authDetails", {}),
            "endpointCount": endpoint_count,
            "lastUpdated": datetime.now().isoformat(),
            "version": api_data.get("version", "1.0.0"),
            # CRITICAL: Include ALL enrichment fields from parser
            "description": api_data.get("description", ""),
            "category": api_data.get("category", "General"),
            "tags": api_data.get("tags", []),
            "rating": api_data.get("rating", 4.0),
            "reviews": api_data.get("reviews", [])
        }
        
        # Debug: Print what we're saving to registry
        print(f"[REGISTRY] Saving to global_index: category={clean_api_data['category']}, tags={clean_api_data['tags']}")
        
        # Update global index
        self.update_global_index(clean_api_data, operation)
        
        # Update search index
        self.update_search_index(clean_api_data, endpoints_with_templates)
        
        # Update current registry
        self.update_current_registry(clean_api_data, operation)
        
        return api_id, operation
    
    def update_global_index(self, api_data, operation):
        """Update the global API index."""
        index = self.load_global_index()
        
        if operation == "UPDATE":
            # Update existing API
            for i, api in enumerate(index["apis"]):
                if api["id"] == api_data["id"]:
                    index["apis"][i] = api_data
                    break
        else:
            # Add new API
            index["apis"].append(api_data)
        
        # Update metadata
        index["metadata"]["totalAPIs"] = len(index["apis"])
        index["metadata"]["totalEndpoints"] = sum(api.get("endpointCount", 0) for api in index["apis"])
        
        self.save_global_index(index)
    
    def update_search_index(self, api_data, endpoints):
        """Update the search index for fast lookups."""
        index_file = self.registry_path / "index.json"
        
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                search_index = json.load(f)
        else:
            search_index = {
                "searchIndex": {
                    "byName": {},
                    "byAuthType": {"none": [], "apiKey": [], "bearer": [], "oauth2": []},
                    "byMethod": {"GET": [], "POST": [], "PUT": [], "DELETE": [], "PATCH": []},
                    "tags": []
                },
                "statistics": {
                    "totalAPIs": 0,
                    "totalEndpoints": 0,
                    "authTypeDistribution": {"none": 0, "apiKey": 0, "bearer": 0, "oauth2": 0}
                }
            }
        
        api_id = api_data["id"]
        api_name = api_data["name"].lower()
        auth_type = api_data.get("authType", "none")
        
        # Update name index
        if api_name not in search_index["searchIndex"]["byName"]:
            search_index["searchIndex"]["byName"][api_name] = []
        
        # Remove existing entry if updating
        search_index["searchIndex"]["byName"][api_name] = [
            aid for aid in search_index["searchIndex"]["byName"][api_name] if aid != api_id
        ]
        search_index["searchIndex"]["byName"][api_name].append(api_id)
        
        # Update auth type index
        for auth_list in search_index["searchIndex"]["byAuthType"].values():
            if api_id in auth_list:
                auth_list.remove(api_id)
        
        if auth_type in search_index["searchIndex"]["byAuthType"]:
            search_index["searchIndex"]["byAuthType"][auth_type].append(api_id)
        
        # Update method index
        for endpoint in endpoints:
            method = endpoint.get("method", "GET")
            if method in search_index["searchIndex"]["byMethod"]:
                if api_id not in search_index["searchIndex"]["byMethod"][method]:
                    search_index["searchIndex"]["byMethod"][method].append(api_id)
        
        # Update statistics
        all_apis = self.load_global_index()["apis"]
        search_index["statistics"]["totalAPIs"] = len(all_apis)
        search_index["statistics"]["totalEndpoints"] = sum(api.get("endpointCount", 0) for api in all_apis)
        
        # Update auth distribution
        auth_dist = {"none": 0, "apiKey": 0, "bearer": 0, "oauth2": 0}
        for api in all_apis:
            auth_type = api.get("authType", "none")
            if auth_type in auth_dist:
                auth_dist[auth_type] += 1
        search_index["statistics"]["authTypeDistribution"] = auth_dist
        
        # Save updated index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, indent=2, ensure_ascii=False)
    
    def update_current_registry(self, api_data, operation):
        """Update the current processing registry."""
        current_file = self.registry_path / "current.json"
        
        if current_file.exists():
            with open(current_file, 'r', encoding='utf-8') as f:
                current = json.load(f)
        else:
            current = {
                "metadata": {
                    "lastSync": datetime.now().isoformat(),
                    "processingStatus": "ready",
                    "apiCount": 0
                },
                "recentlyProcessed": []
            }
        
        # Add to recently processed
        recent_entry = {
            "id": api_data["id"],
            "name": api_data["name"],
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep only last 50 entries
        current["recentlyProcessed"].insert(0, recent_entry)
        current["recentlyProcessed"] = current["recentlyProcessed"][:50]
        
        # Update metadata
        current["metadata"]["lastSync"] = datetime.now().isoformat()
        current["metadata"]["apiCount"] = len(self.load_global_index()["apis"])
        
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
    
    def get_api_templates(self, api_id):
        """Load templates for a specific API."""
        templates_file = self.templates_path / api_id / "templates.json"
        
        if templates_file.exists():
            with open(templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_api_spec(self, api_id):
        """Load OpenAPI specification for a specific API."""
        spec_file = self.apis_path / api_id / "openapi.json"
        
        if spec_file.exists():
            with open(spec_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def list_api_versions(self, api_id):
        """List all versions of an API."""
        api_dir = self.apis_path / api_id
        
        if not api_dir.exists():
            return []
        
        versions = []
        for file in api_dir.glob("v_*.json"):
            version_name = file.stem.replace("v_", "")
            versions.append({
                "version": version_name,
                "file": str(file),
                "created": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        
        return sorted(versions, key=lambda x: x["created"], reverse=True)
    
    def cleanup_old_versions(self, api_id, keep_versions=5):
        """Clean up old API versions, keeping only the most recent."""
        versions = self.list_api_versions(api_id)
        
        if len(versions) > keep_versions:
            for version in versions[keep_versions:]:
                os.remove(version["file"])
                print(f"[CLEANUP] Removed old version: {api_id}/{version['version']}")
    
    def get_registry_stats(self):
        """Get comprehensive registry statistics."""
        global_index = self.load_global_index()
        search_index_file = self.registry_path / "index.json"
        
        stats = {
            "totalAPIs": global_index["metadata"]["totalAPIs"],
            "totalEndpoints": global_index["metadata"]["totalEndpoints"],
            "lastUpdated": global_index["metadata"]["lastUpdated"]
        }
        
        if search_index_file.exists():
            with open(search_index_file, 'r', encoding='utf-8') as f:
                search_data = json.load(f)
                stats.update(search_data["statistics"])
        
        return stats


# Utility functions for backward compatibility
def create_registry_manager():
    """Create a registry manager instance."""
    return RegistryManager()


def migrate_old_registry(old_registry_file="registry/apis.json"):
    """Migrate old monolithic registry to new modular system."""
    if not os.path.exists(old_registry_file):
        print("[MIGRATE] No old registry found, starting fresh")
        return
    
    print("[MIGRATE] Migrating old registry to modular system...")
    
    # Load old registry
    with open(old_registry_file, 'r', encoding='utf-8') as f:
        old_apis = json.load(f)
    
    # Create registry manager
    manager = RegistryManager()
    
    # Migrate each API
    migrated_count = 0
    for api in old_apis:
        try:
            # Add to new system
            api_id, operation = manager.add_or_update_api(api)
            migrated_count += 1
            print(f"[MIGRATE] {operation}: {api.get('name', 'Unknown')} -> {api_id}")
        except Exception as e:
            print(f"[MIGRATE] Failed to migrate API {api.get('name', 'Unknown')}: {e}")
    
    # Create backup of old registry
    backup_file = f"{old_registry_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(old_registry_file, backup_file)
    print(f"[MIGRATE] Created backup: {backup_file}")
    
    print(f"[MIGRATE] Successfully migrated {migrated_count} APIs to modular system")
    
    return migrated_count


if __name__ == "__main__":
    # Run migration if called directly
    migrate_old_registry()