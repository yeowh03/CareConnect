#!/usr/bin/env python3
"""Generate pydoc HTML documentation for CareConnect backend files."""

import os
import sys
import pydoc
from pathlib import Path

def generate_pydoc_html():
    """Generate HTML documentation for all Python files in the backend directory."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    docs_dir = project_root / "docs"
    
    # Create docs directory if it doesn't exist
    docs_dir.mkdir(exist_ok=True)
    
    # Add project root to Python path so imports work
    sys.path.insert(0, str(project_root))
    
    # List of Python modules to document
    modules = [
        "backend.app",
        "backend.config", 
        "backend.extensions",
        "backend.models",
        "backend.broadcast_observer",
        "backend.controllers.auth_controller",
        "backend.controllers.community_controller", 
        "backend.controllers.donations_controller",
        "backend.controllers.inventory_controller",
        "backend.controllers.jobs_controller",
        "backend.controllers.notification_controller",
        "backend.controllers.profile_controller",
        "backend.controllers.requests_controller",
        "backend.database.database_factory",
        "backend.database.database_interface", 
        "backend.database.postgres_database",
        "backend.database.sqlite_database",
        "backend.routes.auth_routes",
        "backend.routes.community_routes",
        "backend.routes.donations_routes", 
        "backend.routes.inventory_routes",
        "backend.routes.jobs_routes",
        "backend.routes.notification_routes",
        "backend.routes.profile_routes",
        "backend.routes.requests_routes",
        "backend.services.auth_strategies",
        "backend.services.community_clubs",
        "backend.services.find_user",
        "backend.services.image_upload", 
        "backend.services.jobs_service",
        "backend.services.metrics",
        "backend.services.notification_service",
        "backend.services.notification_strategies",
        "backend.services.password",
        "backend.services.run_allocation"
    ]
    
    print("Generating pydoc HTML documentation...")
    
    successful = []
    failed = []
    
    for module_name in modules:
        try:
            # Import the module
            __import__(module_name)
            module = sys.modules[module_name]
            
            # Generate HTML documentation
            html_content = pydoc.html.page(
                pydoc.describe(module),
                pydoc.html.document(module, module_name)
            )
            
            # Create output file name
            file_name = module_name.replace("backend.", "").replace(".", "_") + ".html"
            output_file = docs_dir / file_name
            
            # Write HTML file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"[OK] Generated: {file_name}")
            successful.append((module_name, file_name))
            
        except Exception as e:
            print(f"[FAIL] Failed to generate docs for {module_name}: {e}")
            failed.append((module_name, str(e)))
    
    # Generate index page
    generate_index_page(docs_dir, successful)
    
    print(f"\nDocumentation Summary:")
    print(f"   Successfully generated: {len(successful)} files")
    print(f"   Failed: {len(failed)} files")
    
    if failed:
        print(f"\nFailed modules:")
        for module, error in failed:
            print(f"   - {module}: {error}")
    
    print(f"\nDocumentation generated in: {docs_dir}")
    print("Open docs/index.html in your browser to view the documentation.")

def generate_index_page(docs_dir, successful_modules):
    """Generate an index page linking to all documentation files."""
    
    # Group modules by category
    categories = {
        "Core Application": [],
        "Controllers": [],
        "Database": [],
        "Routes": [],
        "Services": []
    }
    
    for module_name, file_name in successful_modules:
        clean_name = module_name.replace("backend.", "")
        
        if "." not in clean_name:
            categories["Core Application"].append((clean_name, file_name))
        elif clean_name.startswith("controllers."):
            categories["Controllers"].append((clean_name.replace("controllers.", ""), file_name))
        elif clean_name.startswith("database."):
            categories["Database"].append((clean_name.replace("database.", ""), file_name))
        elif clean_name.startswith("routes."):
            categories["Routes"].append((clean_name.replace("routes.", ""), file_name))
        elif clean_name.startswith("services."):
            categories["Services"].append((clean_name.replace("services.", ""), file_name))
    
    index_content = """<!DOCTYPE html>
<html>
<head>
    <title>CareConnect Backend Documentation</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 40px;
            background-color: #f8f9fa;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 40px;
        }
        .category { 
            margin-bottom: 40px; 
        }
        .category h2 { 
            color: #34495e; 
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-bottom: 20px;
        }
        .module-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }
        .module-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        .module-card:hover {
            background: #e3f2fd;
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
        }
        .module-card a {
            text-decoration: none;
            color: #2980b9;
            font-weight: 500;
            display: block;
        }
        .module-card a:hover {
            color: #1abc9c;
        }
        .stats {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            text-align: center;
        }
        .stats strong {
            color: #27ae60;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>CareConnect Backend Documentation</h1>
        <p class="subtitle">Comprehensive API documentation generated using Python's pydoc module</p>
        
        <div class="stats">
            <strong>""" + str(sum(len(modules) for modules in categories.values())) + """</strong> modules documented
        </div>
"""
    
    # Add each category
    for category_name, modules in categories.items():
        if modules:  # Only show categories that have modules
            index_content += f"""
        <div class="category">
            <h2>{category_name}</h2>
            <div class="module-grid">"""
            
            for module_name, file_name in sorted(modules):
                index_content += f"""
                <div class="module-card">
                    <a href="{file_name}">{module_name}</a>
                </div>"""
            
            index_content += """
            </div>
        </div>"""
    
    index_content += """
    </div>
</body>
</html>"""
    
    # Write index file
    with open(docs_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_content)

if __name__ == "__main__":
    generate_pydoc_html()