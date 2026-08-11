# 🔌 INTEGRACIÓN RÁPIDA - Dashboard + Agentes

## Para Activar en main.py

### Paso 1: Agregar Imports (al inicio del archivo)

```python
# En main.py, después de los imports existentes, agregar:

from .analytics_service import AnalyticsService
from .agent_orchestrator import (
    MultiAgentOrchestrator, 
    AgentContext, 
    ComplexityLevel,
    AgentType
)
from .models import (
    ExecutiveDashboardMetrics,
    IdeaDuplicationMetrics,
    AIAdoptionMetrics,
    ProductionMetrics,
    InvestmentROIMetrics,
    CollaboratorMetrics,
    AgentExecution,
)
```

### Paso 2: Copiar los 8 Endpoints

En `main.py`, **DESPUÉS** del último endpoint de `ArchitecturePackage` (alrededor de línea 2466), agregar esto:

```python
# ===================== ENDPOINTS EJECUTIVOS & ANALYTICS =====================

@app.get("/admin/metrics/executive-dashboard")
def get_executive_dashboard_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> ExecutiveDashboardMetrics:
    """
    Retorna dashboard ejecutivo con métricas de valor consolidadas.
    - % Reducción de retrabajo
    - % Duplicados evitados
    - % Participación de colaboradores
    - % Adopción de IA
    - Breakdown de métricas detalladas (duplication, adoption, production, ROI)
    """
    _require_admin(current_user)
    
    ideas = idea_store.list_by_tenant(current_user.tenant_id)
    analytics = AnalyticsService(all_ideas=ideas)
    dashboard = analytics.calculate_executive_dashboard(
        tenant_id=current_user.tenant_id,
        annual_ai_investment=100_000,
        period="current"
    )
    
    return dashboard


@app.get("/admin/metrics/duplication")
def get_duplication_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaDuplicationMetrics:
    """Retorna métricas de detección y reducción de duplicación."""
    _require_admin(current_user)
    
    ideas = idea_store.list_by_tenant(current_user.tenant_id)
    analytics = AnalyticsService(all_ideas=ideas)
    return analytics.calculate_duplication_metrics()


@app.get("/admin/metrics/ai-adoption")
def get_ai_adoption_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> AIAdoptionMetrics:
    """Retorna métricas de adopción de IA en la plataforma."""
    _require_admin(current_user)
    
    ideas = idea_store.list_by_tenant(current_user.tenant_id)
    analytics = AnalyticsService(all_ideas=ideas)
    return analytics.calculate_ai_adoption_metrics()


@app.get("/admin/metrics/production")
def get_production_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> ProductionMetrics:
    """Retorna métricas de valor en producción."""
    _require_admin(current_user)
    
    ideas = idea_store.list_by_tenant(current_user.tenant_id)
    analytics = AnalyticsService(all_ideas=ideas)
    return analytics.calculate_production_metrics()


@app.get("/admin/metrics/roi")
def get_roi_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> InvestmentROIMetrics:
    """Retorna métricas de inversión IA vs ROI."""
    _require_admin(current_user)
    
    ideas = idea_store.list_by_tenant(current_user.tenant_id)
    analytics = AnalyticsService(all_ideas=ideas)
    return analytics.calculate_roi_metrics()


@app.get("/admin/metrics/collaborators")
def get_collaborator_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> list[CollaboratorMetrics]:
    """Retorna métricas de participación de colaboradores."""
    _require_admin(current_user)
    
    ideas = idea_store.list_by_tenant(current_user.tenant_id)
    analytics = AnalyticsService(all_ideas=ideas)
    return analytics.calculate_collaborator_participation()


# ===================== ENDPOINTS AGENTIC LAYER =====================

@app.post("/admin/agent-session/{idea_id}/execute")
async def execute_agent_validation(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict:
    """
    Ejecuta validación de idea usando capa agentica no-determinista.
    - Evalúa complejidad
    - Selecciona agentes dinámicamente
    - Activa skills según contexto (Context Engine como ADN)
    - Retorna decisiones y recomendaciones
    """
    _require_admin(current_user)
    
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No access to this idea")
    
    # Construir contexto empresarial (DNA)
    company_context = AgentContext(
        tenant_id=idea.tenant_id,
        company_name="Demo Company",
        industry="Financial Services",
        risk_tolerance="medium",
        strategic_priorities=[
            "AI-First Solutions",
            "Digital Transformation",
            "Customer Experience",
        ],
        prohibited_domains=["High-Risk Geopolitical"],
        regulatory_constraints=[
            "GDPR Compliance",
            "Data Residency - EU",
            "SOC 2 Type II",
        ],
        available_skills=[],  # Se pobla dinámicamente
    )
    
    # Crear orquestador
    orchestrator = MultiAgentOrchestrator(company_context)
    
    # Ejecutar validación
    result = await orchestrator.orchestrate_validation(idea)
    
    return result


@app.get("/admin/agent-session/summary")
def get_agent_execution_summary(
    current_user: UserProfile = Depends(get_current_user),
) -> dict:
    """Retorna resumen de ejecuciones recientes de agentes."""
    _require_admin(current_user)
    
    return {
        "message": "Agent execution summary",
        "recent_executions": [],
        "timestamp": datetime.utcnow().isoformat(),
    }
```

### Paso 3: Agregar en Frontend (App.jsx o router)

