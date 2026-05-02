"""
GhostPrint - Utilities
Output formatters and helpers
"""
import json
from datetime import datetime
from typing import Dict, Any


class OutputFormatter:
    """Format investigation results for different outputs"""
    
    @staticmethod
    def to_json(data: Dict, indent: int = 2) -> str:
        """Convert results to JSON string"""
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    
    @staticmethod
    def to_csv(data: Dict) -> str:
        """Convert results to CSV string"""
        lines = []
        
        def flatten(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten(v, new_key).items())
                elif isinstance(v, list):
                    items.append((new_key, ';'.join(str(x) for x in v)))
                else:
                    items.append((new_key, str(v)))
            return dict(items)
        
        flat = flatten(data)
        for key, value in flat.items():
            lines.append(f'"{key}","{value}"')
        
        return '\n'.join(lines)
    
    @staticmethod
    def to_markdown(data: Dict, title: str = "GhostPrint Report") -> str:
        """Convert results to Markdown report"""
        lines = [
            f"# {title}",
            f"\nGenerated: {datetime.now().isoformat()}\n",
            "## Results\n"
        ]
        
        def format_section(d, level=2):
            for key, value in d.items():
                if isinstance(value, dict):
                    lines.append(f"{'#' * level} {key}\n")
                    format_section(value, level + 1)
                elif isinstance(value, list):
                    lines.append(f"{'#' * level} {key}\n")
                    for item in value:
                        lines.append(f"- {item}")
                    lines.append("")
                else:
                    lines.append(f"- **{key}**: {value}")
            lines.append("")
        
        format_section(data)
        return '\n'.join(lines)


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner():
    """Print GhostPrint ASCII banner"""
    banner = """
    ░██████╗░██╗░░██╗░█████╗░░██████╗████████╗██████╗░██████╗░██╗███╗░░██╗████████╗
    ██╔════╝░██║░░██║██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║████╗░██║╚══██╔══╝
    ██║░░██╗░███████║██║░░██║╚█████╗░░░░██║░░░██████╔╝██████╔╝██║██╔██╗██║░░░██║░░░
    ██║░░╚██╗██╔══██║██║░░██║░╚═══██╗░░░██║░░░██╔═══╝░██╔══██╗██║██║╚████║░░░██║░░░
    ╚██████╔╝██║░░██║╚█████╔╝██████╔╝░░░██║░░░██║░░░░░██║░░██║██║██║░╚███║░░░██║░░░
    ░╚═════╝░╚═╝░░╚═╝░╚════╝░╚═════╝░░░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝╚═╝░░╚══╝░░░╚═╝░░░
    """
    print(f"{Colors.CYAN}{banner}{Colors.END}")