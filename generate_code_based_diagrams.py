#!/usr/bin/env python3
"""
Code-Based Diagram Generator for Momentum Hub

This script analyzes the Python codebase to generate architectural diagrams:
- Class Diagram: Shows classes, attributes, methods, and relationships
- Component Diagram: Shows modules/packages and their dependencies
- System Architecture Diagram: High-level overview of the application structure

Generated diagrams are saved as PlantUML files and rendered to PNG/SVG using PlantUML.
"""

import os
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Configuration
PROJECT_ROOT = Path(__file__).parent
DIAGRAMS_DIR = PROJECT_ROOT / "diagrams"
PLANTUML_JAR = PROJECT_ROOT / "plantuml.jar"

# Files/directories to exclude from analysis
EXCLUDE_DIRS = {'.venv', '__pycache__', 'tests', 'scripts', 'htmlcov', 'backups', 'CSV Export'}
EXCLUDE_FILES = {'setup.py', 'generate_arch_diagrams.py', 'generate_code_based_diagrams.py'}

def get_python_files() -> List[Path]:
    """Get all Python files in the project, excluding specified directories/files."""
    python_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith('.py') and file not in EXCLUDE_FILES:
                python_files.append(Path(root) / file)
    return python_files

def parse_file(file_path: Path) -> Dict:
    """Parse a Python file and extract classes, functions, and imports."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return {'classes': [], 'functions': [], 'imports': []}

    classes = []
    functions = []
    imports = []

    class_stack = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_stack.append(node)
            class_info = {
                'name': node.name,
                'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                'attributes': []
            }
            # Extract attributes from __init__ if present
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    class_info['attributes'].append(target.attr)
            classes.append(class_info)

        elif isinstance(node, ast.FunctionDef):
            # Check if this function is inside a class
            is_method = False
            for parent in reversed(class_stack):
                if node in ast.walk(parent):
                    is_method = True
                    break
            if not is_method:
                functions.append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)

        # Remove class from stack when we exit it
        if isinstance(node, ast.ClassDef):
            # This is a simple way - in practice, we'd need more sophisticated tracking
            pass

    return {
        'classes': classes,
        'functions': functions,
        'imports': imports
    }

def build_dependency_graph() -> Dict[str, Set[str]]:
    """Build a graph of module dependencies based on imports."""
    files = get_python_files()
    graph = defaultdict(set)

    for file_path in files:
        module_name = file_path.relative_to(PROJECT_ROOT).with_suffix('').as_posix().replace('/', '.')
        parsed = parse_file(file_path)

        for imp in parsed['imports']:
            # Simplify import to module level
            if '.' in imp:
                imp_module = imp.split('.')[0]
            else:
                imp_module = imp

            # Only add if it's a local module
            if any(f.stem == imp_module for f in files):
                graph[module_name].add(imp_module)

    return graph

def generate_class_diagram() -> str:
    """Generate PlantUML class diagram from codebase analysis."""
    files = get_python_files()
    plantuml = ["@startuml", "skinparam classAttributeIconSize 0"]

    for file_path in files:
        parsed = parse_file(file_path)
        package = file_path.parent.relative_to(PROJECT_ROOT).as_posix().replace('/', '.')
        if package == '.':
            package = ''

        for cls in parsed['classes']:
            class_name = f"{package}.{cls['name']}" if package else cls['name']
            plantuml.append(f"class {class_name} {{")

            for attr in cls['attributes']:
                plantuml.append(f"  - {attr}")

            for method in cls['methods']:
                plantuml.append(f"  + {method}()")

            plantuml.append("}")

    # Add relationships (simplified - could be enhanced with more analysis)
    plantuml.extend([
        "Habit \"1\" -- \"*\" Completion : has",
        "Habit \"1\" -- \"*\" Goal : has",
        "Category \"1\" -- \"*\" Habit : contains",
        "Goal --> Habit : targets",
        "Completion --> Habit : belongs to"
    ])

    plantuml.append("@enduml")
    return "\n".join(plantuml)

def generate_component_diagram() -> str:
    """Generate PlantUML component diagram showing module dependencies."""
    graph = build_dependency_graph()
    plantuml = ["@startuml", "skinparam componentStyle rectangle"]

    # Define packages
    packages = {
        'cli': ['cli_display', 'cli_habit_management', 'cli_goal_management', 'cli_category_management', 'cli_analysis', 'cli_export', 'cli_utils'],
        'core': ['habit', 'category', 'goal', 'completion'],
        'db': ['momentum_db'],
        'analysis': ['habit_analysis'],
        'utils': ['momentum_utils', 'error_manager', 'encouragements'],
        'main': ['momentum_main', 'momentum_cli']
    }

    for pkg_name, modules in packages.items():
        plantuml.append(f"package \"{pkg_name}\" {{")
        for module in modules:
            plantuml.append(f"  [{module}]")
        plantuml.append("}")

    # Add dependencies
    for from_module, to_modules in graph.items():
        from_pkg = next((pkg for pkg, mods in packages.items() if any(from_module.startswith(mod) for mod in mods)), 'main')
        for to_module in to_modules:
            to_pkg = next((pkg for pkg, mods in packages.items() if any(to_module.startswith(mod) for mod in mods)), 'main')
            if from_pkg != to_pkg:
                plantuml.append(f"[{from_module}] --> [{to_module}]")

    plantuml.append("@enduml")
    return "\n".join(plantuml)

def generate_system_architecture_diagram() -> str:
    """Generate high-level system architecture diagram."""
    plantuml = [
        "@startuml",
        "skinparam componentStyle rectangle",
        "actor \"User\" as User",
        "",
        "package \"CLI Interface\" {",
        "  [momentum_cli.py] as CLI",
        "  [cli_display.py] as Display",
        "  [cli_habit_management.py] as HabitMgmt",
        "  [cli_goal_management.py] as GoalMgmt",
        "  [cli_category_management.py] as CategoryMgmt",
        "  [cli_analysis.py] as Analysis",
        "  [cli_export.py] as Export",
        "  [cli_utils.py] as Utils",
        "}",
        "",
        "package \"Core Classes\" {",
        "  [habit.py] as Habit",
        "  [category.py] as Category",
        "  [goal.py] as Goal",
        "  [completion.py] as Completion",
        "}",
        "",
        "package \"Database Layer\" {",
        "  [momentum_db.py] as DB",
        "  database \"SQLite DB\" as SQLite",
        "}",
        "",
        "package \"Analysis & Utils\" {",
        "  [habit_analysis.py] as HabitAnalysis",
        "  [momentum_utils.py] as MomentumUtils",
        "  [error_manager.py] as ErrorManager",
        "  [encouragements.py] as Encouragements",
        "}",
        "",
        "User --> CLI",
        "CLI --> Display",
        "CLI --> HabitMgmt",
        "CLI --> GoalMgmt",
        "CLI --> CategoryMgmt",
        "CLI --> Analysis",
        "CLI --> Export",
        "CLI --> Utils",
        "",
        "HabitMgmt --> Habit",
        "GoalMgmt --> Goal",
        "CategoryMgmt --> Category",
        "Analysis --> HabitAnalysis",
        "Export --> Completion",
        "",
        "Habit --> DB",
        "Category --> DB",
        "Goal --> DB",
        "Completion --> DB",
        "",
        "DB --> SQLite",
        "",
        "HabitAnalysis --> DB",
        "MomentumUtils --> ErrorManager",
        "MomentumUtils --> Encouragements",
        "@enduml"
    ]
    return "\n".join(plantuml)

def save_and_render_diagram(name: str, plantuml_content: str):
    """Save PlantUML content to file and render to image."""
    DIAGRAMS_DIR.mkdir(exist_ok=True)

    puml_file = DIAGRAMS_DIR / f"{name}.puml"
    with open(puml_file, 'w', encoding='utf-8') as f:
        f.write(plantuml_content)

    print(f"Generated {puml_file}")

    # Render to PNG and SVG if PlantUML is available
    if PLANTUML_JAR.exists():
        try:
            subprocess.run(['java', '-jar', str(PLANTUML_JAR), str(puml_file)],
                         check=True, capture_output=True)
            print(f"Rendered {name}.png and {name}.svg")
        except subprocess.CalledProcessError as e:
            print(f"Failed to render {name}: {e}")
    else:
        print(f"PlantUML JAR not found at {PLANTUML_JAR}. Skipping image generation.")

def main():
    """Main function to generate all diagrams."""
    print("Analyzing codebase and generating diagrams...")

    # Generate and save diagrams
    diagrams = [
        ("class_diagram_code", generate_class_diagram()),
        ("component_diagram_code", generate_component_diagram()),
        ("system_architecture_code", generate_system_architecture_diagram())
    ]

    for name, content in diagrams:
        save_and_render_diagram(name, content)

    print("Diagram generation complete!")

if __name__ == "__main__":
    main()
