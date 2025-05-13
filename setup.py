import os
from setuptools import setup, find_packages

def read_requirements(file):
    with open(file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('-r')]

# Read base requirements
base_requirements = read_requirements('requirements-base.txt')

# Read ML requirements (without base requirements which are included with -r)
ml_requirements = read_requirements('requirements-ml.txt')

# Combine for full requirements
full_requirements = base_requirements + ml_requirements

setup(
    name="folder-icon-annotation",
    version="0.1.0",
    description="A tool for annotating folder icons with AI",
    author="TigerAI",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=base_requirements,
    extras_require={
        'ml': ml_requirements,
        'all': full_requirements,
    },
    entry_points={
        'console_scripts': [
            'folder-icon-annotate=main:cli_entry_point',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)