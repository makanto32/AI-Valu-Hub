# Fabric Medallion + Semantic Model (Admin Dashboard)

## Objetivo
Conectar el dashboard ejecutivo de admin a un modelo semántico alimentado por registros actuales de la base de datos transaccional.

## Estado implementado en API
- Fuente de métricas configurable por variable de entorno:
  - `AIHUB_DASHBOARD_METRICS_SOURCE=local|semantic|powerbi`
- Archivo semántico configurable:
  - `AIHUB_SEMANTIC_METRICS_FILE=/ruta/a/executive_dashboard_current.json`
- Endpoint para refrescar pipeline medallion:
  - `POST /admin/metrics/semantic/refresh`
- Pipeline medallion en backend:
  - Bronze: `ideas_raw.jsonl`
  - Silver: `ideas_clean.csv`
  - Gold: `executive_dashboard_current.json`, `fact_dashboard_kpis.csv`
- Endpoint de snapshot local para sincronización a Fabric:
  - `GET /admin/metrics/executive-dashboard/snapshot`

## Integración end-to-end con Fabric (workspace latamdemos)
Se agregó soporte para leer el dashboard directamente desde un modelo semántico en Fabric/Power BI usando provider `powerbi`.

Variables requeridas en la API:
- `AIHUB_DASHBOARD_METRICS_SOURCE=powerbi`
- `AIHUB_POWERBI_TENANT_ID`
- `AIHUB_POWERBI_CLIENT_ID`
- `AIHUB_POWERBI_CLIENT_SECRET`
- `AIHUB_POWERBI_WORKSPACE_ID`
- `AIHUB_POWERBI_DATASET_ID`
- `AIHUB_POWERBI_TABLE_NAME` (default recomendado: `DashboardPayload`)

Scripts agregados:
- `scripts/fabric-provision-semantic.ps1`
  - Busca workspace por nombre (default `latamdemos`)
  - Crea dataset push `AIHubSemanticModel` si no existe
- `scripts/fabric-sync-semantic.ps1`
  - Lee snapshot real desde la API
  - Limpia e inserta fila `payload_json` en tabla semántica

## Flujo recomendado en Azure (desde versión ACR)
1. Desplegar la API con esta versión de imagen.
2. Configurar variables de entorno en Container App:
   - `AIHUB_DASHBOARD_METRICS_SOURCE=semantic`
   - `AIHUB_FABRIC_DATA_DIR=/mnt/data/fabric` (o ruta persistente equivalente)
   - `AIHUB_SEMANTIC_METRICS_FILE=/mnt/data/fabric/gold/executive_dashboard_current.json`
3. Ejecutar `POST /admin/metrics/semantic/refresh` para generar Bronze/Silver/Gold.
4. Provisión Fabric (Power BI/Fabric API):
  - Ejecutar `scripts/fabric-provision-semantic.ps1 -WorkspaceName latamdemos`
5. Sincronizar payload hacia modelo semántico:
  - Ejecutar `scripts/fabric-sync-semantic.ps1 -WorkspaceId <id> -DatasetId <id>`
6. Configurar API en modo powerbi con variables de entorno anteriores.

## Observación importante
- En esta fase, el dashboard consume el artefacto Gold semántico (`executive_dashboard_current.json`) generado desde datos reales de BD.
- Para conexión nativa directa a dataset Fabric, esta implementación usa `executeQueries` sobre Power BI/Fabric API.
