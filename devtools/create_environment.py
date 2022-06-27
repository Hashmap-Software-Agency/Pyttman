# Set the current working dir to parent directory
import os
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep

sys.path.append(Path.cwd().parent.as_posix())
os.chdir("..")

LAB_ENV_PATH = Path.cwd() / Path("dev_env")
BUILD_OUTPUT_PATH = Path.cwd() / "dist"

if __name__ == "__main__":
    if (LAB_ENV_PATH / "venv").exists():
        shutil.rmtree((LAB_ENV_PATH / "venv").as_posix())

    if not Path("dist").exists():
        print("\nCannot create local testing environment as there is no "
              "build generated for the current local version of Pyttman.",
              "Run 'build.py' to create one.")
        exit(-1)

    LAB_ENV_PATH.mkdir(exist_ok=True)
    os.chdir(LAB_ENV_PATH.as_posix())
    subprocess.run("python -m virtualenv venv".split())

    while not Path("venv").exists():
        sleep(0.01)

    package_file = [
        i for i in os.listdir(BUILD_OUTPUT_PATH.as_posix()) if i.endswith("tar.gz")
    ].pop()

    print(f"Installing package: '{package_file}' from your local build...")
    package_file = (BUILD_OUTPUT_PATH / package_file).as_posix()
    venv_python = (LAB_ENV_PATH / "venv/scripts/python.exe").as_posix()
    subprocess.run(f"{venv_python} -m pip install multidict".split())
    subprocess.run(f"{venv_python} -m pip install {package_file}".split())

    print("\nFinished! You can now create an app and start testing in "
          f"{LAB_ENV_PATH.as_posix()}.")
