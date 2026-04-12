"""API 客户端基类 - 定义标准接口，让系统自动识别"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schema import LLMResponse, Context


class BaseAPIClient(ABC):
    """
    API 客户端基类
    
    所有 API 客户端都应该继承此类，系统会自动识别和加载。
    你只需要实现 _call_api 方法，其他逻辑基类已经处理好了。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化客户端
        
        Args:
            config: API 配置字典（从 config.yaml 中读取）
        """
        self.config = config
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self):
        """设置 API 客户端（SDK 或 HTTP 客户端）"""
        pass
    
    @abstractmethod
    def _call_api(self, prompt: str, system_prompt: str) -> str:
        """
        调用 API（必须实现）
        
        Args:
            prompt: 用户 prompt
            system_prompt: 系统 prompt
        
        Returns:
            str: JSON 格式的响应字符串
        """
        pass
    
    def generate_next_action(
        self,
        task: str,
        context: Context,
        history: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> LLMResponse:
        """
        生成下一步动作（基类已实现，无需重写）
        
        你只需要实现 _call_api 方法即可
        """
        import json
        from api.openai_client import OpenAIClient
        
        # 复用 OpenAI 的 prompt 构建逻辑
        temp_client = OpenAIClient.__new__(OpenAIClient)  # 不调用 __init__
        system_prompt = temp_client._get_system_prompt()
        prompt = temp_client._build_prompt(task, context, history)
        
        for attempt in range(max_retries):
            try:
                # 调用子类实现的 _call_api
                response_text = self._call_api(prompt, system_prompt)
                
                # 解析 JSON
                data = json.loads(response_text)
                
                # 验证并转换为 Pydantic 模型
                return LLMResponse(**data)
            
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    prompt += f"\n\n之前的响应不是有效的 JSON，请修正。错误: {str(e)}"
                    continue
                else:
                    raise ValueError(f"无法解析 JSON 响应（已重试 {max_retries} 次）: {e}")
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                raise
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
