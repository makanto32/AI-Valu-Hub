# Arquitectura propuesta: AI Use Case Factory con Company Context Engine

## 1. Proposito del documento
Este documento actualiza la arquitectura de referencia para una plataforma agentica que captura ideas de usuarios de negocio, valida su viabilidad, habilita una revision tecnica posterior, genera un paquete de arquitectura y permite dar seguimiento al valor generado cuando las ideas llegan a piloto o produccion.

El cambio principal es incorporar un **Company Context Engine** como componente central para que cada cliente pueda desplegar la solucion en su propio ambiente de Azure, cargar o descubrir su contexto empresarial y personalizar la experiencia sin modificar codigo. La solucion tambien debe soportar interacciones multilenguaje para usuarios de negocio, tecnicos y administradores.

## 2. Vision de producto
La solucion funciona como una **AI Use Case Factory**: un acelerador que convierte ideas dispersas en casos de uso trazables, evaluados, priorizados, tecnicamente validados y conectados con valor real de negocio.

La experiencia del usuario debe sentirse como un solo copiloto conversacional, aunque internamente existan agentes especializados, gates formales, contexto del cliente, evaluadores, telemetria, gobierno de prompts y medicion de valor.

## 3. Principios de diseno
1. Un solo copiloto conversacional para el usuario; multiples agentes especializados por debajo.
2. Company Context Engine como fuente de adaptacion por cliente/tenant.
3. Contexto minimo inicial y enriquecimiento progresivo, evitando formularios largos obligatorios.
4. Separacion estricta entre usuario de negocio, usuario tecnico y administrador.
5. Estado del caso de uso como fuente de verdad, no solo historial conversacional.
6. Soporte multilenguaje con deteccion de idioma, normalizacion interna y respuesta en el idioma del usuario.
7. Salidas estructuradas con JSON/Pydantic para evaluacion, auditabilidad y reduccion de sesgos.
8. Gates formales entre etapas: idea, viabilidad de negocio, validacion tecnica, arquitectura, piloto, produccion y valor realizado.
9. Prompts versionados y gobernados, no quemados en codigo.
10. Telemetria obligatoria por agente, prompt, modelo, usuario, etapa, tenant y caso de uso.
11. Empaquetamiento cloud-native para despliegue automatizado en Azure Container Apps.

## 4. Arquitectura logica actualizada

![Arquitectura logica con Company Context Engine](/mnt/data/architecture_images/company_context_architecture.png)

### Componentes principales

| Componente | Tecnologia sugerida | Responsabilidad |
|---|---|---|
| Web App | React + Vite | Interfaz multilenguaje para usuarios de negocio, tecnicos y administradores |
| API | Python FastAPI | Endpoints, autenticacion, autorizacion, orquestacion y telemetria |
| Hosting | Azure Container Apps | Despliegue serverless de frontend, API y workers |
| Agent Runtime | Microsoft Foundry Agent Service | Gestion de agentes, herramientas, instrucciones y conocimiento |
| LLM | Azure OpenAI / modelos en Foundry | Razonamiento, evaluacion, resumen y composicion de respuestas |
| Company Context Engine | Python services + agentes + RAG | Construccion y recuperacion del contexto especifico de cada cliente |
| State Store | Cosmos DB o PostgreSQL | TenantProfile, IdeaCase, decisiones, gates, auditoria y metricas |
| Blob Storage | Azure Blob Storage | Documentos fuente, adjuntos, evidencias, exports y paquetes generados |
| Semantic Search | Azure AI Search | Recuperacion semantica e hibrida sobre conocimiento del cliente |
| Observability | Application Insights + Log Analytics | Tokens, costo, latencia, errores, calidad, trazas y evaluaciones |
| Admin BI | Power BI o Microsoft Fabric | Pipeline, valor, consumo, ROI y gobierno de prompts |
| Secrets | Azure Key Vault | Claves, endpoints, secretos, configuracion sensible |

## 5. Company Context Engine
El **Company Context Engine** es el componente que permite que la herramienta sea reusable para multiples clientes. Su responsabilidad es convertir informacion empresarial dispersa en un contexto operacional util para los agentes.

