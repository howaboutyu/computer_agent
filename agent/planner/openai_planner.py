from __future__ import annotations

import os
import json
from typing import Optional
from .schema import Action, action_to_dict


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SYSTEM_PROMPT = (
    "You are a computer-use planner. Always output a single JSON Action that matches the tool schema. "
    "Prefer DOM selectors when provided. Use bbox only as fallback. Keep responses minimal."
)


def _tools_spec():
    # Minimal tool schema mirroring Action
    return [
        {
            "type": "function",
            "function": {
                "name": "propose_action",
                "description": "Propose the next UI action to make progress towards the goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "enum": [
                                "click","type","scroll","wait_for",
                                "tap","swipe","hotkey","app_launch","focus_window","adb_shell","back","home"
                            ]
                        },
                        "target": {
                            "type": "object",
                            "properties": {
                                "by": {
                                    "type": "object",
                                    "properties": {
                                        "role": {"type": ["string","null"]},
                                        "text": {"type": ["string","null"]},
                                        "title": {"type": ["string","null"]},
                                        "selector": {"type": ["string","null"]},
                                        "ax_path": {"type": ["string","null"]},
                                        "uia_selector": {"type": ["string","null"]},
                                        "atspi_path": {"type": ["string","null"]}
                                    }
                                },
                                "bbox": {"type": ["array","null"], "items": {"type": "number"}}
                            }
                        },
                        "inputText": {"type": ["string","null"]},
                        "args": {"type": ["object","null"]},
                        "assert": {"type": ["string","null"]},
                        "rationale": {"type": ["string","null"]}
                    },
                    "required": ["tool"]
                }
            }
        }
    ]


class OpenAIPlanner:
    def __init__(self, model: Optional[str] = None):
        self.model = model or OPENAI_MODEL
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set; cannot use OpenAIPlanner")

    def plan(self, *, dom_html: Optional[str], screenshot_b64: Optional[str], goal: str) -> Action:
        # Lazy import to avoid hard dependency when not used
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError("openai package not available. Install requirements.") from e

        client = OpenAI()
        parts = [
            {"type": "text", "text": f"Goal: {goal}"},
        ]
        if dom_html:
            parts.append({"type": "text", "text": f"DOM:\n{dom_html[:6000]}"})
        if screenshot_b64:
            parts.append({"type": "input_image", "image_data": screenshot_b64})

        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": parts},
            ],
            tools=_tools_spec(),
            tool_choice={"type": "function", "function": {"name": "propose_action"}},
            temperature=0.2,
        )
        tool_calls = resp.choices[0].message.tool_calls
        if not tool_calls:
            # Fallback: wait
            return Action(tool="wait_for", rationale="No tool call returned; waiting")
        args = json.loads(tool_calls[0].function.arguments)
        try:
            return Action.model_validate(args)
        except Exception:
            # Be tolerant of minor mismatches
            return Action(tool=args.get("tool", "wait_for"))