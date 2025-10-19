from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass
class Subject:
    id: int
    name: str


@dataclass
class Case:
    id: int
    subject_id: int
    text: str


@dataclass
class Question:
    id: int
    subject_id: int
    text: str


@dataclass
class JoinRequest:
    id: int
    user_id: int
    username: Optional[str]
    approved: int  # 0/1


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as con:
            self._init(con)

    @contextmanager
    def _conn(self):
        con = sqlite3.connect(self.db_path)
        try:
            con.row_factory = sqlite3.Row
            yield con
            con.commit()
        finally:
            con.close()

    def _init(self, con: sqlite3.Connection) -> None:
        cur = con.cursor()
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                text TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                text TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS join_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                approved INTEGER NOT NULL DEFAULT 0,
                UNIQUE(user_id)
            );
            """
        )

    # Subjects
    def add_subject(self, name: str) -> int:
        with self._conn() as con:
            cur = con.execute("INSERT INTO subjects(name) VALUES (?)", (name.strip(),))
            return int(cur.lastrowid)

    def list_subjects(self) -> list[Subject]:
        with self._conn() as con:
            rows = con.execute("SELECT id, name FROM subjects ORDER BY name").fetchall()
            return [Subject(int(r["id"]), r["name"]) for r in rows]

    def delete_subject(self, subject_id: int) -> None:
        with self._conn() as con:
            con.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))

    # Cases
    def add_case(self, subject_id: int, text: str) -> int:
        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO cases(subject_id, text) VALUES (?, ?)", (subject_id, text.strip())
            )
            return int(cur.lastrowid)

    def list_cases_by_subject(self, subject_id: int) -> list[Case]:
        with self._conn() as con:
            rows = con.execute(
                "SELECT id, subject_id, text FROM cases WHERE subject_id = ? ORDER BY id DESC",
                (subject_id,),
            ).fetchall()
            return [Case(int(r["id"]), int(r["subject_id"]), r["text"]) for r in rows]

    def delete_case(self, case_id: int) -> None:
        with self._conn() as con:
            con.execute("DELETE FROM cases WHERE id = ?", (case_id,))

    def get_random_case(self, subject_id: Optional[int] = None) -> Optional[Case]:
        query = "SELECT id, subject_id, text FROM cases"
        params: Iterable[object] = ()
        if subject_id is not None:
            query += " WHERE subject_id = ?"
            params = (subject_id,)
        query += " ORDER BY RANDOM() LIMIT 1"
        with self._conn() as con:
            row = con.execute(query, params).fetchone()
            if not row:
                return None
            return Case(int(row["id"]), int(row["subject_id"]), row["text"]) 

    # Questions
    def add_question(self, subject_id: int, text: str) -> int:
        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO questions(subject_id, text) VALUES (?, ?)", (subject_id, text.strip())
            )
            return int(cur.lastrowid)

    def list_questions_by_subject(self, subject_id: int) -> list[Question]:
        with self._conn() as con:
            rows = con.execute(
                "SELECT id, subject_id, text FROM questions WHERE subject_id = ? ORDER BY id DESC",
                (subject_id,),
            ).fetchall()
            return [Question(int(r["id"]), int(r["subject_id"]), r["text"]) for r in rows]

    def delete_question(self, question_id: int) -> None:
        with self._conn() as con:
            con.execute("DELETE FROM questions WHERE id = ?", (question_id,))

    # Join Requests
    def create_join_request(self, user_id: int, username: Optional[str]) -> None:
        with self._conn() as con:
            con.execute(
                "INSERT OR IGNORE INTO join_requests(user_id, username, approved) VALUES (?, ?, 0)",
                (user_id, username),
            )

    def set_join_request(self, user_id: int, approved: bool) -> None:
        with self._conn() as con:
            con.execute(
                "UPDATE join_requests SET approved = ? WHERE user_id = ?",
                (1 if approved else 0, user_id),
            )

    def list_pending_requests(self) -> list[JoinRequest]:
        with self._conn() as con:
            rows = con.execute(
                "SELECT id, user_id, username, approved FROM join_requests WHERE approved = 0 ORDER BY id DESC"
            ).fetchall()
            return [
                JoinRequest(int(r["id"]), int(r["user_id"]), r["username"], int(r["approved"]))
                for r in rows
            ]

    def user_is_approved(self, user_id: int) -> bool:
        with self._conn() as con:
            row = con.execute(
                "SELECT approved FROM join_requests WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return bool(row and int(row["approved"]) == 1)
