import os
import shutil
import subprocess
import sys
from pathlib import Path

# Set the current working dir to parent directory
sys.path.append(Path.cwd().parent.as_posix())
os.chdir("..")
CATALOGS = ("build", "dist")

BUILD_CMD = "python -m setup sdist bdist_wheel".split()

if __name__ == "__main__":
    [shutil.rmtree(i) for i in CATALOGS]
    subprocess.run(BUILD_CMD)
