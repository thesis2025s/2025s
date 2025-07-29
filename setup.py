"""
Setup script for Finance Specialist AI package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="finance-specialist-ai",
    version="1.0.0",
    author="Finance Specialist AI Team",
    author_email="contact@financespecialistai.com",
    description="Advanced AI-powered financial Q&A system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/finance-specialist-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "production": [
            "gunicorn>=21.0.0",
            "psycopg2-binary>=2.9.0",
            "redis>=4.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "finance-ai=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.txt", "*.md"],
    },
    zip_safe=False,
)