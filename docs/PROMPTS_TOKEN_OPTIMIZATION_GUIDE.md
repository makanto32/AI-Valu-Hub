# Prompt Guide: Token Optimization (ES/EN)

## 1) Version en Espanol

### Formato de campos para "Nueva idea" (alineado al formulario actual)
Campos esperados:
- title
- problem_statement
- expected_value
- affected_users (lista separada por coma)
- source_language (es|en|pt)

Nota:
- tenant_id lo toma la aplicacion desde la sesion autenticada, no se captura manualmente en el prompt.

Plantilla recomendada (token-efficient):
```text
title: <3 a 120 caracteres, concreto>
problem_statement: <10 a 450 caracteres, problema observable y actual>
expected_value: <5 a 300 caracteres, impacto medible>
affected_users: <area1, area2, area3>
source_language: <es|en|pt>
```

Ejemplo optimo (ES):
```text
title: Deteccion temprana de fraude en onboarding digital
problem_statement: El equipo de riesgo revisa manualmente demasiados casos en onboarding, generando atrasos y falsos positivos.
expected_value: Reducir 25% el tiempo de revision y 15% los falsos positivos en 8 semanas de piloto.
affected_users: riesgo, operaciones, cumplimiento
source_language: es
```

Ejemplo deficiente (ES):
```text
title: IA banco
problem_statement: Queremos mejorar todo lo del onboarding, fraude y eficiencia cuanto antes.
expected_value: Que todo sea mejor y mas rapido.
affected_users: todos
source_language: es
```

Analisis rapido (formato de campos):
1. title:
- Optimo: especifico y enfocado en un problema.
- Deficiente: ambiguo y sin alcance.
2. problem_statement:
- Optimo: describe situacion actual y dolor operativo.
- Deficiente: generalista, sin contexto util.
3. expected_value:
- Optimo: incluye metricas y horizonte temporal.
- Deficiente: no medible.
4. affected_users:
- Optimo: equipos concretos.
- Deficiente: "todos" no ayuda a priorizar.
5. source_language:
- Optimo y deficiente: valido si usa es|en|pt; la diferencia real esta en calidad de contenido.

### Prompt optimo (token-efficient)
Actua como analista de innovacion empresarial. Evalua esta idea y responde en maximo 220 palabras.

Contexto minimo:
- Empresa: banco retail en Latam
- Objetivo: reducir fraude en onboarding digital
- Restricciones: cumplimiento KYC/AML, sin cambiar core bancario en fase inicial
- Horizonte: piloto en 8 semanas

Idea:
"Aplicar scoring de riesgo con senales de comportamiento y validacion documental asistida por IA para priorizar casos sospechosos y reducir revision manual."

Entrega exactamente en este formato:
1) Resumen de la idea (1 frase)
2) Valor esperado (3 bullets)
3) Riesgos clave (3 bullets)
4) Viabilidad tecnica (Alta/Media/Baja + 1 frase)
5) Proximo paso recomendado (1 accion concreta)

### Prompt deficiente
Necesito que analices una idea que tenemos para mejorar muchos procesos en el banco, sobre IA, fraude, clientes, operacion, tiempos y transformacion digital. Quiero un analisis muy completo y detallado con todo lo que creas relevante: vision estrategica, tactica, operativa, tecnologica, regulatoria, roadmap, costos, riesgos, posibles integraciones, beneficios, impactos, quick wins, largo plazo, roles, metricas, KPIs, gobierno, arquitectura y cualquier otro tema que consideres. Puedes extenderte todo lo que necesites y usar el formato que prefieras.

### Analisis comparativo
1. Claridad de objetivo:
- Optimo: define rol, contexto, limites y salida exacta.
- Deficiente: pide "todo", sin foco ni criterio de priorizacion.

2. Consumo de tokens:
- Optimo: restringe longitud y estructura, reduce expansion innecesaria.
- Deficiente: invita a respuestas largas y dispersas, mayor costo.

3. Calidad operativa:
- Optimo: produce salida accionable y comparable entre ideas.
- Deficiente: salida variable, dificil de estandarizar o automatizar.

