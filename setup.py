#!/usr/bin/env python3
"""Setup script for GPU Resource Profiler."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="gpu-resource-profiler",
    version="1.0.0",
    author="GPU Profiler Team",
    description="A Python-based tool for monitoring and analyzing GPU resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GBanGitHub/GPU_Resource_Profiler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'gpu-profiler=src.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['config/*.yaml'],
    },
    zip_safe=False,
)
