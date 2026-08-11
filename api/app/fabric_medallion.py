from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .analytics_service import AnalyticsService
from .models import IdeaCase
from .store import idea_store


def _base_path() -> Path:
    configured = os.getenv("AIHUB_FABRIC_DATA_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "data" / "fabric"


def _ensure_dirs(base: Path) -> dict[str, Path]:
    bronze = base / "bronze"
    silver = base / "silver"
    gold = base / "gold"
    bronze.mkdir(parents=True, exist_ok=True)
    silver.mkdir(parents=True, exist_ok=True)
    gold.mkdir(parents=True, exist_ok=True)
    return {"bronze": bronze, "silver": silver, "gold": gold}


def _idea_to_bronze_record(idea: IdeaCase) -> dict:
    return idea.model_dump(mode="json")


def _idea_to_silver_row(idea: IdeaCase) -> dict[str, str | int | float]:
    technical = idea.technical_validation
    business = idea.business_validation
    return {
        "idea_id": idea.idea_id,
        "tenant_id": idea.tenant_id,
        "owner_user_id": idea.owner_user_id,
        "owner_display_name": idea.owner_display_name,
        "title": idea.title,
        "status": idea.status.value,
        "current_stage": idea.current_stage.value,
        "deployment_status": idea.deployment_status.value,
        "value_score": business.value_score,
        "risk_score": business.risk_score,
        "feasibility_score": technical.feasibility_score if technical is not None else 0,
        "integration_complexity": technical.integration_complexity if technical is not None else 0,
        "security_risk": technical.security_risk if technical is not None else 0,
        "data_readiness": technical.data_readiness if technical is not None else 0,
        "has_architecture_package": 1 if idea.architecture_package is not None else 0,
        "monthly_token_quota_base": idea.monthly_token_quota_base,
        "extra_quota_current_month": idea.extra_quota_current_month,
        "quota_month": idea.quota_month,
        "created_at": idea.created_at.isoformat(),
        "updated_at": idea.updated_at.isoformat(),
    }


def _write_bronze(bronze_dir: Path, ideas: list[IdeaCase]) -> None:
    target = bronze_dir / "ideas_raw.jsonl"
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for idea in ideas:
            handle.write(json.dumps(_idea_to_bronze_record(idea), ensure_ascii=False) + "\n")


def _write_silver(silver_dir: Path, ideas: list[IdeaCase]) -> None:
    target = silver_dir / "ideas_clean.csv"
    rows = [_idea_to_silver_row(idea) for idea in ideas]
    if not rows:
        target.write_text("", encoding="utf-8")
        return

    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_gold(gold_dir: Path, ideas: list[IdeaCase]) -> None:
    ideas_by_tenant: dict[str, list[IdeaCase]] = defaultdict(list)
    for idea in ideas:
        ideas_by_tenant[idea.tenant_id].append(idea)

    semantic_payload_by_tenant: dict[str, dict] = {}
    kpi_rows: list[dict[str, str | float | int]] = []

    for tenant_id, tenant_ideas in ideas_by_tenant.items():
        analytics = AnalyticsService(all_ideas=tenant_ideas)
        dashboard = analytics.calculate_executive_dashboard(
            tenant_id=tenant_id,
            annual_ai_investment=100_000,
            period="current",
        )
        dashboard_payload = dashboard.model_dump(mode="json")
        semantic_payload_by_tenant[tenant_id] = dashboard_payload

        kpi_rows.append(
            {
                "tenant_id": tenant_id,
                "duplicates_avoided_percentage": dashboard.duplicates_avoided_percentage,
                "retwork_reduction_percentage": dashboard.retwork_reduction_percentage,
                "collaborator_participation_rate": dashboard.collaborator_participation_rate,
                "ai_adoption_rate": dashboard.ai_adoption_rate,
                "ideas_in_production": dashboard.production_metrics.ideas_in_production,
                "estimated_annual_value": dashboard.production_metrics.estimated_annual_value,
                "estimated_annual_value_generated": dashboard.roi_metrics.estimated_annual_value_generated,
                "roi_percentage": dashboard.roi_metrics.roi_percentage,
                "generated_at": datetime.utcnow().isoformat(),
            }
        )

    semantic_file = gold_dir / "executive_dashboard_current.json"
    semantic_file.write_text(
        json.dumps(semantic_payload_by_tenant, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    kpi_file = gold_dir / "fact_dashboard_kpis.csv"
    if not kpi_rows:
        kpi_file.write_text("", encoding="utf-8")
        return

    with kpi_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(kpi_rows[0].keys()))
        writer.writeheader()
        writer.writerows(kpi_rows)


def run_medallion_pipeline() -> dict[str, str]:
    base = _base_path()
    dirs = _ensure_dirs(base)
    ideas = idea_store.list_all()

    _write_bronze(dirs["bronze"], ideas)
    _write_silver(dirs["silver"], ideas)
    _write_gold(dirs["gold"], ideas)

    return {
        "base_dir": str(base),
        "bronze_file": str(dirs["bronze"] / "ideas_raw.jsonl"),
        "silver_file": str(dirs["silver"] / "ideas_clean.csv"),
        "gold_semantic_file": str(dirs["gold"] / "executive_dashboard_current.json"),
        "gold_kpi_file": str(dirs["gold"] / "fact_dashboard_kpis.csv"),
    }
