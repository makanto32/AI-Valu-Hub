# Demo Data - Ideas Persistentes

Este documento describe las 5 ideas de demostración que se han poblado en la base de datos SQLite para visualizar el flujo completo de AIHUB.

## Cómo Usar

Para ejecutar el script y poblar la base de datos:

```bash
python scripts/seed-demo-ideas.py
```

La base de datos se guardará en: `data/aihub.db`

---

## Ideas Creadas

### 1. 📝 [DRAFT] Automatización de Detección de Fraude en Transacciones Retail

**Estado:** Borrador  
**Etapa:** Idea Intake  
**Usuario:** Demo User

Una idea recién capturada que muestra cómo comienza el flujo:
- Propuesta inicial simple
- Sin validaciones aún
- Pendiente de evaluación

**Contexto:**
- Empresa: Contoso Financial Services
- Industria: Servicios financieros
- Riesgo: Low tolerance

---

### 2. ❓ [?] Optimización de Procesos KYC con Análisis de Documentos IA

**Estado:** Requiere Aclaracion  
**Etapa:** Business Validation  
**Usuario:** Demo User

Una idea que está en validación de negocio pero necesita más información:
- 2 preguntas de aclaración pendientes:
  - Volumen de transacciones diarias
  - Disponibilidad de datos históricos
- Score de negocio: 75/100
- Score de riesgo: 40/100

**Propósito:** Reducir tiempo de KYC de 2-3 días a máximo 2 horas

---

### 3. ✅ [OK] Chatbot de Soporte al Cliente con Comprensión Conversacional

**Estado:** Viable de Negocio  
**Etapa:** Business Validation (Completada)  
**Usuario:** Demo User

Una idea que pasó validación de negocio:
- Score de negocio: 82/100
- Score de riesgo: 35/100
- Recomendación: Proceder a validación técnica
- Impacto: Soporte 24/7, reducir carga de equipo en 50%

**Beneficios cuantitativos:**
- Reducir carga en equipo en 50%
- Disponibilidad 24/7
- Mejora CSAT en 20%

---

### 4. ✅ [OK] Análisis Predictivo de Riesgo de Crédito en Onboarding

**Estado:** Viable de Negocio (+ Validación Técnica Completada)  
**Etapa:** Technical Validation  
**Usuario:** Demo User

Una idea que completó TODO el ciclo de validación:

#### Validación Técnica:
- Feasibility: 88/100
- Integration Complexity: 65/100
- Security Risk: 25/100
- Data Readiness: 80/100
- Recomendación: Proceder a implementación

#### Arquitectura Propuesta:
Componentes:
- Event Hub (ingesta de eventos)
- Stream Analytics (procesamiento en tiempo real)
- Azure AI Services (evaluación de riesgo)
- Cosmos DB (almacenamiento y auditoría)

#### Consumo Estimado:
- 1.5M transacciones/mes
- Costo: $2,500/mes
- Latencia: < 100ms requerida

#### Riesgos Identificados:
- Latencia de base de datos compartida
- Costo si no se optimiza
- Cambios en formato de datos

---

### 5. ❌ [X] Automatización de Asesoría de Inversión Personalizada

**Estado:** Rechazada  
**Etapa:** Business Validation  
**Usuario:** Demo User

Una idea que fue **rechazada** por restricciones regulatorias:

**Razón del Rechazo:**
- Fase: Business
- Motivo: No alineado con estrategia actual. Prohibido automatizar decisiones de crédito sin supervisión humana en nuestro modelo de riesgo bajo.

**Por qué se muestra:**
- Demuestra el flujo completo de un rechazo
- Útil para entender decisiones de negocio
- Muestra cuándo se bloquean iniciativas por restricciones regulatorias

---

## Estructura de Datos

Cada idea contiene:

```
- Metadata
  - idea_id (UUID único)
  - tenant_id (contoso-demo)
  - owner_user_id y owner_display_name
  - Timestamps (created_at, updated_at)

- Contenido
  - title: Título de la idea
  - problem_statement: Descripción del problema
  - expected_value: Valor esperado
  - affected_users: Equipos/personas impactadas

- Idiomas
  - source_language: es
  - canonical_language: es
  - supported_languages: [es, en]

- Estado de Validación
  - status: draft | needs_clarification | business_viable | rejected
  - current_stage: idea_intake | business_validation | technical_validation
  - business_validation: Scores y recomendaciones
  - technical_validation: Feasibility, risks, etc.
  - architecture_package: Componentes y costos

- Evaluación
  - clarification_questions: Preguntas pendientes
  - clarification_interactions: Respuestas registradas
  - rejection: Razón si fue rechazada
  - quota_adjustments: Cuota de tokens por mes
```

---

## Contexto de Empresa (Tenant: contoso-demo)

**Contoso Financial Services**

**Prioridades Estratégicas:**
- Reducción de fraude
- Eficiencia operativa en onboarding
- Experiencia digital para clientes retail
- Cumplimiento regulatorio

**Dominios Prohibidos:**
- Asesoría de inversión automatizada sin supervisión
- Criptomonedas no reguladas
- Modelos de crédito sin explicabilidad

**Restricciones Regulatorias:**
- KYC (Know Your Customer)
- AML (Anti-Money Laundering)
- Protección de datos personales
- Trazabilidad de decisiones

---

## Cómo Usar en la Demostración

1. **Ejecutar el script:**
   ```bash
   python scripts/seed-demo-ideas.py
   ```

2. **Iniciar la aplicación:**
   ```bash
   # Terminal 1: Backend
   cd api
   python -m uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

3. **Acceder a la demo:**
   - URL: http://localhost:5173
   - Tenant: contoso-demo
   - Usuario demo: cualquier usuario (auth en demo mode)

4. **Explorar cada idea:**
   - Vista de borrador (etapa inicial)
   - Flujo de aclaraciones
   - Validación de negocio con scores
   - Validación técnica con arquitectura
   - Rechazo con justificación

---

## Notas

- Las ideas se crean con fechas distribuidas en los últimos 21 días para simular un flujo realista
- Cada idea tiene contexto de empresa snapshot adjunto
- Los scores y recomendaciones son realistas para una institución financiera
- El flujo demuestra: intake → aclaraciones → validación → rechazo/aprobación
