"""证据收集工具 - 截图、DOM dump、文件 diff 等"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


def ensure_evidence_dir(session_id: str, step_id: str) -> Path:
    """确保证据目录存在"""
    evidence_dir = Path("logs/sessions") / session_id / "evidence" / step_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return evidence_dir


def capture_screenshot(path: str, element: Optional[str] = None) -> str:
    """
    截图（通过 Playwright，需要在 web_tools 中实现）
    这里提供接口定义
    """
    # 实际实现在 web_tools.py 中
    return path


def dump_dom(url: str, output_path: str) -> str:
    """
    DOM 快照（通过 Playwright）
    实际实现在 web_tools.py 中
    """
    return output_path


def diff_files(before: Dict[str, Any], after: Dict[str, Any], output_path: str) -> str:
    """生成文件变更 diff"""
    diff_data = {
        "timestamp": datetime.now().isoformat(),
        "before": before,
        "after": after,
        "changes": _compute_changes(before, after)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(diff_data, f, indent=2, ensure_ascii=False)
    
    return output_path


def _compute_changes(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """计算变更"""
    changes = {
        "added": [],
        "removed": [],
        "modified": []
    }
    
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    
    # 新增
    for key in after_keys - before_keys:
        changes["added"].append({"key": key, "value": after[key]})
    
    # 删除
    for key in before_keys - after_keys:
        changes["removed"].append({"key": key, "value": before[key]})
    
    # 修改
    for key in before_keys & after_keys:
        if before[key] != after[key]:
            changes["modified"].append({
                "key": key,
                "before": before[key],
                "after": after[key]
            })
    
    return changes


def capture_file_tree(path: str, output_path: str, max_depth: int = 3) -> str:
    """捕获文件树结构"""
    tree = _build_file_tree(Path(path), max_depth)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    
    return output_path


def _build_file_tree(root: Path, max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
    """构建文件树"""
    if current_depth > max_depth:
        return {"type": "truncated", "path": str(root)}
    
    if not root.exists():
        return {"type": "missing", "path": str(root)}
    
    if root.is_file():
        stat = root.stat()
        return {
            "type": "file",
            "path": str(root),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    if root.is_dir():
        children = []
        try:
            for item in sorted(root.iterdir()):
                if item.name.startswith('.'):
                    continue
                children.append(_build_file_tree(item, max_depth, current_depth + 1))
        except PermissionError:
            children.append({"type": "permission_denied", "path": str(root)})
        
        return {
            "type": "directory",
            "path": str(root),
            "children": children
        }
    
    return {"type": "unknown", "path": str(root)}


def create_evidence_package(session_id: str, step_id: str, evidence_list: List[Dict[str, Any]]) -> str:
    """创建证据包（索引文件）"""
    evidence_dir = ensure_evidence_dir(session_id, step_id)
    index_path = evidence_dir / "index.json"
    
    package = {
        "session_id": session_id,
        "step_id": step_id,
        "timestamp": datetime.now().isoformat(),
        "evidence": evidence_list
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(package, f, indent=2, ensure_ascii=False)
    
    return str(index_path)


def save_text_evidence(content: str, output_path: str) -> str:
    """保存文本证据"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path


def copy_file_evidence(src: str, dst: str) -> str:
    """复制文件作为证据"""
    shutil.copy2(src, dst)
    return dst
