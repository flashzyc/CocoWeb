"""Orchestrator - 任务编排和状态机，确保单步执行"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.schema import SessionState, Action, LLMResponse, Decision, ExecutionResult, Context
from app.llm_client import LLMClient
from app.approval_gate import ApprovalGate
from app.context import collect_context, extract_paths_from_action
from app.audit_log import AuditLog
from app.logger import get_logger
from tools.executor import execute_action


class Orchestrator:
    """任务编排器 - 状态机实现"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化编排器"""
        self.llm_client = LLMClient(config_path)
        self.approval_gate = ApprovalGate()
        self.audit_log = AuditLog()
        self.logger = get_logger("orchestrator")
        self.current_state: Optional[SessionState] = None
    
    def start_session(self, task: str) -> SessionState:
        """开始新会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        self.current_state = SessionState(
            session_id=session_id,
            task=task,
            history=[],
            current_context={},
            step_count=0
        )
        
        # 启动审计日志
        self.audit_log.start_session(session_id)
        self.logger.info(f"开始新会话: {session_id}, 任务: {task}")
        
        return self.current_state
    
    def execute_step(self) -> Dict[str, Any]:
        """
        执行单步操作
        
        流程：
        1. 收集上下文
        2. LLM 生成下一步动作
        3. Approval Gate 确认
        4. 执行动作
        5. 记录结果
        6. 更新状态
        
        Returns:
            执行结果字典
        """
        if not self.current_state:
            raise RuntimeError("没有活动会话，请先调用 start_session()")
        
        step_id = f"step-{self.current_state.step_count:04d}"
        
        try:
            # 1. 收集上下文
            context = self._collect_context()
            self.current_state.current_context = context.dict()
            
            # 2. LLM 生成下一步动作
            self.logger.debug(f"生成下一步动作: step_id={step_id}")
            llm_response = self.llm_client.generate_next_action(
                task=self.current_state.task,
                context=context,
                history=self.current_state.history
            )
            
            # 检查是否完成
            if llm_response.is_complete:
                self.logger.info(f"任务完成: {self.current_state.task}")
                return {
                    "status": "complete",
                    "message": "任务已完成",
                    "plan": llm_response.plan.dict()
                }
            
            action = llm_response.next_action
            action.id = step_id  # 确保使用正确的 step_id
            
            self.logger.info(f"LLM 生成动作: {action.tool}, risk={action.risk}")
            
            # 记录 LLM 草案
            self.audit_log.log_llm_draft(action, llm_response.plan.dict())
            
            # 3. Approval Gate 确认
            self.logger.debug("等待用户确认...")
            decision = self.approval_gate.prompt(action, context.dict())
            
            # 记录用户决策
            self.audit_log.log_user_decision(decision, action)
            self.logger.info(f"用户决策: {decision.status}")
            
            if decision.status == "reject":
                self.logger.warning(f"用户拒绝了操作: {action.tool}")
                self.current_state.history.append({
                    "step_id": step_id,
                    "event": "rejected",
                    "draft": action.dict(),
                    "timestamp": datetime.now().isoformat()
                })
                return {
                    "status": "rejected",
                    "message": "用户拒绝了此操作"
                }
            
            # 如果编辑了，使用编辑后的动作
            if decision.status == "edit" and decision.edited_draft:
                self.logger.info("用户编辑了动作参数")
                action = decision.edited_draft
                action.id = step_id
            
            # 4. 执行动作
            self.logger.info(f"执行动作: {action.tool}")
            result = execute_action(action, self.current_state.session_id)
            
            # 记录执行结果
            self.audit_log.log_execution_result(result, action)
            self.audit_log.log_step(step_id, action, decision, result)
            
            # 5. 记录结果
            history_entry = {
                "step_id": step_id,
                "timestamp": datetime.now().isoformat(),
                "draft": action.dict(),
                "decision": decision.dict(),
                "result": result.dict()
            }
            
            self.current_state.history.append(history_entry)
            self.current_state.step_count += 1
            
            if result.success:
                self.logger.info(f"动作执行成功: {action.tool}, 耗时: {result.execution_time:.2f}s")
            else:
                self.logger.error(f"动作执行失败: {action.tool}, 错误: {result.error}")
            
            # 6. 返回结果
            return {
                "status": "success" if result.success else "error",
                "step_id": step_id,
                "action": action.dict(),
                "result": result.dict(),
                "message": "执行成功" if result.success else f"执行失败: {result.error}"
            }
        
        except Exception as e:
            # 记录错误
            self.logger.error(f"执行步骤出错: {step_id}", exc_info=True)
            error_entry = {
                "step_id": step_id,
                "timestamp": datetime.now().isoformat(),
                "event": "error",
                "error": str(e)
            }
            self.current_state.history.append(error_entry)
            
            return {
                "status": "error",
                "step_id": step_id,
                "error": str(e),
                "message": f"执行出错: {e}"
            }
    
    def _collect_context(self) -> Context:
        """收集上下文"""
        # 从历史中提取可能需要检查的路径
        file_paths = []
        
        if self.current_state.history:
            last_entry = self.current_state.history[-1]
            if "draft" in last_entry:
                action_dict = last_entry["draft"]
                args = action_dict.get("args", {})
                file_paths = extract_paths_from_action(args)
        
        # 收集上下文
        context = collect_context(
            file_paths=file_paths if file_paths else None,
            check_browser=False  # 可根据需要启用
        )
        
        return context
    
    def get_state(self) -> Optional[SessionState]:
        """获取当前状态"""
        return self.current_state
    
    def continue_task(self) -> Dict[str, Any]:
        """继续执行下一步（单步）"""
        if not self.current_state:
            raise RuntimeError("没有活动会话")
        
        return self.execute_step()
