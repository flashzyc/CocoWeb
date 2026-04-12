"""LLM Client - 封装层，自动加载和调用 API 模块"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from app.schema import LLMResponse, Context
from api.auto_loader import APIAutoLoader


class LLMClient:
    """LLM 客户端封装层 - 自动加载 API 客户端"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化客户端
        
        自动从配置文件读取 api_provider，然后加载对应的 API 客户端
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # 获取 API 提供商（默认 openai）
        provider = self.config.get("api_provider", "openai")
        
        # 自动创建客户端
        self.api_client = APIAutoLoader.create_client(provider, config_path)
        
        if not self.api_client:
            raise ValueError(f"无法创建 API 客户端: {provider}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            example_file = Path(self.config_path + ".example")
            if example_file.exists():
                config_file = example_file
            else:
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def generate_next_action(
        self,
        task: str,
        context: Context,
        history: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> LLMResponse:
        """
        生成下一步动作
        
        Args:
            task: 用户任务描述
            context: 当前上下文
            history: 执行历史
            max_retries: 最大重试次数（用于 JSON 解析失败时）
        
        Returns:
            LLMResponse: LLM 返回的结构化响应
        """
        return self.api_client.generate_next_action(task, context, history, max_retries)
