"""审计日志系统 - JSONL 事件流 + 证据文件组织"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from app.schema import SessionState, Action, Decision, ExecutionResult
from app.logger import get_logger


class AuditLog:
    """审计日志管理器"""
    
    def __init__(self, logs_dir: str = "logs/sessions"):
        """初始化审计日志"""
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_dir: Optional[Path] = None
        self.current_log_file: Optional[Path] = None
        self.logger = get_logger("audit")
    
    def start_session(self, session_id: str):
        """开始新会话日志"""
        self.current_session_dir = self.logs_dir / session_id
        self.current_session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建证据目录
        (self.current_session_dir / "evidence").mkdir(exist_ok=True)
        
        # 创建日志文件
        self.current_log_file = self.current_session_dir / "events.jsonl"
        
        # 写入会话开始事件
        self.log_event({
            "type": "session_start",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        })
        
        self.logger.info(f"会话开始: {session_id}")
    
    def log_event(self, event: Dict[str, Any]):
        """记录事件到 JSONL"""
        if not self.current_log_file:
            raise RuntimeError("没有活动会话，请先调用 start_session()")
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    def log_llm_draft(self, action: Action, plan: Dict[str, Any]):
        """记录 LLM 生成的动作草案"""
        self.log_event({
            "type": "llm_draft",
            "timestamp": datetime.now().isoformat(),
            "action": action.dict(),
            "plan": plan
        })
    
    def log_user_decision(self, decision: Decision, action: Action):
        """记录用户决策"""
        event = {
            "type": "user_decision",
            "timestamp": datetime.now().isoformat(),
            "status": decision.status,
            "action_id": action.id,
            "action_tool": action.tool
        }
        
        if decision.edited_draft:
            event["edited_action"] = decision.edited_draft.dict()
        
        self.log_event(event)
    
    def log_execution_result(self, result: ExecutionResult, action: Action):
        """记录执行结果"""
        self.log_event({
            "type": "execution_result",
            "timestamp": datetime.now().isoformat(),
            "action_id": action.id,
            "action_tool": action.tool,
            "success": result.success,
            "execution_time": result.execution_time,
            "evidence_paths": result.evidence_paths,
            "error": result.error
        })
    
    def log_step(self, step_id: str, action: Action, decision: Decision, result: ExecutionResult):
        """记录完整步骤（便捷方法）"""
        self.log_event({
            "type": "step_complete",
            "timestamp": datetime.now().isoformat(),
            "step_id": step_id,
            "action": action.dict(),
            "decision": decision.dict(),
            "result": result.dict()
        })
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """记录错误"""
        event = {
            "type": "error",
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        if context:
            event["context"] = context
        
        self.log_event(event)
        self.logger.error(f"审计日志错误: {error}", exc_info=True)
    
    def end_session(self, state: SessionState):
        """结束会话，写入摘要"""
        summary = {
            "type": "session_end",
            "timestamp": datetime.now().isoformat(),
            "session_id": state.session_id,
            "task": state.task,
            "step_count": state.step_count,
            "total_steps": len(state.history),
            "created_at": state.created_at.isoformat()
        }
        
        self.log_event(summary)
        
        # 重置
        self.current_session_dir = None
        self.current_log_file = None
    
    def get_session_log(self, session_id: str) -> list:
        """获取会话日志（读取 JSONL）"""
        log_file = self.logs_dir / session_id / "events.jsonl"
        
        if not log_file.exists():
            return []
        
        events = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return events
    
    def list_sessions(self) -> list:
        """列出所有会话"""
        sessions = []
        for session_dir in self.logs_dir.iterdir():
            if session_dir.is_dir() and (session_dir / "events.jsonl").exists():
                sessions.append({
                    "session_id": session_dir.name,
                    "path": str(session_dir)
                })
        
        return sorted(sessions, key=lambda x: x["session_id"], reverse=True)
