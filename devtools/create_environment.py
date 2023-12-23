# Set the current working dir to parent directory
import os
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep

sys.path.append(Path.cwd().parent.as_posix())

if not Path("setup.py").exists():
    print("You're not in the right directory. Run this script from the "
          r"project's root directory, e.g. 'C:\users\your_user\projects\pyttman'.")
    exit(-1)

LAB_ENV_PATH = Path.cwd() / Path("dev_env")
BUILD_OUTPUT_PATH = Path.cwd() / "dist"

if __name__ == "__main__":
    if (LAB_ENV_PATH / "venv").exists():
        shutil.rmtree((LAB_ENV_PATH / "venv").as_posix())

    if not Path("dist").exists():
        subprocess.check_call("python devtools/build.py".split())

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

    clear_sc = "clear" if os.name == "posix" else "cls"
    os.system(clear_sc)

    os.system("cls")
    print("\nFinished! Here's how to get started:",
          f"1. Activate the virtual environment:\n\tcd dev_env\n\tvenv/scripts/activate",
          f"2. Run the command 'pyttman' to see available commands to the Pyttman CLI",
          "3. If it's the first time you're running Pyttman, run 'pyttman new app {app_name}' to create a new project."
          "4. Run 'pyttman dev {app_name}' to start the development server.",
          "5. If you've made changes to the Pyttman framework which you want to test in your testing project, "
          "run this script again. Your app will be left untouched, but the Pyttman version is upgraded to "
          "your current HEAD in the Pyttman repo.",
          sep="\n")
