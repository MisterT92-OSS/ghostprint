"""
GhostPrint - OSINT CLI Tool
Main CLI interface using Click
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys

console = Console()

@click.group()
@click.version_option(version="0.1.0", prog_name="ghostprint")
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, verbose):
    """
    👻 GhostPrint - OSINT CLI Tool
    
    Find digital footprints from a single identifier.
    
    Examples:
        ghostprint email user@example.com
        ghostprint username johndoe
        ghostprint phone +33612345678
        ghostprint domain example.com
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # Banner
    console.print(Panel.fit(
        "[bold cyan]👻 GhostPrint[/bold cyan] [dim]v0.1.0[/dim]\n"
        "[dim]OSINT CLI Tool - Find digital footprints[/dim]",
        border_style="cyan"
    ))

@cli.command()
@click.argument('email')
@click.option('--breaches', '-b', is_flag=True, help='Check breach databases')
@click.option('--social', '-s', is_flag=True, help='Find social profiles')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def email(ctx, email, breaches, social, output):
    """🔍 Investigate an email address"""
    console.print(f"\n[bold]Investigating email:[/bold] {email}\n")
    
    from ghostprint.modules.email import EmailInvestigator
    
    investigator = EmailInvestigator(verbose=ctx.obj.get('verbose'))
    results = investigator.investigate(
        email=email,
        check_breaches=breaches or not social,  # Default to breaches if no flag
        check_social=social
    )
    
    _display_results(results, output)

@cli.command()
@click.argument('username')
@click.option('--platforms', '-p', multiple=True, help='Specific platforms to check')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def username(ctx, username, platforms, output):
    """🔍 Investigate a username across platforms"""
    console.print(f"\n[bold]Investigating username:[/bold] {username}\n")
    
    from ghostprint.modules.username import UsernameInvestigator
    
    investigator = UsernameInvestigator(verbose=ctx.obj.get('verbose'))
    results = investigator.investigate(
        username=username,
        platforms=list(platforms) if platforms else None
    )
    
    _display_results(results, output)

@cli.command()
@click.argument('phone')
@click.option('--carrier', '-c', is_flag=True, help='Check carrier info')
@click.option('--social', '-s', is_flag=True, help='Find social accounts')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def phone(ctx, phone, carrier, social, output):
    """🔍 Investigate a phone number"""
    console.print(f"\n[bold]Investigating phone:[/bold] {phone}\n")
    
    from ghostprint.modules.phone import PhoneInvestigator
    
    investigator = PhoneInvestigator(verbose=ctx.obj.get('verbose'))
    results = investigator.investigate(
        phone=phone,
        check_carrier=carrier,
        check_social=social
    )
    
    _display_results(results, output)

@cli.command()
@click.argument('domain')
@click.option('--subdomains', '-s', is_flag=True, help='Enumerate subdomains')
@click.option('--dns', '-d', is_flag=True, help='Check DNS records')
@click.option('--whois', '-w', is_flag=True, help='WHOIS lookup')
@click.option('--tech', '-t', is_flag=True, help='Detect technologies')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def domain(ctx, domain, subdomains, dns, whois, tech, output):
    """🔍 Investigate a domain"""
    console.print(f"\n[bold]Investigating domain:[/bold] {domain}\n")
    
    from ghostprint.modules.domain import DomainInvestigator
    
    investigator = DomainInvestigator(verbose=ctx.obj.get('verbose'))
    results = investigator.investigate(
        domain=domain,
        enumerate_subdomains=subdomains or True,
        check_dns=dns or True,
        check_whois=whois or True,
        detect_tech=tech
    )
    
    _display_results(results, output)

def _display_results(results, output_format):
    """Display results in chosen format"""
    if output_format == 'json':
        import json
        console.print(json.dumps(results, indent=2))
    elif output_format == 'csv':
        # Simple CSV output
        for key, value in results.items():
            if isinstance(value, list):
                for item in value:
                    console.print(f"{key},{item}")
            else:
                console.print(f"{key},{value}")
    else:
        # Table format
        table = Table(title="Results")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in results.items():
            if isinstance(value, list):
                table.add_row(key, "\n".join(str(v) for v in value))
            else:
                table.add_row(key, str(value))
        
        console.print(table)

def main():
    """Entry point"""
    cli()

if __name__ == '__main__':
    main()