"""
GhostPrint Extended CLI - All features integrated
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio
import json

console = Console()

# Main CLI group
@click.group()
@click.version_option(version="0.2.0", prog_name="ghostprint")
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, verbose, config):
    """
    👻 GhostPrint v0.2.0 - Advanced OSINT Suite
    
    Multi-source intelligence gathering tool
    
    Commands:
        email       Email investigation + breaches
        username    Social media enumeration (50+ platforms)
        domain      Domain reconnaissance
        phone       Phone number lookup
        ip          Network intelligence
        metadata    File metadata extraction
        advanced    Advanced recon (Shodan, Censys, CT)
        full        Full investigation on target
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    console.print(Panel.fit(
        "[bold cyan]👻 GhostPrint[/bold cyan] [dim]v0.2.0[/dim]\n"
        "[dim]Advanced OSINT Suite - Multi-Source Intelligence[/dim]",
        border_style="cyan"
    ))


# EMAIL COMMAND
@cli.command()
@click.argument('email')
@click.option('--breaches', '-b', is_flag=True, help='Check breach databases')
@click.option('--social', '-s', is_flag=True, help='Find social profiles')
@click.option('--advanced', '-a', is_flag=True, help='Advanced checks')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def email(ctx, email, breaches, social, advanced, output):
    """📧 Email investigation with breach checks"""
    from ghostprint.modules.breach import BreachInvestigator
    from ghostprint.modules.email import EmailInvestigator
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Investigating email...", total=None)
        
        results = {'email': email}
        
        if breaches:
            progress.update(task, description="Checking breach databases...")
            breach_inv = BreachInvestigator(verbose=ctx.obj.get('verbose'))
            results['breaches'] = breach_inv.investigate(email)
        
        if social:
            progress.update(task, description="Searching social profiles...")
            email_inv = EmailInvestigator(verbose=ctx.obj.get('verbose'))
            results['social'] = email_inv.investigate(email, check_social=True)
    
    _display_results(results, output)


# USERNAME COMMAND (Extended)
@cli.command()
@click.argument('username')
@click.option('--platforms', '-p', multiple=True, help='Specific platforms')
@click.option('--extended', '-e', is_flag=True, help='Check 50+ platforms')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def username(ctx, username, platforms, extended, output):
    """👤 Username enumeration (50+ platforms)"""
    if extended:
        from ghostprint.modules.social_advanced import SocialMediaInvestigator
        inv = SocialMediaInvestigator(verbose=ctx.obj.get('verbose'))
    else:
        from ghostprint.modules.username import UsernameInvestigator
        inv = UsernameInvestigator(verbose=ctx.obj.get('verbose'))
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task(f"Searching {username}...", total=None)
        results = inv.investigate(username, platforms=list(platforms) if platforms else None)
    
    _display_results(results, output)


# DOMAIN COMMAND
@cli.command()
@click.argument('domain')
@click.option('--subdomains', '-s', is_flag=True, help='Enumerate subdomains')
@click.option('--dns', '-d', is_flag=True, help='DNS records')
@click.option('--whois', '-w', is_flag=True, help='WHOIS lookup')
@click.option('--tech', '-t', is_flag=True, help='Detect technologies')
@click.option('--advanced', '-a', is_flag=True, help='Certificate Transparency')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def domain(ctx, domain, subdomains, dns, whois, tech, advanced, output):
    """🌐 Domain reconnaissance"""
    from ghostprint.modules.domain import DomainInvestigator
    
    results = {'domain': domain}
    
    inv = DomainInvestigator(verbose=ctx.obj.get('verbose'))
    results.update(inv.investigate(
        domain=domain,
        enumerate_subdomains=subdomains or advanced,
        check_dns=dns or advanced,
        check_whois=whois,
        detect_tech=tech
    ))
    
    if advanced:
        from ghostprint.modules.advanced import AdvancedInvestigator
        adv_inv = AdvancedInvestigator()
        ct_results = adv_inv.investigate(domain, target_type='domain', use_ct=True)
        results['certificate_transparency'] = ct_results.get('certificate_transparency', [])
    
    _display_results(results, output)


# IP COMMAND
@cli.command()
@click.argument('ip')
@click.option('--ports', '-p', is_flag=True, help='Port scan')
@click.option('--shodan', '-s', is_flag=True, help='Shodan lookup (needs API key)')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def ip(ctx, ip, ports, shodan, output):
    """🌍 IP intelligence & network recon"""
    from ghostprint.modules.network import NetworkInvestigator
    
    inv = NetworkInvestigator(verbose=ctx.obj.get('verbose'))
    results = inv.investigate_ip(ip, scan_ports=ports)
    
    if shodan:
        from ghostprint.modules.advanced import AdvancedInvestigator
        adv_inv = AdvancedInvestigator()
        shodan_results = adv_inv.investigate(ip, target_type='ip', use_shodan=True)
        results['shodan'] = shodan_results.get('shodan', {})
    
    _display_results(results, output)


