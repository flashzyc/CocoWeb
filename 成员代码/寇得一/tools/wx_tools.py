"""微信工具 - 半自动实现（AppleScript）"""

import subprocess
import time
from typing import Dict, Any


def wx_open_chat(contact: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """打开指定联系人对话"""
    script = f'''
    tell application "WeChat"
        activate
    end tell
    
    delay 1
    
    tell application "System Events"
        tell process "WeChat"
            -- 使用 Cmd+F 打开搜索
            keystroke "f" using command down
            delay 0.5
            
            -- 输入联系人名称
            keystroke "{contact}"
            delay 1
            
            -- 按回车选择第一个结果
            key code 36
            delay 0.5
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"打开对话失败: {result.stderr}")
        
        return {
            "contact": contact,
            "success": True,
            "opened": True
        }
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("操作超时")
    except Exception as e:
        raise RuntimeError(f"打开对话失败: {e}")


def wx_paste_text(text: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """粘贴文本到输入框（不自动发送）"""
    # 注意：这里只粘贴，不发送，需要用户手动确认发送
    
    script = f'''
    tell application "System Events"
        tell process "WeChat"
            -- 确保焦点在输入框
            keystroke "a" using command down
            delay 0.2
            
            -- 粘贴文本
            set the clipboard to "{text}"
            keystroke "v" using command down
            delay 0.5
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"粘贴文本失败: {result.stderr}")
        
        return {
            "text": text,
            "success": True,
            "pasted": True,
            "note": "文本已粘贴到输入框，请手动确认发送"
        }
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("操作超时")
    except Exception as e:
        raise RuntimeError(f"粘贴文本失败: {e}")
