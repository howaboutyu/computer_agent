from __future__ import annotations

import asyncio
import base64
from typing import Optional, Tuple

from ..planner.schema import Action


async def _maybe_wait_for_selector(page, selector: str, timeout_ms: int = 5000):
    try:
        await page.wait_for_selector(selector, timeout=timeout_ms, state="visible")
        return True
    except Exception:
        return False


def _center_from_bbox(bbox) -> Tuple[int, int]:
    x1, y1, x2, y2 = bbox
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))


async def run_web_task(url: str, planner, goal: str, max_steps: int = 15, headless: bool = True, trace_dir: Optional[str] = None) -> None:
    # Lazy import
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(url)

        for step in range(max_steps):
            # Observation
            screenshot_bytes = await page.screenshot(full_page=True)
            dom_html = await page.content()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # Plan
            action: Action = planner.plan(dom_html=dom_html, screenshot_b64=screenshot_b64, goal=goal)

            # Execute
            tool = action.tool
            by = (action.target.by if action.target and action.target.by else None)
            selector = by.selector if by and getattr(by, "selector", None) else None
            if tool == "click":
                if selector:
                    await page.click(selector, timeout=5000)
                elif action.target and action.target.bbox:
                    cx, cy = _center_from_bbox(action.target.bbox)
                    await page.mouse.click(cx, cy)
            elif tool == "type":
                if selector:
                    await page.click(selector, timeout=5000)
                if action.inputText:
                    await page.keyboard.type(action.inputText, delay=20)
            elif tool == "scroll":
                delta_y = 600
                if action.args and isinstance(action.args.get("deltaY"), (int, float)):
                    delta_y = int(action.args["deltaY"])
                await page.mouse.wheel(0, delta_y)
            elif tool == "wait_for":
                if selector:
                    await _maybe_wait_for_selector(page, selector)
                else:
                    await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(0.3)

            # Optional: basic success heuristic for demo
            if action.assert_ and selector:
                ok = await _maybe_wait_for_selector(page, selector, timeout_ms=8000)
                if ok:
                    break

        await browser.close()