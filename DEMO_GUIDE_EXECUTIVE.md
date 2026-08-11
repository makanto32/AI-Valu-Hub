# AIHUB Demo - Guía de Ejecución para Upper Management

## Objetivo de la Demo

Demostrar que AIHUB automatiza el intake de ideas END-TO-END con:
1. **Detección automática de iniciativas similares** (evita duplicación)
2. **Matching inteligente con contactos** (acelera coordinación)
3. **Validación técnica con agentes IA** (reduce reuniones manuales)
4. **Generación de arquitectura automática** (acelera time-to-value)

Resultado: De 2-3 meses de proceso manual → 15 minutos de intake + validación

---

## Pre-Demo Setup (10 minutos antes)

### 1. Verificar Base de Datos Poblada

```powershell
# Verificar datos en BD
sqlite3 c:\Projects\AI-OPPORTUNIY-HUB\data\aihub.db "SELECT COUNT(*) as total_ideas FROM ideas;"
sqlite3 c:\Projects\AI-OPPORTUNIY-HUB\data\aihub.db "SELECT COUNT(*) as total_contexts FROM company_contexts;"
```

**Resultado esperado:**
- total_ideas: 8+ (ideas de intake + catálogo)
- total_contexts: 1 (Contoso Financial Services)

### 2. Iniciar Backend

```powershell
# Terminal 1
cd c:\Projects\AI-OPPORTUNIY-HUB
python -m uvicorn api.app.main:app --reload --port 8000

# Verificar: http://localhost:8000/docs
```

Debe mostrar Swagger con todos los endpoints disponibles.

### 3. Iniciar Frontend

```powershell
# Terminal 2
cd c:\Projects\AI-OPPORTUNIY-HUB\frontend
npm run dev

# Verificar: http://localhost:5173
# Debe mostrar login demo
```

### 4. Validar Catálogo de Iniciativas Cargado

En Terminal 3:
```powershell
cd c:\Projects\AI-OPPORTUNIY-HUB

# Ejecutar seed nuevamente si es necesario
python scripts/seed-complete-demo.py

# Debe mostrar:
# [OK] PRODUCCION: Fraud Detection Platform v2.0
# [OK] EN DESARROLLO: KYC Document Automation v1.0
# [OK] EN FINANCIAMIENTO: Predictive Credit Risk Engine
# [OK] PRODUCCION: AI Support Chatbot Platform
```

---

## Demo Script (15 minutos)

### LIVE UI MODE: User Session + Admin Session (recommended)

Use the exact current application UI (not static slides) and run two perspectives:

1. **User session (analyst)**
2. **Admin session (portfolio governance)**

#### Admin session data points to highlight (validated in current UI)

**Dashboard (`📊 Dashboard`)**
- Rework Reduction: **70.2%**
- Duplicates Avoided: **59.5%**
- AI Adoption: **21.4%**
- Total Ideas: **42**
- Duplicates Detected: **25**
- Avoided Cost: **$50K**
- ROI: **385%**

**Admin panel (`MVP3 admin panel`)**
- **Use cases**: approved case list with feasibility, estimated tokens/cost, and deployment status.
- **Tokens and cost**:
  - Projects in production: **1**
  - Monthly total quota: **4,500,000 tokens**
  - Quota month estimated cost: **$0.0226**
  - Case-level example cost: **$0.0057**
- **Metrics**:
  - Total ideas: **42**
  - Approval rate: **21.4%**
  - Technical pass rate: **64.3%**
  - Average feasibility: **91**
  - Average cycle time: **933.4 hours**

#### Narrative in English (for this section)
> "In the same product, leadership gets outcome visibility in Dashboard, while admins get execution control in Use cases, Tokens and cost, and Metrics. This is where we connect portfolio impact with operating discipline and AI spend governance."

### ACTO 0.5: Admin Dashboard (2-3 minutos)

**Navegación (usuario admin):**
1. Cambiar `UI language` a `EN`.
2. Click en `Panel admin MVP3`.
3. Recorrer tabs: `Use cases` → `Tokens and cost` → `Metrics`.

**Qué mostrar:**
- **Use cases:** ideas aprobadas, factibilidad, estado de despliegue, y control de lifecycle.
- **Tokens and cost:** cuota mensual, consumo acumulado y costo estimado.
- **Metrics:** approval rate, technical pass rate, tiempo de ciclo y componentes frecuentes.

**Narrative (en inglés recomendado):**
> "This admin panel is where governance happens. Executives see outcomes in the dashboard, and operators see control signals here. In one place we can decide what to prioritize, what to fund, and how to keep AI spend under control."

### ACTO 1: Contexto y Navegación (2 minutos)

