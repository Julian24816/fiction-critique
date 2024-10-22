from setuptools import setup, find_packages

# Function to read the requirements.txt file
def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line and not line.startswith("#")]

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Parse dependencies from requirements.txt
requirements = parse_requirements("requirements.txt")

setup(
    name="fictique",
    version="0.1.0",
    author="Julian Müller",
    author_email="julian24816@gmail.com",
    description="AI assisted fiction critique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/julian24816/fiction-critique",  # Replace with your repo URL
    project_urls={
        "Bug Tracker": "https://github.com/julian24816/fiction-critique/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'fictique_update_rankings=fictique.main:update_rankings',
        ],
    },
)
