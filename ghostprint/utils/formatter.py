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
        """Display username investigation in formatted tables"""
        
        # Header panel
        console.print(Panel.fit(
            f"[bold cyan]Username Investigation: {data['username']}[/bold cyan]\n"
            f"[dim]Found on {len(data.get('found_on', []))} platforms[/dim]",
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
        summary.add_row("Found On", str(len(data.get('found_on', []))))
        summary.add_row("Not Found", str(len(data.get('not_found_on', []))))
        
        console.print(summary)
        console.print()
        
        # Found platforms table
        if data.get('found_on'):
            found_table = Table(
                title="[green]✓ Found On[/green]",
                box=box.MINIMAL_DOUBLE_HEAD,
                show_header=True,
                header_style="bold green"
            )
            found_table.add_column("Platform", style="cyan", width=15)
            found_table.add_column("URL", style="blue", no_wrap=False)
            found_table.add_column("Profile Info", style="dim")
            
            profiles = data.get('profiles', {})
            for platform in data['found_on']:
                profile = profiles.get(platform, {})
                url = profile.get('url', '')
                
                # Extract profile info
                info_parts = []
                if profile.get('name'):
                    info_parts.append(f"Name: {profile['name']}")
                if profile.get('location'):
                    info_parts.append(f"Loc: {profile['location']}")
                if profile.get('created_at'):
                    info_parts.append(f"Since: {profile['created_at'][:10]}")
                
                info = " | ".join(info_parts) if info_parts else "-"
                
                found_table.add_row(platform, url, info)
            
            console.print(found_table)
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
        """Display email investigation results"""
        
        console.print(Panel.fit(
            f"[bold cyan]Email Investigation: {data.get('email', 'N/A')}[/bold cyan]",
            border_style="cyan"
        ))
        
        # Breaches
        if 'breaches' in data and data['breaches']:
            breach_data = data['breaches']
            
            breach_table = Table(
                title=f"Breaches ({breach_data.get('breach_count', 0)} found)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold red"
            )
            breach_table.add_column("Service", style="cyan")
            breach_table.add_column("Date", style="yellow", width=12)
            breach_table.add_column("Data Classes", style="green")
            
            for breach in breach_data.get('breaches', []):
                breach_table.add_row(
                    breach.get('title', 'Unknown'),
                    breach.get('breach_date', 'N/A'),
                    ", ".join(breach.get('data_classes', [])[:3])
                )
            
            console.print(breach_table)
        else:
            console.print("[green]✓ No breaches found[/green]")


def display_results(data: Dict, target_type: str) -> None:
    """Route to appropriate formatter"""
    formatters = {
        'username': ResultFormatter.format_username_results,
        'domain': ResultFormatter.format_domain_results,
        'phone': ResultFormatter.format_phone_results,
        'email': ResultFormatter.format_email_results,
    }
    
    formatter = formatters.get(target_type)
    if formatter:
        formatter(data)
    else:
        # Fallback to JSON
        import json
        console.print_json(json.dumps(data, indent=2, default=str))