**Que mostrar:**
```
Home de AIHUB
├── Hero: "MVP2 Business + Technical Studio"
├── Tenant: contoso-demo (Contoso Financial Services)
├── Menu: Inicio | Mis Ideas | Logout
└── Idea Cards Dashboard (muestra ideas existentes en diferentes estados)
```

**Narrative:**
> "Esta es AIHUB, nuestro motor de captura y validación de ideas. A diferencia de métodos manuales que toman 2-3 meses, aquí todo sucede en 15 minutos. El sistema automáticamente:
> - Detecta si la idea ya existe (evita duplicación)
> - Sugiere contactos de iniciativas relacionadas
> - Valida viabilidad técnica con agentes IA
> - Genera propuesta de arquitectura y costos
> 
> Vamos a ver tres escenarios reales que sucederían en el banco."

### ACTO 2: Scenario 1 - Duplicado en Producción (3-4 minutos)

**Navegación:**
1. Click en "Nueva Idea" o "+ Capturar Idea"
2. Ver formulario con campos:
   - Título
   - Problema
   - Valor Esperado
   - Usuarios Afectados
   - Idioma

**Ingresar Idea 1:**
```
Titulo: Detección de Fraude con Grafos de Comportamiento

Problema: Los patrones de fraude evolucionan rápidamente. Nuestro sistema actual detecta casos pero genera falsos positivos en 15-20%. Necesitamos análisis de grafos de conexión para detectar fraude en anillo.

Valor Esperado: Reducir falsos positivos 40%, detectar fraude organizado en tiempo real.

Usuarios Afectados: seguridad, operaciones, cumplimiento

Idioma: Español
```

**Click: "Validar y Matchear Ideas Similares"**

**Resultado esperado:**
```
[MATCHING INTELLIGENCE]

✓ Idea Similar Detectada
  Titulo: "Fraud Detection Platform v2.0"
  Estado: EN PRODUCCION (Deployed hace 120 dias)
  Score Similitud: 78%
  
  CONTACTO:
  📧 Carlos Mendez (carlos.mendez@contoso.com)
  Rol: Fraud Detection Lead
  Dpto: Risk & Compliance
  
  RECOMENDACION:
  ⚠️ Esta idea EXTIENDE solución en producción.
  Contactar a Carlos antes de proceder a validación formal.
  
  ACCIONES:
  - Agendar reunión con Carlos Mendez
  - Evaluar mejoras propuestas vs roadmap actual
  - Decidir: enhancement o iniciativa paralela
```

**Narrative:**
> "Miren esto. El usuario propuso una idea sobre fraude, pero el sistema AUTOMÁTICAMENTE detectó que ya existe una plataforma en producción desde hace 120 días. No solo eso: sugiere contactar a Carlos Mendez, el propietario actual.
>
> SIN este sistema:
> - Recursos habrían invertido 2 meses en una solución duplicada
> - Costaría $500k+ en personas/tiempo
> - Otra solución en mantenimiento vs una consolidada
>
> CON este sistema:
> - Detección instantánea de duplicación
> - Carlos colaboraría y mejoraría la versión existente
> - Evitamos deuda técnica y fragmentación
> 
> Siguiente escenario: una idea que COMPLEMENTA algo en desarrollo."

---

### ACTO 3: Scenario 2 - Complementaria en Desarrollo (3-4 minutos)

**Navegar:** "Nueva Idea" nuevamente

**Ingresar Idea 2:**
```
Titulo: Validación Biométrica en Onboarding Digital

Problema: El KYC actual solo valida documentos. Regulador requiere validación de identidad más fuerte. Necesitamos verificación de rostro y huellas.

Valor Esperado: Cumplimiento AML mejorado, precisión de identificación 99.9%, reducir fraude de identidad 60%.

Usuarios Afectados: onboarding, compliance, clientes

Idioma: Español
```

**Click: "Validar y Matchear"**

**Resultado esperado:**
```
[MATCHING INTELLIGENCE]

✓ Idea Similar Detectada (Parcial)
  Titulo: "KYC Document Automation v1.0"
  Estado: EN DESARROLLO (65% completada)
  Score Similitud: 65%
  
  CONTACTO PRINCIPAL:
  📧 Rosa Garcia (rosa.garcia@contoso.com)
  Rol: KYC Program Manager
  Dpto: Onboarding
  
  CONTACTO SOPORTE TECNICO:
  📧 Sofia Gonzalez (sofia.gonzalez@contoso.com)
  Rol: Business Analyst
  
  RECOMENDACION:
  ℹ️ Esta idea COMPLEMENTA iniciativa en desarrollo.
  Oportunidad de incorporar requisitos ANTES de go-live.
  
  IMPACTO DE TIMING:
  - Si se integra en v1.0: +2-3 semanas desarrollo, go-live unico
  - Si es v1.1: Go-live v1.0 en plazo, v1.1 en +6 semanas
  
  ACCIONES:
  - Contactar Rosa Garcia esta semana
  - Realizar feasibility assessment (4 horas)
  - Decidir: integración en v1.0 o v1.1
  - Incorporar en roadmap oficial
```

