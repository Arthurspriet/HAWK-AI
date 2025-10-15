#!/usr/bin/env python3
"""
HAWK-AI Capability Showcase
Demonstrates all agent capabilities with comprehensive examples.
"""
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import get_orchestrator
from agents import register_all_agents

console = Console()

# Example queries showcasing different capabilities
EXAMPLES = [
    {
        "name": "🎯 Multi-Agent Intelligence Synthesis",
        "query": "Provide a comprehensive analysis of conflict escalation and geographic hotspots in Sudan from 2022-2025",
        "description": "Demonstrates: Supervisor agent coordinating GeoAgent + AnalystAgent in parallel, producing hotspot maps and analytical synthesis",
        "agents": ["Supervisor", "GeoAgent", "AnalystAgent"]
    },
    {
        "name": "🔍 Real-Time Web Intelligence + Historical Context",
        "query": "Search for latest developments in Yemen conflict and provide historical context",
        "description": "Demonstrates: SearchAgent web scraping + AnalystAgent ACLED data fusion + context enrichment",
        "agents": ["SearchAgent", "AnalystAgent"]
    },
    {
        "name": "🗺️ Geospatial Hotspot Analysis",
        "query": "Generate geospatial hotspot map for Nigeria showing conflict clustering patterns",
        "description": "Demonstrates: GeoAgent DBSCAN clustering, interactive map generation, spatial reasoning",
        "agents": ["GeoAgent"]
    },
    {
        "name": "📊 Temporal Pattern Analysis",
        "query": "Analyze temporal escalation patterns and trends in the Sahel region over the past 3 years",
        "description": "Demonstrates: AnalystAgent statistical analysis, FAISS semantic search across 868K+ events",
        "agents": ["AnalystAgent"]
    },
    {
        "name": "💻 Code Execution for Data Analysis",
        "query": "Execute Python code to find the top 10 countries by conflict fatalities from ACLED data",
        "description": "Demonstrates: CodeExecAgent sandboxed execution with data manipulation",
        "agents": ["CodeExecAgent"]
    },
    {
        "name": "📝 Executive Brief Generation",
        "query": "Create an executive summary brief on the current security situation in the Horn of Africa",
        "description": "Demonstrates: RedactorAgent professional report generation with key findings extraction",
        "agents": ["RedactorAgent", "AnalystAgent"]
    },
    {
        "name": "🧠 Reasoning Chain with Reflection",
        "query": "Analyze the root causes and strategic implications of the Ukraine conflict escalation",
        "description": "Demonstrates: ReflectionAgent structured reasoning (patterns → hypotheses → evaluation → synthesis → review)",
        "agents": ["ReflectionAgent", "AnalystAgent"]
    }
]


def print_banner():
    """Print showcase banner."""
    banner = """
╦ ╦╔═╗╦ ╦╦╔═  ╔═╗╦  
║═╣╠═╣║║║╠╩╗  ╠═╣║  
╩ ╩╩ ╩╚╩╝╩ ╩  ╩ ╩╩  
Capability Showcase
    """
    console.print(Panel.fit(banner, border_style="cyan", title="[bold]HAWK-AI Demonstrations[/bold]"))


