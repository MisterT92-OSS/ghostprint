"""
GhostPrint - Network Reconnaissance
IP, network, and infrastructure intelligence
"""
import asyncio
import aiohttp
import socket
import ipaddress
from typing import Dict, List, Optional


class NetworkInvestigator:
    """Network and infrastructure OSINT"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint-Network/0.2.0'},
                timeout=aiohttp.ClientTimeout(total=15)
            )
    
    def get_ip_info(self, ip: str) -> Dict:
        """Get IP information from ip-api.com"""
        try:
            import requests
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip': ip,
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip': data.get('zip'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as')
                }
        except Exception as e:
            return {'ip': ip, 'error': str(e)}
        
        return {'ip': ip, 'status': 'unknown'}
    
    async def get_asn_info(self, ip: str) -> Dict:
        """Get ASN information from ipinfo.io"""
        try:
            url = f"https://ipinfo.io/{ip}/json"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'ip': data.get('ip'),
                        'hostname': data.get('hostname'),
                        'city': data.get('city'),
                        'region': data.get('region'),
                        'country': data.get('country'),
                        'loc': data.get('loc'),
                        'org': data.get('org'),  # Contains ASN
                        'postal': data.get('postal'),
                        'timezone': data.get('timezone')
                    }
        except Exception as e:
            return {'ip': ip, 'error': str(e)}
        
        return {'ip': ip}
    
    async def check_port(self, ip: str, port: int, timeout: int = 3) -> Dict:
        """Check if port is open"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return {'port': port, 'status': 'open', 'service': self._get_service_name(port)}
        except asyncio.TimeoutError:
            return {'port': port, 'status': 'filtered', 'service': None}
        except Exception as e:
            return {'port': port, 'status': 'closed', 'service': None, 'error': str(e)}
    
    def _get_service_name(self, port: int) -> Optional[str]:
        """Get common service name for port"""
        services = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            993: 'IMAPS',
            995: 'POP3S',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt',
            9200: 'Elasticsearch',
        }
        return services.get(port)
    
    async def port_scan(self, ip: str, ports: Optional[List[int]] = None) -> List[Dict]:
        """Scan common ports"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 
                    3306, 3389, 5432, 5900, 6379, 8080, 8443]
        
        tasks = [self.check_port(ip, port) for port in ports]
        results = await asyncio.gather(*tasks)
        
        return [r for r in results if r['status'] == 'open']
    
    async def get_reverse_dns(self, ip: str) -> List[str]:
        """Get reverse DNS for IP"""
        try:
            hostname = socket.gethostbyaddr(ip)
            return [hostname[0]] if hostname else []
        except:
            return []
    
    async def bgp_he_net_lookup(self, asn: str) -> Dict:
        """Lookup ASN on BGP.he.net"""
        try:
            url = f"https://bgp.he.net/{asn}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # Basic parsing
                    return {
                        'asn': asn,
                        'url': url,
                        'note': 'Additional parsing would extract prefix and peer data'
                    }
        except:
            pass
        return {'asn': asn}
    
    def investigate_ip(self, ip: str, scan_ports: bool = False) -> Dict:
        """Full IP investigation"""
        
        async def run():
            await self._init_session()
            
            results = {
                'target': ip,
                'ip_info': self.get_ip_info(ip),
                'asn_info': await self.get_asn_info(ip),
                'reverse_dns': await self.get_reverse_dns(ip),
                'open_ports': []
            }
            
            if scan_ports:
                results['open_ports'] = await self.port_scan(ip)
            
            if self.session:
                await self.session.close()
            
            return results
        
        return asyncio.run(run())
    
    def investigate_network(self, cidr: str) -> Dict:
        """Investigate CIDR range"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            
            results = {
                'network': cidr,
                'total_hosts': network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses,
                'first_ip': str(network[0]),
                'last_ip': str(network[-1]),
                'is_private': network.is_private,
                'hosts': []
            }
            
            # Sample first few hosts
            for i, ip in enumerate(network):
                if i >= 5 and i < network.num_addresses - 5:
                    continue
                results['hosts'].append(str(ip))
                if len(results['hosts']) >= 10:
                    break
            
            return results
        except Exception as e:
            return {'network': cidr, 'error': str(e)}