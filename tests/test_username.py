import pytest
from ghostprint.modules.username import UsernameInvestigator


class TestUsernameInvestigator:
    """Test username investigation module"""
    
    def test_initialization(self):
        """Test investigator initialization"""
        inv = UsernameInvestigator(verbose=False)
        assert inv.verbose is False
        assert inv.session is None
    
    def test_platforms_defined(self):
        """Test that platforms are defined"""
        assert len(UsernameInvestigator.PLATFORMS) > 0
        assert 'github' in UsernameInvestigator.PLATFORMS
        assert 'twitter' in UsernameInvestigator.PLATFORMS
    
    def test_investigate_known_user(self):
        """Test investigation of known user (Linus Torvalds)"""
        inv = UsernameInvestigator(verbose=False)
        results = inv.investigate('torvalds', platforms=['github'])
        
        assert results['username'] == 'torvalds'
        assert 'github' in results['found_on']
        assert results['profiles']['github']['url'] == 'https://github.com/torvalds'
    
    def test_investigate_nonexistent_user(self):
        """Test investigation of non-existent user"""
        inv = UsernameInvestigator(verbose=False)
        # Use a random unlikely username
        results = inv.investigate('ghostprint_test_user_12345_xyz')
        
        assert results['username'] == 'ghostprint_test_user_12345_xyz'
        # Most platforms should not find this
        assert len(results['found_on']) == 0