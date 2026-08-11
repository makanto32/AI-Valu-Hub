from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime

import requests

from .analytics_service import AnalyticsService
from .models import ExecutiveDashboardMetrics
from .store import idea_store


class DashboardMetricsProvider:
    """Abstract provider for executive dashboard metrics."""

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        raise NotImplementedError


class LocalDashboardMetricsProvider(DashboardMetricsProvider):
    """Build metrics directly from transactional records (SQLite store)."""

    def __init__(self, annual_ai_investment: float = 100_000) -> None:
        self.annual_ai_investment = annual_ai_investment

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        ideas = idea_store.list_by_tenant(tenant_id)
        analytics = AnalyticsService(all_ideas=ideas)
        return analytics.calculate_executive_dashboard(
            tenant_id=tenant_id,
            annual_ai_investment=self.annual_ai_investment,
            period=period,
        )


class SemanticFileDashboardMetricsProvider(DashboardMetricsProvider):
    """Read metrics from a Gold artifact generated for Fabric semantic model ingestion."""

    def __init__(self, semantic_path: Path) -> None:
        self.semantic_path = semantic_path

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        if not self.semantic_path.exists():
            raise FileNotFoundError(f"Semantic metrics file not found: {self.semantic_path}")

        payload = json.loads(self.semantic_path.read_text(encoding="utf-8"))
        # Allow one file per tenant or a full map of tenants.
        if "tenant_id" in payload:
            selected = payload
        else:
            selected = payload.get(tenant_id)
            if selected is None:
                raise KeyError(f"Tenant '{tenant_id}' not found in semantic metrics payload")

        selected["period"] = period
        return ExecutiveDashboardMetrics.model_validate(selected)


class PowerBIDashboardMetricsProvider(DashboardMetricsProvider):
    """Read metrics from a Power BI/Fabric semantic model table."""

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        workspace_id: str,
        dataset_id: str,
        table_name: str,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.workspace_id = workspace_id
        self.dataset_id = dataset_id
        self.table_name = table_name

    def _acquire_token(self) -> str:
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }
        response = requests.post(token_url, data=payload, timeout=20)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise RuntimeError("No access_token returned by Entra token endpoint")
        return token

    def _execute_query(self, token: str, dax_query: str) -> list[dict]:
        url = (
            f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}"
            f"/datasets/{self.dataset_id}/executeQueries"
        )
        body = {
            "queries": [{"query": dax_query}],
            "serializerSettings": {"includeNulls": True},
        }
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=body,
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        if not results:
            return []
        tables = results[0].get("tables", [])
        if not tables:
            return []
        return tables[0].get("rows", [])

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        token = self._acquire_token()
        escaped_tenant = tenant_id.replace("\"", "\"\"")
        escaped_period = period.replace("\"", "\"\"")
        dax = (
            "EVALUATE "
            "TOPN(1, "
            f"FILTER('{self.table_name}', '{self.table_name}'[tenant_id] = \"{escaped_tenant}\" "
            f"&& '{self.table_name}'[period] = \"{escaped_period}\"), "
            f"'{self.table_name}'[generated_at], DESC)"
        )
        rows = self._execute_query(token, dax)
        if not rows:
            raise KeyError(
                f"No semantic dashboard payload found for tenant '{tenant_id}' and period '{period}'"
            )

        row = rows[0]
        payload_key = next((key for key in row.keys() if key.endswith("[payload_json]")), None)
        if payload_key is None:
            raise KeyError("payload_json column not found in semantic model query result")

        payload_json = row[payload_key]
        if not payload_json:
            raise ValueError("payload_json is empty in semantic model")

        selected = json.loads(payload_json)
        selected["period"] = period
        # Ensure generated timestamps exist to satisfy model validation.
        now_iso = datetime.utcnow().isoformat()
        selected.setdefault("generated_at", now_iso)
        selected.setdefault("last_updated", now_iso)
        return ExecutiveDashboardMetrics.model_validate(selected)


def build_dashboard_metrics_provider() -> DashboardMetricsProvider:
    source = os.getenv("AIHUB_DASHBOARD_METRICS_SOURCE", "local").strip().lower()
    semantic_file = Path(
        os.getenv(
            "AIHUB_SEMANTIC_METRICS_FILE",
            str(Path(__file__).resolve().parents[2] / "data" / "fabric" / "gold" / "executive_dashboard_current.json"),
        )
    )

    if source == "semantic":
        return SemanticFileDashboardMetricsProvider(semantic_path=semantic_file)

    if source == "powerbi":
        pbi_tenant = os.getenv("AIHUB_POWERBI_TENANT_ID", "").strip()
        pbi_client_id = os.getenv("AIHUB_POWERBI_CLIENT_ID", "").strip()
        pbi_client_secret = os.getenv("AIHUB_POWERBI_CLIENT_SECRET", "").strip()
        pbi_workspace_id = os.getenv("AIHUB_POWERBI_WORKSPACE_ID", "").strip()
        pbi_dataset_id = os.getenv("AIHUB_POWERBI_DATASET_ID", "").strip()
        pbi_table_name = os.getenv("AIHUB_POWERBI_TABLE_NAME", "DashboardPayload").strip()

        required = [
            pbi_tenant,
            pbi_client_id,
            pbi_client_secret,
            pbi_workspace_id,
            pbi_dataset_id,
            pbi_table_name,
        ]
        if not all(required):
            raise RuntimeError(
                "Missing one or more Power BI semantic provider env vars: "
                "AIHUB_POWERBI_TENANT_ID, AIHUB_POWERBI_CLIENT_ID, AIHUB_POWERBI_CLIENT_SECRET, "
                "AIHUB_POWERBI_WORKSPACE_ID, AIHUB_POWERBI_DATASET_ID, AIHUB_POWERBI_TABLE_NAME"
            )

        return PowerBIDashboardMetricsProvider(
            tenant_id=pbi_tenant,
            client_id=pbi_client_id,
            client_secret=pbi_client_secret,
            workspace_id=pbi_workspace_id,
            dataset_id=pbi_dataset_id,
            table_name=pbi_table_name,
        )

    return LocalDashboardMetricsProvider()
