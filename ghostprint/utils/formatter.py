"""
GhostPrint - Enhanced Output Formatter
Professional table formatting with rich
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from typing import Dict, List, Any

console = Console()


class ResultFormatter:
    """Format investigation results professionally"""
    
    @staticmethod
    def format_username_results(data: Dict) -> None:
        """Display username investigation in formatted tables with confidence scores"""

        # Header panel
        found_count = len(data.get('found_on', []))
        uncertain_count = len(data.get('uncertain', []))

        console.print(Panel.fit(
            f"[bold cyan]Username Investigation: {data['username']}[/bold cyan]\n"
            f"[dim]Found on {found_count} platforms | {uncertain_count} uncertain results[/dim]",
            border_style="cyan"
        ))

        # Summary table
        summary = Table(
            title="Summary",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green")

        summary.add_row("Username", data['username'])
        summary.add_row("Platforms Checked", str(data.get('total_platforms', 0)))
        summary.add_row("Confirmed", f"[green]{found_count}[/green]")
        summary.add_row("Not Found", str(len(data.get('not_found_on', []))))
        if uncertain_count > 0:
            summary.add_row("Uncertain", f"[yellow]{uncertain_count}[/yellow]")

        console.print(summary)
        console.print()

        # Found platforms table with confidence scores
        if data.get('found_on'):
            found_table = Table(
                title="[green]✓ Confirmed Profiles[/green]",
                box=box.MINIMAL_DOUBLE_HEAD,
                show_header=True,
                header_style="bold green"
            )
            found_table.add_column("Platform", style="cyan", width=15)
            found_table.add_column("Confidence", style="yellow", width=10)
            found_table.add_column("URL", style="blue", no_wrap=False)
            found_table.add_column("Profile Info", style="dim")

            profiles = data.get('profiles', {})
            for item in data['found_on']:
                platform = item['platform'] if isinstance(item, dict) else item
                confidence = item.get('confidence', '?') if isinstance(item, dict) else '?'

                profile = profiles.get(platform, {})
                url = profile.get('url', '')

                # Format confidence
                conf_str = f"{confidence:.0f}%" if isinstance(confidence, (int, float)) else str(confidence)

                # Extract profile info
                info_parts = []
                if profile.get('name'):
                    info_parts.append(f"Name: {profile['name']}")
                if profile.get('location'):
                    info_parts.append(f"Loc: {profile['location']}")
                if profile.get('created_at'):
                    info_parts.append(f"Since: {profile['created_at'][:10]}")
                if profile.get('bio'):
                    bio = profile['bio'][:50] + "..." if len(profile['bio']) > 50 else profile['bio']
                    info_parts.append(f"Bio: {bio}")

                info = " | ".join(info_parts) if info_parts else "-"

                found_table.add_row(platform, conf_str, url, info)

            console.print(found_table)
            console.print()

        # Uncertain results table
        if data.get('uncertain'):
            uncertain_table = Table(
                title="[yellow]? Uncertain Results[/yellow]",
                box=box.SIMPLE,
                show_header=True,
                header_style="bold yellow"
            )
            uncertain_table.add_column("Platform", style="cyan", width=15)
            uncertain_table.add_column("Confidence", style="yellow", width=10)
            uncertain_table.add_column("Status", style="dim")

            for item in data['uncertain']:
                platform = item.get('platform', 'Unknown')
                confidence = item.get('confidence', 0)
                exists = item.get('exists', False)

                conf_str = f"{confidence:.0f}%"
                status = "Possibly exists" if exists else "Unknown"

                uncertain_table.add_row(platform, conf_str, status)

            console.print(uncertain_table)
            console.print()

        # Not found platforms
        if data.get('not_found_on'):
            not_found = Table(
                title="[red]✗ Not Found[/red]",
                box=box.SIMPLE,
                show_header=False
            )
            not_found.add_column("Platform", style="dim")

            for platform in data['not_found_on']:
                not_found.add_row(platform)

            console.print(not_found)

        # Errors
        if data.get('errors'):
            error_table = Table(
                title="[red]⚠ Errors[/red]",
                box=box.SIMPLE,
                show_header=False
            )
            error_table.add_column("Error", style="red")

            for error in data['errors']:
                error_table.add_row(str(error)[:80])

            console.print(error_table)
    
    @staticmethod
    def format_domain_results(data: Dict) -> None:
        """Display domain investigation results"""
        
        console.print(Panel.fit(
            f"[bold cyan]Domain Investigation: {data.get('domain', 'N/A')}[/bold cyan]",
            border_style="cyan"
        ))
        
        # DNS Records
        if 'dns' in data and data['dns']:
            dns_table = Table(
                title="DNS Records",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold yellow"
            )
            dns_table.add_column("Type", style="cyan", width=10)
            dns_table.add_column("Values", style="green")
            
            for record_type, values in data['dns'].items():
                if record_type == 'error':
                    continue
                if values:
                    if isinstance(values, list):
                        dns_table.add_row(record_type, "\n".join(str(v) for v in values[:3]))
                    else:
                        dns_table.add_row(record_type, str(values))
            
            console.print(dns_table)
            console.print()
        
        # Subdomains
        if 'subdomains' in data and data['subdomains']:
            sub_table = Table(
                title=f"Subdomains ({len(data['subdomains'])} found)",
                box=box.MINIMAL_DOUBLE_HEAD,
                show_header=True,
                header_style="bold green"
            )
            sub_table.add_column("#", style="dim", width=4)
            sub_table.add_column("Subdomain", style="cyan")
            
            for i, subdomain in enumerate(data['subdomains'][:20], 1):  # Limit to 20
                sub_table.add_row(str(i), subdomain)
            
            if len(data['subdomains']) > 20:
                sub_table.add_row("...", f"+{len(data['subdomains']) - 20} more")
            
            console.print(sub_table)
            console.print()
        
        # WHOIS info
        if 'whois' in data and data['whois']:
            whois = data['whois']
            if whois.get('registrar'):
                whois_table = Table(
                    title="WHOIS Information",
                    box=box.SIMPLE,
                    show_header=True,
                    header_style="bold blue"
                )
                whois_table.add_column("Field", style="cyan")
                whois_table.add_column("Value", style="green")
                
                if whois.get('registrar'):
                    whois_table.add_row("Registrar", whois['registrar'])
                if whois.get('creation_date'):
                    whois_table.add_row("Created", str(whois['creation_date'])[:10])
                if whois.get('expiration_date'):
                    whois_table.add_row("Expires", str(whois['expiration_date'])[:10])
                
                console.print(whois_table)
    
    @staticmethod
    def format_phone_results(data: Dict) -> None:
        """Display phone investigation results"""
        
        console.print(Panel.fit(
            f"[bold cyan]Phone Investigation[/bold cyan]",
            border_style="cyan"
        ))
        
        phone_table = Table(box=box.ROUNDED, show_header=False)
        phone_table.add_column("Field", style="cyan", width=20)
        phone_table.add_column("Value", style="green")
        
        phone_table.add_row("Original", data.get('original', 'N/A'))
        phone_table.add_row("Normalized", data.get('normalized', 'N/A'))
        
        carrier = data.get('carrier_info', {})
        if carrier:
            phone_table.add_row("Country", carrier.get('country', 'Unknown'))
            phone_table.add_row("Type", carrier.get('type', 'Unknown'))
            phone_table.add_row("Carrier", carrier.get('carrier', 'Unknown'))
        
        console.print(phone_table)
    
    @staticmethod
    def format_email_results(data: Dict) -> None:
        """Display email investigation results with validation info"""

        # Validation status
        valid_status = "[green]✓ Valid[/green]" if data.get('valid') else "[red]✗ Invalid[/red]"

        console.print(Panel.fit(
            f"[bold cyan]Email Investigation: {data.get('email', 'N/A')}[/bold cyan]\n"
            f"[dim]Status: {valid_status} | Provider: {data.get('provider', 'Unknown')}[/dim]",
            border_style="cyan"
        ))

        # Email details
        if data.get('valid'):
            details_table = Table(box=box.ROUNDED, show_header=False)
            details_table.add_column("Field", style="cyan", width=20)
            details_table.add_column("Value", style="green")

            details_table.add_row("Email", data['email'])
            details_table.add_row("Provider", data.get('provider', 'Unknown'))

            if data.get('is_disposable'):
                details_table.add_row("Warning", "[red]Disposable email detected[/red]")

            console.print(details_table)
            console.print()

        # Breaches
        if data.get('breach_count', 0) > 0:
            breach_table = Table(
                title=f"[red]⚠ Breaches Found ({data['breach_count']})[/red]",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold red"
            )
            breach_table.add_column("Service", style="cyan")
            breach_table.add_column("Date", style="yellow", width=12)
            breach_table.add_column("Data Classes", style="green")

            for breach in data['breaches'][:10]:  # Limit to 10
                breach_table.add_row(
                    breach.get('Name', breach.get('title', 'Unknown')),
                    breach.get('BreachDate', breach.get('breach_date', 'N/A')),
                    ", ".join(breach.get('DataClasses', breach.get('data_classes', []))[:3])
                )

            if len(data['breaches']) > 10:
                breach_table.add_row("...", "", f"+{len(data['breaches']) - 10} more")

            console.print(breach_table)
        elif data.get('valid'):
            console.print("[green]✓ No breaches found in known databases[/green]")

        # Social Profiles
        if data.get('social_profiles'):
            console.print()
            social_table = Table(
                title="[blue]🔗 Social Profiles Found[/blue]",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold blue"
            )
            social_table.add_column("Platform", style="cyan")
            social_table.add_column("Username", style="green")
            social_table.add_column("URL", style="blue")

            for platform, profile_data in data['social_profiles'].items():
                users = profile_data.get('users', [])
                for user in users[:2]:  # Show first 2
                    social_table.add_row(
                        platform,
                        user.get('username', 'N/A'),
                        user.get('url', 'N/A')
                    )

            console.print(social_table)

        # Gravatar
        if data.get('gravatar') and data['gravatar'].get('exists'):
            console.print()
            gravatar = data['gravatar']
            profile = gravatar.get('profile', {})
            console.print(f"[blue]🖼 Gravatar:[/blue] {profile.get('display_name', 'N/A')}")
            console.print(f"   URL: {gravatar.get('url', 'N/A')}")

        # Errors
        if data.get('errors'):
            console.print()
            error_table = Table(
                title="[red]⚠ Errors[/red]",
                box=box.SIMPLE,
                show_header=False
            )
            error_table.add_column("Error", style="red")

            for error in data['errors']:
                error_table.add_row(str(error)[:80])

            console.print(error_table)


    @staticmethod
    def format_web_results(data: Dict) -> None:
        """Display web search results"""

        # Header
        if data.get('username'):
            title = f"Web Search: {data['username']}"
        elif data.get('email'):
            title = f"Web Search: {data['email']}"
        else:
            title = f"Web Search: {data.get('query', 'N/A')}"

        blocked = len(data.get('blocked_engines', []))
        blocked_str = f" | [red]{blocked} blocked[/red]" if blocked > 0 else ""

        console.print(Panel.fit(
            f"[bold cyan]{title}[/bold cyan]\n"
            f"[dim]Found {data.get('total_results', 0)} results{blocked_str}[/dim]",
            border_style="cyan"
        ))

        # Summary
        summary = Table(box=box.ROUNDED, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green")

        summary.add_row("Total Results", str(data.get('total_results', 0)))
        if data.get('engines_used'):
            summary.add_row("Engines Used", ", ".join(data['engines_used']))
        if data.get('blocked_engines'):
            summary.add_row("[red]Blocked (CAPTCHA)[/red]", ", ".join(data['blocked_engines']))

        console.print(summary)
        console.print()

        # Results
        search_results = data.get('results', [])
        if search_results:
            results_table = Table(
                title=f"[green]Search Results ({len(search_results)} found)[/green]",
                box=box.MINIMAL_DOUBLE_HEAD,
                show_header=True,
                header_style="bold green"
            )
            results_table.add_column("#", style="dim", width=4)
            results_table.add_column("Title", style="cyan")
            results_table.add_column("Engine", style="yellow", width=12)
            results_table.add_column("URL", style="blue")

            for i, result in enumerate(search_results[:20], 1):
                title = result.get('title', '-')[:45]
                engine = result.get('engine', 'Unknown')
                url = result.get('url', 'N/A')[:50]
                results_table.add_row(str(i), title, engine, url)

            console.print(results_table)
            console.print()

            # Snippets
            console.print("[bold yellow]Snippets:[/bold yellow]")
            for i, result in enumerate(search_results[:5], 1):
                snippet = result.get('snippet', '')
                if snippet:
                    snippet_clean = snippet[:180] + '...' if len(snippet) > 180 else snippet
                    console.print(f"  [dim]{i}. {snippet_clean}[/dim]\n")
        else:
            console.print("[yellow]⚠ No results found or blocked by CAPTCHA[/yellow]")

        if data.get('note'):
            console.print(f"\n[dim italic]Note: {data['note']}[/dim italic]")


def display_results(data: Dict, target_type: str) -> None:
    """Route to appropriate formatter"""
    formatters = {
        'username': ResultFormatter.format_username_results,
        'domain': ResultFormatter.format_domain_results,
        'phone': ResultFormatter.format_phone_results,
        'email': ResultFormatter.format_email_results,
        'web': ResultFormatter.format_web_results,
    }

    formatter = formatters.get(target_type)
    if formatter:
        formatter(data)
    else:
        # Fallback to JSON
        import json
        console.print_json(json.dumps(data, indent=2, default=str))