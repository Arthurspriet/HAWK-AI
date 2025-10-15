#!/usr/bin/env python3
"""
HAWK-AI Setup Validation Script
Checks if all components are properly configured and ready to run.
"""
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro} (3.8+ required)"


def check_file_exists(filepath):
    """Check if a file exists."""
    return Path(filepath).exists()


def check_directory_exists(dirpath):
    """Check if a directory exists."""
    return Path(dirpath).is_dir()


def check_ollama_connection():
    """Check if Ollama is accessible."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return True, f"{len(models)} models available"
        return False, "Ollama responded but no models found"
    except Exception as e:
        return False, f"Cannot connect: {str(e)}"


def check_dependencies():
    """Check if key dependencies are installed."""
    dependencies = {
        'yaml': 'PyYAML',
        'ollama': 'ollama',
        'langchain_ollama': 'langchain-ollama',
        'faiss': 'faiss-gpu-cu12 or faiss-cpu',
        'sentence_transformers': 'sentence-transformers',
        'pandas': 'pandas',
        'duckduckgo_search': 'duckduckgo-search',
        'rich': 'rich'
    }
    
    results = {}
    for module, package in dependencies.items():
        try:
            __import__(module)
            results[package] = (True, "Installed")
        except ImportError:
            results[package] = (False, "Missing")
    
    return results


def main():
    """Run all validation checks."""
    console.print(Panel.fit(
        "[bold cyan]HAWK-AI Setup Validation[/bold cyan]\n"
        "Checking system configuration...",
        border_style="cyan"
    ))
    
    # Results table
    table = Table(title="Validation Results", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")
    
    all_passed = True
    
    # Check Python version
    passed, details = check_python_version()
    status = "✓" if passed else "✗"
    table.add_row("Python Version", f"[green]{status}[/green]" if passed else f"[red]{status}[/red]", details)
    all_passed = all_passed and passed
    
    # Check core files
    core_files = [
        ("config/settings.yaml", "Configuration"),
        ("main.py", "Main Entry Point"),
        ("core/orchestrator.py", "Orchestrator"),
        ("core/agent_registry.py", "Agent Registry"),
        ("agents/supervisor_agent.py", "Supervisor Agent"),
    ]
    
    for filepath, name in core_files:
        exists = check_file_exists(filepath)
        status = "✓" if exists else "✗"
        table.add_row(
            name,
            f"[green]{status}[/green]" if exists else f"[red]{status}[/red]",
            filepath
        )
        all_passed = all_passed and exists
    
    # Check directories
    directories = [
        ("agents/", "Agents Directory"),
        ("core/", "Core Directory"),
        ("config/", "Config Directory"),
        ("data/vector_index/", "Vector Index Directory"),
        ("logs/", "Logs Directory"),
    ]
    
    for dirpath, name in directories:
        exists = check_directory_exists(dirpath)
        status = "✓" if exists else "✗"
        table.add_row(
            name,
            f"[green]{status}[/green]" if exists else f"[red]{status}[/red]",
            dirpath
        )
        all_passed = all_passed and exists
    
    # Check Ollama
    passed, details = check_ollama_connection()
    status = "✓" if passed else "✗"
    table.add_row(
        "Ollama Service",
        f"[green]{status}[/green]" if passed else f"[yellow]{status}[/yellow]",
        details
    )
    
    # Check dependencies
    console.print("\n")
    console.print(table)
    
    console.print("\n[bold]Python Dependencies:[/bold]")
    deps_table = Table(show_header=True)
    deps_table.add_column("Package", style="cyan")
    deps_table.add_column("Status", style="white")
    
    dep_results = check_dependencies()
    deps_passed = True
    for package, (installed, msg) in dep_results.items():
        status = "✓" if installed else "✗"
        deps_table.add_row(
            package,
            f"[green]{status}[/green] {msg}" if installed else f"[red]{status}[/red] {msg}"
        )
        deps_passed = deps_passed and installed
    
    console.print(deps_table)
    
    # Summary
    console.print("\n" + "=" * 60)
    if all_passed and deps_passed:
        console.print("[bold green]✓ All checks passed! HAWK-AI is ready to run.[/bold green]")
        console.print("\nTo start HAWK-AI:")
        console.print("  [cyan]python main.py --chat[/cyan]")
        console.print("\nOr simply:")
        console.print("  [cyan]make run[/cyan]")
    else:
        console.print("[bold yellow]⚠ Some checks failed.[/bold yellow]")
        
        if not deps_passed:
            console.print("\n[yellow]Missing dependencies detected.[/yellow]")
            console.print("Run: [cyan]make setup[/cyan] or [cyan]pip install -r requirements.txt[/cyan]")
        
        if not check_ollama_connection()[0]:
            console.print("\n[yellow]Ollama is not accessible.[/yellow]")
            console.print("Make sure Ollama is running: [cyan]ollama serve[/cyan]")
            console.print("Download models: [cyan]ollama pull llama3.1:8b[/cyan]")
    
    console.print("=" * 60)
    
    return 0 if (all_passed and deps_passed) else 1


if __name__ == "__main__":
    sys.exit(main())

