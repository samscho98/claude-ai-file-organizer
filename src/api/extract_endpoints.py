"""
Enhanced Flask API endpoint extraction functionality for Claude AI File Organizer.
"""

import os
import re
import json
import ast
from pathlib import Path


def extract_endpoints_from_file(file_path, file_content=None):
    """
    Extract API endpoints from a file based on its extension.
    
    Args:
        file_path (str): Path to the file
        file_content (str, optional): File content if already loaded
        
    Returns:
        list: List of extracted endpoints
    """
    if file_content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except (UnicodeDecodeError, IOError):
            return []
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Extract based on file extension
    if file_ext in ['.py', '.flask']:
        # Prioritize Flask extraction for Python files
        flask_endpoints = extract_from_flask(file_content)
        
        # If Flask endpoints are found, return them
        if flask_endpoints:
            return flask_endpoints
            
        # Otherwise, try generic Python extraction
        return extract_from_python(file_content)
    elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
        return extract_from_javascript(file_content)
    elif file_ext in ['.java', '.kt', '.scala']:
        return extract_from_java(file_content)
    elif file_ext in ['.rb']:
        return extract_from_ruby(file_content)
    elif file_ext in ['.php']:
        return extract_from_php(file_content)
    elif file_ext in ['.go']:
        return extract_from_go(file_content)
    elif file_ext in ['.yaml', '.yml', '.json']:
        return extract_from_api_spec(file_path, file_content)
    else:
        # Generic extraction
        return extract_generic_urls(file_content)


