"""Approval Gate - 硬闸门，所有操作必须确认"""

import yaml
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from pathlib import Path
from typing import Optional, Dict, Any
from app.schema import Action, Decision


class ApprovalGate:
    """确认闸门 - Tkinter 弹窗实现"""
    
    def __init__(self, policy_path: str = "config/policy.yaml"):
        """初始化，加载风险策略"""
        self.policy = self._load_policy(policy_path)
        self.auto_allow_low_risk = self.policy.get("auto_allow_low_risk", False)
        self.low_risk_confirmed = False  # 首次低风险操作确认标志
    
    def _load_policy(self, policy_path: str) -> Dict[str, Any]:
        """加载风险策略"""
        policy_file = Path(policy_path)
        if not policy_file.exists():
            raise FileNotFoundError(f"策略文件不存在: {policy_path}")
        
        with open(policy_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_risk_level(self, tool_name: str) -> str:
        """根据工具名称获取风险等级"""
        risk_levels = self.policy.get("risk_levels", {})
        
        for level, tools in risk_levels.items():
            if tool_name in tools:
                return level
        
        # 默认中等风险
        return "medium"
    
    def _get_confirmation_strategy(self, risk_level: str) -> str:
        """获取确认策略"""
        strategies = self.policy.get("confirmation_strategy", {})
        return strategies.get(risk_level, "always_prompt")
    
    def prompt(self, action: Action, context: Dict[str, Any] = None) -> Decision:
        """
        显示确认弹窗
        
        Args:
            action: 要确认的动作
            context: 上下文信息（可选）
        
        Returns:
            Decision: 用户决策
        """
        risk_level = self._get_risk_level(action.tool)
        strategy = self._get_confirmation_strategy(risk_level)
        
        # 低风险自动允许（首次确认后）
        if risk_level == "low" and strategy == "auto_allow_after_first":
            if self.auto_allow_low_risk and self.low_risk_confirmed:
                return Decision(status="confirm")
            elif not self.low_risk_confirmed:
                # 首次询问是否自动允许
                decision = self._show_low_risk_prompt(action)
                if decision.status == "confirm":
                    self.low_risk_confirmed = True
                return decision
        
        # 高风险二次确认
        if risk_level == "high" and strategy == "double_confirm":
            return self._show_high_risk_prompt(action, context)
        
        # 中等风险或必须提示的情况
        return self._show_standard_prompt(action, context, risk_level)
    
    def _show_low_risk_prompt(self, action: Action) -> Decision:
        """低风险操作首次提示（询问是否自动允许）"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        msg = f"低风险操作：{action.tool}\n\n{action.why}\n\n是否允许本次会话自动执行所有低风险操作？"
        
        result = messagebox.askyesnocancel(
            "低风险操作确认",
            msg,
            icon="question"
        )
        
        root.destroy()
        
        if result is None:  # Cancel
            return Decision(status="reject")
        elif result:  # Yes - 自动允许
            self.auto_allow_low_risk = True
            return Decision(status="confirm")
        else:  # No - 仅本次确认
            return Decision(status="confirm")
    
    def _show_standard_prompt(self, action: Action, context: Dict[str, Any], risk_level: str) -> Decision:
        """标准确认弹窗"""
        root = tk.Tk()
        root.title(f"操作确认 - {risk_level.upper()} 风险")
        root.geometry("600x500")
        
        decision_result = {"status": None, "edited_draft": None}
        
        # 标题
        title_frame = ttk.Frame(root, padding="10")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(
            title_frame,
            text=f"工具: {action.tool}",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W)
        
        ttk.Label(
            title_frame,
            text=f"风险等级: {risk_level.upper()}",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        # 原因
        reason_frame = ttk.LabelFrame(root, text="执行原因", padding="10")
        reason_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        reason_text = scrolledtext.ScrolledText(reason_frame, height=3, wrap=tk.WORD)
        reason_text.insert("1.0", action.why)
        reason_text.config(state=tk.DISABLED)
        reason_text.pack(fill=tk.BOTH, expand=True)
        
        # 参数
        args_frame = ttk.LabelFrame(root, text="参数", padding="10")
        args_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        args_text = scrolledtext.ScrolledText(args_frame, height=5, wrap=tk.WORD)
        args_text.insert("1.0", json.dumps(action.args, indent=2, ensure_ascii=False))
        args_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮
        button_frame = ttk.Frame(root, padding="10")
        button_frame.pack(fill=tk.X)
        
        def on_confirm():
            decision_result["status"] = "confirm"
            root.quit()
        
        def on_reject():
            decision_result["status"] = "reject"
            root.quit()
        
        def on_edit():
            # 允许编辑参数
            edited_args = args_text.get("1.0", tk.END).strip()
            try:
                edited_dict = json.loads(edited_args)
                edited_action = Action(
                    id=action.id,
                    tool=action.tool,
                    args=edited_dict,
                    risk=action.risk,
                    why=action.why,
                    required_evidence=action.required_evidence
                )
                decision_result["status"] = "edit"
                decision_result["edited_draft"] = edited_action
                root.quit()
            except json.JSONDecodeError:
                messagebox.showerror("错误", "参数格式无效，请输入有效的 JSON")
        
        ttk.Button(button_frame, text="确认执行", command=on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编辑参数", command=on_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="拒绝", command=on_reject).pack(side=tk.LEFT, padx=5)
        
        # 使参数可编辑
        args_text.config(state=tk.NORMAL)
        
        root.mainloop()
        root.destroy()
        
        if decision_result["status"] is None:
            return Decision(status="reject")
        
        if decision_result["status"] == "edit":
            return Decision(status="edit", edited_draft=decision_result["edited_draft"])
        
        return Decision(status=decision_result["status"])
    
    def _show_high_risk_prompt(self, action: Action, context: Dict[str, Any]) -> Decision:
        """高风险操作二次确认"""
        # 第一次确认
        root1 = tk.Tk()
        root1.withdraw()
        
        confirm_word = self.policy.get("high_risk_confirm_word", "CONFIRM")
        
        msg = f"⚠️ 高风险操作警告 ⚠️\n\n工具: {action.tool}\n原因: {action.why}\n\n参数: {json.dumps(action.args, indent=2, ensure_ascii=False)}\n\n此操作可能造成不可逆的后果。\n\n请输入确认词 '{confirm_word}' 继续："
        
        user_input = simpledialog.askstring(
            "高风险操作 - 第一次确认",
            msg,
            parent=root1
        )
        
        root1.destroy()
        
        if user_input != confirm_word:
            return Decision(status="reject")
        
        # 第二次确认（标准弹窗）
        return self._show_standard_prompt(action, context, "high")
