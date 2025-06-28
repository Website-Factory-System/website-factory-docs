"""Setup configuration for DNS Automator"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dns-automator",
    version="1.0.0",
    author="Website Factory System",
    description="DNS automation service for Website Factory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Website-Factory-System/dns-automator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dns-automator=dns_automator.main:main",
        ],
    },
)