def extract_from_flask(content):
    """
    Extract Flask API endpoints using enhanced detection methods.
    
    Args:
        content (str): Python file content
        
    Returns:
        list: List of extracted Flask endpoints
    """
    endpoints = []
    
    # Pattern 1: Flask route decorators
    flask_patterns = [
        # Standard Flask routes
        r'@(?:app|blueprint|api)\.route\([\'"]([^\'"]+)[\'"]',
        # HTTP method-specific routes
        r'@(?:app|blueprint|api)\.(?:get|post|put|delete|patch|options|head)\([\'"]([^\'"]+)[\'"]',
        # Flask-RESTful resource endpoints
        r'api\.add_resource\([^,]+,\s*[\'"]([^\'"]+)[\'"]',
        # Blueprint routes
        r'@(?:\w+)\.route\([\'"]([^\'"]+)[\'"]',
        # Flask-RESTX endpoints
        r'@(?:api\.route|ns\.route)\([\'"]([^\'"]+)[\'"]'
    ]
    
    # Collect matches from all patterns
    for pattern in flask_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    # Try AST parsing for more accurate detection if not many endpoints found
    if len(endpoints) < 5:  # Only try AST parsing if regex didn't find many routes
        try:
            ast_endpoints = extract_flask_endpoints_ast(content)
            # Merge and remove duplicates
            endpoints = list(set(endpoints + ast_endpoints))
        except SyntaxError:
            # If AST parsing fails, continue with regex results
            pass
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_flask_endpoints_ast(content):
    """
    Extract Flask endpoints using AST parsing for more accurate results.
    
    Args:
        content (str): Python file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    try:
        # Parse the Python code
        tree = ast.parse(content)
        
        # Look for route decorators
        for node in ast.walk(tree):
            # Find function definitions
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # Check for app.route() or similar patterns
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr') and decorator.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                            # Get the route path from the first argument
                            if decorator.args and isinstance(decorator.args[0], ast.Str):
                                endpoints.append(decorator.args[0].s)
    except Exception:
        # If AST parsing fails, return what we have
        pass
        
    return endpoints


def extract_from_python(content):
    """
    Extract API endpoints from Python code.
    
    Args:
        content (str): Python file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Flask routes (covered by extract_from_flask)
    
    # FastAPI routes
    fastapi_patterns = [
        r'@(?:app|router)\.(?:get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)[\'"]'
    ]
    
    # Django URL patterns
    django_patterns = [
        r'path\([\'"]([^\'"]+)[\'"]',
        r'url\([\'"](?:\^)?([^\'"^$]+)[\'"]'
    ]
    
    all_patterns = fastapi_patterns + django_patterns
    
    for pattern in all_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_from_javascript(content):
    """
    Extract API endpoints from JavaScript/TypeScript code.
    
    Args:
        content (str): JavaScript file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Express.js routes
    express_patterns = [
        r'(?:app|router)\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
        r'route\([\'"]([^\'"]+)[\'"]'
    ]
    
    # React Router routes
    react_patterns = [
        r'<Route(?:\s+[^>]*)?path=[\'"]([^\'"]+)[\'"]'
    ]
    
    # Axios or fetch calls
    http_patterns = [
        r'(?:axios|fetch)\([\'"](?:https?://[^/]+)?(/[^\'"]+)[\'"]',
        r'url:\s*[\'"](?:https?://[^/]+)?(/[^\'"]+)[\'"]'
    ]
    
    all_patterns = express_patterns + react_patterns + http_patterns
    
    for pattern in all_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_from_java(content):
    """
    Extract API endpoints from Java/Kotlin/Scala code.
    
    Args:
        content (str): Java file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Spring annotations
    spring_patterns = [
        r'@RequestMapping\([\'"]([^\'"]+)[\'"]',
        r'@GetMapping\([\'"]([^\'"]+)[\'"]',
        r'@PostMapping\([\'"]([^\'"]+)[\'"]',
        r'@PutMapping\([\'"]([^\'"]+)[\'"]',
        r'@DeleteMapping\([\'"]([^\'"]+)[\'"]',
        r'@PatchMapping\([\'"]([^\'"]+)[\'"]'
    ]
    
    # JAX-RS annotations
    jaxrs_patterns = [
        r'@Path\([\'"]([^\'"]+)[\'"]'
    ]
    
    all_patterns = spring_patterns + jaxrs_patterns
    
    for pattern in all_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_from_ruby(content):
    """
    Extract API endpoints from Ruby code.
    
    Args:
        content (str): Ruby file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Rails routes
    rails_patterns = [
        r'(?:get|post|put|patch|delete)\s+[\'"]([^\'"]+)[\'"]',
        r'match\s+[\'"]([^\'"]+)[\'"]'
    ]
    
    for pattern in rails_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_from_php(content):
    """
    Extract API endpoints from PHP code.
    
    Args:
        content (str): PHP file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Laravel/Symfony routes
    php_patterns = [
        r'Route::(?:get|post|put|patch|delete)\([\'"]([^\'"]+)[\'"]',
        r'->add\([\'"]([^\'"]+)[\'"]'
    ]
    
    for pattern in php_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_from_go(content):
    """
    Extract API endpoints from Go code.
    
    Args:
        content (str): Go file content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Gin/Echo/Gorilla/Net/HTTP patterns
    go_patterns = [
        r'(?:r|router|e|mux)\.(?:GET|POST|PUT|DELETE|PATCH|Handle(?:Func)?)\([\'"]([^\'"]+)[\'"]',
        r'http\.Handle(?:Func)?\([\'"]([^\'"]+)[\'"]'
    ]
    
    for pattern in go_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_from_api_spec(file_path, content):
    """
    Extract API endpoints from API specification files (OpenAPI/Swagger).
    
    Args:
        file_path (str): File path
        content (str): File content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    if file_path.endswith(('.yaml', '.yml')):
        # Attempt to parse YAML
        try:
            # Check if PyYAML is available
            import importlib.util
            spec = importlib.util.find_spec("yaml")
            if spec is not None:
                import yaml
                data = yaml.safe_load(content)
            else:
                # If PyYAML is not available, fallback to regex extraction
                return extract_generic_urls(content)
        except (ImportError, Exception):
            # Fallback to regex extraction if YAML parsing fails or if import fails
            return extract_generic_urls(content)
    elif file_path.endswith('.json'):
        # Attempt to parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback to regex extraction if JSON parsing fails
            return extract_generic_urls(content)
    else:
        return []
    
    # Extract from OpenAPI/Swagger structure
    if data and isinstance(data, dict):
        # OpenAPI v3
        if 'paths' in data and isinstance(data['paths'], dict):
            endpoints.extend(data['paths'].keys())
        # OpenAPI v2 (Swagger)
        elif 'swagger' in data and 'paths' in data:
            endpoints.extend(data['paths'].keys())
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def extract_generic_urls(content):
    """
    Extract potential API endpoints using generic URL patterns.
    
    Args:
        content (str): File content
        
    Returns:
        list: List of extracted endpoints
    """
    endpoints = []
    
    # Generic API URL patterns
    url_patterns = [
        r'(?:https?://[^/\s]+)?(/api/[^\s\'"]+)[\'"]?',
        r'(?:https?://[^/\s]+)?(/v\d+/[^\s\'"]+)[\'"]?',
        r'(?:https?://[^/\s]+)?(/rest/[^\s\'"]+)[\'"]?'
    ]
    
    for pattern in url_patterns:
        matches = re.findall(pattern, content)
        endpoints.extend(matches)
    
    return [clean_endpoint(endpoint) for endpoint in endpoints]


def clean_endpoint(endpoint):
    """
    Clean and normalize an API endpoint.
    
    Args:
        endpoint (str): Raw endpoint
        
    Returns:
        str: Cleaned endpoint
    """
    # Remove query parameters
    endpoint = endpoint.split('?')[0]
    
    # Remove trailing slashes
    endpoint = endpoint.rstrip('/')
    
    # Ensure leading slash
    if endpoint and not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    
    return endpoint


def group_endpoints_by_prefix(endpoints):
    """
    Group endpoints by common prefixes for better organization.
    
    Args:
        endpoints (list): List of endpoints
        
    Returns:
        dict: Grouped endpoints
    """
    groups = {}
    
    for endpoint in endpoints:
        parts = endpoint.strip('/').split('/')
        
        if len(parts) > 0:
            prefix = parts[0]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(endpoint)
    
    return groups


def save_endpoints(endpoints, output_path):
    """
    Save extracted endpoints to a file.
    
    Args:
        endpoints (list): List of endpoints
        output_path (str): Output file path
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Group endpoints by prefix
    grouped_endpoints = group_endpoints_by_prefix(endpoints)
    
    # Save as JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(grouped_endpoints, f, indent=2)