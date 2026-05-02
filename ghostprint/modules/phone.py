"""
GhostPrint - Phone Investigation Module
Phone number OSINT
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional
import re


class PhoneInvestigator:
    """Investigate phone numbers"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint/0.1.0'},
                timeout=aiohttp.ClientTimeout(total=10)
            )
    
    # Country codes and formats
    COUNTRY_CODES = {
        '33': {'name': 'France', 'min_length': 9, 'max_length': 9},
        '1': {'name': 'United States/Canada', 'min_length': 10, 'max_length': 10},
        '44': {'name': 'United Kingdom', 'min_length': 10, 'max_length': 10},
        '49': {'name': 'Germany', 'min_length': 10, 'max_length': 11},
        '39': {'name': 'Italy', 'min_length': 9, 'max_length': 10},
        '34': {'name': 'Spain', 'min_length': 9, 'max_length': 9},
        '31': {'name': 'Netherlands', 'min_length': 9, 'max_length': 9},
        '32': {'name': 'Belgium', 'min_length': 9, 'max_length': 9},
        '41': {'name': 'Switzerland', 'min_length': 9, 'max_length': 9},
    }

    # French carrier prefixes
    FR_CARRIERS = {
        '06': {'type': 'Mobile', 'carriers': ['Orange', 'SFR', 'Bouygues', 'Free', 'MVNOs']},
        '07': {'type': 'Mobile', 'carriers': ['All carriers']},
        '01': {'type': 'Landline', 'region': 'Paris region (Île-de-France)'},
        '02': {'type': 'Landline', 'region': 'Northwest (Bretagne, Pays de la Loire, etc.)'},
        '03': {'type': 'Landline', 'region': 'Northeast (Hauts-de-France, Grand Est, etc.)'},
        '04': {'type': 'Landline', 'region': 'Southeast (Auvergne-Rhône-Alpes, PACA, etc.)'},
        '05': {'type': 'Landline', 'region': 'Southwest (Nouvelle-Aquitaine, Occitanie, etc.)'},
        '09': {'type': 'VoIP', 'carriers': ['Various VoIP providers']},
    }

    def _normalize_phone(self, phone: str) -> Dict:
        """Normalize phone number and extract components"""
        result = {
            'original': phone,
            'normalized': None,
            'country_code': None,
            'national_number': None,
            'valid': False,
            'errors': []
        }

        if not phone:
            result['errors'].append('Empty phone number')
            return result

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        if len(digits) < 7:
            result['errors'].append('Phone number too short')
            return result

        # Detect country code and format
        if digits.startswith('00'):
            digits = digits[2:]

        # Try to detect country code
        for code, info in sorted(self.COUNTRY_CODES.items(), key=lambda x: -len(x[0])):
            if digits.startswith(code):
                national = digits[len(code):]
                if info['min_length'] <= len(national) <= info['max_length']:
                    result['country_code'] = code
                    result['national_number'] = national
                    result['normalized'] = f"+{digits}"
                    result['valid'] = True
                    break

        # Fallback for French numbers starting with 0
        if not result['valid'] and len(digits) == 10 and digits.startswith('0'):
            result['country_code'] = '33'
            result['national_number'] = digits[1:]
            result['normalized'] = f"+33{digits[1:]}"
            result['valid'] = True

        if not result['valid']:
            result['normalized'] = f"+{digits}" if not digits.startswith('+') else digits
            result['errors'].append('Could not validate phone number format')

        return result

    def _get_carrier_info(self, country_code: str, national_number: str) -> Dict:
        """Get carrier info from number prefix"""
        info = {
            'country': 'Unknown',
            'carrier': 'Unknown',
            'type': 'Unknown',
            'region': None
        }

        country_info = self.COUNTRY_CODES.get(country_code)
        if country_info:
            info['country'] = country_info['name']

        # French-specific detection
        if country_code == '33' and len(national_number) >= 1:
            # First digit after country code determines the line type
            first_digit = national_number[0]
            prefix_map = {
                '6': '06', '7': '07',
                '1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '9': '09'
            }
            prefix = prefix_map.get(first_digit, first_digit)
            carrier_data = self.FR_CARRIERS.get(prefix)
            if carrier_data:
                info['type'] = carrier_data['type']
                info['region'] = carrier_data.get('region')
                if 'carriers' in carrier_data:
                    info['carrier'] = ', '.join(carrier_data['carriers'])

        return info
    
    def investigate(self, phone: str, check_carrier: bool = True,
                   check_social: bool = False) -> Dict:
        """
        Investigate a phone number with validation and carrier detection

        Args:
            phone: Phone number to investigate
            check_carrier: Get carrier info
            check_social: Check social platforms (requires additional sources)

        Returns:
            Dictionary with investigation results
        """
        # Normalize and validate
        normalized = self._normalize_phone(phone)

        results = {
            'original': normalized['original'],
            'normalized': normalized['normalized'],
            'valid': normalized['valid'],
            'country_code': normalized['country_code'],
            'national_number': normalized['national_number'],
            'carrier_info': {},
            'social_accounts': [],
            'errors': normalized['errors'],
            'status': 'completed'
        }

        if not normalized['valid']:
            results['status'] = 'invalid_phone'
            return results

        if check_carrier:
            results['carrier_info'] = self._get_carrier_info(
                normalized['country_code'],
                normalized['national_number']
            )

        if check_social:
            results['social_accounts'] = {
                'note': 'Social check requires external APIs (Numverify, Truecaller, etc.)'
            }

        return results


if __name__ == '__main__':
    import sys

    test_phone = sys.argv[1] if len(sys.argv) > 1 else '+33612345678'

    investigator = PhoneInvestigator(verbose=True)
    results = investigator.investigate(test_phone, check_carrier=True)

    print(f"\n{'='*60}")
    print(f"Phone Investigation: {results['original']}")
    print(f"{'='*60}")
    print(f"Valid: {results['valid']}")
    print(f"Normalized: {results['normalized']}")
    print(f"Country Code: {results['country_code']}")
    print(f"National Number: {results['national_number']}")

    if results['carrier_info']:
        info = results['carrier_info']
        print(f"\n✓ Carrier Info:")
        print(f"  Country: {info['country']}")
        print(f"  Type: {info['type']}")
        print(f"  Carrier: {info['carrier']}")
        if info['region']:
            print(f"  Region: {info['region']}")

    if results['errors']:
        print(f"\n⚠ Errors:")
        for error in results['errors']:
            print(f"  - {error}")

    print(f"\n{'='*60}")