**Narrative:**
> "Segundo escenario. Esta idea propone biometría para KYC. El sistema detecta que hay una iniciativa de KYC Automation ya en desarrollo.
>
> Aquí es donde la coordinación es crítica:
> - Si se comunican HOY: puede integrarse antes de finalizar KYC v1.0 (2-3 semanas extra, pero lanzamiento único)
> - Si se avisan después: tendrían que hacer v1.1 6 semanas más tarde
>
> El sistema:
> - Detecta la complementariedad automáticamente
> - Proporciona contactos de quién lo liderá (Rosa y Sofia)
> - Calcula impacto de timeline
> - Genera acciones concretas
>
> Sin esto: Emails perdidos, reuniones retrasadas, decisiones informales. Con esto: coordinación automática, decisiones documentadas, cero duplicación.
> 
> Ultimo escenario: una idea COMPLEJA que requiere validación de agentes IA."

---

### ACTO 4: Scenario 3 - Validación Técnica con Agentes (5-6 minutos)

**Navegar:** "Nueva Idea"

**Ingresar Idea 3:**
```
Titulo: Análisis Predictivo de Riesgo de Crédito en Onboarding

Problema: Aplicamos scoring de riesgo POST-onboarding, muy tarde. Necesitamos scoring EN onboarding para aprobar mejor casos y rechazar riesgosos temprano.

Valor Esperado: Mejora de calidad de cartera 25%, reducción de charge-offs, optimización de aprovisionamiento.

Usuarios Afectados: credit-team, onboarding, risk-management

Idioma: Español
```

**Click: "Validar y Matchear"**

**Resultado esperado (Parte 1: Matching):**
```
[MATCHING INTELLIGENCE]

✓ Idea Relacionada Encontrada
  Titulo: "Predictive Credit Risk Engine"
  Estado: EN FINANCIAMIENTO (espera presupuesto Q3 2026)
  Score Similitud: 42% (baja, pero relacionada)
  
  CONTACTO:
  📧 Juan Ramirez (juan.ramirez@contoso.com)
  Rol: Credit Risk Officer
  
  RECOMENDACION:
  ⚠️ Iniciativa similar existe pero en fase EARLY.
  Evaluar consolidación de propuestas.
```

**Luego, click en "Proceder a Validación Técnica" o similar**

**Resultado esperado (Parte 2: Agentes):**
```
[AGENT-ASSISTED VALIDATION]

Complejidad técnica ALTA detectada.
Activando validación con 3 agentes IA...

---

AGENT 1: Architecture Reviewer
Pregunta: ¿Integrar con Core Banking System durante onboarding?

Opciones:
  ☐ REST API sync (latencia < 200ms)
  ☐ Async queue (latencia 2-5seg)
  ☐ Batch pre-compute (recompute cada 4h)

→ Seleccionar: REST API sync

---

AGENT 2: Data Science Reviewer
Pregunta: ¿Datos históricos disponibles para entrenar modelo?

Opciones:
  ☐ Si, 3+ años con outcome labels
  ☐ Si, 2 años pero labels incompletos
  ☐ Parcialmente, requiere data cleaning
  ☐ No, necesitaría synthetic data

→ Seleccionar: Si, 3+ años

---

AGENT 3: Risk & Compliance Reviewer
Pregunta: ¿Modelo requiere explicabilidad regulatoria?
(Contexto: Banco con LOW risk tolerance)

Opciones:
  ☐ Si, full explainability (SHAP, feature importance)
  ☐ Parcial, solo en rechazo
  ☐ No, modelo blackbox aceptable

→ Seleccionar: Si, full explainability

---

[VALIDACION COMPLETADA]

Architecture Feasibility: 88/100 ✓
Data Readiness: 95/100 ✓
Regulatory Compliance: 92/100 ✓

Esperando arquitectura generada...
```

**Luego muestra (Parte 3: Arquitectura Auto-Generada):**
```
[ARCHITECTURE PACKAGE - AUTO-GENERATED]

Solution Name:
"Real-time Credit Risk Prediction @ Onboarding"

TECH STACK RECOMENDADO:
- Azure Databricks (ML training & serving)
- Azure ML Endpoints (prediction API)
- Cosmos DB (decision logs & audit trail)
- Event Hub (onboarding events)
- Power BI (risk dashboard)

ESTIMATED CONSUMPTION:
- Monthly Executions: 50,000
- Prompt Tokens/Execution: 200
- Completion Tokens/Execution: 100
- Estimated Cost/Month: USD $850

DEPLOYMENT ROADMAP:
1. Prepare dataset (2 weeks)
   → Clean & validate 3-year historical data
   
2. Train base model (3 weeks)
   → Develop features, train on 80/20 split
   
3. Validate fairness & drift (2 weeks)
   → Fairness audits, performance monitoring
   
4. Integrate with onboarding (2 weeks)
   → API integration, load testing
   
5. UAT & Go-live (2 weeks)
   → User acceptance testing, runbooks

TOTAL TIMELINE: 11 weeks (2.5 months)

NEXT ACTIONS:
→ Contact Juan Ramirez (credit risk owner)
  Decide: consolidate with existing initiative or proceed independently?
  
→ Schedule technical deep-dive (4 hours)
  Data Science team + Architecture team
  
→ Proceed to formal Business Validation
  If approved: kickoff design in 2 weeks
```

