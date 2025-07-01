#!/usr/bin/env python3
"""
Simple Link and Route Validation Script for Flask/Jinja2 Application

This script focuses on finding the most critical template link issues.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

def main():
    """Main function to run basic link validation."""
    
    print("="*60)
    print("SIMPLE LINK VALIDATION REPORT")
    print("="*60)
    
    project_root = Path('.')
    templates_dir = project_root / 'carpool' / 'templates'
    views_dir = project_root / 'carpool' / 'views'
    
    # Extract defined routes from views
    defined_endpoints = set()
    print("\n1. EXTRACTING ROUTES FROM VIEW FILES...")
    
    for view_file in views_dir.glob('*.py'):
        if view_file.name == '__init__.py':
            continue
            
        blueprint_name = view_file.stem
        print(f"   Checking {view_file.name}...")
        
        try:
            with open(view_file, 'r') as f:
                content = f.read()
                
            # Find route decorators and function names
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '@' in line and 'route(' in line:
                    # Look for the function definition on next non-empty lines
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip().startswith('def '):
                            func_name = lines[j].strip().split('(')[0].replace('def ', '')
                            endpoint = f"{blueprint_name}.{func_name}"
                            defined_endpoints.add(endpoint)
                            break
                            
        except Exception as e:
            print(f"   Error reading {view_file}: {e}")
    
    print(f"   Found {len(defined_endpoints)} endpoints")
    
    # Extract url_for calls from templates
    print("\n2. EXTRACTING URL_FOR CALLS FROM TEMPLATES...")
    
    template_url_for_calls = {}
    url_for_pattern = re.compile(r"url_for\s*\(\s*['\"]([^'\"]+)['\"]")
    
    for template_file in templates_dir.rglob('*.html'):
        rel_path = str(template_file.relative_to(templates_dir))
        template_url_for_calls[rel_path] = []
        
        try:
            with open(template_file, 'r') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in url_for_pattern.finditer(line):
                    endpoint = match.group(1)
                    template_url_for_calls[rel_path].append((endpoint, line_num))
                    
        except Exception as e:
            print(f"   Error reading {template_file}: {e}")
    
    total_calls = sum(len(calls) for calls in template_url_for_calls.values())
    print(f"   Found {total_calls} url_for calls")
    
    # Check for missing endpoints
    print("\n3. CHECKING FOR MISSING ENDPOINTS...")
    
    missing_endpoints = set()
    valid_count = 0
    
    for template, calls in template_url_for_calls.items():
        for endpoint, line_num in calls:
            # Skip Flask's built-in static endpoint
            if endpoint == 'static':
                valid_count += 1
                continue
                
            if endpoint in defined_endpoints:
                valid_count += 1
            else:
                missing_endpoints.add(endpoint)
                print(f"   ❌ {template}:{line_num} - Missing endpoint: {endpoint}")
    
    print(f"\n4. SUMMARY:")
    print(f"   ✅ Valid url_for calls: {valid_count}")
    print(f"   ❌ Invalid url_for calls: {len(missing_endpoints)}")
    
    if missing_endpoints:
        print(f"\n5. MISSING ENDPOINTS TO IMPLEMENT:")
        for endpoint in sorted(missing_endpoints):
            if '.' in endpoint:
                blueprint, func = endpoint.split('.', 1)
                print(f"   @{blueprint}_bp.route('/{func.replace('_', '-')}')")
                print(f"   def {func}():")
                print(f"       # TODO: Implement {func}")
                print(f"       pass\n")
    
    print(f"\n6. ALL DEFINED ENDPOINTS:")
    for endpoint in sorted(defined_endpoints):
        print(f"   ✓ {endpoint}")
    
    print("\n" + "="*60)
    print("END OF REPORT")
    print("="*60)
    
    # Return exit code based on validation results
    return 0 if len(missing_endpoints) == 0 else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
