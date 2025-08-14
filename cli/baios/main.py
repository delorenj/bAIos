#!/usr/bin/env python3
"""
bAIos CLI main entry point.

This module provides the main CLI interface using Typer for command-line
argument parsing and Rich for enhanced terminal output.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from . import __version__
from .commands import check

# Initialize Typer app and Rich console
app = typer.Typer(
    name="baios",
    help="🤖 bAIos - AI-powered workspace management and automation CLI",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()

# Add subcommands
app.add_typer(check.app, name="check", help="🔍 System and workspace checks")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v", 
        help="Show version information",
        is_flag=True
    ),
    verbose: Optional[bool] = typer.Option(
        False, 
        "--verbose", 
        help="Enable verbose output",
        is_flag=True
    )
):
    """
    🤖 bAIos - AI-powered workspace management and automation CLI
    
    Welcome to bAIos, your intelligent workspace companion!
    """
    if version:
        rprint(f"[bold green]bAIos[/bold green] version [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()
    
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@app.command()
def hello(
    name: str = typer.Argument("World", help="Name to greet")
):
    """
    👋 Say hello (example command)
    """
    rprint(f"[bold green]Hello[/bold green] [bold cyan]{name}[/bold cyan] from bAIos! 🤖")


@app.command()
def status():
    """
    📊 Show bAIos system status
    """
    table = Table(title="🤖 bAIos System Status")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")
    
    table.add_row("CLI", "✅ Active", f"v{__version__}")
    table.add_row("Workspace", "🔍 Scanning", "Checking...")
    table.add_row("AI Services", "⏸️  Standby", "Ready to activate")
    
    console.print(table)
    rprint("\n[bold green]bAIos is ready to assist! 🚀[/bold green]")


if __name__ == "__main__":
    app()