from __future__ import annotations

import argparse
import os
from typing import Optional

from .planner.simple_planner import SimplePlanner
from .planner.openai_planner import OpenAIPlanner
from .config import DEFAULT_HEADLESS, DEFAULT_MAX_STEPS
from .tracing import make_trace_dir


def make_planner(name: str):
    if name == "openai":
        return OpenAIPlanner()
    return SimplePlanner()


def run_web(url: str, planner_name: str, goal: str, headless: bool, max_steps: int):
    planner = make_planner(planner_name)
    trace_dir = make_trace_dir()
    # Lazy import to avoid dependency when not needed
    from .executors.web_executor import run_web_task
    import asyncio
    asyncio.run(run_web_task(url=url, planner=planner, goal=goal, max_steps=max_steps, headless=headless, trace_dir=trace_dir))


def run_desktop(goal: str):
    raise NotImplementedError("Desktop executor is a placeholder. Implement using UIA/AX/AT-SPI.")


def run_mobile(platform: str, goal: str):
    raise NotImplementedError("Mobile executor is a placeholder. Implement using Appium (uiautomator2/WDA).")


def main(argv: Optional[list[str]] = None):
    parser = argparse.ArgumentParser(description="Computer-use agent runner")
    parser.add_argument("--platform", required=True, choices=["web", "desktop", "android", "ios"], help="Target platform")
    parser.add_argument("--planner", default=os.getenv("PLANNER", "simple"), choices=["simple", "openai"], help="Planner type")
    parser.add_argument("--url", help="URL for web platform")
    parser.add_argument("--goal", required=True, help="Natural language goal or simple patterned goal")
    parser.add_argument("--headless", action="store_true", help="Run headless browser (web)")
    parser.add_argument("--max_steps", type=int, default=DEFAULT_MAX_STEPS, help="Maximum planning steps")

    args = parser.parse_args(argv)

    if args.platform == "web":
        if not args.url:
            parser.error("--url is required for web platform")
        run_web(url=args.url, planner_name=args.planner, goal=args.goal, headless=(args.headless or DEFAULT_HEADLESS), max_steps=args.max_steps)
    elif args.platform == "desktop":
        run_desktop(goal=args.goal)
    elif args.platform in ("android", "ios"):
        run_mobile(platform=args.platform, goal=args.goal)
    else:
        parser.error("Unsupported platform")


if __name__ == "__main__":
    main()