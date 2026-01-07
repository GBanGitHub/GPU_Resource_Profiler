#!/usr/bin/env python3
"""
Unified CLI entry point for GPU Resource Profiler.
"""

import click
import sys
from pathlib import Path

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """GPU Resource Profiler - Monitor and analyze GPU usage."""
    pass

@cli.command()
@click.option('--output-dir', default='profiles', help='Directory to store profile data')
@click.option('--interval', type=float, default=1.0, help='Sampling interval in seconds')
@click.option('--duration', type=float, help='Duration to profile in seconds (optional)')
def profile(output_dir, interval, duration):
    """Start profiling GPU resources."""
    from src.profiler import GPUProfiler

    click.echo(f"Starting GPU profiling...")
    click.echo(f"  Output directory: {output_dir}")
    click.echo(f"  Sampling interval: {interval}s")
    if duration:
        click.echo(f"  Duration: {duration}s")
    else:
        click.echo(f"  Duration: Until interrupted (Ctrl+C)")

    profiler = GPUProfiler(
        output_dir=output_dir,
        sampling_interval=interval
    )
    profiler.start_profiling(duration=duration)

@cli.command()
@click.option('--host', default='localhost', help='Host to bind the dashboard')
@click.option('--port', type=int, default=8050, help='Port to bind the dashboard')
@click.option('--config', default='config/config.yaml', help='Path to config file')
def dashboard(host, port, config):
    """Launch the web dashboard for visualization."""
    import yaml
    import os

    click.echo(f"Starting GPU Profiler Dashboard...")
    click.echo(f"  Dashboard URL: http://{host}:{port}")
    click.echo(f"  Config file: {config}")

    # Load config
    if os.path.exists(config):
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
    else:
        click.echo(f"Warning: Config file not found at {config}, using defaults")
        config_data = {
            'dashboard': {
                'host': host,
                'port': port,
                'refresh_interval': 1.0,
                'theme': 'dark'
            },
            'profiling': {
                'output_dir': 'profiles'
            }
        }

    # Override with CLI arguments
    config_data['dashboard']['host'] = host
    config_data['dashboard']['port'] = port

    # Import and run dashboard
    from src.dashboard import app
    app.run(
        host=host,
        port=port,
        debug=False
    )

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind the API server')
@click.option('--port', type=int, default=8000, help='Port to bind the API server')
def api(host, port):
    """Start the REST API server."""
    import uvicorn

    click.echo(f"Starting GPU Profiler API...")
    click.echo(f"  API URL: http://{host}:{port}")
    click.echo(f"  Docs: http://{host}:{port}/docs")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        log_level="info"
    )

@cli.command()
def info():
    """Display GPU information."""
    from src.utils.gpu import GPUMonitor
    from rich.console import Console
    from rich.table import Table

    console = Console()

    try:
        monitor = GPUMonitor()
        gpu_count = monitor.get_gpu_count()

        console.print(f"\n[bold green]Found {gpu_count} GPU(s)[/bold green]\n")

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Name")
        table.add_column("Utilization", justify="right")
        table.add_column("Memory Used", justify="right")
        table.add_column("Memory Total", justify="right")
        table.add_column("Temperature", justify="right")
        table.add_column("Power", justify="right")

        stats = monitor.get_all_gpu_stats()
        for stat in stats:
            table.add_row(
                str(stat.device_id),
                stat.name,
                f"{stat.utilization:.1f}%",
                f"{stat.memory_used} MB",
                f"{stat.memory_total} MB",
                f"{stat.temperature}°C",
                f"{stat.power_usage:.1f}W"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('profile_file', type=click.Path(exists=True))
@click.option('--config', default='config/config.yaml', help='Path to config file')
def analyze(profile_file, config):
    """Analyze a profile file and generate insights."""
    import json
    import yaml
    import os
    import pandas as pd
    from rich.console import Console
    from rich.table import Table
    from src.analysis import PerformanceAnalyzer

    console = Console()

    # Load config
    if os.path.exists(config):
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
    else:
        console.print(f"[yellow]Warning:[/yellow] Config file not found, using defaults")
        config_data = {
            'alerts': {
                'gpu': {
                    'utilization': {'warning': 90, 'critical': 95},
                    'memory': {'warning': 85, 'critical': 90},
                    'temperature': {'warning': 80, 'critical': 85},
                    'power': {'warning': 90, 'critical': 95}
                }
            }
        }

    # Load profile
    console.print(f"\n[bold]Analyzing profile:[/bold] {profile_file}\n")

    with open(profile_file, 'r') as f:
        data = json.load(f)

    # Convert to DataFrame
    gpu_stats = []
    for sample in data['gpu_stats']:
        for gpu in sample:
            gpu_stats.append(gpu)

    df = pd.DataFrame(gpu_stats)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Analyze
    analyzer = PerformanceAnalyzer(config_data)
    insights = analyzer.analyze_profile(df)

    # Display insights
    if not insights:
        console.print("[green]No performance issues detected![/green]")
    else:
        console.print(f"[bold]Found {len(insights)} insight(s):[/bold]\n")

        for insight in insights:
            severity_color = {
                'info': 'blue',
                'warning': 'yellow',
                'critical': 'red'
            }.get(insight.severity, 'white')

            console.print(f"[{severity_color}]{insight.severity.upper()}[/{severity_color}] {insight.message}")
            console.print(f"  Metric: {insight.metric} = {insight.value:.2f} (threshold: {insight.threshold})")
            console.print(f"  Suggestion: {insight.suggestion}\n")

@cli.command()
def list_profiles():
    """List available profile files."""
    from pathlib import Path
    from rich.console import Console
    from rich.table import Table
    import os

    console = Console()
    profile_dir = Path('profiles')

    if not profile_dir.exists():
        console.print("[yellow]No profiles directory found[/yellow]")
        return

    profiles = sorted(profile_dir.glob('profile_*.json'), key=os.path.getmtime, reverse=True)

    if not profiles:
        console.print("[yellow]No profile files found[/yellow]")
        return

    console.print(f"\n[bold]Found {len(profiles)} profile(s):[/bold]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Size", justify="right")
    table.add_column("Modified", justify="right")

    for profile in profiles:
        size = profile.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
        mtime = profile.stat().st_mtime
        from datetime import datetime
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

        table.add_row(profile.name, size_str, mtime_str)

    console.print(table)

def main():
    """Main entry point."""
    cli()

if __name__ == '__main__':
    main()
