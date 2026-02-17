"""
Command-line interface for BT-SecTester.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from bt_sectester.core.engine import BTSecEngine
from bt_sectester.modules.attacks.attack_simulator import AttackType
from bt_sectester.modules.reporting.report_generator import ReportGenerator
from bt_sectester.utils.config import Config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], debug: bool) -> None:
    """BT-SecTester - Bluetooth Security Testing Framework."""
    # Load configuration
    cfg = Config.load(config) if config else Config.load()

    if debug:
        cfg.set("logging.level", "DEBUG")

    ctx.obj = {"config": cfg}


@cli.command()
@click.option("--duration", "-d", type=int, default=10, help="Scan duration in seconds")
@click.option("--classic/--no-classic", default=True, help="Scan for Classic Bluetooth")
@click.option("--ble/--no-ble", default=True, help="Scan for BLE devices")
@click.option("--output", "-o", type=click.Path(), help="Save results to JSON file")
@click.pass_context
def scan(
    ctx: click.Context,
    duration: int,
    classic: bool,
    ble: bool,
    output: Optional[str],
) -> None:
    """Scan for Bluetooth devices."""
    config = ctx.obj["config"]

    console.print(f"\n[bold cyan]Starting Bluetooth scan...[/bold cyan]")
    console.print(f"Duration: {duration}s | Classic: {classic} | BLE: {ble}\n")

    try:
        engine = BTSecEngine(config)
        devices = engine.scan_devices(duration=duration, classic=classic, ble=ble)

        if not devices:
            console.print("[yellow]No devices found.[/yellow]")
            return

        # Display results in a table
        table = Table(title=f"Discovered Devices ({len(devices)})")
        table.add_column("MAC Address", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("RSSI", style="yellow")

        for device in devices:
            table.add_row(
                device.get("mac", "N/A"),
                device.get("name", "Unknown"),
                device.get("type", "N/A"),
                f"{device.get('rssi', 'N/A')} dBm" if device.get("rssi") else "N/A",
            )

        console.print(table)

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(devices, f, indent=2)
            console.print(f"\n[green]Results saved to {output}[/green]")

        engine.shutdown()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("mac")
@click.option("--output", "-o", type=click.Path(), help="Save results to JSON file")
@click.pass_context
def enumerate(ctx: click.Context, mac: str, output: Optional[str]) -> None:
    """Enumerate services for a device."""
    config = ctx.obj["config"]

    console.print(f"\n[bold cyan]Enumerating services for {mac}...[/bold cyan]\n")

    try:
        engine = BTSecEngine(config)
        services = engine.enumerate_services(mac)

        service_list = services.get("services", [])

        if not service_list:
            console.print("[yellow]No services found.[/yellow]")
            return

        # Display results
        table = Table(title=f"Services for {mac}")
        table.add_column("Name", style="cyan")
        table.add_column("UUID/Protocol", style="green")
        table.add_column("Details", style="yellow")

        for service in service_list:
            name = service.get("name", service.get("description", "Unknown"))
            uuid = service.get("uuid", service.get("protocol", "N/A"))
            details = service.get("port", service.get("properties", ""))

            table.add_row(name, uuid, str(details))

        console.print(table)

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(services, f, indent=2)
            console.print(f"\n[green]Results saved to {output}[/green]")

        engine.shutdown()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("attack_type", type=click.Choice(["dos", "deauth", "sniff", "pin-brute"]))
@click.argument("target")
@click.option("--duration", "-d", type=int, help="Attack duration in seconds")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def simulate(
    ctx: click.Context,
    attack_type: str,
    target: str,
    duration: Optional[int],
    yes: bool,
) -> None:
    """Execute security simulation."""
    config = ctx.obj["config"]

    # Map CLI attack type to enum
    attack_map = {
        "dos": AttackType.DOS_FLOOD,
        "deauth": AttackType.DEAUTH,
        "sniff": AttackType.SNIFF,
        "pin-brute": AttackType.PIN_BRUTE,
    }

    attack_enum = attack_map[attack_type]

    console.print(f"\n[bold yellow]⚠️  WARNING ⚠️[/bold yellow]")
    console.print(f"You are about to simulate: [bold]{attack_type.upper()}[/bold]")
    console.print(f"Target: [cyan]{target}[/cyan]")
    console.print(f"Duration: [cyan]{duration or 'N/A'}[/cyan] seconds\n")

    if not yes:
        console.print("[yellow]This action requires authorization.[/yellow]")
        response = input("Do you have authorization to test this device? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            console.print("[red]Operation cancelled.[/red]")
            return

    try:
        engine = BTSecEngine(config)

        # Import attack simulator from engine
        from bt_sectester.modules.attacks.attack_simulator import AttackSimulator

        simulator = AttackSimulator(
            privilege_manager=engine.privilege_manager,
            ethical_mode=config.app.ethical_mode,
            require_confirmation=not yes,
        )

        console.print(f"\n[bold cyan]Executing {attack_type} attack...[/bold cyan]\n")

        result = simulator.execute_attack(
            attack_type=attack_enum,
            target=target,
            duration=duration,
        )

        # Display result
        console.print(f"\n[bold]Attack Result:[/bold]")
        console.print(f"Status: [{'green' if result.status.value == 'success' else 'red'}]{result.status.value}[/]")
        console.print(f"Duration: {(result.end_time - result.start_time).total_seconds():.2f}s")

        if result.details:
            console.print("\nDetails:")
            for key, value in result.details.items():
                console.print(f"  {key}: {value}")

        if result.errors:
            console.print("\n[red]Errors:[/red]")
            for error in result.errors:
                console.print(f"  - {error}")

        engine.shutdown()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("session_id")
@click.option("--format", "-f", type=click.Choice(["pdf", "html"]), default="pdf", help="Report format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def report(ctx: click.Context, session_id: str, format: str, output: Optional[str]) -> None:
    """Generate report from session data."""
    config = ctx.obj["config"]

    console.print(f"\n[bold cyan]Generating {format.upper()} report...[/bold cyan]\n")

    try:
        # Load session data
        session_file = Path("sessions") / f"{session_id}.json"
        if not session_file.exists():
            console.print(f"[red]Session file not found: {session_file}[/red]")
            sys.exit(1)

        with open(session_file, "r") as f:
            session_data = json.load(f)

        # Generate report
        generator = ReportGenerator(
            output_dir=Path(config.reporting.get("output_dir", "reports")),
            company_name=config.reporting.get("company_name", "Security Assessment"),
        )

        if format == "pdf":
            report_path = generator.generate_pdf_report(session_data, output_filename=output)
        else:
            report_path = generator.generate_html_report(session_data, output_filename=output)

        console.print(f"[green]✓ Report generated:[/green] {report_path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def main() -> None:
    """CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
