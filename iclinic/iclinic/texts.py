from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class TextStore:
    root: Path

    @classmethod
    def default(cls) -> "TextStore":
        return cls(root=Path(__file__).resolve().parents[1] / "iclinic" / "data")

    def _load(self, *parts: str) -> Dict[str, Any] | List[Any]:
        path = self.root.joinpath(*parts)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # Shared
    def emojis(self) -> Dict[str, str]:
        return self._load("emojis.json")

    # Admin
    def admin_main_menu(self) -> Dict[str, Any]:
        return self._load("admin", "main_menu.json")

    def admin_add_subject(self) -> Dict[str, Any]:
        return self._load("admin", "add_subject.json")

    def admin_add_case_or_question(self) -> Dict[str, Any]:
        return self._load("admin", "add_case_or_question.json")

    # User
    def user_first_time(self) -> Dict[str, Any]:
        return self._load("user", "first_time.json")

    def user_home(self) -> Dict[str, Any]:
        return self._load("user", "home.json")