**Narrative:**
> "Este es el tercero y más sofisticado escenario. El usuario propone un modelo de machine learning complejo.
>
> Detrás de cámaras:
> - El sistema detectó que esta idea es compleja (credibilidad de ML, regulatory risk, arquitectura)
> - Automáticamente activó validación con 3 agentes IA especializados:
>   * Agent 1: Pregunta sobre arquitectura (el usuario elige: API sync)
>   * Agent 2: Pregunta sobre datos (usuario: datos limpios, 3 años)
>   * Agent 3: Pregunta sobre regulación (usuario: full explainability)
>
> Con esas respuestas, en SEGUNDOS el sistema:
> - Generó stack tecnológico recomendado (Databricks, Azure ML, Cosmos)
> - Calculó costo mensual: USD 850
> - Generó roadmap detallado: 11 semanas
> - Sugirió contactos: Juan Ramirez (owner de iniciativa similar)
> - Recomendó próximos pasos
>
> Sin esto: Consulting externo para feasibility = 2 semanas + $50k+. Con esto: 2 minutos, automático, gratis.
>
> ESTO es lo que significa tomar decisiones rápidas con inteligencia."

---

## Post-Demo: Preguntas & Respuestas

**P: ¿Dónde se almacenan las ideas?**
R: Base de datos SQLite local (`data/aihub.db`). En producción: Azure SQL o Cosmos DB.

**P: ¿Cómo mejora si ingestamos más ideas?**
R: El catálogo crece, el matching se vuelve más inteligente. Machine Learning puede mejorar a futuro.

**P: ¿Las preguntas de agentes son customizables?**
R: Sí, se pueden agregar nuevas preguntas, criterios, agentes según dominio.

**P: ¿Integramos con Entra ID?**
R: Demo usa auth simple, pero está lista para integración Entra ID.

**P: ¿Cómo mide el impacto?**
R: Métricas: tiempo de intake (antes: 2h → 15 min), costo de arquitectura consultivo (antes: $50k → auto), coordinación (antes: informal → documentada).

**P: ¿Escalable?**
R: Sí, probado con 100+ ideas. Con agentes más sofisticados, puede llegar a 1000+.

---

## Notas Técnicas para Demo

### Si API Falla

```powershell
# Reiniciar backend
Kill-Process -Name "python" -ErrorAction SilentlyContinue
python -m uvicorn api.app.main:app --reload --port 8000
```

### Si BD está corrupta

```powershell
# Re-seed catálogo
cd scripts/
python seed-complete-demo.py
```

### Si necesita más ideas para mostrar

```powershell
# Las ideas están en scripts/seed-complete-demo.py
# Editar y agregar más casos antes de ejecutar
```

---

## Métricas Finales para Upper Management

**Muestra estas métricas al cierre:**

```
AIHUB - Impacto Demostrado

[VELOCIDAD]
- Intake manual: 2-3 horas → AIHUB: 15 minutos (8-12x más rápido)
- Arquitectura consultiva: 2 semanas → AIHUB: 2 minutos (1000x más rápido)
- Coordinación inter-team: emails + reuniones → AIHUB: automática

[PRECISIÓN]
- Detección de duplicados: 30% (manual) → 100% (automático)
- Contactos sugeridos: 0 (manual) → 5 por idea (automático)
- Recomendaciones técnicas: inconsistentes → consistentes

[COSTO]
- Overhead de intake por idea: $2,000 → $0 (automático)
- Ahorro en 10 ideas/año: $20,000
- Ahorro en 100 ideas/año: $200,000

[VISIBILIDAD]
- Catálogo de iniciativas: fragmentado → centralizado
- Contactos por tema: desconocidos → mapeados
- Roadmap: informal → documentado
```

---

## Links Útiles

- **Frontend:** http://localhost:5173
- **API Swagger:** http://localhost:8000/docs
- **BD:** `data/aihub.db`
- **Seed Script:** `scripts/seed-complete-demo.py`
- **Doc Guía:** `docs/PROMPTS_TOKEN_OPTIMIZATION_GUIDE.md`
