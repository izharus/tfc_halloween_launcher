"""Tests for src.launcher.utility.minecraft_query"""

# pylint: disable=W0212
import base64
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from src.launcher.utility.custom_exceptions import ServerQueryStatusError
from src.launcher.utility.minecraft_query import JavaServerData
from src.launcher.utility.pydantic_models import ServerConfig


class TestJavaServerData:
    """Tests for JavaServerData."""

    def test_init(self, pydantic_server_config: ServerConfig):
        """Test that JavaServerData initializes without errors."""
        assert JavaServerData(server_config=pydantic_server_config)

    def test_fetch_players_success(
        self,
        pydantic_server_config: ServerConfig,
        mocker: MockerFixture,
    ):
        """
        Test that fetch_players correctly retrieves online and max players.
        """
        expected_online = 89
        expected_max = 200
        server = JavaServerData(server_config=pydantic_server_config)
        mock_status = MagicMock()
        mock_status.players.online = expected_online
        mock_status.players.max = expected_max

        mocker.patch.object(server._server, "status", return_value=mock_status)
        online, max_players = server.fetch_players()

        assert online == expected_online
        assert max_players == expected_max

    def test_fetch_players_query_error(
        self,
        pydantic_server_config: ServerConfig,
        mocker: MockerFixture,
    ):
        """
        Test that fetch_players raises ServerQueryStatusError
        on query failure.
        """
        server = JavaServerData(server_config=pydantic_server_config)

        mocker.patch.object(server._server, "status", side_effect=Exception)

        with pytest.raises(ServerQueryStatusError):
            server.fetch_players()

    def test_fetch_icon_success(
        self,
        pydantic_server_config: ServerConfig,
        mocker: MockerFixture,
    ):
        """
        Test that fetch_icon correctly retrieves and decodes
        the server's icon.
        """
        # Prepare expected icon data in Base64 format
        expected_icon = b"some_data"
        encoded_icon = (
            "data:image/png;base64," + base64.b64encode(expected_icon).decode()
        )

        # Create mock status object and set the favicon property
        mock_status = MagicMock()
        mock_status.favicon = (
            encoded_icon  # Свойство `favicon` как строка Base64
        )

        # Mock the status method and retrieve icon
        server = JavaServerData(server_config=pydantic_server_config)
        mocker.patch.object(server._server, "status", return_value=mock_status)

        icon = server.fetch_icon()
        assert icon == expected_icon

    def test_fetch_icon_error(
        self,
        pydantic_server_config: ServerConfig,
        mocker: MockerFixture,
    ):
        """
        Test that fetch_icon raises ServerQueryStatusError
        on query failure.
        """
        server = JavaServerData(server_config=pydantic_server_config)

        mocker.patch.object(server._server, "status", side_effect=Exception)

        with pytest.raises(ServerQueryStatusError):
            server.fetch_icon()