### 5.1 Objetivos
- Personalizar las respuestas por industria, pais, estrategia, procesos, stack tecnologico y restricciones.
- Reducir dependencia de formularios extensos.
- Mantener contexto versionado, auditable y actualizable.
- Evitar que los agentes usen todo el contexto siempre; solo deben recibir el contexto relevante por etapa.
- Habilitar despliegues por cliente con configuracion independiente.

### 5.2 Modos de captura de contexto
| Modo | Uso | Descripcion |
|---|---|---|
| Quick Start | Demo o MVP | Solo se piden datos minimos: empresa, industria, pais, unidades, stack principal |
| Guided Setup | Cliente nuevo | Formulario corto + preguntas guiadas por un Discovery Agent |
| Enterprise Bootstrap | Cliente enterprise | Carga de documentos, arquitecturas, politicas, OKRs, roadmaps y presentaciones |
| Progressive Enrichment | Uso continuo | El contexto se enriquece conforme los usuarios interactuan y se validan ideas |

### 5.3 Subcomponentes
| Subcomponente | Responsabilidad |
|---|---|
| Tenant Onboarding Service | Crea tenant, configuracion, idioma por defecto y parametros de despliegue |
| Discovery Agent | Entrevista al cliente para completar informacion critica faltante |
| Document Ingestion Worker | Extrae contenido de PDF, Word, PPT, Markdown y otros adjuntos |
| Context Normalizer | Convierte contenido en entidades estructuradas: objetivos, capacidades, sistemas, riesgos |
| Knowledge Indexer | Publica documentos y fragmentos al indice de Azure AI Search |
| Context Retriever | Selecciona contexto relevante por rol, etapa, idioma e idea |
| Readiness Scorer | Calcula madurez de negocio, datos, IA, seguridad y nube |
| Context Governance | Versiona, aprueba, retira o corrige contexto usado por los agentes |

### 5.4 TenantProfile sugerido
```json
{
  "tenant_id": "uuid",
  "company_name": "",
  "default_language": "es",
  "supported_languages": ["es", "en", "pt"],
  "industry": "",
  "country": "",
  "business_units": [],
  "strategic_goals": [],
  "business_capabilities": [],
  "key_processes": [],
  "technology_stack": [],
  "data_platforms": [],
  "security_constraints": [],
  "compliance_requirements": [],
  "ai_readiness": {
    "business_maturity": 0,
    "data_maturity": 0,
    "cloud_maturity": 0,
    "security_maturity": 0
  },
  "glossary": {
    "preferred_terms": [],
    "forbidden_terms": [],
    "domain_acronyms": []
  },
  "context_versions": []
}
```

## 6. Soporte multilenguaje
El sistema debe permitir que un usuario describa ideas, preguntas tecnicas o decisiones administrativas en diferentes idiomas sin romper el estado del caso ni la trazabilidad.

### 6.1 Principios multilenguaje
- Detectar idioma por mensaje y conservar el idioma original.
- Responder en el idioma del usuario, salvo que el tenant o el caso indique otra preferencia.
- Mantener campos estructurados normalizados en un idioma canonico interno configurable, por ejemplo ingles o espanol.
- Guardar tanto el texto original como el resumen normalizado.
- Usar embeddings multilenguaje o una estrategia de indice que soporte busquedas cross-language.
- Mantener un glosario por tenant para siglas, nombres de sistemas, terminos internos y traducciones preferidas.

### 6.2 Language Layer
| Funcion | Descripcion |
|---|---|
| Language Detection | Detecta idioma del mensaje y confianza |
| Locale Resolver | Define idioma de respuesta considerando usuario, tenant y caso |
| Canonicalization | Normaliza resumen, requisitos y entidades a idioma canonico |
| Terminology Control | Aplica glosario del tenant para consistencia |
| Multilingual Retrieval | Recupera contexto aunque el documento este en otro idioma |
| Response Localization | Genera respuesta natural en el idioma correcto |

### 6.3 Campos recomendados en mensajes
```json
{
  "message_id": "uuid",
  "idea_id": "uuid",
  "user_id": "uuid",
  "role": "business_user | technical_user | admin",
  "detected_language": "es",
  "original_text": "",
  "canonical_summary": "",
  "response_language": "es",
  "created_at": "datetime"
}
```