4. Tiempo de iteracion:
- Optimo: mas rapido para revisar y decidir siguiente paso.
- Deficiente: mas lento de leer, extraer y convertir en accion.

5. Riesgo de alucinacion:
- Optimo: menos espacio para inventar por falta de alcance.
- Deficiente: al abrir demasiados frentes, aumenta suposiciones.

---

## 2) DEMO LIVE: Ejemplos de Ideas Ingresadas en Tiempo Real

Esta sección muestra casos de demostración que pueden ejecutarse durante una presentación a Upper Management.

### Escenario 1: Idea Similar a Iniciativa en PRODUCCIÓN (Matching + Contacto)

**Contexto:**
El usuario ingresa una idea que es muy similar a un sistema ya desplegado en producción. 
El sistema detecta la similitud, sugiere colaboración y proporciona contacto del propietario de la iniciativa actual.

**Idea Ingresada:**
```
Titulo: Deteccion de Fraude con Grafos de Comportamiento
Problema: Los patrones de fraude evolucionan rapidamente. Nuestro sistema actual detecta casos pero genera falsos positivos en 15-20% de transacciones. Necesitamos analisis de grafos de conexion para detectar fraude en anillo.
Valor esperado: Reducir falsos positivos 40%, detectar fraude organizado en tiempo real.
Usuarios afectados: seguridad, operaciones, cumplimiento
source_language: es
```

**Respuesta del Sistema:**

```
[MATCHING RESULT]

Idea detectada: "Deteccion de Fraude con Grafos de Comportamiento" 
Score de similitud: 78%

INICIATIVA RELACIONADA ENCONTRADA:
✓ Titulo: Fraud Detection Platform v2.0
  Estado: EN PRODUCCION (desplegada hace 120 dias)
  Etapa: Deployed & Operacional
  Similitud: 78% - Resuelve problema muy similar con tecnologias complementarias

RECOMENDACION:
⚠️  Esta idea EXTIENDE o MEJORA una solucion ya en produccion.
Evitar duplicacion de esfuerzo. CONTACTAR con propietario actual.

CONTACTO RESPONSABLE:
📧 Carlos Mendez, Fraud Detection Lead
   Email: carlos.mendez@contoso.com
   Departamento: Risk & Compliance
   Telefono: +34-91-555-0001

ACCIONES RECOMENDADAS:
1. Agendar reunion con Carlos Mendez para presentar mejoras propuestas
2. Evaluar integracion de analisis de grafos en plataforma existente
3. Considerar es enhancement vs. nueva iniciativa paralela
4. Documentar decision de colaboracion o independencia

SIGUIENTE PASO:
→ Contactar a Carlos antes de proceder a validacion formal
→ Si viable colaborar: incorporar como roadmap de Platform v2.1
→ Si es independiente: justificar por que no reutilizar plataforma existente
```

**Proposito para Demo:**
Demuestra que el sistema DETECTA duplicacion, SUGIERE CONTACTOS y PREVIENE desperdicio de recursos.

---

### Escenario 2: Idea Complementaria a Iniciativa en DESARROLLO (Coordinacion)

**Contexto:**
El usuario ingresa una idea que EXTIENDE funcionalidades de un proyecto en desarrollo. 
El sistema recomienda coordinacion temprana para incorporar requisitos.

**Idea Ingresada:**
```
Titulo: Validacion Biometrica en Onboarding Digital
Problema: El KYC actual solo valida documentos. Regulador requiere validacion de identidad mas fuerte. Necesitamos agregar verificacion de rostro y huellas.
Valor esperado: Cumplimiento AML mejorado, precisión de identificacion 99.9%, reducir fraude de identidad 60%.
Usuarios afectados: onboarding, compliance, clientes
source_language: es
```

**Respuesta del Sistema:**

