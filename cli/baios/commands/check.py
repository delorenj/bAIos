#!/usr/bin/env python3
"""
bAIos CLI check commands.

This module provides system and workspace checking functionality
for the bAIos CLI tool.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from typer import Context
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from ..models.inventory import InventoryStatus
from ..parsers.inventory_parser import InventoryParser
from ..parsers.inventory_evaluator import InventoryEvaluator

app = typer.Typer(help="🔍 System and workspace checks")
console = Console()


@app.callback(invoke_without_command=True)
def check_callback(
    ctx: Context,
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed inventory status"),
    evaluate: bool = typer.Option(True, "--evaluate/--no-evaluate", help="Evaluate current system status"),
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Filter by specific section")
):
    """🔍 System and workspace checks
    
    When run without a subcommand, performs inventory check by default.
    """
    if ctx.invoked_subcommand is None:
        # Run inventory check by default when no subcommand is provided
        inventory(detailed=detailed, evaluate=evaluate, section=section)


@app.command()
def system(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed system information")
):
    """
    🖥️ Check system requirements and environment
    """
    rprint("[bold blue]🔍 Running system checks...[/bold blue]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking system...", total=None)
        
        checks = []
        
        # Python version check
        python_version = platform.python_version()
        python_ok = sys.version_info >= (3, 8)
        checks.append({
            "component": "Python",
            "status": "✅ OK" if python_ok else "❌ FAIL",
            "details": f"v{python_version}" + ("" if python_ok else " (requires 3.8+)")
        })
        
        # Platform info
        system_info = platform.system()
        checks.append({
            "component": "Platform",
            "status": "ℹ️  INFO",
            "details": f"{system_info} {platform.release()}"
        })
        
        # Git check
        try:
            git_version = subprocess.check_output(
                ["git", "--version"], 
                text=True, 
                stderr=subprocess.DEVNULL
            ).strip()
            checks.append({
                "component": "Git",
                "status": "✅ OK",
                "details": git_version.replace("git version ", "v")
            })
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks.append({
                "component": "Git",
                "status": "❌ MISSING",
                "details": "Git not found in PATH"
            })
        
        # Node.js check (for potential integrations)
        try:
            node_version = subprocess.check_output(
                ["node", "--version"], 
                text=True, 
                stderr=subprocess.DEVNULL
            ).strip()
            checks.append({
                "component": "Node.js",
                "status": "✅ OK",
                "details": node_version
            })
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks.append({
                "component": "Node.js",
                "status": "⚠️  OPTIONAL",
                "details": "Not required but recommended"
            })
        
        progress.update(task, completed=True)
    
    # Display results
    table = Table(title="🖥️ System Check Results")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")
    
    for check in checks:
        table.add_row(check["component"], check["status"], check["details"])
    
    console.print(table)
    
    if verbose:
        rprint(f"\n[dim]Additional System Information:[/dim]")
        rprint(f"[dim]• Architecture: {platform.machine()}[/dim]")
        rprint(f"[dim]• Processor: {platform.processor() or 'Unknown'}[/dim]")
        rprint(f"[dim]• Python Executable: {sys.executable}[/dim]")


@app.command()
def workspace(
    path: Optional[str] = typer.Argument(None, help="Path to workspace (default: current directory)")
):
    """
    📁 Check current workspace configuration and health
    """
    workspace_path = Path(path) if path else Path.cwd()
    
    rprint(f"[bold blue]🔍 Checking workspace: [cyan]{workspace_path.absolute()}[/cyan][/bold blue]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning workspace...", total=None)
        
        checks = []
        
        # Workspace exists and is accessible
        if workspace_path.exists() and workspace_path.is_dir():
            checks.append({
                "component": "Workspace Access",
                "status": "✅ OK",
                "details": "Directory accessible"
            })
        else:
            checks.append({
                "component": "Workspace Access",
                "status": "❌ FAIL",
                "details": "Directory not found or not accessible"
            })
            console.print(table)
            return
        
        # Git repository check
        git_dir = workspace_path / ".git"
        if git_dir.exists():
            checks.append({
                "component": "Git Repository",
                "status": "✅ OK",
                "details": "Git repository detected"
            })
            
            # Check for uncommitted changes
            try:
                os.chdir(workspace_path)
                result = subprocess.run(
                    ["git", "status", "--porcelain"], 
                    capture_output=True, 
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    checks.append({
                        "component": "Git Status",
                        "status": "⚠️  CHANGES",
                        "details": "Uncommitted changes detected"
                    })
                else:
                    checks.append({
                        "component": "Git Status",
                        "status": "✅ CLEAN",
                        "details": "Working directory clean"
                    })
            except subprocess.CalledProcessError:
                checks.append({
                    "component": "Git Status",
                    "status": "❌ ERROR",
                    "details": "Could not check git status"
                })
        else:
            checks.append({
                "component": "Git Repository",
                "status": "ℹ️  NONE",
                "details": "No git repository found"
            })
        
        # Check for common configuration files
        config_files = [
            (".env", "Environment configuration"),
            ("package.json", "Node.js project"),
            ("requirements.txt", "Python requirements"),
            ("pyproject.toml", "Python project"),
            ("Dockerfile", "Docker configuration"),
            ("docker-compose.yml", "Docker Compose"),
            ("README.md", "Project documentation"),
            ("CLAUDE.md", "Claude configuration")
        ]
        
        found_configs = []
        for filename, description in config_files:
            if (workspace_path / filename).exists():
                found_configs.append(f"{filename} ({description})")
        
        if found_configs:
            checks.append({
                "component": "Configuration Files",
                "status": "✅ FOUND",
                "details": f"{len(found_configs)} config file(s)"
            })
        else:
            checks.append({
                "component": "Configuration Files",
                "status": "ℹ️  NONE",
                "details": "No common config files found"
            })
        
        progress.update(task, completed=True)
    
    # Display results
    table = Table(title="📁 Workspace Check Results")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")
    
    for check in checks:
        table.add_row(check["component"], check["status"], check["details"])
    
    console.print(table)
    
    if found_configs:
        rprint(f"\n[bold]Found configuration files:[/bold]")
        for config in found_configs:
            rprint(f"  • {config}")


@app.command()
def all(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """
    🔍 Run all available checks
    """
    rprint("[bold green]🤖 Running comprehensive bAIos checks...[/bold green]\n")
    
    # Run system check
    rprint("[bold blue]═══ System Check ═══[/bold blue]")
    system(verbose=verbose)
    
    rprint("\n")
    
    # Run workspace check
    rprint("[bold blue]═══ Workspace Check ═══[/bold blue]")
    workspace()
    
    rprint(f"\n[bold green]✨ bAIos checks completed![/bold green]")


@app.command()
def health():
    """
    💚 Quick health check with summary
    """
    rprint("[bold green]💚 bAIos Health Check[/bold green]\n")
    
    # Quick system essentials
    python_ok = sys.version_info >= (3, 8)
    git_available = True
    
    try:
        subprocess.check_output(["git", "--version"], stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_available = False
    
    workspace_ok = Path.cwd().exists()
    
    if python_ok and git_available and workspace_ok:
        status_color = "green"
        status_text = "🟢 HEALTHY"
        message = "All essential components are working properly!"
    elif python_ok and workspace_ok:
        status_color = "yellow"
        status_text = "🟡 MOSTLY HEALTHY"
        message = "Core components OK, some optional tools missing."
    else:
        status_color = "red"
        status_text = "🔴 ISSUES DETECTED"
        message = "Critical components need attention."
    
    panel = Panel.fit(
        f"[bold]{status_text}[/bold]\n\n{message}",
        title="Health Status",
        border_style=status_color
    )
    console.print(panel)
    
    rprint(f"\n[dim]Run '[bold]baios check all[/bold]' for detailed diagnostics.[/dim]")


@app.command()
def inventory(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed inventory status"),
    evaluate: bool = typer.Option(True, "--evaluate/--no-evaluate", help="Evaluate current system status"),
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Filter by specific section")
):
    """
    📋 Check bAIos inventory requirements and status
    """
    rprint("[bold blue]📋 Checking bAIos inventory requirements...[/bold blue]\n")
    
    try:
        # Parse the inventory
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            parse_task = progress.add_task("Parsing inventory...", total=None)
            
            parser = InventoryParser()
            report = parser.parse()
            
            progress.update(parse_task, completed=True)
            
            if evaluate:
                eval_task = progress.add_task("Evaluating system status...", total=None)
                evaluator = InventoryEvaluator()
                report = evaluator.evaluate_report(report)
                progress.update(eval_task, completed=True)
        
        # Filter by section if requested
        sections_to_show = report.sections
        if section:
            sections_to_show = [s for s in report.sections if section.lower() in s.name.lower()]
            if not sections_to_show:
                rprint(f"[red]No sections found matching '{section}'[/red]")
                return
        
        # Display overall summary
        _display_inventory_summary(report)
        
        # Display sections
        for section_obj in sections_to_show:
            _display_inventory_section(section_obj, detailed)
        
        # Display environment keys
        if report.env_keys:
            _display_env_keys(report.env_keys)
        
        # Display recommendations
        _display_inventory_recommendations(report)
        
    except FileNotFoundError as e:
        rprint(f"[red]❌ Inventory file not found: {e}[/red]")
        rprint("[yellow]Make sure docs/INVENTORY.md exists in the project root.[/yellow]")
    except Exception as e:
        rprint(f"[red]❌ Error processing inventory: {e}[/red]")
        if detailed:
            import traceback
            rprint("[dim]" + traceback.format_exc() + "[/dim]")


def _display_inventory_summary(report):
    """Display overall inventory summary."""
    total_items = report.total_items
    completed = report.completed_items
    failed_critical = report.failed_critical_items
    completion_pct = report.overall_completion_percentage
    
    status_color = "green" if completion_pct >= 80 else "yellow" if completion_pct >= 50 else "red"
    status_emoji = "✅" if completion_pct >= 80 else "⚠️" if completion_pct >= 50 else "❌"
    
    summary_table = Table(title="📊 Overall Inventory Status")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="bold")
    
    summary_table.add_row("Total Items", str(total_items))
    summary_table.add_row("Completed", f"[green]{completed}[/green]")
    summary_table.add_row("Failed (Critical)", f"[red]{failed_critical}[/red]" if failed_critical else "0")
    summary_table.add_row("Completion", f"[{status_color}]{completion_pct:.1f}%[/{status_color}]")
    
    console.print(summary_table)
    
    # Overall status panel
    if completion_pct >= 80 and failed_critical == 0:
        status_msg = "System is ready! Most requirements are satisfied."
        panel_style = "green"
    elif completion_pct >= 50:
        status_msg = "System partially ready. Some requirements need attention."
        panel_style = "yellow"
    else:
        status_msg = "System needs setup. Many requirements are not satisfied."
        panel_style = "red"
    
    status_panel = Panel.fit(
        f"[bold]{status_emoji} {status_msg}[/bold]",
        title="System Status",
        border_style=panel_style
    )
    console.print(status_panel)
    rprint("")


def _display_inventory_section(section, detailed=False):
    """Display a single inventory section."""
    # Section header
    completion = section.completion_percentage
    status_color = "green" if completion >= 80 else "yellow" if completion >= 50 else "red"
    
    rprint(f"[bold blue]═══ {section.name} ({completion:.1f}% complete) ═══[/bold blue]")
    
    if detailed:
        # Detailed view with all items
        section_table = Table()
        section_table.add_column("Status", width=8)
        section_table.add_column("Requirement", style="cyan", no_wrap=False)
        section_table.add_column("Details", style="dim", no_wrap=False)
        
        for item in section.items:
            status_str = item.status.emoji + " " + item.status.name.replace('_', ' ').title()
            details = item.details if item.details else "No details available"
            
            section_table.add_row(
                f"[{item.status.color}]{status_str}[/{item.status.color}]",
                item.description,
                details
            )
        
        console.print(section_table)
    else:
        # Summary view with status counts
        status_summary = section.status_summary
        
        # Create a tree view for better organization
        tree = Tree(f"[bold]{section.name}[/bold]")
        
        # Group by status
        for status in InventoryStatus:
            count = status_summary.get(status.value, 0)
            if count > 0:
                status_branch = tree.add(f"[{status.color}]{status} ({count})[/{status.color}]")
                
                # Add items for this status (limit to show space)
                items_with_status = [item for item in section.items if item.status == status]
                for item in items_with_status[:3]:  # Show first 3
                    status_branch.add(f"[dim]{item.description[:60]}{'...' if len(item.description) > 60 else ''}[/dim]")
                
                if len(items_with_status) > 3:
                    status_branch.add(f"[dim]... and {len(items_with_status) - 3} more[/dim]")
        
        console.print(tree)
    
    rprint("")


def _display_env_keys(env_keys):
    """Display required environment keys."""
    rprint("[bold blue]═══ Required Environment Keys ═══[/bold blue]")
    
    env_table = Table()
    env_table.add_column("Key", style="cyan")
    env_table.add_column("Status", style="magenta")
    env_table.add_column("Details", style="dim")
    
    for key in env_keys:
        value = os.environ.get(key)
        if value:
            status = "✅ Set"
            details = f"Value: {'*' * min(len(value), 8)}{'...' if len(value) > 8 else ''}"
        else:
            status = "❌ Missing"
            details = "Environment variable not set"
        
        env_table.add_row(key, status, details)
    
    console.print(env_table)
    rprint("")


def _display_inventory_recommendations(report):
    """Display recommendations based on inventory status."""
    # Get critical items that need attention
    critical_items = [item for item in report.get_all_items() 
                     if item.is_critical and item.needs_attention]
    
    if critical_items:
        rprint("[bold red]🚨 Critical Items Needing Attention:[/bold red]")
        
        for item in critical_items[:5]:  # Show top 5
            rprint(f"  • [red]{item.description}[/red]")
            if item.install_command:
                rprint(f"    [dim]Install: {item.install_command}[/dim]")
        
        if len(critical_items) > 5:
            rprint(f"  [dim]... and {len(critical_items) - 5} more critical items[/dim]")
        
        rprint("")
    
    # Show next steps
    incomplete_items = [item for item in report.get_all_items() if item.needs_attention]
    if incomplete_items:
        rprint("[bold yellow]📝 Next Steps:[/bold yellow]")
        rprint("  1. Address critical items first (marked in red)")
        rprint("  2. Run 'baios check inventory --detailed' for complete item list")
        rprint("  3. Use install commands shown above to resolve issues")
        rprint("  4. Re-run this check to verify progress")
        rprint("")


if __name__ == "__main__":
    app()