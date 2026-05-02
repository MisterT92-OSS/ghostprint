# Changelog

All notable changes to GhostPrint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-05-02

### Added
- **Advanced Reconnaissance Module**
  - Shodan host search (requires API key)
  - Censys search (requires API key)
  - Certificate Transparency log queries via crt.sh
  - ThreatCrowd lookups
  - VirusTotal lookups (requires API key)
  - URLScan.io searches

- **Breach Intelligence Module**
  - HaveIBeenPwned API integration
  - Dehashed database queries
  - LeakLookup database queries
  - Public paste search
  - Password strength analyzer

- **Enhanced Social Media Module**
  - 50+ platforms supported (up from 15)
  - Profile data extraction from HTML
  - Presence scoring and analysis
  - Platform categorization

- **Network Intelligence Module**
  - IP geolocation via ip-api.com
  - ASN information from ipinfo.io
  - Port scanning (async)
  - Reverse DNS lookups
  - CIDR range investigation

- **Metadata Extraction Module**
  - EXIF data from images
  - GPS coordinate extraction
  - PDF metadata extraction
  - Microsoft Office document metadata

- **Plugin System**
  - Extensible plugin architecture
  - Hook system for customization
  - Plugin template generator

- **Extended CLI**
  - `full` command for comprehensive investigations
  - Progress indicators with Rich
  - HTML report generation support
  - Better table formatting

## [0.1.0] - 2025-05-02

### Added
- Initial release
- CLI with Click framework
- Email investigation module
- Username enumeration (15 platforms)
- Domain reconnaissance (DNS, WHOIS, subdomains)
- Phone number lookup
- Rich terminal output
- JSON/CSV export formats

[0.2.0]: https://github.com/MisterT92-OSS/ghostprint/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/MisterT92-OSS/ghostprint/releases/tag/v0.1.0