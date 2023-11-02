# tfc_halloween_launcher

This project involves the use of PyQt6 Designer to create a user interface. The generated source code is in Python and is intended for use on Python 3.11 and Windows 10.


## Requirements
The project dependencies are stored in the "requirements" directory. There are two sets of requirements:
### Development Environment
- To set up a development environment, you can create a virtual environment with the following commands:
```bash
python -m venv dev_venv
pip install -r requirements/dev.txt --target dev_venv
```
### Production Environment
- To set up a production environment, create a virtual environment as follows:
```bash
python -m venv prod_venv
pip install -r requirements/prod.txt --target prod_venv
```
## Launch Program
To launch the program, you can execute the main.py file:
```bash
python main.py
```
## Adding New Dependencies
If you want to make commits and add new dependencies to the project, follow these steps:
- Install pip-tools and pre-commit:
```bash
pip install pip-tools
pip install pre-commit
pre-commit install
```
### Adding a new pip module to the development environment
- Write the module name and its version to the "requirements/dev.in" file.
- Compile the requirements:
```bash
pip-compile requirements/dev.in
```
Install the new dependencies to the development environment:
```bash
pip install -r requirements/dev.txt --target dev_venv```
```
### Adding a new pip module to the production environment:
- Write the module name and its version to the "requirements/prod.in" file.
- Compile the requirements:
```
pip-compile requirements/prod.in
```
- Install the new dependencies to both the production and development environments:
```bash
pip install -r requirements/prod.txt --target prod_venv
pip install -r requirements/prod.txt --target dev_venv
```
### Conversion of UI File

To convert the UI file created in PyQt6 Designer (design.ui) into a Python file (design.py), you can use the following command:

```bash
pyuic6 design.ui -o design.py
```
## Code Style and Linting
Maintaining code quality and style is essential. You can use the following commands to ensure code consistency (there are many hooks in the pre-commit config):
- Activate the development virtual environment:
```bash
.\dev_venv\scripts\activate
```
- Run some of hooks:
```bash
pre-commit run isort
pre-commit run pylint
```
- Or run them all

```bash
pre-commit run --all-files
```
eel free to adjust and expand this readme as needed for your project documentation.