# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

"""Controller module for the robot dog Miloco runtime."""

from miloco_server.controller.auth_controller import router as auth_router
from miloco_server.controller.chat_controller import router as chat_router
from miloco_server.controller.mcp_controller import router as mcp_router
from miloco_server.controller.model_controller import router as model_router
from miloco_server.controller.web_controller import router as web_router


__all__ = [
    "web_router",
    "auth_router",
    "chat_router",
    "model_router",
    "mcp_router",
]
