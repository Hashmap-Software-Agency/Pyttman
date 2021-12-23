from pyttman.version import __version__
from pathlib import Path
from setuptools import setup, find_packages


HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


# This call to setup() does all the work
setup(
    name="Pyttman",
    version=__version__,
    description="The Python chatbot framework with batteries included",
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
        "discord",
        "requests",
        "py7zr",
        "ordered_set"
    ],
    entry_points={
        "console_scripts": [
            "pyttman=pyttman.tools.pyttmancli:run",
        ]
    },
)