# PHONE COMMAND
@cli.command()
@click.argument('phone')
@click.option('--carrier', '-c', is_flag=True, help='Carrier info')
@click.option('--social', '-s', is_flag=True, help='Find social accounts')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def phone(ctx, phone, carrier, social, output):
    """📱 Phone number OSINT"""
    from ghostprint.modules.phone import PhoneInvestigator
    
    inv = PhoneInvestigator(verbose=ctx.obj.get('verbose'))
    results = inv.investigate(phone, check_carrier=carrier, check_social=social)
    
    _display_results(results, output)


# METADATA COMMAND
@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--extract-gps', '-g', is_flag=True, help='Extract GPS coordinates')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def metadata(ctx, file_path, extract_gps, output):
    """📄 Extract metadata from files (images, docs)"""
    from ghostprint.modules.metadata import MetadataExtractor
    
    inv = MetadataExtractor(verbose=ctx.obj.get('verbose'))
    results = inv.analyze(file_path)
    
    _display_results(results, output)


# ADVANCED COMMAND
@cli.command()
@click.argument('target')
@click.option('--type', 'target_type', type=click.Choice(['domain', 'ip', 'email']), default='domain')
@click.option('--shodan', is_flag=True, help='Query Shodan')
@click.option('--censys', is_flag=True, help='Query Censys')
@click.option('--ct', is_flag=True, help='Certificate Transparency')
@click.option('--threat', is_flag=True, help='Threat intelligence')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def advanced(ctx, target, target_type, shodan, censys, ct, threat, output):
    """🔬 Advanced recon (Shodan, Censys, CT, Threat Intel)"""
    from ghostprint.modules.advanced import AdvancedInvestigator
    
    inv = AdvancedInvestigator(verbose=ctx.obj.get('verbose'))
    results = inv.investigate(
        target=target,
        target_type=target_type,
        use_shodan=shodan,
        use_censys=censys,
        use_ct=ct,
        use_threat_intel=threat
    )
    
    _display_results(results, output)


# FULL INVESTIGATION
@cli.command()
@click.argument('target')
@click.option('--type', 'target_type', type=click.Choice(['email', 'username', 'domain', 'ip']), required=True)
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table', 'html']), default='json')
@click.option('--output-file', '-f', type=click.Path(), help='Save to file')
@click.pass_context
def full(ctx, target, target_type, output, output_file):
    """🕵️ Full investigation (comprehensive)"""
    console.print(f"[yellow]Running full {target_type} investigation on {target}...[/yellow]\n")
    
    results = {
        'target': target,
        'type': target_type,
        'modules': {}
    }
    
    # Run appropriate modules based on type
    if target_type == 'username':
        from ghostprint.modules.social_advanced import SocialMediaInvestigator
        inv = SocialMediaInvestigator(verbose=ctx.obj.get('verbose'))
        results['modules']['social'] = inv.investigate(target)
    
    elif target_type == 'email':
        from ghostprint.modules.breach import BreachInvestigator
        inv = BreachInvestigator(verbose=ctx.obj.get('verbose'))
        results['modules']['breaches'] = inv.investigate(target)
    
    elif target_type == 'domain':
        from ghostprint.modules.domain import DomainInvestigator
        from ghostprint.modules.advanced import AdvancedInvestigator
        
        dom_inv = DomainInvestigator(verbose=ctx.obj.get('verbose'))
        results['modules']['domain'] = dom_inv.investigate(target)
        
        adv_inv = AdvancedInvestigator()
        results['modules']['advanced'] = adv_inv.investigate(target, target_type='domain', use_ct=True)
    
    elif target_type == 'ip':
        from ghostprint.modules.network import NetworkInvestigator
        inv = NetworkInvestigator(verbose=ctx.obj.get('verbose'))
        results['modules']['network'] = inv.investigate_ip(target, scan_ports=True)
    
    # Display or save
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"[green]Results saved to {output_file}[/green]")
    else:
        _display_results(results, output)


def _display_results(results, output_format):
    """Display results in chosen format"""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2, default=str))
    elif output_format == 'csv':
        import csv
        import io
        # Simple CSV flattening
        output = io.StringIO()
        writer = csv.writer(output)
        
        def flatten_dict(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key))
                else:
                    items.append((new_key, str(v)))
            return items
        
        for key, value in flatten_dict(results):
            writer.writerow([key, value])
        
        console.print(output.getvalue())
    else:
        # Rich table display
        table = Table(title="Investigation Results", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        def add_to_table(data, prefix=''):
            for key, value in data.items():
                display_key = f"{prefix}{key}" if prefix else key
                if isinstance(value, dict):
                    add_to_table(value, f"{display_key}.")
                elif isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        for i, item in enumerate(value[:5]):  # Limit to 5 items
                            add_to_table(item, f"{display_key}[{i}].")
                        if len(value) > 5:
                            table.add_row(f"{display_key}...", f"({len(value) - 5} more items)")
                    else:
                        table.add_row(display_key, "\n".join(str(v) for v in value[:10]))
                        if len(value) > 10:
                            table.add_row("", f"({len(value) - 10} more items)")
                else:
                    table.add_row(display_key, str(value))
        
        add_to_table(results)
        console.print(table)


def main():
    """Entry point"""
    cli()


if __name__ == '__main__':
    main()