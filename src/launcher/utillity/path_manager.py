"""
path_manager.py - Module for managing file paths.

This module provides a class for managing file paths used in the application.
It includes methods for retrieving paths to various resources, such as music
files and image files, and ensures consistent and platform-independent path
handling.

External Dependencies:
    None

Classes:
    PathManager: A class for managing file paths used in the application.

Usage:
    from path_manager import PathManager

    # Create an instance of PathManager
    path_manager = PathManager()

    # Get the path to a music file
    music_path = path_manager.get_music_path('song.mp3')

    # Get the path to an image file
    image_path = path_manager.get_image_path('image.png')
"""
import os
import sys


# class PathManager
class PathManager:
    """
    A class for managing paths in the application.
    """

    def __init__(self, path_to_module: str = ""):
        """
        Initialize the PathManager instance.

        Args:
            path_to_module (str): The path to the ui_controller module
                directory, if project installed as a submodule.
        """
        # Get the path to the executable file
        if getattr(sys, "frozen", False):
            # Running as a bundled executable (pyinstaller)
            self.base_path = sys._MEIPASS
            self.root_path = os.path.join(self.base_path, "root_dir")
        else:
            # Running as a script
            self.base_path = path_to_module
            self.root_path = os.getcwd()
        self.data_path = os.path.join(self.base_path, "data")
        self.image_path = os.path.join(self.data_path, "image")
        self.music_path = os.path.join(self.data_path, "music")

    def get_image_path(self, icon_file_name) -> str:
        """
        Get the path to an image file.

        Args:
            None

        Returns:
            str: The path to the image file.
        """
        return os.path.join(self.image_path, icon_file_name)

    def get_music_path(self, music_file_name) -> str:
        """
        Get the path to a music file.

        Args:
            None

        Returns:
            str: The path to the music file.
        """
        return os.path.join(self.music_path, music_file_name)

    def get_current_root_path(self, file_name: str) -> str:
        """
        Get the root path of the current project based on the context.

        - If running as a Python script, it returns the path to the 'file_name'
            located in the root directory.
        - If running as an executable, it returns the path to the 'file_name'
            within the project.

        Args:
            file_name (str): The name of the file to retrieve the path for.

        Returns:
            str: The root path of the project.
        """
        return os.path.join(self.root_path, file_name)
