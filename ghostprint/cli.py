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
@click.option('--carrier', '-c', is_flag=True, default=True, help='Check carrier info (default: enabled)')
@click.option('--no-carrier', '-C', is_flag=True, help='Skip carrier info check')
@click.option('--social', '-s', is_flag=True, help='Find social accounts')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def phone(ctx, phone, carrier, no_carrier, social, output):
    """🔍 Investigate a phone number"""
    console.print(f"\n[bold]Investigating phone:[/bold] {phone}\n")

    from ghostprint.modules.phone import PhoneInvestigator

    investigator = PhoneInvestigator(verbose=ctx.obj.get('verbose'))
    results = investigator.investigate(
        phone=phone,
        check_carrier=carrier and not no_carrier,
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

@cli.command('search')
@click.argument('query')
@click.option('--type', '-t', 'search_type', type=click.Choice(['username', 'email', 'custom']), default='username',
              help='Type of search query')
@click.option('--limit', '-l', type=int, default=20, help='Maximum results to show')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'table']), default='table')
@click.pass_context
def search_web(ctx, query, search_type, limit, output):
    """🔎 Search the web for mentions using free APIs (no API key required)"""
    console.print(f"\n[bold]Searching web for:[/bold] {query}\n")
    console.print("[dim]Using: GitHub, Reddit, Wikipedia, HackerNews APIs[/dim]\n")

    from ghostprint.modules.web_search import WebSearchInvestigator

    investigator = WebSearchInvestigator(verbose=ctx.obj.get('verbose'))
    results = investigator.investigate(
        query=query,
        query_type=search_type
    )

    if output == 'table':
        _display_web_results(results, limit)
    else:
        _display_results(results, output)

def _display_web_results(results, limit=20):
    """Display web search results from free APIs"""
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

    # Header
    query = results.get('query', 'N/A')
    query_type = results.get('query_type', 'search')

    console.print(Panel.fit(
        f"[bold cyan]Web Search: {query}[/bold cyan]\n"
        f"[dim]Type: {query_type} | Found {results.get('total_results', 0)} results[/dim]",
        border_style="cyan"
    ))

    # Summary
    summary = Table(box=box.ROUNDED, show_header=False)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="green")

    summary.add_row("Total Results", str(results.get('total_results', 0)))
    if results.get('engines_working'):
        summary.add_row("Sources OK", ", ".join(results['engines_working']))
    if results.get('engines_failed'):
        summary.add_row("[red]Sources Failed[/red]", ", ".join(results['engines_failed']))

    console.print(summary)
    console.print()

    # Results table
    search_results = results.get('results', [])[:limit]
    if search_results:
        results_table = Table(
            title=f"[green]Search Results ({len(search_results)} found)[/green]",
            box=box.MINIMAL_DOUBLE_HEAD,
            show_header=True,
            header_style="bold green"
        )
        results_table.add_column("#", style="dim", width=4)
        results_table.add_column("Source", style="yellow", width=12)
        results_table.add_column("Title", style="cyan")
        results_table.add_column("URL", style="blue", no_wrap=False)

        for i, result in enumerate(search_results, 1):
            title = result.get('title', 'N/A')[:45] if result.get('title') else '-'
            engine = result.get('engine', 'Unknown')
            url = result.get('url', 'N/A')[:50] + '...' if len(result.get('url', '')) > 50 else result.get('url', 'N/A')

            results_table.add_row(str(i), engine, title, url)

        console.print(results_table)

        # Show snippets
        console.print("\n[bold yellow]Details:[/bold yellow]")
        for i, result in enumerate(search_results[:5], 1):
            snippet = result.get('snippet', '')
            if snippet:
                snippet_clean = snippet[:150] + '...' if len(snippet) > 150 else snippet
                console.print(f"  {i}. [dim]{snippet_clean}[/dim]")
    else:
        console.print("[yellow]⚠ No results found[/yellow]")

def _display_results(results, output_format):
    """Display results in chosen format"""
    if output_format == 'json':
        import json
        console.print_json(json.dumps(results, indent=2, default=str))
    elif output_format == 'csv':
        import csv
        import io
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
        # Use new professional formatter
        from ghostprint.utils.formatter import display_results
        
        # Determine target type from results
        if 'username' in results and 'total_results' in results:
            display_results(results, 'web')
        elif 'username' in results:
            display_results(results, 'username')
        elif 'domain' in results:
            display_results(results, 'domain')
        elif 'phone' in results or 'original' in results:
            display_results(results, 'phone')
        elif 'email' in results:
            display_results(results, 'email')
        else:
            # Fallback to table format
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