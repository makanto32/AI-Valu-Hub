from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from .models import CompanyContext, IdeaCase


DEFAULT_DB_PATH = Path(
    os.getenv("AIHUB_DB_PATH", str(Path(__file__).resolve().parents[2] / "data" / "aihub.db"))
)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _ensure_parent_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    _ensure_parent_directory(DEFAULT_DB_PATH)
    connection = sqlite3.connect(DEFAULT_DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def _to_json(model: Any) -> str:
    if isinstance(model, list):
        return json.dumps(
            [item.model_dump(mode="json") if hasattr(item, "model_dump") else item for item in model],
            ensure_ascii=False,
        )
    if isinstance(model, dict):
        normalized = {
            key: value.model_dump(mode="json") if hasattr(value, "model_dump") else value for key, value in model.items()
        }
        return json.dumps(normalized, ensure_ascii=False)
    if hasattr(model, "model_dump"):
        return json.dumps(model.model_dump(mode="json"), ensure_ascii=False)
    return json.dumps(model, ensure_ascii=False)


def _from_json(payload: str | None) -> Any:
    if not payload:
        return None
    return json.loads(payload)


def _ensure_column(connection: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_names = {column[1] for column in columns}
    if column_name in existing_names:
        return
    connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def _init_schema() -> None:
    with _connect() as connection:
        connection.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS company_contexts (
                tenant_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ideas (
                idea_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                owner_user_id TEXT NOT NULL,
                owner_display_name TEXT NOT NULL,
                title TEXT NOT NULL,
                canonical_language TEXT NOT NULL,
                supported_languages TEXT NOT NULL,
                source_language TEXT NOT NULL,
                detected_language TEXT NOT NULL,
                response_language TEXT NOT NULL,
                original_text TEXT NOT NULL,
                canonical_summary TEXT NOT NULL,
                current_stage TEXT NOT NULL,
                status TEXT NOT NULL,
                problem_statement TEXT NOT NULL,
                expected_value TEXT NOT NULL,
                affected_users TEXT NOT NULL,
                context_snapshot TEXT,
                business_validation TEXT NOT NULL,
                technical_questions TEXT NOT NULL,
                technical_interactions TEXT NOT NULL,
                technical_validation TEXT,
                architecture_package TEXT,
                response_composition TEXT,
                rejection TEXT,
                deployment_status TEXT NOT NULL DEFAULT 'development',
                monthly_token_quota_base INTEGER NOT NULL DEFAULT 250000,
                extra_quota_current_month INTEGER NOT NULL DEFAULT 0,
                quota_month TEXT NOT NULL DEFAULT '',
                quota_adjustments TEXT NOT NULL DEFAULT '[]',
                clarification_questions TEXT NOT NULL,
                clarification_interactions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_ideas_owner_created ON ideas(owner_user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_ideas_tenant_created ON ideas(tenant_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS auth_sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS context_files (
                file_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                uploaded_by_user_id TEXT,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                blob_path TEXT NOT NULL,
                blob_url TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        # Backward-compatible migration for databases created before MVP2 fields existed.
        _ensure_column(connection, "ideas", "technical_validation", "TEXT")
        _ensure_column(connection, "ideas", "architecture_package", "TEXT")
        _ensure_column(connection, "ideas", "response_composition", "TEXT")
        _ensure_column(connection, "ideas", "context_snapshot", "TEXT")
        _ensure_column(connection, "ideas", "deployment_status", "TEXT NOT NULL DEFAULT 'development'")
        _ensure_column(connection, "ideas", "monthly_token_quota_base", "INTEGER NOT NULL DEFAULT 250000")
        _ensure_column(connection, "ideas", "extra_quota_current_month", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(connection, "ideas", "quota_month", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "ideas", "quota_adjustments", "TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(connection, "ideas", "technical_questions", "TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(connection, "ideas", "technical_interactions", "TEXT NOT NULL DEFAULT '[]'")


_init_schema()


class IdeaStore:
    def save(self, idea: IdeaCase) -> IdeaCase:
        existing = self.get(idea.idea_id)
        if existing is not None:
            idea.created_at = existing.created_at
        idea.updated_at = datetime.utcnow()

        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO ideas (
                    idea_id, tenant_id, owner_user_id, owner_display_name, title, canonical_language,
                    supported_languages, source_language, detected_language, response_language,
                    original_text, canonical_summary, current_stage, status, problem_statement,
                    expected_value, affected_users, context_snapshot, business_validation,
                    technical_questions, technical_interactions, technical_validation,
                    architecture_package, response_composition, rejection,
                    deployment_status, monthly_token_quota_base, extra_quota_current_month,
                    quota_month, quota_adjustments, clarification_questions, clarification_interactions, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(idea_id) DO UPDATE SET
                    tenant_id=excluded.tenant_id,
                    owner_user_id=excluded.owner_user_id,
                    owner_display_name=excluded.owner_display_name,
                    title=excluded.title,
                    canonical_language=excluded.canonical_language,
                    supported_languages=excluded.supported_languages,
                    source_language=excluded.source_language,
                    detected_language=excluded.detected_language,
                    response_language=excluded.response_language,
                    original_text=excluded.original_text,
                    canonical_summary=excluded.canonical_summary,
                    current_stage=excluded.current_stage,
                    status=excluded.status,
                    problem_statement=excluded.problem_statement,
                    expected_value=excluded.expected_value,
                    affected_users=excluded.affected_users,
                    context_snapshot=excluded.context_snapshot,
                    business_validation=excluded.business_validation,
                    technical_questions=excluded.technical_questions,
                    technical_interactions=excluded.technical_interactions,
                    technical_validation=excluded.technical_validation,
                    architecture_package=excluded.architecture_package,
                    response_composition=excluded.response_composition,
                    rejection=excluded.rejection,
                    deployment_status=excluded.deployment_status,
                    monthly_token_quota_base=excluded.monthly_token_quota_base,
                    extra_quota_current_month=excluded.extra_quota_current_month,
                    quota_month=excluded.quota_month,
                    quota_adjustments=excluded.quota_adjustments,
                    clarification_questions=excluded.clarification_questions,
                    clarification_interactions=excluded.clarification_interactions,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    idea.idea_id,
                    idea.tenant_id,
                    idea.owner_user_id,
                    idea.owner_display_name,
                    idea.title,
                    idea.canonical_language,
                    json.dumps(idea.supported_languages, ensure_ascii=False),
                    idea.source_language,
                    idea.detected_language,
                    idea.response_language,
                    idea.original_text,
                    idea.canonical_summary,
                    idea.current_stage.value,
                    idea.status.value,
                    idea.problem_statement,
                    idea.expected_value,
                    json.dumps(idea.affected_users, ensure_ascii=False),
                    _to_json(idea.context_snapshot),
                    _to_json(idea.business_validation),
                    _to_json(idea.technical_questions),
                    _to_json(idea.technical_interactions),
                    _to_json(idea.technical_validation),
                    _to_json(idea.architecture_package),
                    _to_json(idea.response_composition),
                    _to_json(idea.rejection),
                    idea.deployment_status.value,
                    idea.monthly_token_quota_base,
                    idea.extra_quota_current_month,
                    idea.quota_month,
                    _to_json(idea.quota_adjustments),
                    _to_json(idea.clarification_questions),
                    _to_json(idea.clarification_interactions),
                    idea.created_at.isoformat(),
                    idea.updated_at.isoformat(),
                ),
            )
        return idea

    def _row_to_idea(self, row: sqlite3.Row) -> IdeaCase:
        technical_validation = _from_json(row["technical_validation"])
        if technical_validation == {}:
            technical_validation = None

        architecture_package = _from_json(row["architecture_package"])
        if architecture_package == {}:
            architecture_package = None

        response_composition = _from_json(row["response_composition"])
        if response_composition == {}:
            response_composition = None

        return IdeaCase.model_validate(
            {
                "idea_id": row["idea_id"],
                "tenant_id": row["tenant_id"],
                "owner_user_id": row["owner_user_id"],
                "owner_display_name": row["owner_display_name"],
                "title": row["title"],
                "canonical_language": row["canonical_language"],
                "supported_languages": _from_json(row["supported_languages"]) or [],
                "source_language": row["source_language"],
                "detected_language": row["detected_language"],
                "response_language": row["response_language"],
                "original_text": row["original_text"],
                "canonical_summary": row["canonical_summary"],
                "current_stage": row["current_stage"],
                "status": row["status"],
                "problem_statement": row["problem_statement"],
                "expected_value": row["expected_value"],
                "affected_users": _from_json(row["affected_users"]) or [],
                "context_snapshot": _from_json(row["context_snapshot"]),
                "business_validation": _from_json(row["business_validation"]),
                "technical_questions": _from_json(row["technical_questions"]) or [],
                "technical_interactions": _from_json(row["technical_interactions"]) or [],
                "technical_validation": technical_validation,
                "architecture_package": architecture_package,
                "response_composition": response_composition,
                "rejection": _from_json(row["rejection"]),
                "deployment_status": row["deployment_status"] or "development",
                "monthly_token_quota_base": row["monthly_token_quota_base"] or 250000,
                "extra_quota_current_month": row["extra_quota_current_month"] or 0,
                "quota_month": row["quota_month"] or "",
                "quota_adjustments": _from_json(row["quota_adjustments"]) or [],
                "clarification_questions": _from_json(row["clarification_questions"]) or [],
                "clarification_interactions": _from_json(row["clarification_interactions"]) or [],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
        )

    def get(self, idea_id: str) -> IdeaCase | None:
        with _connect() as connection:
            row = connection.execute("SELECT * FROM ideas WHERE idea_id = ?", (idea_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_idea(row)

    def list_all(self) -> List[IdeaCase]:
        with _connect() as connection:
            rows = connection.execute("SELECT * FROM ideas ORDER BY created_at DESC").fetchall()
        return [self._row_to_idea(row) for row in rows]

    def list_by_owner(self, owner_user_id: str) -> List[IdeaCase]:
        with _connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ideas WHERE owner_user_id = ? ORDER BY created_at DESC",
                (owner_user_id,),
            ).fetchall()
        return [self._row_to_idea(row) for row in rows]

    def list_by_tenant(self, tenant_id: str) -> List[IdeaCase]:
        with _connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ideas WHERE tenant_id = ? ORDER BY created_at DESC",
                (tenant_id,),
            ).fetchall()
        return [self._row_to_idea(row) for row in rows]

    def delete(self, idea_id: str) -> None:
        with _connect() as connection:
            connection.execute("DELETE FROM ideas WHERE idea_id = ?", (idea_id,))


idea_store = IdeaStore()


class CompanyContextStore:
    def save(self, context: CompanyContext) -> CompanyContext:
        existing = self.get(context.tenant_id)
        if existing is not None:
            context.created_at = existing.created_at
        context.updated_at = datetime.utcnow()

        payload = _to_json(context)
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO company_contexts (tenant_id, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(tenant_id) DO UPDATE SET
                    payload=excluded.payload,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    context.tenant_id,
                    payload,
                    context.created_at.isoformat(),
                    context.updated_at.isoformat(),
                ),
            )
        return context

    def get(self, tenant_id: str) -> CompanyContext | None:
        with _connect() as connection:
            row = connection.execute("SELECT payload FROM company_contexts WHERE tenant_id = ?", (tenant_id,)).fetchone()
        if row is None:
            return None
        return CompanyContext.model_validate(_from_json(row[0]))


company_context_store = CompanyContextStore()


class ContextFileStore:
    def record_upload(
        self,
        tenant_id: str,
        filename: str,
        content_type: str,
        blob_path: str,
        blob_url: str,
        uploaded_by_user_id: str | None = None,
    ) -> Dict[str, str]:
        file_id = str(uuid4())
        created_at = _now_iso()
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO context_files (
                    file_id, tenant_id, uploaded_by_user_id, filename, content_type, blob_path, blob_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id,
                    tenant_id,
                    uploaded_by_user_id,
                    filename,
                    content_type,
                    blob_path,
                    blob_url,
                    created_at,
                ),
            )
        return {
            "file_id": file_id,
            "tenant_id": tenant_id,
            "filename": filename,
            "content_type": content_type,
            "blob_path": blob_path,
            "blob_url": blob_url,
            "uploaded_by_user_id": uploaded_by_user_id or "",
            "created_at": created_at,
        }


context_file_store = ContextFileStore()


class AuthStore:
    def __init__(self) -> None:
        self._users_by_username: Dict[str, Dict[str, str]] = {
            "analista.finanzas": {
                "user_id": "user-fin-01",
                "username": "analista.finanzas",
                "display_name": "Ana Finanzas",
                "tenant_id": "contoso-demo",
                "role": "analyst",
                "password": "Demo1234!",
            },
            "analista.riesgo": {
                "user_id": "user-risk-02",
                "username": "analista.riesgo",
                "display_name": "Rafa Riesgo",
                "tenant_id": "contoso-demo",
                "role": "analyst",
                "password": "Demo1234!",
            },
            "admin.valuehub": {
                "user_id": "user-admin-00",
                "username": "admin.valuehub",
                "display_name": "Admin Value Hub",
                "tenant_id": "contoso-demo",
                "role": "admin",
                "password": "Demo1234!",
            },
            "tecnico.platform": {
                "user_id": "user-tech-03",
                "username": "tecnico.platform",
                "display_name": "Equipo Tecnico Platform",
                "tenant_id": "contoso-demo",
                "role": "technical",
                "password": "Demo1234!",
            },
        }

    def authenticate(self, username: str, password: str) -> Dict[str, str] | None:
        user = self._users_by_username.get(username)
        if user is None:
            return None
        if user["password"] != password:
            return None
        return user

    def issue_token(self, user_id: str) -> str:
        token = str(uuid4())
        with _connect() as connection:
            connection.execute(
                "INSERT INTO auth_sessions (token, user_id, created_at) VALUES (?, ?, ?)",
                (token, user_id, _now_iso()),
            )
        return token

    def get_user_by_token(self, token: str) -> Dict[str, str] | None:
        with _connect() as connection:
            row = connection.execute(
                "SELECT user_id FROM auth_sessions WHERE token = ?",
                (token,),
            ).fetchone()
        if row is None:
            return None

        user_id = row[0]
        for user in self._users_by_username.values():
            if user["user_id"] == user_id:
                return user
        return None


auth_store = AuthStore()