```
[MATCHING RESULT]

Idea detectada: "Validacion Biometrica en Onboarding Digital"
Score de similitud: 65%

INICIATIVA RELACIONADA ENCONTRADA:
⏳ Titulo: KYC Document Automation v1.0
   Estado: EN DESARROLLO (etapa: technical_validation)
   Etapa: 65% completada (estimado)
   Similitud: 65% - Complementaria con plataforma en desarrollo

RECOMENDACION:
ℹ️  Esta idea COMPLEMENTA iniciativa actual en desarrollo.
Oportunidad de incorporar requisitos ANTES de go-live.

CONTACTO RESPONSABLE:
📧 Rosa Garcia, KYC Program Manager
   Email: rosa.garcia@contoso.com
   Departamento: Onboarding
   Telefono: +34-91-555-0002

   Soporte tecnico:
   📧 Sofia Gonzalez, Business Analyst
      Email: sofia.gonzalez@contoso.com

ACCIONES RECOMENDADAS:
1. Incluir biometria en requerimientos de KYC v1.0 ANTES de testing
2. Coordinar con equipo de desarrollo para evaluacion de effort
3. Decidir: Feature en v1.0 o v1.1 post-deployment
4. Validar compatibilidad con proveedores de validacion biometrica seleccionados

TIMELINE IMPACTO:
- Si se integra en v1.0: +2-3 semanas de desarrollo, pero go-live unico
- Si es v1.1: Go-live v1.0 en plazo, v1.1 con biometria en +6 semanas

SIGUIENTE PASO:
→ Contactar a Rosa Garcia esta semana
→ Realizar tech feasibility assessment (estimado: 4 horas)
→ Decidir estrategia de incorporacion
→ Si procede: integrar en backlog/roadmap oficial
```

**Proposito para Demo:**
Demuestra que el sistema COORDINA iniciativas paralelas, EVITA duplicacion y ACELERA value-time.

---

### Escenario 3: Idea con Agentes (Validacion Tecnica Compleja)

**Contexto:**
El usuario ingresa una idea que requiere validacion TECNICA compleja con agentes IA.
El sistema detecta que necesita profundidad y activa validacion asistida por agentes.

**Idea Ingresada:**
```
Titulo: Analisis Predictivo de Riesgo de Credito en Onboarding
Problema: Aplicamos scoring de riesgo POST-onboarding, muy tarde. Necesitamos scoring EN onboarding para aprobar mejor casos y rechazar riesgosos temprano.
Valor esperado: Mejora de calidad de cartera 25%, reduccion de charge-offs, optimizacion de aprovisionamiento.
Usuarios afectados: credit-team, onboarding, risk-management
source_language: es
```

**Respuesta del Sistema (con orquestación de Agentes):**

