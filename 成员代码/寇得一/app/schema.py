"""数据模型定义 - 使用 Pydantic 进行结构化验证"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Action(BaseModel):
    """单个动作定义"""
    id: str = Field(..., description="动作唯一标识")
    tool: str = Field(..., description="工具名称，如 fs.move, web.click")
    args: Dict[str, Any] = Field(..., description="工具参数")
    risk: Literal["low", "medium", "high"] = Field(..., description="风险等级")
    why: str = Field(..., description="执行此动作的原因")
    required_evidence: List[str] = Field(default_factory=list, description="需要收集的证据类型")


class Plan(BaseModel):
    """执行计划（步骤列表）"""
    steps: List[str] = Field(..., description="计划步骤描述列表")


class LLMResponse(BaseModel):
    """LLM 返回的结构化响应"""
    plan: Plan = Field(..., description="整体执行计划")
    next_action: Action = Field(..., description="下一步要执行的动作")
    rationale: str = Field(default="", description="选择此动作的理由")
    is_complete: bool = Field(default=False, description="任务是否已完成")


class ExecutionResult(BaseModel):
    """工具执行结果"""
    success: bool = Field(..., description="是否成功")
    output: Any = Field(default=None, description="执行输出（工具特定）")
    evidence_paths: List[str] = Field(default_factory=list, description="证据文件路径列表")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")
    execution_time: float = Field(default=0.0, description="执行耗时（秒）")


class Decision(BaseModel):
    """用户决策结果"""
    status: Literal["confirm", "reject", "edit"] = Field(..., description="决策状态")
    edited_draft: Optional[Action] = Field(default=None, description="编辑后的动作（仅当 status=edit 时）")
    timestamp: datetime = Field(default_factory=datetime.now, description="决策时间")


class SessionState(BaseModel):
    """会话状态"""
    session_id: str = Field(..., description="会话唯一标识")
    task: str = Field(..., description="用户任务描述")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="执行历史")
    current_context: Dict[str, Any] = Field(default_factory=dict, description="当前上下文")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    step_count: int = Field(default=0, description="已执行步数")


class Context(BaseModel):
    """上下文信息"""
    front_app: Optional[str] = Field(default=None, description="前台应用名称")
    front_window: Optional[str] = Field(default=None, description="前台窗口标题")
    browser_url: Optional[str] = Field(default=None, description="浏览器当前 URL")
    browser_title: Optional[str] = Field(default=None, description="浏览器页面标题")
    file_context: Dict[str, Any] = Field(default_factory=dict, description="文件系统上下文")
    timestamp: datetime = Field(default_factory=datetime.now, description="上下文采集时间")
