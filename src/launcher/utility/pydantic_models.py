"""A module with Pydantic models."""

from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator


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
        hash (HashInfo): Represents filehash.
        dist_file_path (str): The path where the file should
            be downloaded.
    """

    file_name: str
    api_url: str
    yan_obj_storage: str
    hash: "HashInfo"
    dist_file_path: str


class ServerConfig(BaseModel):
    """
    Represents configuration data for installing and executing
    Vanilla Minecraft.

    Attributes:
        display_name (str): The visible name for the current modpack
            configuration.
        minecraft_version (str): The version of Minecraft.
        forge_version (str): The Forge version.
        minecraft_profile (str): The name of the Minecraft profile.
        minecraft_server_ip (str): The IP address of the Minecraft server.
        minecraft_server_port (str): The port of the Minecraft server.
        description (str): Server description in launcher.
    """

    display_name: str
    minecraft_version: str
    forge_version: str
    minecraft_profile: str
    minecraft_server_ip: str
    minecraft_server_port: str
    description: str
    server_icon: FileInfo


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

    @field_validator("modpacks")
    @classmethod
    def modpacks_must_not_be_empty(
        cls, modpacks: Dict[str, Modpack]
    ) -> Dict[str, Modpack]:
        """Ensure modpacks dictionary is not empty."""
        if not modpacks:
            raise ValueError("modpacks dictionary could not be empty")
        return modpacks


class AuthData(BaseModel):
    """
    Represents user credential data.
    """

    status: str
    username: str
    uuid: str
    accessToken: str


class HashInfo(BaseModel):
    """Represents the hash information."""

    value: str
    algorithm: str = "sha256"


class S3Credentials(BaseModel):
    """
    Pydantic model representing AWS S3 credentials for object storage.

    Attributes:
        aws_access_key_id (str): AWS access key ID for S3 authentication.
        aws_secret_access_key (str): AWS secret access key for S3
            authentication.
        bucket_name (str): Name of the S3 bucket.
        endpoint_url (str): URL of the S3 endpoint.
        region_name (Optional[str]): AWS region name. Optional,
            defaults to None.
    """

    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: str
    endpoint_url: str
    region_name: Optional[str] = None