```
[MATCHING RESULT]

Idea detectada: "Analisis Predictivo de Riesgo de Credito"
Score de similitud: 42% (baja) → Idea potencialmente NUEVA

Iniciativa relacionada encontrada:
⏳ Titulo: Predictive Credit Risk Engine
   Estado: EN FINANCIAMIENTO (espera presupuesto Q3 2026)
   Etapa: business_validation
   Similitud: 42% - Solapamiento parcial pero diferente timing y scope

RECOMENDACION:
⚠️  Iniciativa similar existe pero en fase EARLY. Evaluar consolidacion de propuestas.

CONTACTO RESPONSABLE (Iniciativa en Financiamiento):
📧 Juan Ramirez, Credit Risk Officer
   Email: juan.ramirez@contoso.com
   Departamento: Risk Management

VALIDACION TECNICA REQUERIDA:
→ Complejidad ALTA detectada. Activando validacion con Agentes IA...

[AGENT VALIDATION PHASE - AUTOMATED]

Agent 1 - Architecture Reviewer:
  Pregunta: ¿Integrar con Core Banking System durante onboarding?
  Opciones sugeridas: 
    - REST API sync (latencia < 200ms)
    - Async queue con enriquecimiento (latencia 2-5seg)
    - Batch pre-compute (recompute cada 4h)

Agent 2 - Data Science Reviewer:
  Pregunta: ¿Datos historicos disponibles para entrenar modelo?
  Opciones sugeridas:
    - Si, 3+ años con outcome labels
    - Si, 2 anos pero labels incompletos
    - Parcialmente, requiere data cleaning
    - No, necesitaria synthetic data o transfer learning

Agent 3 - Risk & Compliance Reviewer:
  Pregunta: ¿Modelo requiere explicabilidad regulatoria?
  Contexto: Banco con risk_tolerance=LOW
  Opciones sugeridas:
    - Si, full explainability (SHAP, feature importance)
    - Parcial, explicabilidad en rechazo
    - No requiere, modelo blackbox aceptable

RESPUESTAS ESPERADAS DE USUARIO (live demo):
1. "REST API sync" - integración en tiempo real
2. "Si, 3+ anos" - datos limpios disponibles
3. "Si, full explainability" - requisito de cumplimiento

RESULTADO DE VALIDACION:
✓ Arquitectura: VIABLE - 88/100 feasibility
✓ Data: LISTA - 3 anos historicos, etiquetado
✓ Regulatory: FEASIBLE - explainability requerida, implementable

NEXT PHASE: Technical Architecture Package (auto-generated)

[ARCHITECTURE SUGGESTION]

Solution Name: Real-time Credit Risk Prediction @ Onboarding
Component Stack:
  - Azure Databricks (model training & serving)
  - Azure ML Endpoints (API para predicción)
  - Cosmos DB (decisions log & audit trail)
  - Event Hub (ingesta de eventos onboarding)
  - Power BI (dashboard para risk team)

Estimated Consumption:
  - Monthly executions: 50,000
  - Prompt tokens per execution: 200
  - Completion tokens per execution: 100
  - Estimated monthly cost: USD $850

Deployment Steps:
  1. Preparar dataset historico (2 semanas)
  2. Entrenar modelo base (3 semanas)
  3. Validar fairness & drift (2 semanas)
  4. Integrar con onboarding flow (2 semanas)
  5. UAT & go-live (2 semanas)
  Timeline: 11 semanas (2.5 meses)

ACCIONES SIGUIENTES:
→ Contactar a Juan Ramirez para discutir consolidacion con iniciativa en financiamiento
→ Si se consolidan: combinar propuestas para presupuesto Q3 2026
→ Si independiente: evaluar timeline (11 semanas) vs presupuesto actual
→ Programar sesion de aclaración técnica con Data Science team
→ Proceder a validación formal de negocio
```

**Proposito para Demo:**
Demuestra que el sistema:
- Detecta complejidad tecnica AUTOMATICAMENTE
- Activa validacion ASISTIDA por agentes IA (no es manual)
- Sugiere arquitectura y costos AUTO-GENERADOS
- Proporciona roadmap detallado y contactos

---

## 3) Script de Ejecución para Demo (Upper Management)

### Preparacion Previa (5 minutos antes de demo)
```bash
# Terminal 1: Backend
cd api/
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend/
npm run dev

# Terminal 3: (opcional) Mostrar BD populated
sqlite3 data/aihub.db "SELECT COUNT(*) FROM ideas; SELECT COUNT(*) FROM company_contexts;"
```

### Flujo de Demostración (15 minutos)

**Minuto 0-2: Contexto**
- "Esta es AIHUB - nuestro motor de intake de ideas IA-first"
- "Demuestra proceso COMPLETO: captura → matching → validación"
- Mostrar 3 scenarios: duplicado en prod, complementaria en dev, requiere agentes

**Minuto 2-5: Scenario 1 (Duplicado en Producción)**
1. Navegar a "Nueva Idea"
2. Ingresar datos de "Idea Similar a Iniciativa en Producción"
3. Presionar "Validar y Matchear"
4. Sistema detecta y muestra iniciativa similar + contacto (Carlos Mendez)
5. "Miren como el sistema EVITA duplicacion antes de gastar recursos"

**Minuto 5-10: Scenario 2 (Complementaria en Desarrollo)**
1. Ingresar segunda idea (Validacion Biometrica)
2. Sistema detecta iniciativa en desarrollo (KYC Automation)
3. Muestra contacto (Rosa Garcia) y timeline de impacto
4. "El sistema COORDINA iniciativas paralelas automáticamente"

