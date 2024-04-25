"""A module with Pydantic models."""
from typing import Dict, List

from pydantic import BaseModel


# pylint: disable=R0903
class FileInfo(BaseModel):
    """
    Represents information about a file in the modpack.
    Every file in the modpack has own FileInfo instance.

    Attributes:
        file_name (str): The name of the file.
        api_url (str): The API URL on github for downloading
            the file.
        yan_obj_storage (str): The object key to the file in
            Yandex Object Storage.
        hash (str): The hash value of the file.
        dist_file_path (str): The path where the file should
            be downloaded.
    """

    file_name: str
    api_url: str
    yan_obj_storage: str
    hash: str
    dist_file_path: str


class ServerConfig(BaseModel):
    """
    Represents configuration data for installing and executing
    Vanilla Minecraft.

    Attributes:
        config_name (str): The visible name for the current modpack
            configuration.
        minecraft_version (str): The version of Minecraft.
        forge_version (str): The Forge version.
        minecraft_profile (str): The name of the Minecraft profile.
        minecraft_server_ip (str): The IP address of the Minecraft server.
        minecraft_server_port (str): The port of the Minecraft server.
    """

    config_name: str
    minecraft_version: str
    forge_version: str
    minecraft_profile: str
    minecraft_server_ip: str
    minecraft_server_port: str


class Modpack(BaseModel):
    """
    Represents a Minecraft modpack.

    Attributes:
        config (ConfigJson): The configuration data
            for the modpack.
        main_data (List[FileInfo]): Essential data files.
        client_additional_data [Dict[str, List[FileInfo]]]:
            Additional files that can be added if needed.
    """

    server_config: ServerConfig
    main_data: List[FileInfo]
    client_additional_data: Dict[str, List[FileInfo]]


class MapJson(BaseModel):
    """
    Represents the structure of a map.json file containing
    information about modpacks.

    Attributes:
        modpacks (Dict[str, Modpack]): A dictionary where keys
            are modpack names and values are Modpack instances.
    """

    modpacks: Dict[str, Modpack]
