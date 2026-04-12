"""浏览器工具 - 基于 Playwright"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from tools.evidence import ensure_evidence_dir, save_text_evidence


# 全局浏览器实例（单例）
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None
_page: Optional[Page] = None


async def _ensure_browser():
    """确保浏览器已启动"""
    global _browser, _context, _page
    
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=False)
        _context = await _browser.new_context()
        _page = await _context.new_page()
    
    return _browser, _context, _page


def _run_async(coro):
    """运行异步函数（同步包装）"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def web_open(url: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """打开网页"""
    async def _open():
        browser, context, page = await _ensure_browser()
        await page.goto(url, wait_until="networkidle")
        return {
            "url": page.url,
            "title": await page.title()
        }
    
    result = _run_async(_open())
    result["success"] = True
    
    # 收集证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        evidence_path = evidence_dir / "page_info.json"
        save_text_evidence(str(result), str(evidence_path))
        result["evidence_path"] = str(evidence_path)
    
    return result


def web_click(selector: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """点击元素"""
    async def _click():
        browser, context, page = await _ensure_browser()
        await page.click(selector)
        return {"selector": selector, "clicked": True}
    
    result = _run_async(_click())
    result["success"] = True
    
    # 收集证据（截图）
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        screenshot_path = evidence_dir / "after_click.png"
        _run_async(_snapshot(str(screenshot_path)))
        result["evidence_path"] = str(screenshot_path)
    
    return result


def web_type(selector: str, text: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """输入文本"""
    async def _type():
        browser, context, page = await _ensure_browser()
        await page.fill(selector, text)
        return {"selector": selector, "text": text, "typed": True}
    
    result = _run_async(_type())
    result["success"] = True
    
    # 收集证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        screenshot_path = evidence_dir / "after_type.png"
        _run_async(_snapshot(str(screenshot_path)))
        result["evidence_path"] = str(screenshot_path)
    
    return result


def web_extract(selector: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """提取元素内容"""
    async def _extract():
        browser, context, page = await _ensure_browser()
        element = await page.query_selector(selector)
        if element:
            text = await element.inner_text()
            html = await element.inner_html()
            return {
                "selector": selector,
                "text": text,
                "html": html
            }
        return {"selector": selector, "found": False}
    
    result = _run_async(_extract())
    result["success"] = True
    
    # 收集证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        evidence_path = evidence_dir / "extracted_content.json"
        save_text_evidence(str(result), str(evidence_path))
        result["evidence_path"] = str(evidence_path)
    
    return result


def web_snapshot(session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """截图 + DOM dump"""
    async def _snapshot_full():
        browser, context, page = await _ensure_browser()
        url = page.url
        title = await page.title()
        html = await page.content()
        
        evidence_dir = None
        screenshot_path = None
        dom_path = None
        
        if session_id and step_id:
            evidence_dir = Path(ensure_evidence_dir(session_id, step_id))
            screenshot_path = evidence_dir / "snapshot.png"
            dom_path = evidence_dir / "dom.html"
            
            await page.screenshot(path=str(screenshot_path), full_page=True)
            save_text_evidence(html, str(dom_path))
        
        return {
            "url": url,
            "title": title,
            "screenshot": str(screenshot_path) if screenshot_path else None,
            "dom": str(dom_path) if dom_path else None
        }
    
    result = _run_async(_snapshot_full())
    result["success"] = True
    return result


async def _snapshot(path: str):
    """内部截图函数"""
    browser, context, page = await _ensure_browser()
    await page.screenshot(path=path, full_page=True)


def web_download(url: str, save_path: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """下载文件"""
    async def _download():
        browser, context, page = await _ensure_browser()
        
        async with page.expect_download() as download_info:
            await page.goto(url)
        download = await download_info.value
        
        abs_path = Path(save_path).resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        
        await download.save_as(str(abs_path))
        
        return {
            "url": url,
            "save_path": str(abs_path),
            "size": abs_path.stat().st_size if abs_path.exists() else 0
        }
    
    result = _run_async(_download())
    result["success"] = True
    
    # 收集证据
    if session_id and step_id:
        result["evidence_path"] = result["save_path"]
    
    return result


def web_submit(selector: str, session_id: str = "", step_id: str = "") -> Dict[str, Any]:
    """提交表单（高风险操作）"""
    async def _submit():
        browser, context, page = await _ensure_browser()
        await page.click(selector)  # 或使用 form.submit()
        await page.wait_for_load_state("networkidle")
        return {
            "selector": selector,
            "submitted": True,
            "new_url": page.url
        }
    
    result = _run_async(_submit())
    result["success"] = True
    
    # 收集证据
    if session_id and step_id:
        evidence_dir = ensure_evidence_dir(session_id, step_id)
        screenshot_path = evidence_dir / "after_submit.png"
        _run_async(_snapshot(str(screenshot_path)))
        result["evidence_path"] = str(screenshot_path)
    
    return result


def get_browser_state() -> Dict[str, Optional[str]]:
    """获取当前浏览器状态（用于上下文采集）"""
    async def _get_state():
        try:
            browser, context, page = await _ensure_browser()
            url = page.url
            title = await page.title()
            return {"url": url, "title": title}
        except:
            return {"url": None, "title": None}
    
    return _run_async(_get_state())