**Minuto 10-15: Scenario 3 (Con Agentes)**
1. Ingresar tercera idea (Credit Risk Prediction)
2. Sistema activa VALIDACION CON AGENTES
3. Mostrar preguntas de clarificación de agentes
4. Responder preguntas (demo: "API sync", "3+ years", "Full explainability")
5. Sistema genera arquitectura + costo + timeline
6. "Los agentes validan complejidad TECNICA en segundos"

**Minuto 15: Cierre**
- "Hemos visto intake end-to-end: matching → contactos → validación técnica con agentes"
- "Todo automatizado, sin admin manual"
- Preguntas de audience

---

## 4) Metricas de Éxito (para Upper Management)

Mostrar al final de la demo:

```
AIHUB - Métricas de Valor Demostrado

[EFICIENCIA DE INTAKE]
- Tiempo promedio por idea: 15 min (antes: 2 horas manual)
- Detección de duplicados: 100% automatizada (antes: 30% encontraban)
- Contactos sugeridos auto: 5 por idea (antes: 0, búsqueda manual)

[VALIDACION TECNICA]
- Preguntas de agentes por idea: 3-5 (evita 10-15 reuniones)
- Arquitectura auto-generada: 5 min (antes: 2 semanas de consulting)
- Costo estimado calculado: instant (antes: N/A, no existía)

[GOBERNAN ZA]
- Catalogo de iniciativas: on-demand (antes: Excel + email)
- Contactos por iniciativa: catalogado (antes: scattered emails)
- Roadmap visibility: 100% (antes: fragmentado)

[BUSINESS IMPACT]
- Ideas viables identificadas: semanas vs months
- Evitar falsa duplicacion: $500k+ en overhead reducido
- Accelerate time-to-value: 60% faster idea-to-deployment cycle
```

---

## 2) English Version

### "New Idea" field format (aligned with current form)
Expected fields:
- title
- problem_statement
- expected_value
- affected_users (comma-separated list)
- source_language (es|en|pt)

Note:
- tenant_id is taken from the authenticated session by the app; it is not manually entered in the prompt.

Recommended template (token-efficient):
```text
title: <3 to 120 chars, specific>
problem_statement: <10 to 450 chars, observable current pain>
expected_value: <5 to 300 chars, measurable outcome>
affected_users: <team1, team2, team3>
source_language: <es|en|pt>
```

Optimal example (EN):
```text
title: Early fraud detection in digital onboarding
problem_statement: The risk team manually reviews too many onboarding cases, causing delays and false positives.
expected_value: Reduce review time by 25% and false positives by 15% in an 8-week pilot.
affected_users: risk, operations, compliance
source_language: en
```

Poor example (EN):
```text
title: AI for bank
problem_statement: We want to improve everything in onboarding, fraud, and efficiency as soon as possible.
expected_value: Make everything better and faster.
affected_users: everyone
source_language: en
```

Quick analysis (field format):
1. title:
- Optimal: specific and scoped.
- Poor: vague and broad.
2. problem_statement:
- Optimal: concrete current-state pain.
- Poor: generic, low signal.
3. expected_value:
- Optimal: measurable target plus timeline.
- Poor: not measurable.
4. affected_users:
- Optimal: concrete teams.
- Poor: "everyone" prevents prioritization.
5. source_language:
- Both can be valid if using es|en|pt; the real difference is content quality.

### Optimal prompt (token-efficient)
Act as an enterprise innovation analyst. Evaluate this idea and answer in no more than 220 words.

Minimal context:
- Company: retail bank in LatAm
- Goal: reduce fraud in digital onboarding
- Constraints: KYC/AML compliance, no core banking replacement in initial phase
- Timeline: 8-week pilot

Idea:
"Use AI-assisted risk scoring with behavioral signals and document validation to prioritize suspicious cases and reduce manual review workload."

Return exactly in this format:
1) Idea summary (1 sentence)
2) Expected value (3 bullets)
3) Key risks (3 bullets)
4) Technical feasibility (High/Medium/Low + 1 sentence)
5) Recommended next step (1 concrete action)

