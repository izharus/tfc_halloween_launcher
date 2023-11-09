# Changelog

## Version 1.0.0 (5.11.2023)
## Version 1.0.0 (5.11.2023)

### Features
- Added support for multiple servers with different modpacks (we needed a second server for tests only). In the future, we can start a third server, e.g., for version 1.7.10.
- Implemented auto-downloading of all launcher files for multiple modpacks. Mod files are checked using hash values, and any unknown mods are deleted.
- Enhanced the informativeness of all messages regarding installation errors.
- Added a feature to skip installation if Minecraft for the current active configuration is already installed.
- Updated the design of the item for installing shaders. Shaders will automatically install/delete based on checkbox status (checked/unchecked).
- Improved the informativeness of log messages.
- Other small interface improvements.

### Bug Fixes
- Fixed critical errors that led to an unexpected stop of the program if Java hadn't been installed in the system, or if it was not added to the PATH variable, or for any other errors during installation.
- Fixed critical errors that led to an unexpected stop of the program if any error occurred while installing Minecraft.
- Removed automatic reference to the user's browser if Java is not found on the user's system. The Java installation link is now pasted into the error message box.
