"""
This module provides a function to determine the version and bitness
of the current Python environment."""

import os
import subprocess

LAUNCHER_SPEC_FILE = "main.spec"
INSTALLER_SPEC_FILE = "installer.spec"


WIN10X64_ENV = ".venv_3_12x64"
WIN7X64_ENV = ".venv_3_8x64"
WIN7X86_ENV = ".venv_3_8x86"


def run_pyinstaller_in_env(env_path, spec_file):
    """Run a command in the virtual environment."""
    activate_script = os.path.join(env_path, "Scripts", "activate")
    if not os.path.exists(activate_script):
        raise RuntimeError(f"Activation script not found in {env_path}")

    command = f"{activate_script} && pyinstaller {spec_file}"

    subprocess.run(command, shell=True, check=True)


def main():
    """Create all binaries."""
    for env in (WIN10X64_ENV, WIN7X64_ENV, WIN7X86_ENV):
        # Binaries for main launcher for different systems
        run_pyinstaller_in_env(env, LAUNCHER_SPEC_FILE)

    # for env in (WIN7X64_ENV, WIN7X86_ENV):
    #     # Binaries for installers
    #     run_pyinstaller_in_env(env, INSTALLER_SPEC_FILE)


if "__main__" == __name__:
    main()
