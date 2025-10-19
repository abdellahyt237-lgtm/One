from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class BotTexts:
    base_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.base_dir is None:
            # Resolve to this package directory
            self.base_dir = Path(__file__).resolve().parent
        # Validate required subfolders
        self._admin = self.base_dir / "admin"
        self._user = self.base_dir / "user"
        self._shared = self.base_dir / "shared"

    # ---------- Internal utilities ----------
    def _read_json(self, relative_path: str) -> Dict[str, Any]:
        path = self.base_dir / relative_path
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- Shared ----------
    def emojis(self) -> Dict[str, str]:
        return self._read_json("shared/emojis.json")

    # ---------- Admin ----------
    def admin_main_menu(self) -> Dict[str, Any]:
        return self._read_json("admin/main_menu.json")

    def admin_flow_add_subject(self) -> Dict[str, Any]:
        return self._read_json("admin/flows/add_subject.json")

    def admin_flow_add_case_or_question(self) -> Dict[str, Any]:
        return self._read_json("admin/flows/add_case_or_question.json")

    def admin_flow_delete(self) -> Dict[str, Any]:
        return self._read_json("admin/flows/delete.json")

    def admin_join_requests(self) -> Dict[str, Any]:
        return self._read_json("admin/flows/join_requests.json")

    # ---------- User ----------
    def user_first_time(self) -> Dict[str, Any]:
        return self._read_json("user/first_time.json")

    def user_after_approval(self) -> Dict[str, Any]:
        return self._read_json("user/after_approval.json")

    def user_display_formats(self) -> Dict[str, Any]:
        return self._read_json("user/display_formats.json")
