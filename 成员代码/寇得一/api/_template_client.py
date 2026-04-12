"""API 客户端模板 - 复制此文件创建新的 API 客户端"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.schema import LLMResponse, Context


class TemplateClient:
    """
    API 客户端模板
    
    使用步骤：
    1. 复制此文件为 api/your_api_client.py
    2. 将 TemplateClient 重命名为 YourAPIClient
    3. 实现 _call_api 方法
    4. 在 api/__init__.py 中导出
    5. 在 config/config.yaml 中添加配置
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化客户端"""
        self.config = self._load_config(config_path)
        # TODO: 初始化你的 API 客户端（SDK 或 HTTP 客户端）
        # self.client = YourAPISDK(api_key=self.config["your_api"]["api_key"])
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            example_file = Path(config_path + ".example")
            if example_file.exists():
                config_file = example_file
            else:
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # TODO: 从配置中读取你的 API 配置部分
            return config.get("your_api", {})
    
    def generate_next_action(
        self,
        task: str,
        context: Context,
        history: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> LLMResponse:
        """
        生成下一步动作（必须实现）
        
        Args:
            task: 用户任务描述
            context: 当前上下文
            history: 执行历史
            max_retries: 最大重试次数
        
        Returns:
            LLMResponse: LLM 返回的结构化响应
        """
        prompt = self._build_prompt(task, context, history)
        
        for attempt in range(max_retries):
            try:
                # 调用 API
                response_text = self._call_api(prompt)
                
                # 解析 JSON 响应
                data = json.loads(response_text)
                
                # 验证并转换为 Pydantic 模型
                return LLMResponse(**data)
            
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    # 请求模型修正
                    prompt += f"\n\n之前的响应不是有效的 JSON，请修正。错误: {str(e)}"
                    continue
                else:
                    raise ValueError(f"无法解析 JSON 响应（已重试 {max_retries} 次）: {e}")
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                raise
    
    def _call_api(self, prompt: str) -> str:
        """
        调用 API（必须实现）
        
        Args:
            prompt: 完整的 prompt 文本
        
        Returns:
            str: JSON 格式的响应字符串
        """
        # TODO: 实现你的 API 调用逻辑
        # 示例（HTTP 请求）:
        # import requests
        # response = requests.post(
        #     "https://api.example.com/v1/chat",
        #     json={"prompt": prompt},
        #     headers={"Authorization": f"Bearer {self.config['api_key']}"}
        # )
        # return response.json()["content"]
        
        raise NotImplementedError("请实现 _call_api 方法")
    
    def _build_prompt(
        self,
        task: str,
        context: Context,
        history: List[Dict[str, Any]]
    ) -> str:
        """
        构建 prompt（可选：可以复用 OpenAI 的 prompt 构建逻辑）
        """
        # 方式 1: 复用 OpenAI 的 prompt 构建
        from api.openai_client import OpenAIClient
        temp_client = OpenAIClient()
        return temp_client._build_prompt(task, context, history)
        
        # 方式 2: 自定义 prompt 格式
        # prompt = f"用户任务: {task}\n\n"
        # # 添加上下文...
        # return prompt
    
    def _get_system_prompt(self) -> str:
        """
        获取系统提示词（可选：可以复用 OpenAI 的系统提示词）
        """
        from api.openai_client import OpenAIClient
        temp_client = OpenAIClient()
        return temp_client._get_system_prompt()
