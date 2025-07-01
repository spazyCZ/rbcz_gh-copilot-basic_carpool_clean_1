#!/usr/bin/env python3
"""
Script to check if all template links match actual routes in the Flask application.
Analyzes templates for url_for() calls and verifies them against defined routes.
"""

import os
import re
import ast
import glob
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class RouteChecker:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "carpool" / "templates"
        self.views_path = self.base_path / "carpool" / "views"
        
        # Store found routes and template links
        self.defined_routes: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.template_links: List[Tuple[str, str, str]] = []  # (file, blueprint.endpoint, line)
        self.missing_routes: List[Tuple[str, str, str]] = []
        self.orphaned_routes: Set[str] = set()
        
    def extract_routes_from_views(self) -> None:
        """Extract all route definitions from view files."""
        print("🔍 Extracting routes from view files...")
        
        for view_file in self.views_path.glob("*.py"):
            if view_file.name == "__init__.py":
                continue
                
            print(f"  📄 Analyzing {view_file.name}")
            
            with open(view_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find blueprint name
            blueprint_match = re.search(r'(\w+)_bp\s*=\s*Blueprint\([\'"](\w+)[\'"]', content)
            if not blueprint_match:
                continue
                
            blueprint_var = blueprint_match.group(1)
            blueprint_name = blueprint_match.group(2)
            
            # Find route definitions
            route_pattern = rf'@{re.escape(blueprint_var)}_bp\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[[^\]]+\])?\)\s*(?:@\w+\s*)*def\s+(\w+)'
            
            for match in re.finditer(route_pattern, content, re.MULTILINE):
                route_path = match.group(1)
                function_name = match.group(2)
                endpoint = f"{blueprint_name}.{function_name}"
                
                self.defined_routes[blueprint_name][function_name].append(route_path)
                print(f"    ✓ Found route: {endpoint} -> {route_path}")
    
    def extract_template_links(self) -> None:
        """Extract all url_for() calls from template files."""
        print("\n🔍 Extracting template links...")
        
        template_files = list(self.templates_path.rglob("*.html"))
        
        for template_file in template_files:
            relative_path = template_file.relative_to(self.templates_path)
            print(f"  📄 Analyzing {relative_path}")
            
            with open(template_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Pattern to match url_for() calls
            url_for_pattern = r'url_for\([\'"]([^\'"]+)[\'"](?:,\s*[^)]+)?\)'
            
            for line_num, line in enumerate(lines, 1):
                for match in re.finditer(url_for_pattern, line):
                    endpoint = match.group(1)
                    self.template_links.append((str(relative_path), endpoint, line_num))
                    print(f"    🔗 Found link: {endpoint} (line {line_num})")
    
    def check_route_matches(self) -> None:
        """Check if template links match defined routes."""
        print("\n🔍 Checking route matches...")
        
        # Create a set of all defined endpoints
        defined_endpoints = set()
        for blueprint_name, functions in self.defined_routes.items():
            for function_name in functions.keys():
                defined_endpoints.add(f"{blueprint_name}.{function_name}")
        
        # Check each template link
        template_endpoints = set()
        for template_file, endpoint, line_num in self.template_links:
            template_endpoints.add(endpoint)
            
            if endpoint not in defined_endpoints:
                self.missing_routes.append((template_file, endpoint, line_num))
        
        # Find orphaned routes (defined but never used in templates)
        self.orphaned_routes = defined_endpoints - template_endpoints
    
    def analyze_static_links(self) -> List[Tuple[str, str, str]]:
        """Find static href links that don't use url_for()."""
        print("\n🔍 Checking for static href links...")
        
        static_links = []
        template_files = list(self.templates_path.rglob("*.html"))
        
        # Pattern to match href attributes that don't use url_for
        href_pattern = r'href=[\'"]([^\'\"]+)[\'"]'
        url_for_in_href_pattern = r'href=[\'\"]\{\{\s*url_for'
        
        for template_file in template_files:
            relative_path = template_file.relative_to(self.templates_path)
            
            with open(template_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip lines that use url_for in href
                if re.search(url_for_in_href_pattern, line):
                    continue
                
                # Find static href links
                for match in re.finditer(href_pattern, line):
                    href_value = match.group(1)
                    
                    # Skip external links, anchors, and javascript
                    if (href_value.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:')) or
                        href_value.startswith('{{') or  # Skip template variables
                        href_value in ['#', '/']):  # Skip common non-route hrefs
                        continue
                    
                    static_links.append((str(relative_path), href_value, line_num))
        
        return static_links
    
    def analyze_form_actions(self) -> List[Tuple[str, str, str]]:
        """Find form action attributes and check if they use url_for()."""
        print("\n🔍 Checking form actions...")
        
        form_actions = []
        template_files = list(self.templates_path.rglob("*.html"))
        
        # Pattern to match form action attributes
        action_pattern = r'action=[\'"]([^\'\"]+)[\'"]'
        url_for_in_action_pattern = r'action=[\'\"]\{\{\s*url_for'
        
        for template_file in template_files:
            relative_path = template_file.relative_to(self.templates_path)
            
            with open(template_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Find form tags with action
                if '<form' in line.lower() and 'action=' in line:
                    # Check if it uses url_for
                    uses_url_for = bool(re.search(url_for_in_action_pattern, line))
                    
                    for match in re.finditer(action_pattern, line):
                        action_value = match.group(1)
                        status = "✓ Uses url_for" if uses_url_for else "⚠️  Static URL"
                        form_actions.append((str(relative_path), action_value, f"line {line_num} - {status}"))
        
        return form_actions
    
    def print_summary(self) -> None:
        """Print a comprehensive summary of the analysis."""
        print("\n" + "="*80)
        print("📊 ROUTE ANALYSIS SUMMARY")
        print("="*80)
        
        # Route statistics
        total_blueprints = len(self.defined_routes)
        total_routes = sum(len(functions) for functions in self.defined_routes.values())
        total_template_links = len(self.template_links)
        
        print(f"\n📈 Statistics:")
        print(f"  • Blueprints found: {total_blueprints}")
        print(f"  • Routes defined: {total_routes}")
        print(f"  • Template links found: {total_template_links}")
        print(f"  • Missing routes: {len(self.missing_routes)}")
        print(f"  • Orphaned routes: {len(self.orphaned_routes)}")
        
        # Defined routes summary
        print(f"\n📋 Defined Routes by Blueprint:")
        for blueprint_name, functions in self.defined_routes.items():
            print(f"\n  🔷 {blueprint_name}:")
            for function_name, paths in functions.items():
                for path in paths:
                    print(f"    • {function_name} -> {path}")
        
        # Missing routes
        if self.missing_routes:
            print(f"\n❌ Missing Routes ({len(self.missing_routes)}):")
            print("   These endpoints are used in templates but not defined in views:")
            for template_file, endpoint, line_num in self.missing_routes:
                print(f"    • {endpoint}")
                print(f"      Used in: {template_file}:{line_num}")
        else:
            print(f"\n✅ No missing routes found!")
        
        # Orphaned routes
        if self.orphaned_routes:
            print(f"\n🔸 Orphaned Routes ({len(self.orphaned_routes)}):")
            print("   These routes are defined but never used in templates:")
            for endpoint in sorted(self.orphaned_routes):
                print(f"    • {endpoint}")
        else:
            print(f"\n✅ No orphaned routes found!")
        
        # Static links analysis
        static_links = self.analyze_static_links()
        if static_links:
            print(f"\n⚠️  Static href Links ({len(static_links)}):")
            print("   These links don't use url_for() and may break if routes change:")
            for template_file, href_value, line_num in static_links:
                print(f"    • {href_value}")
                print(f"      In: {template_file}:{line_num}")
        
        # Form actions analysis
        form_actions = self.analyze_form_actions()
        if form_actions:
            print(f"\n📝 Form Actions ({len(form_actions)}):")
            for template_file, action_value, status in form_actions:
                print(f"    • {action_value} - {status}")
                print(f"      In: {template_file}")
    
    def generate_fix_suggestions(self) -> None:
        """Generate suggestions for fixing found issues."""
        print("\n" + "="*80)
        print("🔧 FIX SUGGESTIONS")
        print("="*80)
        
        if self.missing_routes:
            print("\n❌ Missing Routes - Action Required:")
            
            missing_by_blueprint = defaultdict(list)
            for template_file, endpoint, line_num in self.missing_routes:
                if '.' in endpoint:
                    blueprint, function = endpoint.split('.', 1)
                    missing_by_blueprint[blueprint].append((function, template_file, line_num))
                else:
                    missing_by_blueprint['unknown'].append((endpoint, template_file, line_num))
            
            for blueprint, missing_functions in missing_by_blueprint.items():
                print(f"\n  🔷 Blueprint: {blueprint}")
                for function, template_file, line_num in missing_functions:
                    print(f"    • Add route for '{function}' function")
                    print(f"      Referenced in: {template_file}:{line_num}")
                    
                    # Suggest route pattern based on function name
                    if blueprint != 'unknown':
                        suggested_route = self._suggest_route_pattern(function, blueprint)
                        print(f"      Suggested route: @{blueprint}_bp.route('{suggested_route}')")
        
        if self.orphaned_routes:
            print(f"\n🔸 Orphaned Routes - Consider Review:")
            print("   These routes exist but aren't linked from templates.")
            print("   They might be API endpoints, redirects, or unused code.")
            for endpoint in sorted(self.orphaned_routes):
                print(f"    • {endpoint}")
        
        # Suggestions for static links
        static_links = self.analyze_static_links()
        if static_links:
            print(f"\n⚠️  Static Links - Recommended Changes:")
            print("   Consider using url_for() for these links:")
            for template_file, href_value, line_num in static_links:
                suggested_endpoint = self._suggest_endpoint_for_path(href_value)
                print(f"    • {href_value} in {template_file}:{line_num}")
                if suggested_endpoint:
                    print(f"      Suggestion: {{ url_for('{suggested_endpoint}') }}")
    
    def _suggest_route_pattern(self, function_name: str, blueprint: str) -> str:
        """Suggest a route pattern based on function name and blueprint."""
        # Common patterns based on function names
        patterns = {
            'index': '/',
            'list': '/',
            'new': '/new',
            'create': '/new',
            'edit': '/<int:id>/edit',
            'update': '/<int:id>/edit',
            'delete': '/<int:id>/delete',
            'show': '/<int:id>',
            'detail': '/<int:id>',
            'view': '/<int:id>',
        }
        
        # Check for common suffixes
        for pattern, route in patterns.items():
            if function_name.endswith(pattern) or function_name == pattern:
                if blueprint == 'main':
                    return route
                else:
                    return f'/{blueprint}{route}' if route != '/' else f'/{blueprint}'
        
        # Default pattern
        if blueprint == 'main':
            return f'/{function_name.replace("_", "-")}'
        else:
            return f'/{blueprint}/{function_name.replace("_", "-")}'
    
    def _suggest_endpoint_for_path(self, path: str) -> str:
        """Suggest an endpoint name for a static path."""
        # Simple heuristic to suggest endpoints for common paths
        path_mappings = {
            '/': 'main.index',
            '/dashboard': 'main.dashboard',
            '/login': 'auth.login',
            '/logout': 'auth.logout',
            '/register': 'auth.register',
            '/profile': 'main.profile',
            '/reservations': 'main.reservations',
            '/carpools': 'main.carpools',
            '/admin': 'admin.dashboard',
        }
        
        return path_mappings.get(path, '')
    
    def run_analysis(self) -> None:
        """Run the complete analysis."""
        print("🚀 Starting route analysis...")
        print(f"📁 Base path: {self.base_path}")
        print(f"📁 Templates path: {self.templates_path}")
        print(f"📁 Views path: {self.views_path}")
        
        self.extract_routes_from_views()
        self.extract_template_links()
        self.check_route_matches()
        self.print_summary()
        self.generate_fix_suggestions()
        
        print("\n✅ Analysis complete!")


def main():
    """Main function to run the route checker."""
    # Get the script directory and assume the project is in the same directory
    script_dir = Path(__file__).parent
    
    checker = RouteChecker(str(script_dir))
    checker.run_analysis()


if __name__ == "__main__":
    main()