## 7. Flujo end-to-end actualizado

![Flujo end-to-end con Company Context Engine](/mnt/data/architecture_images/end_to_end_flow.png)

### Flujo detallado
1. **Tenant onboarding:** se crea el tenant y se configura idioma, pais, industria y parametros basicos.
2. **Context bootstrap:** el cliente puede completar un formulario corto, conversar con el Discovery Agent o cargar documentos.
3. **Company Context Engine:** normaliza documentos, crea el TenantProfile, indexa conocimiento y calcula madurez.
4. **Business idea intake:** el usuario de negocio describe una idea en su idioma.
5. **Business validation:** los agentes evaluan valor, impacto, riesgo, supuestos y preguntas abiertas.
6. **Gate 1:** si la idea es viable, se congela la version de negocio y se genera un Technical Brief.
7. **Technical validation:** el usuario tecnico valida sistemas, datos, integraciones, seguridad y factibilidad.
8. **Gate 2:** si la idea es tecnicamente viable, se genera paquete de arquitectura y despliegue.
9. **Pilot / production tracking:** el administrador mide avance, adopcion, valor realizado, tokens y costo.
10. **Context feedback loop:** decisiones y resultados alimentan el contexto del tenant y mejoran futuras recomendaciones.

## 8. Separacion de experiencias por rol
| Rol | Interaccion | Contexto visible | Puede editar | Resultado esperado |
|---|---|---|---|---|
| Usuario de negocio | Conversacion natural para explicar idea | Contexto de negocio y preguntas abiertas | Campos de negocio | Business Case y viabilidad |
| Usuario tecnico | Validacion guiada del brief aprobado | Technical Brief y contexto tecnico relevante | Campos tecnicos | Factibilidad y arquitectura candidata |
| Administrador | Dashboard y gobierno | Todos los casos, trazas y metricas | Estados, prompts, configuracion | Pipeline, ROI, FinOps, auditabilidad |

## 9. Agentes propuestos
| Agente | Responsabilidad | Salida principal |
|---|---|---|
| Discovery Agent | Construir y actualizar contexto del cliente | TenantProfile parcial/completo |
| Business Intake Agent | Capturar idea, aclarar problema, usuarios y valor | Idea summary estructurado |
| Business Viability Agent | Evaluar valor, impacto, riesgos y supuestos | BusinessValidation JSON |
| Technical Validation Agent | Validar factibilidad, sistemas, datos y seguridad | TechnicalValidation JSON |
| Architecture Agent | Crear arquitectura objetivo y componentes | ArchitecturePackage |
| Deployment Plan Agent | Generar roadmap, backlog y pasos de despliegue | DeploymentPlan |
| Evaluator / Critic Agent | Revisar sesgos, calidad, contexto y consistencia | EvaluationReport |
| Response Composer | Convertir salidas estructuradas en conversacion natural | Respuesta final localizada |

## 10. Modelo de datos extendido
Ademas de `IdeaCase`, la arquitectura debe incorporar entidades para tenant, contexto, documentos, mensajes multilenguaje, ejecuciones de agentes y prompt governance.

```json
{
  "IdeaCase": {
    "idea_id": "uuid",
    "tenant_id": "uuid",
    "title": "",
    "current_stage": "business_validation",
    "status": "draft | needs_clarification | business_viable | technical_validation | architecture_ready | pilot | production | rejected",
    "source_language": "es",
    "business_context": {},
    "business_validation": {},
    "technical_brief": {},
    "technical_validation": {},
    "architecture_package": {},
    "value_tracking": {},
    "audit": {
      "decisions": [],
      "prompt_versions": [],
      "agent_runs": []
    }
  },
  "TenantContextDocument": {
    "document_id": "uuid",
    "tenant_id": "uuid",
    "source_uri": "blob-url",
    "language": "es",
    "document_type": "strategy | architecture | policy | roadmap | other",
    "status": "indexed | needs_review | retired",
    "version": "1.0"
  },
  "AgentRunTelemetry": {
    "agent_run_id": "uuid",
    "tenant_id": "uuid",
    "idea_id": "uuid",
    "agent_name": "Business Viability Agent",
    "prompt_version": "business_viability_v3",
    "model": "gpt-4o",
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost": 0,
    "latency_ms": 0,
    "quality_score": 0
  }
}
```

