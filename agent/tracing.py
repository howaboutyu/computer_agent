from __future__ import annotations

import base64
import os
from datetime import datetime
from typing import Optional


def make_trace_dir(base: str = "traces") -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base, ts)
    os.makedirs(path, exist_ok=True)
    return path


def save_text(path: str, name: str, text: str) -> None:
    with open(os.path.join(path, name), "w", encoding="utf-8") as f:
        f.write(text)


def save_image_b64(path: str, name: str, image_b64: str) -> None:
    with open(os.path.join(path, name), "wb") as f:
        f.write(base64.b64decode(image_b64))