#!/usr/bin/env python3
"""
bAIos CLI agent commands.

This module provides agent management and interaction functionality
for the bAIos CLI tool.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import the agent system
from ..agents.agent_registry import agent_registry

app = typer.Typer(help="🤖 Agent management and interaction")
console = Console()


@app.command()
def list(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed information")
):
    """
    📋 List all available agents
    
    Shows all registered agents with their capabilities and specializations.
    """
    rprint("[bold blue]🤖 Available bAIos Agents[/bold blue]\n")
    
    agents = agent_registry.list_agents()
    
    if not agents:
        rprint("[yellow]No agents available.[/yellow]")
        return
    
    if detailed:
        # Detailed view
        for i, agent in enumerate(agents, 1):
            rprint(f"[bold blue]{i}. {agent.name}[/bold blue]")
            rprint(f"   [italic]{agent.expertise}[/italic]")
            if hasattr(agent, 'personality') and agent.personality:
                rprint(f"   [dim]{agent.personality}[/dim]")
            rprint()
    else:
        # Table view
        table = Table(title="🤖 bAIos Agents")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Expertise", style="green")
        
        for agent in agents:
            table.add_row(agent.name, agent.expertise)
        
        console.print(table)
    
    rprint(f"\n[dim]💡 Use '[bold]baios agent ask <agent_name> \"<question>\"[/bold]' to interact with an agent[/dim]")


@app.command()
def ask(
    agent_name: str = typer.Argument(..., help="Name of the agent to ask"),
    question: str = typer.Argument(..., help="Question to ask the agent"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show additional information")
):
    """
    💬 Ask a specific agent a question
    
    Interact with a specialized agent by asking questions in their domain of expertise.
    
    Examples:
    
        baios agent ask Shelldon "What is my default shell?"
        
        baios agent ask "Bill The Coordinator" "Help me set up a development environment"
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Consulting {agent_name}...", total=None)
        
        # Get the agent
        agent = agent_registry.get_agent(agent_name)
        
        if not agent:
            progress.stop()
            # Try to find similar agent names
            all_agents = agent_registry.list_agents()
            agent_names = [a.name.lower() for a in all_agents]
            
            rprint(f"[red]❌ Agent '{agent_name}' not found.[/red]\n")
            
            # Suggest similar names
            from difflib import get_close_matches
            suggestions = get_close_matches(agent_name.lower(), agent_names, n=3, cutoff=0.6)
            if suggestions:
                rprint("[yellow]Did you mean:[/yellow]")
                for suggestion in suggestions:
                    # Find the actual agent with this name
                    actual_agent = next(a for a in all_agents if a.name.lower() == suggestion)
                    rprint(f"  • [cyan]{actual_agent.name}[/cyan] - {actual_agent.expertise}")
            else:
                rprint("[yellow]Available agents:[/yellow]")
                for a in all_agents:
                    rprint(f"  • [cyan]{a.name}[/cyan] - {a.expertise}")
            
            rprint(f"\n[dim]Use '[bold]baios agent list[/bold]' to see all available agents.[/dim]")
            raise typer.Exit(1)
        
        progress.update(task, description=f"Getting response from {agent.name}...")
        
        # Ask the agent
        try:
            response = agent.ask(question)
            progress.update(task, completed=True)
        except Exception as e:
            progress.stop()
            rprint(f"[red]❌ Error getting response from {agent.name}: {e}[/red]")
            raise typer.Exit(1)
    
    # Display the interaction
    rprint(f"\n[bold blue]🤖 {agent.name}[/bold blue]")
    rprint(f"[dim]❓ Question: {question}[/dim]\n")
    
    # Create a nice panel for the response
    response_panel = Panel(
        response,
        title=f"💬 {agent.name}'s Response",
        title_align="left",
        border_style="green",
        padding=(1, 2)
    )
    console.print(response_panel)
    
    if verbose:
        rprint(f"\n[dim]💡 {agent.name} specializes in: {agent.expertise}[/dim]")


@app.command()
def info(
    agent_name: str = typer.Argument(..., help="Name of the agent to get info about")
):
    """
    ℹ️  Get detailed information about a specific agent
    
    Shows comprehensive information about an agent including capabilities
    and specialization details.
    """
    agent = agent_registry.get_agent(agent_name)
    
    if not agent:
        all_agents = agent_registry.list_agents()
        agent_names = [a.name.lower() for a in all_agents]
        
        rprint(f"[red]❌ Agent '{agent_name}' not found.[/red]\n")
        
        # Suggest similar names
        from difflib import get_close_matches
        suggestions = get_close_matches(agent_name.lower(), agent_names, n=3, cutoff=0.6)
        if suggestions:
            rprint("[yellow]Did you mean:[/yellow]")
            for suggestion in suggestions:
                actual_agent = next(a for a in all_agents if a.name.lower() == suggestion)
                rprint(f"  • [cyan]{actual_agent.name}[/cyan]")
        
        raise typer.Exit(1)
    
    # Agent header
    rprint(f"[bold blue]🤖 {agent.name}[/bold blue]")
    rprint(f"[dim]{agent.expertise}[/dim]\n")
    
    # Basic information table
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Field", style="cyan", width=15)
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Name", agent.name)
    info_table.add_row("Expertise", agent.expertise)
    
    if hasattr(agent, 'personality') and agent.personality:
        info_table.add_row("Personality", agent.personality)
    
    console.print(info_table)
    
    rprint(f"\n[dim]💬 Try: [bold]baios agent ask \"{agent.name}\" \"<your question>\"[/bold][/dim]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (keywords)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results")
):
    """
    🔍 Search for agents by name or expertise
    
    Find agents that can help with specific topics or areas of expertise.
    """
    rprint(f"[bold blue]🔍 Searching agents for: [cyan]\"{query}\"[/cyan][/bold blue]\n")
    
    matches = agent_registry.find_agents_by_keyword(query)
    
    if not matches:
        rprint("[yellow]❌ No agents found matching your search.[/yellow]")
        rprint("[dim]Try broader keywords or use '[bold]baios agent list[/bold]' to see all agents.[/dim]")
        return
    
    # Limit results
    matches = matches[:limit]
    
    # Display results
    for i, agent in enumerate(matches, 1):
        rprint(f"[bold]{i}. [cyan]{agent.name}[/cyan][/bold]")
        rprint(f"   {agent.expertise}")
        
        if i < len(matches):
            rprint()
    
    rprint(f"\n[dim]💬 Try asking one of these agents: [bold]baios agent ask \"<agent_name>\" \"<question>\"[/bold][/dim]")


if __name__ == "__main__":
    app()