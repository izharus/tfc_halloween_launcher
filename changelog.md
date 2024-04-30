# Changelog

## Version 1.0.0 (10.11.2023)

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


## Version 2.0.0 (05.12.2023)

### Features
- Added authorization feature in the launcher.
- Introduced the opportunity to add user skins (slim and non-slim) and capes. Only non-HD skins are available, but HD capes are available.
- Added a feature to indicate whether the current profile is installed or not.
### Bug Fixes
- Refactored the configuration structure to eliminate some bugs. During the first launch, the launcher will check the hash of game files.
- Multiple minor refinements...

## Version 3.0.0 (30.04.2024)

### Features
- Added integration with Yandex Object Storage. Modes now download from two separate services to make updates more stable.
- Added multiple logging messages.
- Fancy ru-locale names of modpacks.
- Added loguru for logging messages instead of low_wizard.
- Pydantic models were integrated into launcher_configs for validation of modpacks configs.
- Refactored launcher_configs to make the application more independent and easier to update.
- Implemented other small features.

### Bug Fixes
- Fixed launcher crashing if ethernet connection was lost.
- Fixed launcher crashing if web service for downloading config was unreachable.
- Corrected typos in info/error messages.
- Fixed main button text not changing game installation.
- Addressed other small fixes.

## Version 3.0.1 (30.04.2024)
### Features
- Added handling stderr from Minecraft thread.
### Bug Fixes
- Console now is no visible.

## Version 3.0.2 (30.04.2024)
### Bug Fixes
- Now the console is hidden while the game launched, not only in launcher mode.