# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

"""Local MCP server implementations."""

import logging
from typing import Dict

from fastmcp import FastMCP

from miloco_server.schema.mcp_schema import LocalMcpClientId

logger = logging.getLogger(__name__)


class LocalMCPBase:
    """Base class for local MCP servers."""

    def __init__(self, name: str, instructions: str = None):
        from miloco_server.service.manager import get_manager  # pylint: disable=import-outside-toplevel

        self.name = name
        self.instructions = instructions or f"Local tool server: {name}"
        self.mcp: FastMCP = None
        self._initialized = False
        self._manager = get_manager()

    async def init_async(self):
        """Initialize MCP server."""
        if self._initialized:
            return
        self.mcp = FastMCP(
            name=self.name,
            instructions=self.instructions,
            on_duplicate="error",
            mask_error_details=True,
        )
        await self._register_tools()
        self._initialized = True
        logger.info("Local MCP server %s initialization completed", self.name)

    async def _register_tools(self):
        raise NotImplementedError("Subclass must implement _register_tools")

    @property
    def mcp_instance(self) -> FastMCP:
        if not self._initialized:
            raise RuntimeError("MCP server not initialized")
        return self.mcp


class LocalDefaultMcp(LocalMCPBase):
    """Default local tool namespace."""

    def __init__(self):
        super().__init__(
            name="Local Default Tools",
            instructions="Provides core local tools.",
        )

    async def _register_tools(self):
        logger.info("No default local tools are registered in robot dog runtime")


class LocalMCPServerFactory:
    """Local MCP server factory."""

    @staticmethod
    async def create_all_servers(robot_service=None) -> Dict[str, LocalMCPBase]:
        servers: Dict[str, LocalMCPBase] = {}
        default_server = LocalDefaultMcp()
        await default_server.init_async()
        servers[LocalMcpClientId.LOCAL_DEFAULT] = default_server

        if robot_service is not None:
            from miloco_server.mcp.robot_dog_mcp import RobotDogMcp  # pylint: disable=import-outside-toplevel

            robot_server = RobotDogMcp(robot_service)
            await robot_server.init_async()
            servers[LocalMcpClientId.ROBOT_DOG] = robot_server

        logger.info("Successfully created %d local MCP servers", len(servers))
        return servers
