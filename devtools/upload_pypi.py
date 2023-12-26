import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from twine.commands.upload import upload

# Replace these with your package information
package_name = "Pyttman"

# Get the package version dynamically
# the file location is in a sibling directory, add it to the path

# Upload to PyPI using twine
confirm = input("Deploying to PyPi.\n\n1: For pypi production, type 'production'"
                "\n2: For test.pypi.org, type 'test'\n\n")

if not Path("dist").exists():
    print("You need to build the package first. Run devtools/build.py.")
    exit(0)

print("Enter '__token__' for username, and the token for password")
if confirm == "production":
    subprocess.run(["twine", "upload", "dist/*"])
elif confirm == "test":
    subprocess.run(["twine", "upload", "--repository-url", "https://test.pypi.org/legacy/", "dist/*"])

