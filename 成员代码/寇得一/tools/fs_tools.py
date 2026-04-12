"""文件系统工具 - 带路径校验和证据输出"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from tools.evidence import (
    ensure_evidence_dir, capture_file_tree, diff_files,
    create_evidence_package, save_text_evidence
)


def validate_path(path: str, home_dir: str = None) -> Path:
    """验证路径是否在允许范围内"""
    if home_dir is None:
        home_dir = os.path.expanduser("~")
    
    abs_path = Path(path).resolve()
    home_path = Path(home_dir).resolve()
    
    if not str(abs_path).startswith(str(home_path)):
        raise ValueError(f"路径超出允许范围: {path} (必须在 {home_dir} 内)")
    
    return abs_path


def fs_list(path: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """列出目录内容"""
    abs_path = validate_path(path)
    
    if not abs_path.exists():
        raise FileNotFoundError(f"路径不存在: {path}")
    
    if not abs_path.is_dir():
        raise ValueError(f"不是目录: {path}")
    
    result = {
        "path": str(abs_path),
        "items": []
    }
    
    try:
        for item in sorted(abs_path.iterdir()):
            if item.name.startswith('.'):
                continue
            
            stat = item.stat()
            result["items"].append({
                "name": item.name,
                "path": str(item),
                "type": "file" if item.is_file() else "directory",
                "size": stat.st_size if item.is_file() else None,
                "modified": stat.st_mtime
            })
    except PermissionError:
        result["error"] = "权限不足"
    
    # 收集证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        evidence_path = evidence_dir / "file_list.json"
        save_text_evidence(str(result), str(evidence_path))
        result["evidence_path"] = str(evidence_path)
    
    return result


def fs_search(pattern: str, root: str = None, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """使用 Spotlight 搜索文件"""
    if root is None:
        root = os.path.expanduser("~")
    
    validate_path(root)
    
    # 使用 mdfind (Spotlight 命令行工具)
    try:
        cmd = ["mdfind", "-name", pattern]
        if root:
            cmd.extend(["-onlyin", root])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        search_result = {
            "pattern": pattern,
            "root": root,
            "matches": files[:50]  # 限制结果数量
        }
        
        # 收集证据
        if session_id and step_id:
            evidence_dir = ensure_evidence_dir(session_id, step_id)
            evidence_path = evidence_dir / "search_results.json"
            save_text_evidence(str(search_result), str(evidence_path))
            search_result["evidence_path"] = str(evidence_path)
        
        return search_result
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("搜索超时")
    except Exception as e:
        raise RuntimeError(f"搜索失败: {e}")


def fs_move(src: str, dst: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """移动文件/目录"""
    abs_src = validate_path(src)
    abs_dst = validate_path(dst)
    
    if not abs_src.exists():
        raise FileNotFoundError(f"源文件不存在: {src}")
    
    # 如果目标是目录，则移动到目录内
    if abs_dst.exists() and abs_dst.is_dir():
        abs_dst = abs_dst / abs_src.name
    
    # 收集变更前证据
    before_state = {}
    if abs_src.exists():
        before_state["src"] = {
            "exists": True,
            "size": abs_src.stat().st_size if abs_src.is_file() else None
        }
    if abs_dst.exists():
        before_state["dst"] = {"exists": True}
    
    # 执行移动
    shutil.move(str(abs_src), str(abs_dst))
    
    # 收集变更后证据
    after_state = {
        "src": {"exists": abs_src.exists()},
        "dst": {"exists": abs_dst.exists(), "size": abs_dst.stat().st_size if abs_dst.is_file() else None}
    }
    
    result = {
        "src": str(abs_src),
        "dst": str(abs_dst),
        "success": True
    }
    
    # 生成 diff 证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        diff_path = evidence_dir / "move_diff.json"
        diff_files(before_state, after_state, str(diff_path))
        result["evidence_path"] = str(diff_path)
    
    return result


def fs_rename(path: str, new_name: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """重命名文件/目录"""
    abs_path = validate_path(path)
    
    if not abs_path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    
    new_path = abs_path.parent / new_name
    
    # 收集变更前证据
    before_state = {
        "old_name": abs_path.name,
        "old_path": str(abs_path),
        "size": abs_path.stat().st_size if abs_path.is_file() else None
    }
    
    # 执行重命名
    abs_path.rename(new_path)
    
    # 收集变更后证据
    after_state = {
        "new_name": new_path.name,
        "new_path": str(new_path),
        "size": new_path.stat().st_size if new_path.is_file() else None
    }
    
    result = {
        "old_path": str(abs_path),
        "new_path": str(new_path),
        "success": True
    }
    
    # 生成 diff 证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        diff_path = evidence_dir / "rename_diff.json"
        diff_files(before_state, after_state, str(diff_path))
        result["evidence_path"] = str(diff_path)
    
    return result


def fs_copy(src: str, dst: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """复制文件/目录"""
    abs_src = validate_path(src)
    abs_dst = validate_path(dst)
    
    if not abs_src.exists():
        raise FileNotFoundError(f"源文件不存在: {src}")
    
    # 如果目标是目录，则复制到目录内
    if abs_dst.exists() and abs_dst.is_dir():
        abs_dst = abs_dst / abs_src.name
    
    # 收集变更前证据
    before_state = {
        "src": {"exists": True, "size": abs_src.stat().st_size if abs_src.is_file() else None},
        "dst": {"exists": abs_dst.exists()}
    }
    
    # 执行复制
    if abs_src.is_file():
        shutil.copy2(str(abs_src), str(abs_dst))
    else:
        shutil.copytree(str(abs_src), str(abs_dst), dirs_exist_ok=True)
    
    # 收集变更后证据
    after_state = {
        "src": {"exists": True},
        "dst": {"exists": True, "size": abs_dst.stat().st_size if abs_dst.is_file() else None}
    }
    
    result = {
        "src": str(abs_src),
        "dst": str(abs_dst),
        "success": True
    }
    
    # 生成 diff 证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        diff_path = evidence_dir / "copy_diff.json"
        diff_files(before_state, after_state, str(diff_path))
        result["evidence_path"] = str(diff_path)
    
    return result


def fs_trash(path: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """移至废纸篓（使用 AppleScript）"""
    abs_path = validate_path(path)
    
    if not abs_path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    
    # 收集变更前证据
    before_state = {
        "path": str(abs_path),
        "exists": True,
        "size": abs_path.stat().st_size if abs_path.is_file() else None
    }
    
    # 使用 AppleScript 移至废纸篓
    script = f'''
    tell application "Finder"
        set theFile to POSIX file "{abs_path}"
        move theFile to trash
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
            raise RuntimeError(f"移至废纸篓失败: {result.stderr}")
        
        # 收集变更后证据
        after_state = {
            "path": str(abs_path),
            "exists": abs_path.exists()
        }
        
        trash_result = {
            "path": str(abs_path),
            "success": True,
            "trashed": not abs_path.exists()
        }
        
        # 生成 diff 证据
        if session_id and step_id:
            evidence_dir = ensure_evidence_dir(session_id, step_id)
            diff_path = evidence_dir / "trash_diff.json"
            diff_files(before_state, after_state, str(diff_path))
            trash_result["evidence_path"] = str(diff_path)
        
        return trash_result
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("操作超时")
    except Exception as e:
        raise RuntimeError(f"移至废纸篓失败: {e}")
