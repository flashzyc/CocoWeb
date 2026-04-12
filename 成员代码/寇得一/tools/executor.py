"""工具执行器 - 统一入口，路由到各工具模块"""

import time
from typing import Dict, Any
from app.schema import Action, ExecutionResult
import tools.fs_tools as fs_tools
import tools.web_tools as web_tools
import tools.wx_tools as wx_tools
import tools.notes_tools as notes_tools


def execute_action(action: Action, session_id: str = "") -> ExecutionResult:
    """
    执行单个动作
    
    Args:
        action: 要执行的动作
        session_id: 会话 ID（用于证据收集）
    """
    start_time = time.time()
    step_id = action.id
    
    try:
        # 路由到对应工具
        tool_name = action.tool
        args = action.args
        
        if tool_name.startswith("fs."):
            result = _execute_fs_tool(tool_name, args, session_id, step_id)
        elif tool_name.startswith("web."):
            result = _execute_web_tool(tool_name, args, session_id, step_id)
        elif tool_name.startswith("wx."):
            result = _execute_wx_tool(tool_name, args, session_id, step_id)
        elif tool_name.startswith("notes."):
            result = _execute_notes_tool(tool_name, args, session_id, step_id)
        else:
            raise ValueError(f"未知工具: {tool_name}")
        
        execution_time = time.time() - start_time
        
        # 提取证据路径
        evidence_paths = []
        if isinstance(result, dict):
            if "evidence_path" in result:
                evidence_paths.append(result["evidence_path"])
            elif "evidence_paths" in result:
                evidence_paths.extend(result["evidence_paths"])
        
        return ExecutionResult(
            success=result.get("success", True),
            output=result,
            evidence_paths=evidence_paths,
            execution_time=execution_time
        )
    
    except Exception as e:
        execution_time = time.time() - start_time
        return ExecutionResult(
            success=False,
            output=None,
            error=str(e),
            execution_time=execution_time
        )


def _execute_fs_tool(tool_name: str, args: Dict[str, Any], session_id: str, step_id: str) -> Dict[str, Any]:
    """执行文件系统工具"""
    if tool_name == "fs.list":
        return fs_tools.fs_list(args.get("path", ""), session_id, step_id)
    elif tool_name == "fs.search":
        return fs_tools.fs_search(args.get("pattern", ""), args.get("root"), session_id, step_id)
    elif tool_name == "fs.move":
        return fs_tools.fs_move(args.get("src", ""), args.get("dst", ""), session_id, step_id)
    elif tool_name == "fs.rename":
        return fs_tools.fs_rename(args.get("path", ""), args.get("new_name", ""), session_id, step_id)
    elif tool_name == "fs.copy":
        return fs_tools.fs_copy(args.get("src", ""), args.get("dst", ""), session_id, step_id)
    elif tool_name == "fs.trash":
        return fs_tools.fs_trash(args.get("path", ""), session_id, step_id)
    else:
        raise ValueError(f"未知文件系统工具: {tool_name}")


def _execute_web_tool(tool_name: str, args: Dict[str, Any], session_id: str, step_id: str) -> Dict[str, Any]:
    """执行浏览器工具"""
    if tool_name == "web.open":
        return web_tools.web_open(args.get("url", ""), session_id, step_id)
    elif tool_name == "web.click":
        return web_tools.web_click(args.get("selector", ""), session_id, step_id)
    elif tool_name == "web.type":
        return web_tools.web_type(args.get("selector", ""), args.get("text", ""), session_id, step_id)
    elif tool_name == "web.extract":
        return web_tools.web_extract(args.get("selector", ""), session_id, step_id)
    elif tool_name == "web.snapshot":
        return web_tools.web_snapshot(session_id, step_id)
    elif tool_name == "web.download":
        return web_tools.web_download(args.get("url", ""), args.get("save_path", ""), session_id, step_id)
    elif tool_name == "web.submit":
        return web_tools.web_submit(args.get("selector", ""), session_id, step_id)
    else:
        raise ValueError(f"未知浏览器工具: {tool_name}")


def _execute_wx_tool(tool_name: str, args: Dict[str, Any], session_id: str, step_id: str) -> Dict[str, Any]:
    """执行微信工具"""
    if tool_name == "wx.open_chat":
        return wx_tools.wx_open_chat(args.get("contact", ""), session_id, step_id)
    elif tool_name == "wx.paste_text":
        return wx_tools.wx_paste_text(args.get("text", ""), session_id, step_id)
    else:
        raise ValueError(f"未知微信工具: {tool_name}")


def _execute_notes_tool(tool_name: str, args: Dict[str, Any], session_id: str, step_id: str) -> Dict[str, Any]:
    """执行备忘录工具"""
    if tool_name == "notes.search":
        return notes_tools.notes_search(args.get("query", ""), session_id, step_id)
    elif tool_name == "notes.create":
        return notes_tools.notes_create(args.get("title", ""), args.get("content", ""), session_id, step_id)
    elif tool_name == "notes.append":
        return notes_tools.notes_append(args.get("note_id", ""), args.get("text", ""), session_id, step_id)
    else:
        raise ValueError(f"未知备忘录工具: {tool_name}")
