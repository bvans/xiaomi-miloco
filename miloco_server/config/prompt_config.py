# Copyright (C) 2025 Xiaomi Corporation
# This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.

"""
Prompt configuration file
Unified management of system prompts in different languages
Load configuration from prompt_config.yaml
"""

from enum import Enum
from miloco_server.config.config_loader import load_yaml_config, get_project_root


class UserLanguage(str, Enum):
    """User language enumeration - avoid circular imports"""
    CHINESE = "zh"
    ENGLISH = "en"


class PromptType(str, Enum):
    """Prompt type enumeration"""
    CHAT = "chat"                           # Chat conversation prompts
    VISION_UNDERSTANDING = "vision_understanding"  # Vision understanding prompts

# Get project root directory
PROJECT_ROOT = get_project_root()

# Load server config for template variables (avoid circular import by loading directly)
SERVER_CONFIG_FILE = PROJECT_ROOT.parent / "config" / "server_config.yaml"
_server_config = load_yaml_config(SERVER_CONFIG_FILE)

# Get configuration values for template variables
CAMERA_IMG_FRAME_INTERVAL = _server_config["camera"]["frame_interval"]
CHAT_VISION_USE_IMG_COUNT = _server_config["chat"]["vision_use_img_count"]

# Load prompt configuration
PROMPT_CONFIG_FILE = PROJECT_ROOT.parent / "config" / "prompt_config.yaml"
_config = load_yaml_config(PROMPT_CONFIG_FILE)

def _format_vision_system_prompt(prompt_text: str) -> str:
    """Format prompt text, replace template variables"""
    return prompt_text.format(
        frame_interval=CAMERA_IMG_FRAME_INTERVAL,
        vision_use_img_count=CHAT_VISION_USE_IMG_COUNT
    )

class PromptConfig:
    """Prompt configuration class - supports multiple types of prompts"""
    # Chat conversation prompts
    CHAT_PROMPTS = {
        UserLanguage.CHINESE: _format_vision_system_prompt(_config["prompts"]["chat"]["chinese"]),
        UserLanguage.ENGLISH: _format_vision_system_prompt(_config["prompts"]["chat"]["english"])
    }

    # Vision understanding prompts
    VISION_UNDERSTANDING_PROMPTS = {
        UserLanguage.CHINESE: _format_vision_system_prompt(_config["prompts"]["vision_understanding"]["chinese"]),
        UserLanguage.ENGLISH: _format_vision_system_prompt(_config["prompts"]["vision_understanding"]["english"])
    }

    # Vision understanding UI text prefixes
    VISION_UNDERSTANDING_PREFIXES = {
        UserLanguage.CHINESE: _config["prompts"]["vision_understanding_prefixes"]["chinese"],
        UserLanguage.ENGLISH: _config["prompts"]["vision_understanding_prefixes"]["english"]
    }

    # Unified mapping of all prompts
    ALL_PROMPTS = {
        PromptType.CHAT: CHAT_PROMPTS,
        PromptType.VISION_UNDERSTANDING: VISION_UNDERSTANDING_PROMPTS,
    }

    @classmethod
    def get_prompt(cls, prompt_type: PromptType, language: UserLanguage) -> str:
        """
        Get prompt based on type and language
        
        Args:
            prompt_type: Prompt type
            language: User language, defaults to Chinese
            
        Returns:
            Prompt corresponding to the type and language
        """
        prompts_dict = cls.ALL_PROMPTS.get(prompt_type, cls.CHAT_PROMPTS)
        return prompts_dict.get(language, prompts_dict[UserLanguage.CHINESE])

    @classmethod
    def get_system_prompt(cls, prompt_type: PromptType, language: UserLanguage) -> str:
        """
        Get prompt (backward compatibility)
        
        Args:
            prompt_type: Prompt type
            language: User language, defaults to Chinese
            
        Returns:
            Prompt
        """
        return cls.get_prompt(prompt_type, language)

    @classmethod
    def get_vision_understanding_prefixes(cls, language: UserLanguage) -> dict[str, str]:
        """
        Get vision understanding UI text prefixes based on language
        
        Args:
            language: User language, defaults to Chinese
            
        Returns:
            Dictionary containing user_content, camera_prefix, channel_prefix, sequence_prefix
        """
        return cls.VISION_UNDERSTANDING_PREFIXES.get(language, cls.VISION_UNDERSTANDING_PREFIXES[UserLanguage.CHINESE])
