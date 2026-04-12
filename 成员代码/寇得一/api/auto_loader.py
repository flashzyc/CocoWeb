"""自动加载 API 客户端 - 系统自动发现和加载所有 API 客户端"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Type, Optional
import yaml
from api.base_client import BaseAPIClient


class APIAutoLoader:
    """自动加载 API 客户端"""
    
    _clients: Dict[str, Type[BaseAPIClient]] = {}
    _initialized = False
    
    @classmethod
    def discover_clients(cls, api_dir: str = "api") -> Dict[str, Type[BaseAPIClient]]:
        """
        自动发现所有 API 客户端
        
        扫描 api/ 目录，找到所有继承 BaseAPIClient 的类
        """
        if cls._initialized:
            return cls._clients
        
        api_path = Path(api_dir)
        
        # 扫描所有 Python 文件
        for file_path in api_path.glob("*.py"):
            # 跳过特殊文件
            if file_path.name.startswith("_") or file_path.name == "base_client.py":
                continue
            
            module_name = file_path.stem
            
            try:
                # 动态导入模块
                module = importlib.import_module(f"api.{module_name}")
                
                # 查找所有继承 BaseAPIClient 的类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseAPIClient) and 
                        obj != BaseAPIClient and
                        obj.__module__ == module.__name__):
                        
                        # 使用类名或配置键作为标识
                        client_key = cls._get_client_key(name, module_name)
                        cls._clients[client_key] = obj
                        print(f"发现 API 客户端: {client_key} ({name})")
            
            except Exception as e:
                print(f"加载模块 {module_name} 失败: {e}")
                continue
        
        cls._initialized = True
        return cls._clients
    
    @classmethod
    def _get_client_key(cls, class_name: str, module_name: str) -> str:
        """获取客户端标识键"""
        # 尝试从类名推断（如 OpenAIClient -> openai）
        if class_name.endswith("Client"):
            key = class_name[:-6].lower()  # 移除 "Client"
            # 处理驼峰命名（如 ClaudeClient -> claude）
            if key and key[0].isupper():
                key = key.lower()
            return key
        
        # 否则使用模块名
        return module_name.replace("_client", "").replace("_", "")
    
    @classmethod
    def create_client(cls, provider: str, config_path: str = "config/config.yaml") -> Optional[BaseAPIClient]:
        """
        根据提供商名称自动创建客户端
        
        Args:
            provider: 提供商名称（如 "openai", "claude"）
            config_path: 配置文件路径
        
        Returns:
            BaseAPIClient 实例，如果未找到则返回 None
        """
        # 发现所有客户端
        clients = cls.discover_clients()
        
        if provider not in clients:
            available = ", ".join(clients.keys())
            raise ValueError(
                f"未找到 API 提供商 '{provider}'。"
                f"可用提供商: {available}"
            )
        
        # 加载配置
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
        
        # 获取该提供商的配置
        provider_config = full_config.get(provider, {})
        
        if not provider_config:
            raise ValueError(f"配置文件中未找到 '{provider}' 的配置")
        
        # 创建客户端实例
        client_class = clients[provider]
        return client_class(provider_config)
    
    @classmethod
    def list_providers(cls) -> list:
        """列出所有可用的 API 提供商"""
        clients = cls.discover_clients()
        return list(clients.keys())
    
    @classmethod
    def get_client_info(cls, provider: str) -> Dict[str, str]:
        """获取客户端信息"""
        clients = cls.discover_clients()
        
        if provider not in clients:
            return {}
        
        client_class = clients[provider]
        return {
            "name": client_class.__name__,
            "module": client_class.__module__,
            "doc": client_class.__doc__ or ""
        }
