"""日志查看器工具 - 查看和分析日志"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict


class LogViewer:
    """日志查看器"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.runtime_logs_dir = self.logs_dir / "runtime"
        self.audit_logs_dir = self.logs_dir / "sessions"
    
    def read_runtime_log(self, log_file: str = "app.log", 
                        level: Optional[str] = None,
                        module: Optional[str] = None,
                        lines: int = 100) -> List[str]:
        """
        读取运行日志
        
        Args:
            log_file: 日志文件名（app.log 或 error.log）
            level: 过滤级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            module: 过滤模块名
            lines: 读取行数（从末尾开始）
        """
        log_path = self.runtime_logs_dir / log_file
        
        if not log_path.exists():
            return []
        
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # 取最后 N 行
        lines_to_read = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # 过滤
        filtered_lines = []
        for line in lines_to_read:
            if level and level not in line:
                continue
            if module and module not in line:
                continue
            filtered_lines.append(line.strip())
        
        return filtered_lines
    
    def read_session_log(self, session_id: str) -> List[Dict[str, Any]]:
        """读取会话日志（JSONL）"""
        log_file = self.audit_logs_dir / session_id / "events.jsonl"
        
        if not log_file.exists():
            return []
        
        events = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        return events
    
    def search_logs(self, query: str, log_file: str = "app.log", 
                   case_sensitive: bool = False) -> List[str]:
        """搜索日志"""
        log_path = self.runtime_logs_dir / log_file
        
        if not log_path.exists():
            return []
        
        pattern = re.compile(query if case_sensitive else query.lower())
        matches = []
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                search_text = line if case_sensitive else line.lower()
                if pattern.search(search_text):
                    matches.append(line.strip())
        
        return matches
    
    def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取错误摘要"""
        error_log = self.runtime_logs_dir / "error.log"
        
        if not error_log.exists():
            return {"total": 0, "by_level": {}, "recent": []}
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        errors_by_level = defaultdict(int)
        recent_errors = []
        
        with open(error_log, 'r', encoding='utf-8') as f:
            for line in f:
                # 解析日志行
                # 格式: 2024-01-01 12:00:00 | ERROR | module | message
                parts = line.split('|')
                if len(parts) >= 3:
                    level = parts[1].strip()
                    message = '|'.join(parts[2:]).strip()
                    
                    errors_by_level[level] += 1
                    recent_errors.append({
                        "level": level,
                        "message": message,
                        "line": line.strip()
                    })
        
        return {
            "total": sum(errors_by_level.values()),
            "by_level": dict(errors_by_level),
            "recent": recent_errors[-20:]  # 最近 20 条
        }
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """列出所有会话"""
        sessions = []
        
        for session_dir in sorted(self.audit_logs_dir.iterdir(), reverse=True):
            if not session_dir.is_dir():
                continue
            
            log_file = session_dir / "events.jsonl"
            if not log_file.exists():
                continue
            
            # 读取第一条和最后一条记录获取时间范围
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line:
                        first_event = json.loads(first_line)
                        start_time = first_event.get("timestamp", "")
                    
                    # 读取最后一行
                    f.seek(0)
                    last_line = None
                    for line in f:
                        last_line = line
                    
                    if last_line:
                        last_event = json.loads(last_line)
                        end_time = last_event.get("timestamp", "")
                    else:
                        end_time = start_time
            except:
                start_time = ""
                end_time = ""
            
            sessions.append({
                "session_id": session_dir.name,
                "start_time": start_time,
                "end_time": end_time,
                "path": str(session_dir)
            })
            
            if len(sessions) >= limit:
                break
        
        return sessions
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        events = self.read_session_log(session_id)
        
        if not events:
            return {}
        
        stats = {
            "total_events": len(events),
            "event_types": defaultdict(int),
            "actions": [],
            "errors": [],
            "duration": None
        }
        
        for event in events:
            event_type = event.get("type", "unknown")
            stats["event_types"][event_type] += 1
            
            if event_type == "step_complete":
                action = event.get("action", {})
                stats["actions"].append({
                    "tool": action.get("tool", ""),
                    "success": event.get("result", {}).get("success", False)
                })
            
            if event_type == "error":
                stats["errors"].append(event.get("error", ""))
        
        # 计算持续时间
        if len(events) >= 2:
            start_time = events[0].get("timestamp", "")
            end_time = events[-1].get("timestamp", "")
            if start_time and end_time:
                try:
                    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()
                    stats["duration"] = duration
                except:
                    pass
        
        stats["event_types"] = dict(stats["event_types"])
        return stats
    
    def export_logs(self, output_path: str, session_id: Optional[str] = None,
                    format: str = "json") -> str:
        """导出日志"""
        output = Path(output_path)
        
        if session_id:
            # 导出会话日志
            events = self.read_session_log(session_id)
            data = {
                "session_id": session_id,
                "export_time": datetime.now().isoformat(),
                "events": events
            }
        else:
            # 导出运行日志摘要
            error_summary = self.get_error_summary()
            sessions = self.list_sessions(limit=50)
            data = {
                "export_time": datetime.now().isoformat(),
                "error_summary": error_summary,
                "recent_sessions": sessions
            }
        
        if format == "json":
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            # 文本格式
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"日志导出时间: {data['export_time']}\n\n")
                if "events" in data:
                    for event in data["events"]:
                        f.write(f"{event.get('timestamp', '')} | {event.get('type', '')}\n")
                        f.write(f"{json.dumps(event, indent=2, ensure_ascii=False)}\n\n")
        
        return str(output)
