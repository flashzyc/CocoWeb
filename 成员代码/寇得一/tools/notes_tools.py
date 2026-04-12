"""备忘录工具 - AppleScript/Shortcuts"""

import subprocess
import json
from typing import Dict, Any, List, Optional


def notes_search(query: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """搜索备忘录"""
    script = f'''
    tell application "Notes"
        set matchingNotes to {}
        repeat with aNote in notes
            if (name of aNote contains "{query}") or (body of aNote contains "{query}") then
                set end of matchingNotes to {{id: id of aNote, name: name of aNote, body: body of aNote}}
            end if
        end repeat
        return matchingNotes
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"搜索失败: {result.stderr}")
        
        # 解析 AppleScript 返回的列表（简化处理）
        matches = []
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('{'):
                matches.append({"name": line.strip()})
        
        return {
            "query": query,
            "matches": matches[:20],  # 限制结果数量
            "success": True
        }
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("搜索超时")
    except Exception as e:
        raise RuntimeError(f"搜索失败: {e}")


def notes_create(title: str, content: str = "", session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """创建新备忘录"""
    script = f'''
    tell application "Notes"
        set newNote to make new note at folder "Notes"
        set name of newNote to "{title}"
        set body of newNote to "{content}"
        return id of newNote
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
            raise RuntimeError(f"创建失败: {result.stderr}")
        
        note_id = result.stdout.strip()
        
        return {
            "title": title,
            "content": content,
            "note_id": note_id,
            "success": True
        }
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("操作超时")
    except Exception as e:
        raise RuntimeError(f"创建失败: {e}")


def notes_append(note_id: str, text: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """追加内容到备忘录"""
    script = f'''
    tell application "Notes"
        set targetNote to note id "{note_id}"
        set currentBody to body of targetNote
        set body of targetNote to currentBody & "\\n" & "{text}"
        return name of targetNote
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
            raise RuntimeError(f"追加失败: {result.stderr}")
        
        note_name = result.stdout.strip()
        
        return {
            "note_id": note_id,
            "note_name": note_name,
            "appended_text": text,
            "success": True
        }
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("操作超时")
    except Exception as e:
        raise RuntimeError(f"追加失败: {e}")
