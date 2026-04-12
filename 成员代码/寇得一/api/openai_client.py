"""OpenAI API 客户端 - 封装所有 OpenAI API 调用"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.schema import LLMResponse, Action, Plan, Context
from api.base_client import BaseAPIClient


class OpenAIClient(BaseAPIClient):
    """OpenAI API 客户端"""
    
    def __init__(self, config: Dict[str, Any] = None, config_path: str = None):
        """
        初始化客户端
        
        Args:
            config: API 配置字典（优先使用，从 config.yaml 的 openai 部分读取）
            config_path: 配置文件路径（向后兼容，如果 config 为 None）
        """
        # 向后兼容：支持旧的 config_path 方式
        if config is None:
            if config_path:
                full_config = self._load_config(config_path)
                config = full_config.get("openai", {})
            else:
                raise ValueError("必须提供 config 或 config_path")
        
        super().__init__(config)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件（向后兼容）"""
        config_file = Path(config_path)
        if not config_file.exists():
            example_file = Path(config_path + ".example")
            if example_file.exists():
                config_file = example_file
            else:
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_client(self):
        """设置 OpenAI 客户端"""
        self.client = OpenAI(api_key=self.config["api_key"])
        self.model = self.config.get("model", "gpt-4")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)
        self.base_url = self.config.get("base_url")  # 可选的自定义端点
    
    def _call_api(self, prompt: str, system_prompt: str) -> str:
        """
        调用 OpenAI API（实现基类的抽象方法）
        
        Args:
            prompt: 用户 prompt
            system_prompt: 系统 prompt
        
        Returns:
            str: JSON 格式的响应字符串
        """
        # 如果配置了自定义 base_url，使用它
        if self.base_url:
            from openai import OpenAI
            client = OpenAI(api_key=self.config["api_key"], base_url=self.base_url)
        else:
            client = self.client
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}  # 强制 JSON 输出
        )
        
        return response.choices[0].message.content
    
    def _get_system_prompt(self) -> str:
        """系统提示词"""
        return """你是一个 macOS 自动化助手。你的任务是分析用户需求，生成结构化的执行计划和下一步动作。

输出格式必须是有效的 JSON，包含以下字段：
{
  "plan": {
    "steps": ["步骤1描述", "步骤2描述", ...]
  },
  "next_action": {
    "id": "唯一标识符",
    "tool": "工具名称（如 fs.move, web.click）",
    "args": {"参数名": "参数值"},
    "risk": "low|medium|high",
    "why": "执行此动作的原因",
    "required_evidence": ["证据类型列表"]
  },
  "rationale": "选择此动作的理由",
  "is_complete": false
}

可用工具：
- fs.list, fs.search, fs.move, fs.rename, fs.copy, fs.trash
- web.open, web.click, web.type, web.extract, web.snapshot, web.download
- wx.open_chat, wx.paste_text
- notes.search, notes.create, notes.append

风险等级：
- low: 只读操作（list, search, snapshot, extract）
- medium: 可逆变更（move, rename, copy, type, create）
- high: 不可逆或对外操作（trash, submit, download）

每次只生成一个 next_action，执行完后再生成下一步。"""
    
    def _build_prompt(
        self,
        task: str,
        context: Context,
        history: List[Dict[str, Any]]
    ) -> str:
        """构建用户提示词"""
        prompt = f"用户任务: {task}\n\n"
        
        # 添加上下文
        prompt += "当前上下文:\n"
        if context.front_app:
            prompt += f"- 前台应用: {context.front_app}\n"
        if context.front_window:
            prompt += f"- 前台窗口: {context.front_window}\n"
        if context.browser_url:
            prompt += f"- 浏览器 URL: {context.browser_url}\n"
        if context.file_context:
            prompt += f"- 文件上下文: {json.dumps(context.file_context, indent=2, ensure_ascii=False)}\n"
        
        # 添加历史
        if history:
            prompt += "\n执行历史:\n"
            for i, entry in enumerate(history[-5:], 1):  # 只显示最近 5 条
                if "draft" in entry:
                    action = entry["draft"].get("next_action", {})
                    prompt += f"{i}. {action.get('tool', 'unknown')}: {action.get('why', '')}\n"
                    if "result" in entry:
                        result = entry["result"]
                        prompt += f"   结果: {'成功' if result.get('success') else '失败'}\n"
        
        prompt += "\n请生成下一步动作（JSON 格式）。"
        
        return prompt
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        通用聊天补全接口
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数（可选，使用默认值）
            max_tokens: 最大 token 数（可选，使用默认值）
        
        Returns:
            响应文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens
        )
        
        return response.choices[0].message.content
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本嵌入向量
        
        Args:
            text: 输入文本
        
        Returns:
            嵌入向量
        """
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        
        return response.data[0].embedding
