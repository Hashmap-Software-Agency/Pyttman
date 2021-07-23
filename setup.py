from pathlib import Path
from setuptools import setup, find_packages

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


# This call to setup() does all the work
setup(
    name="Pyttman",
    version="1.0.4",
    description="The virtual assistant framework made for developers with ideas",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/dotchetter/Pyttman",
    author="Simon Olofsson",
    project_urls={
        "Bug Tracker": "https://github.com/dotchetter/Pyttman/issues",
    },
    author_email="dotchetter@protonmail.ch",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    data_files=[('', ['pyttman/core/terraform_template/project_template.7z'])],
    install_requires=[
        "multidict",
        "pytz",
        "requests",
        "py7zr"
    ],
    entry_points={
        "console_scripts": [
            "pyttman-cli=pyttman.tools.pyttmancli:run",
        ]
    },
)


