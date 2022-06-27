import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path

# Set the current working dir to parent directory
sys.path.append(Path.cwd().parent.as_posix())
os.chdir("..")

BUILD_CMD = "python -m setup sdist bdist_wheel".split()


if __name__ == "__main__":
    subprocess.Popen(BUILD_CMD)
