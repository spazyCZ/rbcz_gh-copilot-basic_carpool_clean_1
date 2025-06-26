#!/usr/bin/env python3
"""
Link and Route Validation Script for Flask/Jinja2 Application

This script scans all HTML templates in the carpool application to find:
- url_for() calls in templates
- href attributes in HTML elements
- action attributes in forms
- JavaScript redirects and fetch calls

Then it checks if these links match actual routes defined in the Flask blueprints.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RouteChecker:
    """
    A class to check consistency between template links and actual Flask routes.
    """

    def __init__(self, project_root: str):
        """
        Initialize the route checker with the project root directory.
        
        :param project_root: The root directory of the Flask project
        """
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / 'carpool' / 'templates'
        self.views_dir = self.project_root / 'carpool' / 'views'
        self.static_dir = self.project_root / 'carpool' / 'static'
        
        # Storage for found routes and links
        self.defined_routes: Dict[str, List[str]] = {}  # blueprint -> [routes]
        self.template_links: Dict[str, List[Tuple[str, str, int]]] = {}  # template -> [(link, type, line)]
        self.static_files: Set[str] = set()
        
        # Patterns for finding different types of links
        self.url_for_pattern = re.compile(r"url_for\s*\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*([^)]*))?\s*\)")
        self.href_pattern = re.compile(r'href\s*=\s*["\']([^"\']*\{\{[^}]*\}\}[^"\']*|[^"\']+)["\']', re.IGNORECASE)
        self.action_pattern = re.compile(r'action\s*=\s*["\']([^"\']*\{\{[^}]*\}\}[^"\']*|[^"\']+)["\']', re.IGNORECASE)
        self.js_redirect_pattern = re.compile(r'(?:window\.location(?:\.href)?|location\.href)\s*=\s*["\']([^"\']*\{\{[^}]*\}\}[^"\']*|[^"\']+)["\']')
        self.js_fetch_pattern = re.compile(r'fetch\s*\(\s*["\']([^"\']*\{\{[^}]*\}\}[^"\']*|[^"\']+)["\']')
        
        # Flask route decorators pattern
        self.route_pattern = re.compile(r"@\w+\.route\s*\(\s*['\"]([^'\"]+)['\"]")

    def scan_static_files(self) -> None:
        """
        Scan the static directory to build a list of available static files.
        """
        logger.info("Scanning static files...")
        
        if not self.static_dir.exists():
            logger.warning(f"Static directory not found: {self.static_dir}")
            return
            
        for root, dirs, files in os.walk(self.static_dir):
            for file in files:
                # Get relative path from static directory
                rel_path = os.path.relpath(os.path.join(root, file), self.static_dir)
                self.static_files.add(rel_path.replace('\\', '/'))  # Normalize path separators
                
        logger.info(f"Found {len(self.static_files)} static files")

    def extract_routes_from_views(self) -> None:
        """
        Extract all defined routes from Flask view files.
        """
        logger.info("Extracting routes from view files...")
        
        if not self.views_dir.exists():
            logger.error(f"Views directory not found: {self.views_dir}")
            return
            
        for view_file in self.views_dir.glob('*.py'):
            if view_file.name == '__init__.py':
                continue
                
            blueprint_name = view_file.stem
            self.defined_routes[blueprint_name] = []
            
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all route decorators
                routes = self.route_pattern.findall(content)
                
                # Also look for function definitions that follow route decorators
                lines = content.split('\n')
                current_routes = []
                
                for i, line in enumerate(lines):
                    # Check for route decorator
                    route_match = self.route_pattern.search(line)
                    if route_match:
                        current_routes.append(route_match.group(1))
                    
                    # Check for function definition (route handler)
                    elif line.strip().startswith('def ') and current_routes:
                        func_name = line.strip().split('(')[0].replace('def ', '')
                        for route in current_routes:
                            full_route = f"{blueprint_name}.{func_name}"
                            self.defined_routes[blueprint_name].append(full_route)
                            # Also add the route path for direct URL matching
                            self.defined_routes[blueprint_name].append(route)
                        current_routes = []
                        
            except Exception as e:
                logger.error(f"Error reading {view_file}: {e}")
                
        # Log found routes
        total_routes = sum(len(routes) for routes in self.defined_routes.values())
        logger.info(f"Found {total_routes} routes across {len(self.defined_routes)} blueprints")
        
        for blueprint, routes in self.defined_routes.items():
            logger.debug(f"  {blueprint}: {len(routes)} routes")

    def extract_links_from_templates(self) -> None:
        """
        Extract all links, hrefs, and form actions from template files.
        """
        logger.info("Extracting links from template files...")
        
        if not self.templates_dir.exists():
            logger.error(f"Templates directory not found: {self.templates_dir}")
            return
            
        for template_file in self.templates_dir.rglob('*.html'):
            rel_path = str(template_file.relative_to(self.templates_dir))
            self.template_links[rel_path] = []
            
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    # Find url_for calls
                    for match in self.url_for_pattern.finditer(line):
                        endpoint = match.group(1)
                        self.template_links[rel_path].append((endpoint, 'url_for', line_num))
                    
                    # Find href attributes - skip if they contain Jinja2 syntax
                    for match in self.href_pattern.finditer(line):
                        href = match.group(1)
                        # Skip Jinja2 template expressions
                        if '{{' in href and '}}' in href:
                            # Try to extract url_for from within Jinja2 expressions
                            url_for_matches = self.url_for_pattern.finditer(href)
                            for url_match in url_for_matches:
                                endpoint = url_match.group(1)
                                self.template_links[rel_path].append((endpoint, 'url_for', line_num))
                        elif not href.startswith(('http', 'mailto:', 'tel:', '#', '{{')):
                            self.template_links[rel_path].append((href, 'href', line_num))
                    
                    # Find form action attributes - skip if they contain Jinja2 syntax
                    for match in self.action_pattern.finditer(line):
                        action = match.group(1)
                        # Skip Jinja2 template expressions
                        if '{{' in action and '}}' in action:
                            # Try to extract url_for from within Jinja2 expressions
                            url_for_matches = self.url_for_pattern.finditer(action)
                            for url_match in url_for_matches:
                                endpoint = url_match.group(1)
                                self.template_links[rel_path].append((endpoint, 'url_for', line_num))
                        elif not action.startswith(('http', 'mailto:', 'tel:', '{{')):
                            self.template_links[rel_path].append((action, 'action', line_num))
                    
                    # Find JavaScript redirects - skip if they contain Jinja2 syntax
                    for match in self.js_redirect_pattern.finditer(line):
                        url = match.group(1)
                        if '{{' in url and '}}' in url:
                            # Try to extract url_for from within Jinja2 expressions
                            url_for_matches = self.url_for_pattern.finditer(url)
                            for url_match in url_for_matches:
                                endpoint = url_match.group(1)
                                self.template_links[rel_path].append((endpoint, 'url_for', line_num))
                        elif not url.startswith(('http', 'mailto:', 'tel:', '{{')):
                            self.template_links[rel_path].append((url, 'js_redirect', line_num))
                    
                    # Find fetch calls - skip if they contain Jinja2 syntax
                    for match in self.js_fetch_pattern.finditer(line):
                        url = match.group(1)
                        if '{{' in url and '}}' in url:
                            # Try to extract url_for from within Jinja2 expressions
                            url_for_matches = self.url_for_pattern.finditer(url)
                            for url_match in url_for_matches:
                                endpoint = url_match.group(1)
                                self.template_links[rel_path].append((endpoint, 'url_for', line_num))
                        elif not url.startswith(('http', 'mailto:', 'tel:', '{{')):
                            self.template_links[rel_path].append((url, 'fetch', line_num))
                            
            except Exception as e:
                logger.error(f"Error reading {template_file}: {e}")
                
        total_links = sum(len(links) for links in self.template_links.values())
        logger.info(f"Found {total_links} links across {len(self.template_links)} templates")

    def is_static_file_link(self, link: str) -> bool:
        """
        Check if a link points to a static file.
        
        :param link: The link to check
        :return: True if it's a static file link
        """
        # Remove leading slash and static prefix
        clean_link = link.lstrip('/')
        if clean_link.startswith('static/'):
            clean_link = clean_link[7:]  # Remove 'static/' prefix
            
        return clean_link in self.static_files

    def normalize_route(self, route: str) -> str:
        """
        Normalize a route for comparison.
        
        :param route: The route to normalize
        :return: Normalized route string
        """
        # Remove parameters and query strings
        route = route.split('?')[0]
        route = re.sub(r'<[^>]+>', '<param>', route)
        return route.strip('/')

    def check_route_exists(self, link: str, link_type: str) -> Tuple[bool, str]:
        """
        Check if a route exists in the defined routes.
        
        :param link: The link to check
        :param link_type: The type of link (url_for, href, etc.)
        :return: Tuple of (exists, reason)
        """
        if link_type == 'url_for':
            # Special handling for Flask's static endpoint
            if link == 'static':
                return True, "Flask static endpoint"
                
            # For url_for, check blueprint.function format
            all_routes = []
            for blueprint_routes in self.defined_routes.values():
                all_routes.extend(blueprint_routes)
                
            if link in all_routes:
                return True, "Found"
            else:
                # Check if it's a blueprint name only
                if '.' not in link and link in self.defined_routes:
                    return True, "Blueprint exists"
                return False, "Route not defined"
        
        else:
            # For direct URLs, check against route paths
            normalized_link = self.normalize_route(link)
            
            # Check static files
            if self.is_static_file_link(link):
                return True, "Static file"
            
            # Check against all defined route paths
            all_paths = []
            for blueprint_routes in self.defined_routes.values():
                for route in blueprint_routes:
                    if route.startswith('/'):  # It's a path, not a blueprint.function
                        all_paths.append(self.normalize_route(route))
            
            if normalized_link in all_paths:
                return True, "Found"
            
            # Check for common patterns that might be dynamically generated
            if any(keyword in link.lower() for keyword in ['api', 'ajax', 'json']):
                return True, "Likely API endpoint"
                
            return False, "Route not found"

    def generate_report(self) -> None:
        """
        Generate a comprehensive report of link validation results.
        """
        print("\n" + "="*80)
        print("LINK AND ROUTE VALIDATION REPORT")
        print("="*80)
        
        # Summary statistics
        total_links = sum(len(links) for links in self.template_links.values())
        total_routes = sum(len(routes) for routes in self.defined_routes.values())
        
        print(f"\nSUMMARY:")
        print(f"  Templates scanned: {len(self.template_links)}")
        print(f"  Total links found: {total_links}")
        print(f"  Total routes defined: {total_routes}")
        print(f"  Static files found: {len(self.static_files)}")
        
        # Check each link
        valid_links = 0
        invalid_links = []
        warnings = []
        
        for template, links in self.template_links.items():
            for link, link_type, line_num in links:
                exists, reason = self.check_route_exists(link, link_type)
                
                if exists:
                    valid_links += 1
                    if reason in ["Likely API endpoint"]:
                        warnings.append((template, link, link_type, line_num, reason))
                else:
                    invalid_links.append((template, link, link_type, line_num, reason))
        
        print(f"\nRESULTS:")
        print(f"  Valid links: {valid_links}")
        print(f"  Invalid links: {len(invalid_links)}")
        print(f"  Warnings: {len(warnings)}")
        
        # Report invalid links
        if invalid_links:
            print(f"\n❌ INVALID LINKS ({len(invalid_links)}):")
            print("-" * 60)
            for template, link, link_type, line_num, reason in invalid_links:
                print(f"  {template}:{line_num} - {link_type}: '{link}' - {reason}")
        
        # Report warnings
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            print("-" * 60)
            for template, link, link_type, line_num, reason in warnings:
                print(f"  {template}:{line_num} - {link_type}: '{link}' - {reason}")
        
        # Report defined routes
        print(f"\n📋 DEFINED ROUTES:")
        print("-" * 60)
        for blueprint, routes in self.defined_routes.items():
            print(f"  {blueprint}:")
            for route in sorted(set(routes)):
                print(f"    - {route}")
        
        # Suggest missing routes
        missing_endpoints = set()
        for template, link, link_type, line_num, reason in invalid_links:
            if link_type == 'url_for':
                missing_endpoints.add(link)
        
        if missing_endpoints:
            print(f"\n💡 SUGGESTED MISSING ENDPOINTS:")
            print("-" * 60)
            for endpoint in sorted(missing_endpoints):
                blueprint, func = endpoint.split('.') if '.' in endpoint else ('main', endpoint)
                print(f"  @{blueprint}_bp.route('/{func.replace('_', '-')}')")
                print(f"  def {func}():")
                print(f"      # TODO: Implement {func}")
                print(f"      pass\n")
        
        # Report unused static files (basic check)
        referenced_static = set()
        for template, links in self.template_links.items():
            for link, link_type, line_num in links:
                if self.is_static_file_link(link):
                    clean_link = link.lstrip('/').replace('static/', '')
                    referenced_static.add(clean_link)
        
        unused_static = self.static_files - referenced_static
        if unused_static:
            print(f"\n📁 POTENTIALLY UNUSED STATIC FILES ({len(unused_static)}):")
            print("-" * 60)
            for static_file in sorted(unused_static):
                print(f"  static/{static_file}")
        
        print("\n" + "="*80)
        print("END OF REPORT")
        print("="*80)

    def run_validation(self) -> bool:
        """
        Run the complete link validation process.
        
        :return: True if validation passed (no invalid links), False otherwise
        """
        logger.info("Starting link and route validation...")
        
        try:
            self.scan_static_files()
            self.extract_routes_from_views()
            self.extract_links_from_templates()
            self.generate_report()
            
            # Check if there are any invalid links
            invalid_count = 0
            for template, links in self.template_links.items():
                for link, link_type, line_num in links:
                    exists, reason = self.check_route_exists(link, link_type)
                    if not exists:
                        invalid_count += 1
            
            return invalid_count == 0
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


def main():
    """
    Main function to run the link validation script.
    """
    try:
        # Get project root directory
        if len(sys.argv) > 1:
            project_root = sys.argv[1]
        else:
            project_root = os.path.dirname(os.path.abspath(__file__))
        
        print(f"Checking links and routes in: {project_root}")
        
        # Create and run the route checker
        checker = RouteChecker(project_root)
        success = checker.run_validation()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
