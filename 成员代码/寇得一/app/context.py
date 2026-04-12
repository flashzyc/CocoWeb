"""上下文采集 - 前台应用、文件系统、浏览器状态"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.schema import Context


def get_front_app() -> Optional[str]:
    """获取前台应用名称（AppleScript）"""
    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_front_window() -> Optional[str]:
    """获取前台窗口标题"""
    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to name of first window
                return frontWindow
            end tell
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_browser_state() -> Dict[str, Optional[str]]:
    """
    获取浏览器状态（通过 Playwright）
    """
    try:
        from tools.web_tools import get_browser_state as web_get_state
        return web_get_state()
    except Exception:
        return {
            "url": None,
            "title": None
        }


def get_file_context(path: str) -> Dict[str, Any]:
    """获取文件系统上下文"""
    context = {
        "path": path,
        "exists": False,
        "is_file": False,
        "is_dir": False,
        "size": None,
        "children_count": None
    }
    
    try:
        p = Path(path)
        if p.exists():
            context["exists"] = True
            context["is_file"] = p.is_file()
            context["is_dir"] = p.is_dir()
            
            if p.is_file():
                context["size"] = p.stat().st_size
            elif p.is_dir():
                try:
                    children = list(p.iterdir())
                    context["children_count"] = len(children)
                    # 只列出前 20 个文件/目录
                    context["children"] = [
                        {
                            "name": child.name,
                            "is_file": child.is_file(),
                            "size": child.stat().st_size if child.is_file() else None
                        }
                        for child in sorted(children)[:20]
                    ]
                except PermissionError:
                    context["permission_denied"] = True
    except Exception as e:
        context["error"] = str(e)
    
    return context


def collect_context(
    file_paths: Optional[list] = None,
    check_browser: bool = False
) -> Context:
    """
    收集完整上下文
    
    Args:
        file_paths: 需要检查的文件路径列表
        check_browser: 是否检查浏览器状态
    """
    context = Context()
    
    # 前台应用
    context.front_app = get_front_app()
    context.front_window = get_front_window()
    
    # 浏览器状态（如果需要）
    if check_browser:
        browser_state = get_browser_state()
        context.browser_url = browser_state.get("url")
        context.browser_title = browser_state.get("title")
    
    # 文件上下文
    if file_paths:
        context.file_context = {
            path: get_file_context(path)
            for path in file_paths
        }
    
    return context


def extract_paths_from_action(action_args: Dict[str, Any]) -> list:
    """从动作参数中提取文件路径"""
    paths = []
    
    for key, value in action_args.items():
        if key in ["src", "dst", "path", "file", "directory", "root"]:
            if isinstance(value, str):
                paths.append(value)
        elif isinstance(value, dict):
            paths.extend(extract_paths_from_action(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and Path(item).exists():
                    paths.append(item)
                elif isinstance(item, dict):
                    paths.extend(extract_paths_from_action(item))
    
    return paths
