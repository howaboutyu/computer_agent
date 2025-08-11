from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


ActionTool = Literal[
    "click",
    "type",
    "scroll",
    "wait_for",
    # Non-web extensions
    "tap",
    "swipe",
    "hotkey",
    "app_launch",
    "focus_window",
    "adb_shell",
    "back",
    "home",
]


class TargetBy(BaseModel):
    role: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    selector: Optional[str] = None  # CSS/XPath for web
    ax_path: Optional[str] = None  # macOS Accessibility path
    uia_selector: Optional[str] = None  # Windows UIA selector string
    atspi_path: Optional[str] = None  # Linux AT-SPI path


class Target(BaseModel):
    by: Optional[TargetBy] = None
    bbox: Optional[List[int]] = None  # [x1, y1, x2, y2] fallback


class Action(BaseModel):
    tool: ActionTool
    target: Optional[Target] = None
    inputText: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    assert_: Optional[str] = Field(default=None, alias="assert")
    rationale: Optional[str] = None

    class Config:
        populate_by_name = True


def action_to_dict(action: Action) -> Dict[str, Any]:
    return action.model_dump(by_alias=True, exclude_none=True)