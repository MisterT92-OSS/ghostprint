import pytest
from ghostprint.modules.domain import DomainInvestigator


class TestDomainInvestigator:
    """Test domain investigation module"""
    
    def test_initialization(self):
        """Test investigator initialization"""
        inv = DomainInvestigator(verbose=False)
        assert inv.verbose is False
    
    def test_subdomain_wordlist(self):
        """Test that wordlist is populated"""
        inv = DomainInvestigator(verbose=False)
        assert len(inv.SUBDOMAIN_WORDLIST) > 0
        assert 'www' in inv.SUBDOMAIN_WORDLIST
        assert 'mail' in inv.SUBDOMAIN_WORDLIST
    
    def test_check_dns(self):
        """Test DNS checking"""
        inv = DomainInvestigator(verbose=False)
        results = inv._check_dns('google.com')
        
        # Should have A records
        assert 'A' in results
        assert len(results['A']) > 0
    
    def test_investigate_domain(self):
        """Test full domain investigation"""
        inv = DomainInvestigator(verbose=False)
        results = inv.investigate(
            'github.com',
            enumerate_subdomains=False,  # Faster for tests
            check_whois=False
        )
        
        assert results['domain'] == 'github.com'
        assert 'dns' in results
        assert len(results['dns']['A']) > 0