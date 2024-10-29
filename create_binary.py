"""
This module provides a function to determine the version and bitness
of the current Python environment."""

import os
import subprocess

SPEC_FILE = "main.spec"

# Paths to virtual environments
virtual_envs = [
    ".venv_3_12x64",
    ".venv_3_8x64",
    ".venv_3_8x86",
]


def run_pyinstaller_in_env(env_path):
    """Run a command in the virtual environment."""
    activate_script = os.path.join(env_path, "Scripts", "activate")
    if not os.path.exists(activate_script):
        raise RuntimeError(f"Activation script not found in {env_path}")

    command = f"{activate_script} && pyinstaller {SPEC_FILE}"

    subprocess.run(command, shell=True, check=True)


for env in virtual_envs:
    run_pyinstaller_in_env(env)
