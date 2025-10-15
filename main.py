#!/usr/bin/env python3
"""
HAWK-AI: Local OSINT-capable Reasoning Agent
Main entry point for the system.
"""
import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import get_orchestrator
from agents import register_all_agents

console = Console()


def print_banner():
    """Print HAWK-AI banner."""
    banner = """
╦ ╦╔═╗╦ ╦╦╔═  ╔═╗╦
║═╣╠═╣║║║╠╩╗  ╠═╣║
╩ ╩╩ ╩╚╩╝╩ ╩  ╩ ╩╩
OSINT-Capable Reasoning Agent
    """
    console.print(Panel.fit(banner, border_style="cyan", title="[bold]Welcome[/bold]"))


def print_help():
    """Print help information."""
    help_text = """
[bold cyan]Available Commands:[/bold cyan]

  [yellow]help[/yellow]           Show this help message
  [yellow]status[/yellow]         Show system status
  [yellow]history[/yellow]        Show session history
  [yellow]clear[/yellow]          Clear screen
  [yellow]exit / quit[/yellow]    Exit HAWK-AI
  
[bold cyan]Query Types:[/bold cyan]

  • Web searches: "Search for latest conflict in Sudan"
  • Data analysis: "Analyze conflict patterns in Niger"
  • Code execution: "Execute this code: ```python\\nprint('Hello')\\n```"
  • Summarization: "Summarize the following text..."
  • General queries: Ask any question!

[bold cyan]Examples:[/bold cyan]

  > Search for recent protests in Kenya
  > Analyze events in Ukraine since 2023
  > What are the conflict escalation patterns in the Sahel?
  > Create a brief on Middle East tensions
    """
    console.print(help_text)


def interactive_mode():
    """Run HAWK-AI in interactive chat mode."""
    print_banner()
    console.print("\n[bold green]HAWK-AI Interactive Mode[/bold green]")
    console.print("[dim]Type 'help' for commands, 'exit' to quit[/dim]\n")
    
    # Initialize system
    console.print("[cyan]Initializing system...[/cyan]")
    register_all_agents()
    orchestrator = get_orchestrator()
    console.print("[green]✓ System ready[/green]\n")
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            query = Prompt.ask("\n[bold cyan]HAWK-AI[/bold cyan]")
            
            if not query.strip():
                continue
            
            query_lower = query.lower().strip()
            
            # Handle special commands
            if query_lower in ['exit', 'quit', 'q']:
                console.print("\n[yellow]Shutting down HAWK-AI...[/yellow]")
                console.print("[green]Session saved. Goodbye![/green]")
                break
            
            elif query_lower == 'help':
                print_help()
                continue
            
            elif query_lower == 'status':
                orchestrator.display_status()
                continue
            
            elif query_lower == 'history':
                summary = orchestrator.tracker.get_session_summary()
                console.print(f"\n[bold]Session Summary:[/bold]")
                console.print(f"Session ID: {summary['session_id']}")
                console.print(f"Total Events: {summary['total_events']}")
                console.print(f"Event Types: {summary.get('event_types', {})}")
                console.print(f"Agents Used: {summary.get('agents_used', [])}")
                continue
            
            elif query_lower == 'clear':
                console.clear()
                print_banner()
                continue
            
            # Process query
            result = orchestrator.execute_task(query)
            
            # Display result
            if result['status'] == 'success':
                console.print(f"\n[bold green]Result:[/bold green]")
                console.print(Panel(result['result'], border_style="green"))
                console.print(f"\n[dim]Completed in {result['duration']:.2f}s using: {', '.join(result['agents_used'])}[/dim]")
            else:
                console.print(f"\n[bold red]Error:[/bold red] {result.get('error', 'Unknown error')}")
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted by user[/yellow]")
            confirm = Prompt.ask("Exit HAWK-AI? (y/n)", default="n")
            if confirm.lower() == 'y':
                break
        
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/red]")
            console.print("[dim]Type 'exit' to quit or continue querying[/dim]")


def single_query_mode(query: str, output_file: str = None):
    """Run HAWK-AI with a single query."""
    console.print("[cyan]Initializing HAWK-AI...[/cyan]")
    
    # Initialize system
    register_all_agents()
    orchestrator = get_orchestrator()
    
    # Execute query
    console.print(f"\n[bold cyan]Processing query:[/bold cyan] {query}\n")
    result = orchestrator.execute_task(query)
    
    # Display result
    if result['status'] == 'success':
        console.print(f"\n[bold green]Result:[/bold green]")
        console.print(result['result'])
        console.print(f"\n[dim]Completed in {result['duration']:.2f}s[/dim]")
        
        # Save to file if requested
        if output_file:
            Path(output_file).write_text(result['result'])
            console.print(f"\n[green]✓ Result saved to {output_file}[/green]")
    else:
        console.print(f"\n[bold red]Error:[/bold red] {result.get('error', 'Unknown error')}")
        sys.exit(1)


def dev_mode():
    """Run HAWK-AI in development mode with status display."""
    print_banner()
    console.print("\n[bold yellow]Development Mode[/bold yellow]\n")
    
    # Initialize and show status
    console.print("[cyan]Initializing system...[/cyan]")
    register_all_agents()
    orchestrator = get_orchestrator()
    
    console.print("\n[bold]System Status:[/bold]")
    orchestrator.display_status()
    
    console.print("\n[green]✓ System initialized successfully[/green]")
    console.print("\n[dim]Use --chat to enter interactive mode[/dim]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HAWK-AI: Local OSINT-capable Reasoning Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --chat                                  # Interactive mode
  %(prog)s "Analyze conflicts in Sudan"            # Single query
  %(prog)s "Search for latest news" -o result.txt  # Save output
  %(prog)s --dev                                   # Development mode
  %(prog)s --status                                # Show system status
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Query to process (omit for interactive mode)'
    )
    
    parser.add_argument(
        '--chat', '-c',
        action='store_true',
        help='Enter interactive chat mode'
    )
    
    parser.add_argument(
        '--output', '-o',
        metavar='FILE',
        help='Save output to file'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode (show system status)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='HAWK-AI v1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Development mode
        if args.dev:
            dev_mode()
        
        # Status only
        elif args.status:
            register_all_agents()
            orchestrator = get_orchestrator()
            orchestrator.display_status()
        
        # Interactive mode
        elif args.chat or (not args.query and not sys.stdin.isatty()):
            interactive_mode()
        
        # Single query mode
        elif args.query:
            single_query_mode(args.query, args.output)
        
        # No arguments - default to interactive
        else:
            interactive_mode()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Goodbye![/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()

