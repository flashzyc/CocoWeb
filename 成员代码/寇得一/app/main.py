"""主应用 - rumps 菜单栏应用"""

import rumps
import subprocess
from pathlib import Path
from app.orchestrator import Orchestrator
from app.audit_log import AuditLog
from app.config_manager import ConfigManager


class MacAgentApp(rumps.App):
    """macOS 自动化代理菜单栏应用"""
    
    def __init__(self):
        super(MacAgentApp, self).__init__("Mac Agent", quit_button=None)
        
        # 检查配置
        self.config_manager = ConfigManager()
        if not self.config_manager.check_and_init():
            # 配置未完成，显示提示
            rumps.alert(
                "请先配置 OpenAI API 密钥",
                title="配置未完成"
            )
        
        self.orchestrator = Orchestrator()
        self.audit_log = AuditLog()
        self.current_task = None
        
        # 菜单项
        self.menu = [
            rumps.MenuItem("新任务", callback=self.new_task),
            rumps.separator,
            rumps.MenuItem("继续执行", callback=self.continue_task),
            rumps.separator,
            rumps.MenuItem("查看日志", callback=self.view_logs),
            rumps.MenuItem("配置", callback=self.open_config),
            rumps.separator,
            rumps.MenuItem("退出", callback=self.quit_app)
        ]
    
    @rumps.clicked("新任务")
    def new_task(self, _):
        """开始新任务"""
        # 使用 rumps 的 Window 获取用户输入
        window = rumps.Window(
            message="请输入任务描述：",
            title="新任务",
            default_text="",
            ok="开始",
            cancel="取消"
        )
        response = window.run()
        
        if response.clicked and response.text and response.text.strip():
            task = response.text.strip()
            try:
                # 开始新会话
                state = self.orchestrator.start_session(task)
                self.current_task = task
                
                # 执行第一步
                result = self.orchestrator.execute_step()
                
                # 显示结果
                self._show_result(result)
                
            except Exception as e:
                rumps.alert(f"错误: {str(e)}", title="执行失败")
    
    @rumps.clicked("继续执行")
    def continue_task(self, _):
        """继续执行下一步"""
        if not self.orchestrator.current_state:
            rumps.alert("没有活动任务，请先创建新任务", title="提示")
            return
        
        try:
            result = self.orchestrator.continue_task()
            self._show_result(result)
            
            # 如果任务完成，清理状态
            if result.get("status") == "complete":
                self._end_session()
        
        except Exception as e:
            rumps.alert(f"错误: {str(e)}", title="执行失败")
    
    def _show_result(self, result: dict):
        """显示执行结果"""
        status = result.get("status", "unknown")
        message = result.get("message", "")
        
        if status == "complete":
            rumps.alert(message, title="任务完成")
            self._end_session()
        elif status == "rejected":
            rumps.alert(message, title="操作已拒绝")
        elif status == "success":
            # 成功但不显示弹窗，只在通知中提示
            rumps.notification(
                title="执行成功",
                subtitle=result.get("action", {}).get("tool", ""),
                message=message
            )
        elif status == "error":
            rumps.alert(f"执行失败: {message}", title="错误")
    
    def _end_session(self):
        """结束会话"""
        if self.orchestrator.current_state:
            self.audit_log.end_session(self.orchestrator.current_state)
            self.current_task = None
    
    @rumps.clicked("查看日志")
    def view_logs(self, _):
        """打开日志目录"""
        logs_dir = Path("logs/sessions")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        subprocess.run(["open", str(logs_dir.resolve())])
    
    @rumps.clicked("配置")
    def open_config(self, _):
        """打开配置文件"""
        self.config_manager._open_config_file()
    
    @rumps.clicked("退出")
    def quit_app(self, _):
        """退出应用"""
        # 结束当前会话
        if self.orchestrator.current_state:
            self._end_session()
        
        rumps.quit_application()


if __name__ == "__main__":
    app = MacAgentApp()
    app.run()
