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
- Updated Java installation url, now it supports multiple versions of Windows.
- Other small interface improvements.

### Bug Fixes
- Fixed critical errors that led to an unexpected stop of the program if Java hadn't been installed in the system, or if it was not added to the PATH variable, or for any other errors during installation.
- Fixed critical errors that led to an unexpected stop of the program if any error occurred while installing Minecraft.
- Removed automatic reference to the user's browser if Java is not found on the user's system. The Java installation link is now pasted into the error message box.
- Java indication has been simplified, so now you don't especially need to install Java 17.

### Note: Windows 7 Support
- Please note that launcher do not supports for Windows 7. Windows 7 is an outdated operating system, and making compatibility could require extensive time and resources. Even major platforms like Steam will cease support for Windows 7 in January 2024. I recommend upgrading to a more recent Windows version for an improved and secure experience.
