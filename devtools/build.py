import os
import shutil
import subprocess
import sys
from pathlib import Path

# Set the current working dir to parent directory
sys.path.append(Path.cwd().parent.as_posix())

CATALOGS = ("build", "dist")
BUILD_CMD = "python -m setup sdist bdist_wheel".split()


if __name__ == "__main__":
    subprocess.Popen(BUILD_CMD)
    [shutil.rmtree(i) for i in CATALOGS if Path(i).exists()]
    subprocess.run(BUILD_CMD)

