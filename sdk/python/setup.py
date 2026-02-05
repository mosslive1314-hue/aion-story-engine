from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aion-sdk",
    version="6.0.0",
    author="AION Story Engine Team",
    author_email="support@aion-story.com",
    description="AION Story Engine Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aion-story/sdk-python",
    project_urls={
        "Bug Reports": "https://github.com/aion-story/sdk-python/issues",
        "Source": "https://github.com/aion-story/sdk-python",
        "Documentation": "https://docs.aion-story.com/sdk/python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "responses>=0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aion=aion_sdk.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
