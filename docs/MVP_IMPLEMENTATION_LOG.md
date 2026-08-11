# MVP Implementation Log

Este documento consolida el avance funcional y tecnico por MVP.
Se actualiza en cada iteracion para mantener trazabilidad de lo implementado.

## Estado general
- MVP1: completado
- MVP2: completado en entorno local (pendiente publicacion en ACR/Container Apps)
- MVP3: pendiente
- MVP4: pendiente
- MVP5: pendiente

---

## MVP1 - Implementado

### Objetivo
Habilitar captura de ideas y validacion inicial de negocio con estado por caso.

### Alcance implementado
- Idea intake con formulario web.
- Context Engine base por tenant (carga/consulta de contexto).
- Business validation con scores de valor/riesgo y recomendaciones.
- Flujo de aclaraciones para ideas con informacion insuficiente.
- Estado de caso (etapa y estado) con trazabilidad de rechazo por fase.
- Autenticacion demo por bearer token.
- Aislamiento por usuario en listado de ideas (mis ideas).
- Base multilenguaje (es/en/pt).

### Endpoints clave MVP1
- `POST /auth/login`
- `GET /auth/me`
- `GET /context/{tenant_id}`
- `PUT /context/{tenant_id}`
- `PUT /admin/context/{tenant_id}`
- `POST /admin/context/{tenant_id}/files`
- `POST /ideas/intake`
- `GET /ideas/mine`
- `GET /ideas/{idea_id}`
- `GET /ideas/{idea_id}/clarification-questions`
- `POST /ideas/{idea_id}/clarify`

### Integracion en UI MVP1
- Login demo.
- Gestion de contexto (admin).
- Formulario de nueva idea.
- Vista Mis ideas con detalle de scores, supuestos, preguntas y rechazo.

---

## MVP2 - Implementado (local)

### Objetivo
Extender MVP1 para completar flujo negocio-tecnico con validacion tecnica explicita y generacion de arquitectura.

### Alcance implementado
- Persistencia real de estado en DB (SQLite) con migraciones backward-compatible.
- Persistencia de metadata de archivos de contexto.
- Blob storage con soporte Azure y fallback local.
- Validacion tecnica explicita por endpoint dedicado.
- Generacion de Architecture Package por idea.
- Response Composer (mensaje final + siguientes acciones).
- Snapshot de contexto por idea (auditoria de evaluacion).
- Score breakdown en validacion de negocio (explicabilidad).
- Endpoint de reevaluacion de negocio con contexto actual.
- Deteccion de idea duplicada en analisis por tenant.
- Preguntas de aclaracion con respuestas sugeridas seleccionables en UI.

### Endpoints agregados MVP2
- `POST /ideas/{idea_id}/technical-validate`
- `POST /ideas/{idea_id}/architecture-package`
- `POST /ideas/{idea_id}/reevaluate-business`

### Integracion con MVP1
- Reutiliza la salida de business validation de MVP1 como gate de entrada a fase tecnica.
- Mantiene auth, contexto tenant y aislamiento por usuario sin cambios de contrato para MVP1.
- Conserva flujo de aclaraciones y lo mejora con sugerencias predefinidas.
- Mantiene lista de ideas y agrega artefactos tecnicos en el mismo objeto de caso.

### Integracion en UI MVP2
- Accion para ejecutar validacion tecnica desde ideas viables.
- Accion para generar paquete de arquitectura.
- Visualizacion de resultado tecnico (recomendacion y score).
- Visualizacion de resumen de arquitectura y respuesta compuesta.
- Botones para usar respuestas sugeridas en aclaraciones.
- Configuracion de API por variable `VITE_API_URL` para pruebas locales.

### Estado de despliegue
- Implementado y validado localmente.
- Pendiente push de imagenes a ACR.
- Pendiente update de Container Apps al tag MVP2.

---

## MVP3 - Pendiente

### Objetivo esperado
Company Context Engine avanzado con quick setup y carga documental empresarial.

### Backlog inicial
- Ingestion documental estructurada (PDF/Word/PPT/MD).
- Normalizacion de entidades de negocio.
- Indexacion semantica y retrieval contextual.
- Enriquecimiento progresivo de contexto por tenant.

### Criterios de cierre (propuestos)
- Onboarding de tenant guiado.
- Contexto utilizable por agentes en evaluacion de ideas.
- Evidencia de mejora en precision de recomendaciones.

---

## MVP4 - Pendiente

### Objetivo esperado
Admin Center para trazabilidad, valor y FinOps.

### Backlog inicial
- KPIs de pipeline y valor.
- Trazabilidad de decisiones por caso.
- Telemetria de tokens/costo por etapa, usuario y tenant.
- Governance de prompts/versiones.

---

## MVP5 - Pendiente

### Objetivo esperado
Empaquetado multi-tenant y despliegue simplificado por cliente.

### Backlog inicial
- IaC completo por cliente (infra + apps + secretos).
- Provisionamiento automatizado con ACR habilitado.
- Guia de instalacion y operacion por tenant.
- Templates de release por MVP para GitHub.

---

## Registro de actualizacion
- 2026-06-01: Consolidacion MVP1 + MVP2 y estructura base para MVP3/MVP4/MVP5.
