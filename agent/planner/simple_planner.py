from __future__ import annotations

import re
from typing import Optional
from .schema import Action, Target, TargetBy


class SimplePlanner:
    """A trivial planner for demos. Parses patterns in the goal string:
    - "click selector=..."
    - "type selector=... text=..."
    - "wait_for selector=..."
    """

    CLICK_RE = re.compile(r"click\s+selector=(?P<sel>[^\s]+)", re.I)
    TYPE_RE = re.compile(r"type\s+selector=(?P<sel>[^\s]+)\s+text=(?P<txt>.+)", re.I)
    WAIT_RE = re.compile(r"wait_for\s+selector=(?P<sel>[^\s]+)", re.I)

    def plan(self, *, dom_html: Optional[str], screenshot_b64: Optional[str], goal: str) -> Action:
        if m := self.TYPE_RE.search(goal):
            sel = m.group("sel")
            txt = m.group("txt")
            return Action(
                tool="type",
                target=Target(by=TargetBy(selector=sel)),
                inputText=txt,
                rationale="Typing requested by goal"
            )
        if m := self.CLICK_RE.search(goal):
            sel = m.group("sel")
            return Action(
                tool="click",
                target=Target(by=TargetBy(selector=sel)),
                rationale="Click requested by goal"
            )
        if m := self.WAIT_RE.search(goal):
            sel = m.group("sel")
            return Action(
                tool="wait_for",
                target=Target(by=TargetBy(selector=sel)),
                rationale="Wait requested by goal"
            )
        # Default: do nothing and wait
        return Action(tool="wait_for", rationale="No matching pattern; waiting")