# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

"""MCP client manager module for managing MCP clients and tools."""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from miloco_server.dao.mcp_config_dao import MCPConfigDAO
from miloco_server.mcp.local_mcp_servers import LocalMCPServerFactory
from miloco_server.mcp.mcp_client import LocalMCPConfig, MCPClientBase, MCPClientConfig, MCPClientFactory, TransportType
from miloco_server.schema.mcp_schema import CallToolResult, LocalMcpClientId, MCPClientStatus, MCPToolInfo
from miloco_server.utils.mcp_util import MCPConfigConverter

logger = logging.getLogger(__name__)


@dataclass
class ToolInfo:
    """Tool information."""

    client_id: str
    client_name: str
    tool_name: str
    client: MCPClientBase


class MCPClientManager:
    """MCP client manager for robot dog runtime."""

    def __init__(self, config_dao: MCPConfigDAO, robot_service=None):
        self.clients: Dict[str, MCPClientBase] = {}
        self.config_dao = config_dao
        self.robot_service = robot_service
        self._initialized = False

    @classmethod
    async def create(cls, config_dao: MCPConfigDAO, robot_service=None) -> "MCPClientManager":
        """Create and initialize MCP clients."""
        instance = cls(config_dao, robot_service)
        await instance._init_all_clients()
        return instance

    async def _init_all_clients(self):
        """Initialize default robot tools and user-configured external MCP clients."""
        if self._initialized:
            return

        logger.info("Starting to initialize all MCP clients...")
        try:
            await asyncio.gather(
                self._init_default_clients(),
                self._init_clients(),
                return_exceptions=True,
            )
            self._initialized = True
            logger.info("All MCP clients initialization completed")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error occurred while initializing MCP clients: %s", str(e))
            raise

    async def _init_clients(self):
        """Initialize user-configured external MCP clients."""
        logger.info("init mcp clients")
        configs = self.config_dao.get_all()
        tasks = []

        for config in configs:
            try:
                if not config.enable:
                    logger.info("MCP client %s is disabled, skipping", config.name)
                    continue
                client_config = MCPConfigConverter.to_mcp_client_config(config)
                tasks.append(asyncio.create_task(self._add_client(config.access_type, client_config)))
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Failed to convert MCP config: %s, error: %s", config.name, str(e))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            enabled_configs = [config for config in configs if config.enable]
            for i, result in enumerate(results):
                config_name = enabled_configs[i].name if i < len(enabled_configs) else "<unknown>"
                if isinstance(result, Exception):
                    logger.error("Failed to initialize MCP Client: %s, error: %s", config_name, str(result))
                elif result:
                    logger.info("Successfully initialized MCP Client: %s", config_name)
                else:
                    logger.warning("Failed to initialize MCP Client: %s", config_name)

    async def _init_default_clients(self):
        """Initialize built-in robot dog MCP clients."""
        logger.info("init default mcp clients")
        try:
            await self._init_local_mcp_servers()
            logger.info("init default mcp clients done")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to initialize default MCP clients: %s", e, exc_info=True)

    async def _init_local_mcp_servers(self):
        """Initialize local MCP servers."""
        logger.info("Initializing local MCP servers...")
        local_servers = await LocalMCPServerFactory.create_all_servers(robot_service=self.robot_service)

        for client_id, server in local_servers.items():
            try:
                await self._add_client(
                    transport_type=TransportType.LOCAL,
                    config=LocalMCPConfig(
                        client_id=client_id,
                        server_name=server.name,
                        mcp_server=server.mcp_instance,
                    ),
                )
                logger.info("Successfully initialized local MCP server: %s", server.name)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Failed to initialize local MCP server %s: %s", server.name, e)

        logger.info("Local MCP servers initialization completed, total %d servers", len(local_servers))

    async def _add_client(self, transport_type: TransportType, config: MCPClientConfig) -> bool:
        """Add MCP client."""
        client_id = config.id
        if client_id in self.clients:
            logger.warning("Client '%s' already exists, will be overwritten", client_id)
            await self.clients[client_id].disconnect()

        client = MCPClientFactory.create_client(transport_type, config)
        self.clients[client_id] = client
        return await client.connect()

    async def add_client(self, transport_type: TransportType, config: MCPClientConfig) -> bool:
        """Add MCP client."""
        return await self._add_client(transport_type, config)

    async def update_client(self, transport_type: TransportType, config: MCPClientConfig) -> bool:
        """Update MCP client."""
        client_id = config.id
        if client_id not in self.clients:
            logger.warning("Client '%s' does not exist, attempting to add new client", client_id)
            return await self._add_client(transport_type, config)

        await self.clients[client_id].disconnect()
        client = MCPClientFactory.create_client(transport_type, config)
        if await client.connect():
            self.clients[client_id] = client
            return True
        return False

    async def remove_client(self, client_id: str):
        """Remove MCP client."""
        if client_id in self.clients:
            await self.clients[client_id].disconnect()
            del self.clients[client_id]

    def has_client(self, client_id: str) -> bool:
        """Check if client exists."""
        return client_id in self.clients

    def get_client(self, client_id: str) -> Optional[MCPClientBase]:
        """Get MCP client."""
        logger.debug("mcp_client_manager get_client: %s, clients: %s", client_id, self.clients)
        return self.clients.get(client_id)

    async def cleanup(self):
        """Clean up all client connections."""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()

    async def get_all_clients_status(self) -> List[MCPClientStatus]:
        """Get status of all clients."""
        client_items = list(filter(lambda x: x[0] != LocalMcpClientId.LOCAL_DEFAULT, self.clients.items()))
        ping_tasks = [self._verify_client_connection(client_id, client) for client_id, client in client_items]
        ping_results = await asyncio.gather(*ping_tasks, return_exceptions=True)

        results = []
        for i, (client_id, client) in enumerate(client_items):
            ping_result = ping_results[i]
            connected = False if isinstance(ping_result, Exception) else ping_result
            results.append(MCPClientStatus(
                client_id=client_id,
                server_name=client.config.server_name,
                connected=connected,
            ))

        results.sort(key=lambda x: x.server_name)
        return results

    async def _verify_client_connection(self, client_id: str, client: MCPClientBase) -> bool:
        """Verify client connection status."""
        try:
            return await asyncio.wait_for(client.ping(), timeout=1.0)
        except asyncio.TimeoutError:
            logger.debug("Client %s ping timeout", client_id)
            return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Client %s ping exception: %s", client_id, e)
            return False

    def _validate_client(self, client_id: str) -> Optional[MCPClientBase]:
        """Validate if client exists and is connected."""
        client = self.get_client(client_id)
        if not client:
            logger.error("Client %s does not exist", client_id)
            return None
        if not client.is_connected():
            logger.warning("Client %s is not connected", client_id)
            return None
        return client

    async def call_tool(self, client_id: str, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call MCP tool."""
        tool_info = self._get_tool_info(client_id, tool_name)
        if not tool_info:
            return CallToolResult(success=False, error_message="Tool not found", response=None)
        return await self._execute_tool_call(tool_info, arguments)

    def _get_tool_info(self, client_id: str, tool_name: str) -> Optional[ToolInfo]:
        """Get tool information."""
        try:
            client = self._validate_client(client_id)
            if not client:
                return None
            tool = client.get_tool(tool_name)
            if not tool:
                logger.error("Tool %s does not exist in client %s", tool_name, client_id)
                return None
            return ToolInfo(client_id, client.config.server_name, tool_name, client)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to get tool info for client %s, tool %s: %s", client_id, tool_name, e)
            return None

    async def _execute_tool_call(self, tool_info: ToolInfo, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute tool call."""
        try:
            logger.info("Calling tool %s in client %s (%s), arguments type: %s, arguments: %s",
                        tool_info.tool_name, tool_info.client_name, tool_info.client_id, type(arguments), arguments)
            result = await tool_info.client.call_tool(tool_info.tool_name, arguments)
            return CallToolResult(success=True, error_message=None, response=result)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to call tool %s: %s", tool_info.tool_name, e)
            return CallToolResult(success=False, error_message=str(e), response=None)

    def get_tools_by_ids(self, client_ids: Optional[List[str]]) -> List[MCPToolInfo]:
        """Get tool information for selected clients."""
        if client_ids is None:
            client_ids = list(self.clients.keys())

        unique_client_ids = list(dict.fromkeys(client_ids))
        clients_to_process: List[tuple[str, MCPClientBase]] = [
            (client_id, self.clients[client_id])
            for client_id in unique_client_ids
            if client_id in self.clients
        ]

        tools = []
        for client_id, client in clients_to_process:
            if not client.is_connected():
                continue
            try:
                for tool in client.get_tools():
                    tools.append(MCPToolInfo(
                        client_id=client_id,
                        tool_name=tool.name,
                        description=tool.description or f"MCP server {client.config.server_name} tools: {tool.name}",
                        parameters=tool.inputSchema,
                        tool_info=tool,
                    ))
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Failed to get tools for client %s: %s", client_id, e)
        return tools
