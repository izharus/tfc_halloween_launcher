## About The Project

Minecraft launcher for your own servers. Features:
* Support for several custom modpacks.  
* User authorization.
* Installation of Minecraft/Forge versions.
* Downloading additional files, such as mods.
* Checking client files before Minecraft execution.
* Uploading skins and capes.

Supported OS:
* Windows 10 x64
* Windows 7 x86/x64


## Requirements

The project dependencies are stored in the "requirements" directory:
* `requirements/3_12.txt` - Python 3.12 requirements for Windows 10. GUI - PySide6.
* `requirements/3_8.txt` - Python 3.8 requirements for Windows 7. For x86, use 32-bit Python; for x64, use 64-bit Python. GUI - PySide2.

Note that the execution launcher also requires the latest version of Java, 32-bit or 64-bit, depending on the target system.



## Get started

Install virtual environment for target system, activate it and install all dependencies:
```bash
py -3.12-64 -m venv .venv_3_12x64
.\.venv_3_12x64\scripts\activate
python -m pip install -r requirements/3_12.txt
python main.py
```


## Issues
Detailed logs stores in "[minecraft_directory]/halloween_data/log" directory.


## Contributing
If you want to make commits to the project, follow these steps:
- Install pip-tools and pre-commit:
```bash
python -m pip install pip-tools
python -m pip install pre-commit
pre-commit install
```

### Adding a new pip module to the development environment
- Write the module name and its version to the "requirements/dev.in" file.
- Compile the requirements:
```bash
pip-compile requirements/3_12.in
```

### Conversion of UI File
To convert the UI file created in PySide Designer (design.ui) into a Python file (design.py), you can use the following command:

```cmd
pyside6_uic design.ui -o design.py
```

### Packing to exe
Activate target environment (Python 3.12, Python 3.8 32 bit or Python 3.8 64 bit) and run pyinstaller.
```bash
.\.venv_3_12x64\scripts\activate
pyinstaller main.spec
```

### Code Style and Linting
Maintaining code quality and style is essential. You can use the following command to ensure code consistency (there are many hooks in the pre-commit config):
```cmd
pre-commit run
```

Feel free to adjust and expand this readme as needed for your project documentation.