from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ghostprint",
    version="0.1.0",
    author="Toufik",
    author_email="your.email@example.com",
    description="OSINT CLI Tool - Find digital footprints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toufik/ghostprint",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "aiohttp>=3.8",
        "colorama>=0.4",
        "tldextract>=3.4",
        "python-whois>=0.8",
        "dnspython>=2.3",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "ghostprint=ghostprint.cli:main",
            "gp=ghostprint.cli:main",
        ],
    },
)