def run_example(orchestrator, example_num: int):
    """Run a single example."""
    example = EXAMPLES[example_num]
    
    # Display example info
    console.print(f"\n[bold cyan]═══ Example {example_num + 1}/{len(EXAMPLES)} ═══[/bold cyan]")
    console.print(Panel(
        f"[bold]{example['name']}[/bold]\n\n"
        f"[dim]{example['description']}[/dim]\n\n"
        f"[yellow]Agents:[/yellow] {', '.join(example['agents'])}\n"
        f"[yellow]Query:[/yellow] {example['query']}",
        border_style="blue"
    ))
    
    # Execute query
    console.print("\n[cyan]Processing...[/cyan]")
    start_time = time.time()
    
    try:
        result = orchestrator.execute_task(example['query'])
        duration = time.time() - start_time
        
        if result['status'] == 'success':
            console.print(f"\n[bold green]✓ Success![/bold green] [dim]({duration:.2f}s)[/dim]")
            console.print("\n[bold]Result:[/bold]")
            console.print(Panel(
                result['result'][:1500] + ("..." if len(result['result']) > 1500 else ""),
                border_style="green",
                title="[bold]Output Preview[/bold]"
            ))
            console.print(f"\n[dim]Agents used: {', '.join(result.get('agents_used', []))}[/dim]")
            
            # Check for generated artifacts
            if "map" in result['result'].lower() or "Sudan" in example['query'] or "Nigeria" in example['query']:
                console.print("\n[yellow]📁 Artifact:[/yellow] Interactive map generated in [cyan]data/maps/[/cyan]")
            
            if "report" in result['result'].lower() or "reasoning" in result['result'].lower():
                console.print("[yellow]📁 Artifact:[/yellow] Analysis report saved in [cyan]data/analysis/[/cyan]")
                
        else:
            console.print(f"\n[bold red]✗ Error:[/bold red] {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        console.print(f"\n[bold red]✗ Exception:[/bold red] {str(e)}")
    
    console.print("\n" + "─" * 80)


def run_all_examples():
    """Run all capability examples."""
    print_banner()
    
    console.print("\n[bold yellow]Initializing HAWK-AI...[/bold yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading agents and models...", total=None)
        register_all_agents()
        orchestrator = get_orchestrator()
        progress.update(task, completed=True)
    
    console.print("[green]✓ System ready[/green]")
    console.print(f"\n[bold]Running {len(EXAMPLES)} capability demonstrations...[/bold]\n")
    
    # Run each example
    for i in range(len(EXAMPLES)):
        run_example(orchestrator, i)
        
        # Small delay between examples
        if i < len(EXAMPLES) - 1:
            console.print("\n[dim]Waiting 2s before next example...[/dim]")
            time.sleep(2)
    
    # Summary
    console.print("\n" + "═" * 80)
    console.print("\n[bold green]🎉 All Examples Complete![/bold green]\n")
    console.print("[bold]Generated Artifacts:[/bold]")
    console.print("  • [cyan]data/maps/[/cyan] - Interactive hotspot maps")
    console.print("  • [cyan]data/analysis/[/cyan] - Reasoning chains and reports")
    console.print("  • [cyan]logs/[/cyan] - Session logs and summaries")
    
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. View reasoning chains: [yellow]python tools/reasoning_viewer.py[/yellow]")
    console.print("  2. Open hotspot maps: [yellow]data/maps/*.html[/yellow]")
    console.print("  3. Review session logs: [yellow]logs/session_*.jsonl[/yellow]")
    console.print("  4. Try interactive mode: [yellow]python main.py --chat[/yellow]")
    
    console.print("\n[dim]For detailed documentation, see README.md[/dim]\n")


def run_single_example(example_num: int):
    """Run a specific example by number."""
    if example_num < 1 or example_num > len(EXAMPLES):
        console.print(f"[red]Error: Example number must be between 1 and {len(EXAMPLES)}[/red]")
        return
    
    print_banner()
    console.print(f"\n[bold]Running Example {example_num}[/bold]\n")
    
    # Initialize
    register_all_agents()
    orchestrator = get_orchestrator()
    
    # Run example
    run_example(orchestrator, example_num - 1)


def list_examples():
    """List all available examples."""
    print_banner()
    console.print("\n[bold]Available Examples:[/bold]\n")
    
    for i, example in enumerate(EXAMPLES, 1):
        console.print(f"[cyan]{i}.[/cyan] {example['name']}")
        console.print(f"   [dim]{example['description']}[/dim]")
        console.print(f"   [yellow]Agents:[/yellow] {', '.join(example['agents'])}\n")
    
    console.print("[bold]Usage:[/bold]")
    console.print("  Run all:      [yellow]python examples_showcase.py[/yellow]")
    console.print("  Run specific: [yellow]python examples_showcase.py --example N[/yellow]")
    console.print("  List all:     [yellow]python examples_showcase.py --list[/yellow]\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HAWK-AI Capability Showcase - Demonstrate all agent capabilities"
    )
    parser.add_argument(
        '--example', '-e',
        type=int,
        help='Run specific example number (1-7)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available examples'
    )
    
    args = parser.parse_args()
    
    try:
        if args.list:
            list_examples()
        elif args.example:
            run_single_example(args.example)
        else:
            run_all_examples()
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