En `frontend/src/App.jsx`:

```jsx
import ExecutiveDashboard from './pages/ExecutiveDashboard';

// En la definición de rutas:
{
  path: '/admin/dashboard',
  element: <ExecutiveDashboard />,
  requiresAdmin: true,
}
```

### Paso 4: Agregar Link en Menu (Opcional)

En el componente de menú administrador:

```jsx
<NavLink to="/admin/dashboard" className="menu-link">
  📊 Dashboard Ejecutivo
</NavLink>
```

---

## Verificación de Funcionamiento

### 1. Backend - Verificar Modelos
```bash
python -c "from api.app.models import ExecutiveDashboardMetrics; print('✓ OK')"
python -c "from api.app.analytics_service import AnalyticsService; print('✓ OK')"
python -c "from api.app.agent_orchestrator import MultiAgentOrchestrator; print('✓ OK')"
```

### 2. Backend - Verificar Endpoints
```bash
# Con token válido en autorización:
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/admin/metrics/executive-dashboard
```

**Respuesta esperada** (JSON):
```json
{
  "tenant_id": "...",
  "period": "current",
  "duplicates_avoided_percentage": 42.3,
  "retwork_reduction_percentage": 87.5,
  "collaborator_participation_rate": 65.0,
  "ai_adoption_rate": 78.5,
  "duplication_metrics": {...},
  "adoption_metrics": {...},
  "production_metrics": {...},
  "roi_metrics": {...},
  "top_collaborators": [...],
  "monthly_ideas_submitted": [1, 2, 3, ...],
  "monthly_ideas_approved": [1, 1, 2, ...],
  "monthly_ai_cost": [850, 850, 850, ...],
  "generated_at": "2024-...",
  "last_updated": "2024-..."
}
```

### 3. Frontend - Verificar Componente
```bash
# En navegador:
http://localhost:3000/admin/dashboard
```

Debería ver:
- ✅ 4 KPIs principales en cards
- ✅ 6 secciones de métricas
- ✅ Tabla de colaboradores
- ✅ Gráficos de tendencias
- ✅ Selector de período
- ✅ Datos cargados en tiempo real

---

## Archivos a Verificar que Existen

Antes de integrar, asegurar que estos archivos existen:

```
✓ api/app/models.py              (modificado con +175 líneas)
✓ api/app/analytics_service.py   (nuevo, 460 líneas)
✓ api/app/agent_orchestrator.py  (nuevo, 570 líneas)
✓ api/app/new_endpoints.py       (referencia, 165 líneas)
✓ frontend/src/pages/ExecutiveDashboard.tsx  (nuevo, 330 líneas)
✓ frontend/src/styles/dashboard.module.css   (nuevo, 450 líneas)
```

---

## Troubleshooting

### Error: "ImportError: cannot import name 'AnalyticsService'"
- Verificar que `analytics_service.py` existe en `api/app/`
- Ejecutar: `python -c "from api.app.analytics_service import AnalyticsService"`

### Error: "ExecutiveDashboardMetrics is not defined"
- Verificar que modelos en `models.py` fueron agregados correctamente
- Buscar línea: `class ExecutiveDashboardMetrics(BaseModel):`

### Error: "Dashboard no carga datos"
- Verificar que hay ideas en la DB: `GET /ideas` debe retornar datos
- Verificar token admin en localStorage
- Revisar Network tab en DevTools para ver respuesta del servidor

### Error: "405 Method Not Allowed"
- Verificar que decorador es `@app.get` (no `@app.post` para endpoints de métrica)
- Revisar que endpoint está en lista de endpoints correctamente

### Error: "403 Forbidden"
- Usuario actual no tiene rol admin
- Verificar función `_require_admin(current_user)` está siendo llamada
- Usuario debe tener `role == "admin"`

---

## Variables de Entorno (Opcional)

En `.env`:

```env
# Métricas de negocio
ANNUAL_AI_INVESTMENT=100000              # Presupuesto anual en USD
PLATFORM_MONTHLY_COST=850                # Costo mensual de plataforma
COST_PER_DUPLICATE_AVOIDED=500000        # Valor por duplicado evitado
HOURS_PER_VALIDATION_MANUAL=8            # Horas de validación manual
HOURLY_RATE=150                          # Tarifa promedio USD/hora

# Agentes
AGENT_RISK_TOLERANCE=medium              # low|medium|high
AGENT_STRATEGIC_PRIORITIES=AI-First,Digital Transformation
AGENT_REGULATORY_CONSTRAINTS=GDPR,SOC 2 Type II
```

---

## Timing de Integración

- **Modelos**: 5 minutos (copiar-pegar en models.py)
- **Servicios**: 2 minutos (analytics_service.py ya existe)
- **Endpoints**: 5 minutos (copiar-pegar en main.py)
- **Frontend**: 3 minutos (copiar componente y ruta)
- **Testing**: 10 minutos (verificar endpoints y UI)

**Total: ~25 minutos para activación completa**

---

## Post-Integración

1. Ejecutar seed script para datos demo:
   ```bash
   python scripts/seed-complete-demo.py
   ```

2. Verificar que 3-4 ideas están en DB

3. Acceder a dashboard: `http://localhost:3000/admin/dashboard`

4. Ver métricas pobladas en tiempo real

---

¡Listo para demostración! 🚀