### Poor prompt
Please analyze an idea we have to improve many banking processes related to AI, fraud, customer experience, operations, speed, and digital transformation. I want a very complete and detailed analysis covering everything you think is relevant: strategic vision, tactical and operational planning, technology, regulatory aspects, roadmap, costs, risks, integrations, benefits, impacts, quick wins, long-term opportunities, roles, metrics, KPIs, governance, architecture, and anything else you can think of. Feel free to be as long as needed and use any format you prefer.

### Comparative analysis
1. Objective clarity:
- Optimal: clear role, context, boundaries, and output format.
- Poor: asks for "everything," with no prioritization criteria.

2. Token usage:
- Optimal: length cap and fixed structure prevent unnecessary expansion.
- Poor: encourages long, unfocused output and higher cost.

3. Operational quality:
- Optimal: actionable and easy to compare across ideas.
- Poor: inconsistent output, hard to standardize or automate.

4. Iteration speed:
- Optimal: faster to review and decide next actions.
- Poor: slower to read, extract, and operationalize.

5. Hallucination risk:
- Optimal: less room for unsupported assumptions.
- Poor: broader scope increases speculative content.

---

## 3) Demo Examples for UI "New Idea" (EN/ES/PT)

Use these examples directly in the UI form with this exact field structure:
- title
- problem_statement
- expected_value
- affected_users
- source_language

### A. Examples likely to pass business viability

#### A1) English (viable)
```text
title: AI-assisted KYC anomaly triage for digital onboarding
problem_statement: The risk team manually reviews all onboarding alerts, creating long queues and inconsistent decisions during peak periods.
expected_value: Reduce manual review time by 30% and false positives by 18% in a 10-week pilot while keeping KYC/AML controls.
affected_users: risk, operations, compliance
source_language: en
```

#### A2) Espanol (viable)
```text
title: Priorizacion inteligente de alertas de fraude en onboarding
problem_statement: En onboarding digital, el equipo de riesgo revisa alertas de forma manual y tarda demasiado en resolver casos de bajo riesgo.
expected_value: Reducir 28% el tiempo promedio de revision y 15% los falsos positivos en 2 meses, manteniendo controles KYC.
affected_users: riesgo, operaciones, cumplimiento
source_language: es
```

#### A3) Portugues (viable)
```text
title: Priorizacao de alertas de fraude no onboarding digital
problem_statement: O time de risco analisa alertas manualmente no onboarding, com alto volume e baixa padronizacao de decisao.
expected_value: Reduzir em 25% o tempo de analise e em 12% os falsos positivos em 8 semanas, sem reduzir controles de compliance.
affected_users: risco, operacoes, compliance
source_language: pt
```

### B. Examples likely to require more information (clarification)

#### B1) English (needs more info)
```text
title: Improve onboarding quality with AI recommendations
problem_statement: We think onboarding could be better with AI guidance, but we still do not know which cases should be prioritized first.
expected_value: Better performance and faster reviews, to be defined after initial exploration.
affected_users: risk, operations
source_language: en
```

#### B2) Espanol (requiere mas informacion)
```text
title: Mejorar decisiones de onboarding con apoyo de IA
problem_statement: Queremos apoyar al equipo con IA en onboarding, pero aun no tenemos claro que reglas, datos y umbrales se deben usar.
expected_value: Mejorar tiempos y calidad de decision, pendiente definir metrica concreta y alcance por canal.
affected_users: riesgo, operaciones
source_language: es
```

#### B3) Portugues (requer mais informacao)
```text
title: Apoio de IA para decisao em onboarding
problem_statement: Existe interesse em usar IA no onboarding, mas ainda ha duvida sobre dados disponiveis, criterios de priorizacao e controles.
expected_value: Ganho de eficiencia e melhor qualidade de analise, com metas a definir apos levantamento inicial.
affected_users: risco, operacoes
source_language: pt
```

### Practical notes for demo behavior
1. Viable examples include clearer metrics, timeline, and regulated context (KYC/compliance), which usually improves business viability scoring.
2. Clarification examples keep real business intent but leave key evidence open (exact KPI baseline, thresholds, or data readiness), so they are better candidates for "needs more information" in demo flows.