## 11. Admin Center: valor, trazabilidad y FinOps
La seccion administrativa debe demostrar el valor de la plataforma y controlar su consumo.

| Tab | KPIs sugeridos |
|---|---|
| Pipeline de ideas | Ideas por etapa, area, industria, tiempo promedio por gate, bloqueadores |
| Valor generado | Ahorro estimado, ahorro real, horas reducidas, ingresos incrementales, ROI |
| FinOps de IA | Tokens por tenant, agente, modelo, usuario, etapa y caso de uso |
| Prompt Governance | Versiones activas, costo promedio, calidad, aprobador, fecha de cambio |
| Auditoria | Decisiones, responsables, evidencia, cambios de estado, evaluaciones |

## 12. Despliegue empaquetado por cliente
Para permitir que cada cliente despliegue la solucion en su propio ambiente Azure, se recomienda usar infraestructura como codigo y configuracion por tenant.

### Recursos Azure sugeridos
- Azure Container Apps Environment.
- Container App para frontend React/Vite.
- Container App para API Python/FastAPI.
- Container App Job o Worker para ingestion y procesamiento de documentos.
- Azure Container Registry.
- Azure OpenAI o modelos desplegados desde Foundry.
- Foundry Agent Service.
- Azure AI Search.
- Azure Blob Storage.
- Cosmos DB o Azure Database for PostgreSQL.
- Azure Key Vault.
- Application Insights y Log Analytics.
- Managed Identity para acceso seguro entre servicios.

### Parametros de deployment
```json
{
  "tenant_name": "contoso",
  "region": "eastus",
  "default_language": "es",
  "supported_languages": ["es", "en", "pt"],
  "database_engine": "postgresql",
  "vector_index_name": "contoso-context-index",
  "container_image_tag": "v1.0.0",
  "enable_admin_dashboard": true,
  "enable_document_ingestion": true
}
```

## 13. Recomendaciones para GitHub Copilot
Usar este documento como backlog tecnico y pedir a GitHub Copilot implementar por modulos:

1. Crear estructura base del monorepo: `/frontend`, `/api`, `/workers`, `/infra`, `/docs`.
2. Implementar modelos Pydantic: TenantProfile, IdeaCase, AgentRunTelemetry, PromptVersion.
3. Crear endpoints FastAPI para tenant onboarding, idea intake, business submit, technical validation y admin metrics.
4. Implementar Language Layer con deteccion de idioma, locale resolver y campos `original_text` + `canonical_summary`.
5. Implementar Company Context Engine con servicios de ingestion, normalizacion, indexing y retrieval.
6. Crear cliente para Foundry Agents y wrappers por agente especializado.
7. Implementar Telemetry Middleware para capturar tokens, latencia, costo estimado, modelo y prompt version.
8. Crear UI React/Vite con tres experiencias: Business, Technical y Admin.
9. Crear IaC para desplegar recursos en Azure Container Apps con Managed Identity y Key Vault.

## 14. Roadmap recomendado
| Fase | Alcance | Resultado |
|---|---|---|
| MVP 1 | Idea intake, business validation, estado del caso, UI simple | Captura y validacion basica |
| MVP 2 | Technical validation, architecture package, response composer | Flujo completo negocio-tecnico |
| MVP 3 | Company Context Engine con quick setup y documentos | Personalizacion por cliente |
| MVP 4 | Admin center con tokens, costo, ROI y prompts | Gobierno y FinOps |
| MVP 5 | IaC multi-tenant y despliegue empaquetado | Producto reusable por cliente |

## 15. Decision arquitectonica clave
El mayor diferenciador no es simplemente usar agentes. El diferenciador es combinar agentes con un **Company Context Engine**, un **Language Layer**, un **estado de caso versionado** y un **Admin Center de valor y FinOps**. Esto permite que la solucion escale de una prueba de concepto a una plataforma empresarial empaquetable, gobernable y adaptable a cada cliente.