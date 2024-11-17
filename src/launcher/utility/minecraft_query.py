"""Querying information from the minecraft server."""

import base64
from typing import Optional, Tuple

import mcstatus
from loguru import logger as log

from .custom_exceptions import ServerQueryStatusError
from .pydantic_models import ServerConfig


class JavaServerData:
    """Class for retrieving data from a Minecraft Java server."""

    def __init__(
        self,
        server_config: ServerConfig,
        timeout: int = 3,
    ) -> None:
        """
        Initializes the JavaServerData instance with server
        configuration and timeout.

        Args:
            server_config (ServerConfig): Configuration object containing
                the Minecraft server's IP and port.
            timeout (int, optional): Connection timeout in seconds.
                Defaults to 3.
        """

        server_ip = server_config.minecraft_server_ip
        try:
            port = int(server_config.minecraft_server_port)
        except Exception as error:
            log.error(f"Failed to fetch port for: {server_ip}")
            log.error(error)
            return

        log.info(f"'{server_ip}', '{port}'")
        self._server = mcstatus.JavaServer(
            host=server_ip,
            port=port,
            timeout=timeout,
        )

    def fetch_players(self) -> Tuple[int, int]:
        """
        Fetches the current number of online players and the maximum
        player capacity of the server.

        Returns:
            Tuple[int, int]: A tuple containing the number of online players
                and the maximum number of players allowed.

        Raises:
            ServerQueryStatusError: If the server's player status could
                not be retrieved.
        """
        try:
            status = self._server.status()
        except Exception as error:
            log.debug(f"Failed to query minecraft server status: {error}")
            raise ServerQueryStatusError from error
        return status.players.online, status.players.max

    def fetch_icon(self) -> Optional[bytes]:
        """
        Fetches the server's icon as a byte array if available.

        Returns:
            Optional[bytes]: The server's icon in PNG format as bytes,
                or None if not available.

        Raises:
            ServerQueryStatusError: If the server's icon could not
                be retrieved.
        """
        try:
            favicon = self._server.status().favicon
            icon_data = favicon.split(",")[1]
            icon_bytes = base64.b64decode(icon_data)

            return icon_bytes

        except Exception as error:
            log.debug(f"Failed to query minecraft server icon: {error}")
            raise ServerQueryStatusError from error
