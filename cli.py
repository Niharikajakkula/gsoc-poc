#!/usr/bin/env python3
"""
API Explorer Pipeline - Unified CLI
Production-level command-line interface for the API Explorer system.

Usage:
    python cli.py parse <file>              # Parse single OpenAPI file
    python cli.py batch <folder>            # Batch process folder
    python cli.py validate                  # Validate registry
    python cli.py sync                      # Sync registry
    python cli.py stats                     # Show statistics
    python cli.py serve                     # Start backend server
    python cli.py demo                      # Open demo page
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add pipeline to path
sys.path.append(str(Path(__file__).parent / "pipeline"))

def parse_single_file(file_path):
    """Parse a single OpenAPI file."""
    print(f"🔍 Parsing OpenAPI file: {file_path}")
    
    try:
        from parser import load_openapi_file, parse_openapi, normalize_data
        from template_generator import generate_templates
        from registry_manager import RegistryManager
        
        # Load and parse file
        openapi_data = load_openapi_file(file_path)
        if not openapi_data:
            print("❌ Failed to load OpenAPI file")
            return False
        
        api_data = parse_openapi(openapi_data)
        if not api_data:
            print("❌ Failed to parse OpenAPI data")
            return False
        
        normalized_data = normalize_data(api_data)
        
        # Generate templates
        for endpoint in normalized_data.get('endpoints', []):
            templates = generate_templates(endpoint, normalized_data)
            endpoint['templates'] = templates
        
        # Save to registry
        manager = RegistryManager()
        api_id, operation = manager.add_or_update_api(normalized_data, openapi_data)
        
        print(f"✅ {operation} API: {normalized_data.get('name')} -> {api_id}")
        print(f"📊 Endpoints: {len(normalized_data.get('endpoints', []))}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def batch_process(folder_path, recursive=False, clear=False):
    """Batch process OpenAPI files."""
    print(f"📁 Batch processing: {folder_path}")
    
    cmd = [sys.executable, "pipeline/batch_processor.py", folder_path]
    if recursive:
        cmd.append("--recursive")
    if clear:
        cmd.append("--clear")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Batch processing failed: {e}")
        return False

def validate_registry():
    """Validate the registry system."""
    print("🔍 Validating registry...")
    
    try:
        result = subprocess.run([sys.executable, "scripts/validate_registry.py"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Validation failed: {e}")
        return False

def sync_registry():
    """Sync the registry system."""
    print("🔄 Syncing registry...")
    
    try:
        result = subprocess.run([sys.executable, "scripts/sync_registry.py"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Sync failed: {e}")
        return False

def show_stats():
    """Show registry statistics."""
    print("📊 Registry Statistics")
    print("=" * 50)
    
    try:
        from pipeline.registry_manager import RegistryManager
        
        manager = RegistryManager()
        stats = manager.get_registry_stats()
        
        print(f"Total APIs: {stats.get('totalAPIs', 0)}")
        print(f"Total Endpoints: {stats.get('totalEndpoints', 0)}")
        print(f"Last Updated: {stats.get('lastUpdated', 'Unknown')}")
        
        # Auth distribution
        auth_dist = stats.get('authTypeDistribution', {})
        if auth_dist:
            print(f"\nAuthentication Distribution:")
            for auth_type, count in auth_dist.items():
                print(f"  {auth_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading statistics: {e}")
        return False

def start_server():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        os.chdir(backend_path)
        subprocess.run(["node", "server.js"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return True

def open_demo():
    """Open the demo page."""
    print("🎨 Opening demo page...")
    
    demo_path = Path("github_pages_demo/index.html")
    if not demo_path.exists():
        print("❌ Demo page not found")
        return False
    
    try:
        import webbrowser
        webbrowser.open(f"file://{demo_path.absolute()}")
        print("✅ Demo page opened in browser")
        return True
    except Exception as e:
        print(f"❌ Failed to open demo: {e}")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="API Explorer Pipeline - Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py parse data/sample_petstore.yaml
  python cli.py batch data/ --recursive --clear
  python cli.py validate
  python cli.py sync
  python cli.py stats
  python cli.py serve
  python cli.py demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse single OpenAPI file')
    parse_parser.add_argument('file', help='Path to OpenAPI file')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process OpenAPI files')
    batch_parser.add_argument('folder', help='Path to folder containing OpenAPI files')
    batch_parser.add_argument('--recursive', '-r', action='store_true', help='Scan recursively')
    batch_parser.add_argument('--clear', '-c', action='store_true', help='Clear registry first')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate registry integrity')
    
    # Sync command
    subparsers.add_parser('sync', help='Sync registry system')
    
    # Stats command
    subparsers.add_parser('stats', help='Show registry statistics')
    
    # Serve command
    subparsers.add_parser('serve', help='Start backend server')
    
    # Demo command
    subparsers.add_parser('demo', help='Open demo page')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 API Explorer Pipeline CLI")
    print("=" * 50)
    
    success = False
    
    if args.command == 'parse':
        success = parse_single_file(args.file)
    elif args.command == 'batch':
        success = batch_process(args.folder, args.recursive, args.clear)
    elif args.command == 'validate':
        success = validate_registry()
    elif args.command == 'sync':
        success = sync_registry()
    elif args.command == 'stats':
        success = show_stats()
    elif args.command == 'serve':
        success = start_server()
    elif args.command == 'demo':
        success = open_demo()
    
    if success:
        print("\n✅ Command completed successfully!")
    else:
        print("\n❌ Command failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()