"""日志分析工具 - 分析日志数据，生成报告"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
from tools.log_viewer import LogViewer


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.viewer = LogViewer(logs_dir)
    
    def analyze_performance(self, session_id: Optional[str] = None,
                           days: int = 7) -> Dict[str, Any]:
        """分析性能数据"""
        if session_id:
            events = self.viewer.read_session_log(session_id)
        else:
            # 分析最近 N 天的所有会话
            sessions = self.viewer.list_sessions(limit=100)
            events = []
            for session in sessions:
                session_events = self.viewer.read_session_log(session["session_id"])
                events.extend(session_events)
        
        performance_data = {
            "total_actions": 0,
            "avg_execution_time": 0.0,
            "slow_actions": [],
            "tool_performance": defaultdict(list),
            "error_rate": 0.0
        }
        
        total_time = 0.0
        total_actions = 0
        errors = 0
        
        for event in events:
            if event.get("type") == "execution_result":
                result = event.get("result", {})
                execution_time = result.get("execution_time", 0)
                tool = event.get("action_tool", "unknown")
                
                performance_data["total_actions"] += 1
                total_time += execution_time
                total_actions += 1
                performance_data["tool_performance"][tool].append(execution_time)
                
                if not result.get("success", False):
                    errors += 1
                
                # 慢操作（> 1 秒）
                if execution_time > 1.0:
                    performance_data["slow_actions"].append({
                        "tool": tool,
                        "time": execution_time,
                        "timestamp": event.get("timestamp", "")
                    })
        
        if total_actions > 0:
            performance_data["avg_execution_time"] = total_time / total_actions
            performance_data["error_rate"] = errors / total_actions
        
        # 计算每个工具的平均执行时间
        tool_stats = {}
        for tool, times in performance_data["tool_performance"].items():
            if times:
                tool_stats[tool] = {
                    "avg_time": sum(times) / len(times),
                    "max_time": max(times),
                    "min_time": min(times),
                    "count": len(times)
                }
        
        performance_data["tool_stats"] = tool_stats
        return performance_data
    
    def analyze_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """分析使用模式"""
        sessions = self.viewer.list_sessions(limit=200)
        
        patterns = {
            "daily_usage": defaultdict(int),
            "tool_usage": Counter(),
            "action_types": Counter(),
            "user_decisions": {
                "confirm": 0,
                "reject": 0,
                "edit": 0
            },
            "peak_hours": defaultdict(int)
        }
        
        for session in sessions:
            events = self.viewer.read_session_log(session["session_id"])
            
            for event in events:
                event_type = event.get("type", "")
                timestamp = event.get("timestamp", "")
                
                # 日期统计
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        date_key = dt.strftime("%Y-%m-%d")
                        patterns["daily_usage"][date_key] += 1
                        
                        hour = dt.hour
                        patterns["peak_hours"][hour] += 1
                    except:
                        pass
                
                # 工具使用统计
                if event_type == "execution_result":
                    tool = event.get("action_tool", "unknown")
                    patterns["tool_usage"][tool] += 1
                
                # 动作类型统计
                if event_type in ["llm_draft", "user_decision", "execution_result"]:
                    patterns["action_types"][event_type] += 1
                
                # 用户决策统计
                if event_type == "user_decision":
                    status = event.get("status", "")
                    if status in patterns["user_decisions"]:
                        patterns["user_decisions"][status] += 1
        
        return {
            "daily_usage": dict(patterns["daily_usage"]),
            "tool_usage": dict(patterns["tool_usage"]),
            "action_types": dict(patterns["action_types"]),
            "user_decisions": patterns["user_decisions"],
            "peak_hours": dict(patterns["peak_hours"])
        }
    
    def generate_report(self, output_path: str = "logs/analysis_report.json") -> str:
        """生成分析报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "performance": self.analyze_performance(),
            "usage_patterns": self.analyze_usage_patterns(),
            "error_summary": self.viewer.get_error_summary(),
            "recent_sessions": self.viewer.list_sessions(limit=10)
        }
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(output)
    
    def find_issues(self) -> List[Dict[str, Any]]:
        """查找潜在问题"""
        issues = []
        
        # 检查错误率
        error_summary = self.viewer.get_error_summary()
        if error_summary["total"] > 10:
            issues.append({
                "type": "high_error_rate",
                "severity": "warning",
                "message": f"检测到 {error_summary['total']} 个错误",
                "details": error_summary
            })
        
        # 检查性能问题
        performance = self.analyze_performance()
        if performance["slow_actions"]:
            issues.append({
                "type": "slow_operations",
                "severity": "info",
                "message": f"发现 {len(performance['slow_actions'])} 个慢操作",
                "details": performance["slow_actions"][:10]
            })
        
        # 检查用户拒绝率
        patterns = self.analyze_usage_patterns()
        decisions = patterns.get("user_decisions", {})
        total_decisions = sum(decisions.values())
        if total_decisions > 0:
            reject_rate = decisions.get("reject", 0) / total_decisions
            if reject_rate > 0.3:
                issues.append({
                    "type": "high_reject_rate",
                    "severity": "warning",
                    "message": f"用户拒绝率较高: {reject_rate:.1%}",
                    "details": decisions
                })
        
        return issues
