"""
Face Recognition System - Python Package Setup
A modern AI-powered face recognition system with web dashboard
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    requirements_path = os.path.join("config", "requirements-setup.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="face-recognition-system",
    version="2.2.0",
    author="Ahmed Taner",
    author_email="your-email@example.com",
    description="A modern AI-powered face recognition system with web dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/image_processing",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/image_processing/issues",
        "Documentation": "https://github.com/yourusername/image_processing/wiki",
        "Source Code": "https://github.com/yourusername/image_processing",
    },
    packages=find_packages(include=["core", "core.*", "api", "api.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "gpu": [
            "tensorflow-gpu>=2.13.0",
            "torch>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "face-recognition-server=api.main:main",
            "face-recognition-cli=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
        "static": ["**/*"],
        "templates": ["**/*"],
    },
    keywords=[
        "face-recognition",
        "computer-vision",
        "artificial-intelligence", 
        "machine-learning",
        "deep-learning",
        "opencv",
        "dlib",
        "facial-recognition",
        "biometrics",
        "security",
        "dashboard",
        "web-app",
        "fastapi",
        "real-time",
    ],
    license="MIT",
    zip_safe=False,
) 