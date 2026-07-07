# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

"""
Service manager module
"""

import logging
import uuid
from typing import Callable, Optional


from miloco_server.dao.chat_history_dao import ChatHistoryDAO
from miloco_server.schema.auth_schema import UserLanguage
from miloco_server.schema.model_purpose import ModelPurpose
from miloco_server.mcp.tool_executor import ToolExecutor
from miloco_server.utils.cleaner import Cleaner
from miloco_server.dao.kv_dao import KVDao, SystemConfigKeys
from miloco_server.dao.third_party_model_dao import ThirdPartyModelDAO
from miloco_server.dao.mcp_config_dao import MCPConfigDAO
from miloco_server.proxy.llm_proxy import LLMProxy
from miloco_server.mcp.mcp_client_manager import MCPClientManager
from miloco_server.service.auth_service import AuthService
from miloco_server.service.model_service import ModelService
from miloco_server.service.mcp_service import McpService
from miloco_server.service.chat_history_service import ChatHistoryService
from miloco_server.proxy.robot_proxy import RobotProxy
from miloco_server.service.robot_service import RobotService
from miloco_server.utils.chat_companion import ChatCompanion

logger = logging.getLogger(__name__)


class Manager:
    """
    Service manager singleton class - simplified version
    Only responsible for service initialization and providing access interfaces, no business logic
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Manager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        pass

    async def initialize(self, callback: Optional[Callable[[], None]] = None):
        """
        Initialize all services
        """
        if getattr(self, "_initialized", False):
            logger.debug("Manager already initialized, skipping duplicate initialization")
            return

        logger.info("Manager initialization started")

        self._initialized = True

        # Initialize DAO layer
        self._kv_dao = KVDao()
        self._third_party_model_dao = ThirdPartyModelDAO()
        self._mcp_config_dao = MCPConfigDAO()
        self._chat_history_dao = ChatHistoryDAO()
        self._cleaner = Cleaner(self._chat_history_dao)
        self._chat_companion = ChatCompanion(self._chat_history_dao)

        # Initialize device UUID
        self.init_device_uuid()

        # Initialize model service before robot service so robot vision can use configured LLM proxies.
        self._model_service = ModelService(self._kv_dao, self._third_party_model_dao)
        self._robot_proxy = RobotProxy()
        self._robot_service = RobotService(self._robot_proxy, self.get_llm_proxy_by_purpose)
        self._mcp_client_manager = await MCPClientManager.create(
            self._mcp_config_dao,
            robot_service=self._robot_service)

        # Initialize tool executor
        self._tool_executor = ToolExecutor(self._mcp_client_manager)

        # Initialize all services
        self._auth_service = AuthService(self._kv_dao)
        self._mcp_service = McpService(self._mcp_config_dao, self._mcp_client_manager)
        self._chat_service = ChatHistoryService(self._chat_history_dao, self._chat_companion)

        if callback:
            callback()
        logger.info("Manager initialization completed")

    def init_device_uuid(self):
        """Initialize device UUID"""
        device_uuid = self._kv_dao.get(SystemConfigKeys.DEVICE_UUID_KEY)
        if not device_uuid:
            device_uuid = uuid.uuid4().hex
            self._kv_dao.set(SystemConfigKeys.DEVICE_UUID_KEY, device_uuid)
        self.device_uuid = device_uuid

    # Service access properties
    @property
    def auth_service(self) -> AuthService:
        return self._auth_service

    @property
    def model_service(self) -> ModelService:
        return self._model_service

    @property
    def mcp_service(self) -> McpService:
        return self._mcp_service

    @property
    def chat_service(self) -> ChatHistoryService:
        return self._chat_service

    @property
    def chat_companion(self) -> ChatCompanion:
        return self._chat_companion

    @property
    def robot_service(self) -> RobotService:
        return self._robot_service

    # Tool and proxy access properties
    @property
    def tool_executor(self) -> ToolExecutor:
        return self._tool_executor

    def get_llm_proxy_by_purpose(self, purpose: ModelPurpose) -> LLMProxy:
        llm_proxy_by_purpose = self._model_service.get_llm_proxy()
        if purpose not in llm_proxy_by_purpose:
            logger.warning("LLM proxy not set in purpose: %s", purpose)
            return None
        return llm_proxy_by_purpose[purpose]

    def get_language(self) -> UserLanguage:
        return self._auth_service.get_user_language().language

    # DAO layer access properties
    @property
    def kv_dao(self) -> KVDao:
        return self._kv_dao

    @property
    def third_party_model_dao(self) -> ThirdPartyModelDAO:
        return self._third_party_model_dao

    @property
    def mcp_config_dao(self) -> MCPConfigDAO:
        return self._mcp_config_dao

    @property
    def chat_history_dao(self) -> ChatHistoryDAO:
        return self._chat_history_dao

    @property
    def cleaner(self) -> Cleaner:
        return self._cleaner

# Global singleton instance
manager_instance = None


def get_manager():
    """Get Manager singleton instance"""
    global manager_instance
    if manager_instance is None:
        manager_instance = Manager()
    return manager_instance
