import { useEffect, useMemo, useRef, useState } from "react";
import ExecutiveDashboard from "./pages/ExecutiveDashboard";

const API_URL = import.meta.env.VITE_API_URL || "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io";
const AUTH_KEY = "aihub_demo_token";
const LANG_KEY = "aihub_ui_lang";
const BRAND_NAME = "AI Value Hub";
const WELCOME_LANGUAGES = ["en"];
const QUOTA_INPUT_TOKENS_PER_INTERACTION = 3000;
const QUOTA_OUTPUT_TOKENS_PER_INTERACTION = 1000;
const QUOTA_INPUT_USD_PER_1M = 2.5;
const QUOTA_OUTPUT_USD_PER_1M = 10;
const QUOTA_TOKENS_PER_INTERACTION = QUOTA_INPUT_TOKENS_PER_INTERACTION + QUOTA_OUTPUT_TOKENS_PER_INTERACTION;
const QUOTA_COST_PER_INTERACTION_USD =
  (QUOTA_INPUT_TOKENS_PER_INTERACTION / 1_000_000) * QUOTA_INPUT_USD_PER_1M +
  (QUOTA_OUTPUT_TOKENS_PER_INTERACTION / 1_000_000) * QUOTA_OUTPUT_USD_PER_1M;

const initialLoginForm = {
  username: "",
  password: "",
};

const initialForm = {
  tenant_id: "",
  title: "",
  problem_statement: "",
  expected_value: "",
  affected_users: "",
  source_language: "en",
};

const initialContextForm = {
  company_name: "",
  industry: "",
  strategic_priorities: "",
  prohibited_domains: "",
  regulatory_constraints: "",
  operating_model_summary: "",
  risk_tolerance: "medium",
};

const statusLabelByLanguage = {
  es: {
    draft: "Borrador",
    needs_clarification: "Requiere aclaracion",
    business_viable: "Viable negocio",
    rejected: "Rechazada",
  },
  en: {
    draft: "Draft",
    needs_clarification: "Needs clarification",
    business_viable: "Business viable",
    rejected: "Rejected",
  },
  pt: {
    draft: "Rascunho",
    needs_clarification: "Requer esclarecimento",
    business_viable: "Viavel negocio",
    rejected: "Rejeitada",
  },
};

const uiText = {
  es: {
    demoAccess: "Acceso Demo",
    loginDescription: "Ingresa con un usuario de prueba. Esta capa esta preparada para integrar Entra ID en fases siguientes.",
    username: "Usuario",
    password: "Clave",
    login: "Iniciar sesion",
    loggingIn: "Iniciando...",
    session: "Sesion",
    home: "Inicio",
    myIdeas: "Mis ideas",
    logout: "Cerrar sesion",
    heroTitle: "Business + Technical Studio",
    heroCopy: "Captura ideas, valida negocio, ejecuta validacion tecnica y genera paquete de arquitectura por caso.",
    tenant: "Tenant",
    authReady: "Auth demo lista para Entra",
    stages: "Etapas: negocio y tecnica",
    viable: "Viables",
    rejected: "Rechazadas",
    clarification: "Aclaracion",
    contextTitle: "Contexto base del tenant",
    contextSubtitle: "Se registra una vez y se usa como linea base para calificar viabilidad.",
    loadContext: "Cargar contexto",
    company: "Empresa",
    industry: "Industria",
    strategicPriorities: "Prioridades estrategicas (separadas por coma)",
    prohibitedDomains: "Dominios prohibidos (separados por coma)",
    regulatoryConstraints: "Restricciones regulatorias (separadas por coma)",
    operatingSummary: "Resumen operativo",
    riskTolerance: "Tolerancia de riesgo",
    saveContext: "Guardar contexto",
    editContext: "Editar contexto",
    savingContext: "Guardando contexto...",
    contextStatusLoaded: "Estado contexto: cargado",
    contextStatusPending: "Estado contexto: pendiente",
    contextRegistered: "Contexto empresarial registrado",
    contextRegisteredBody: "El contexto ya fue guardado y se aplica automaticamente en la evaluacion de ideas. La edicion quedara disponible para perfil admin en una fase posterior.",
    newIdea: "Nueva idea",
    newIdeaSubtitle: "La calificacion usa contexto de negocio + filtro tecnico de viabilidad.",
    title: "Titulo",
    problem: "Problema",
    expectedValue: "Valor esperado",
    affectedUsers: "Usuarios afectados (separados por coma)",
    sourceLanguage: "Idioma fuente",
    saveIdea: "Crear y validar",
    savingIdea: "Guardando...",
    myIdeasSubtitle: "Solo ves ideas creadas con tu sesion. Incluye fase y motivo de rechazo. Se muestran ideas en espanol, ingles y portugues sin filtrar por idioma UI.",
    statusDetail: "Estado",
    stageIdeaIntake: "Intake de idea",
    stageBusinessValidation: "Validacion de negocio",
    stageTechnicalValidation: "Validacion tecnica",
    owner: "Propietario",
    currentStage: "Etapa actual",
    scores: "Scores",
    rejectionInPhase: "Rechazo en fase",
    viewDetail: "Ver detalle",
    contextSignals: "Senales de contexto",
    assumptions: "Supuestos",
    openQuestions: "Preguntas abiertas",
    agentSummary: "Resumen agente",
    clarifyWithAgent: "Aclarar con agente",
    resubmitForReview: "Reenviar para revision",
    submittingResubmit: "Reenviando para revision...",
    resubmitSuccess: "Idea reenviada. Puedes proporcionar mas informacion.",
    resubmitFailed: "No fue posible reenviar la idea.",
    clarificationTitle: "Aclaracion guiada",
    clarificationIntro: "Responde las preguntas para recalificar la idea y decidir si pasa a validacion tecnica o se rechaza en fase 1.",
    clarificationWhy: "Por que se pregunta",
    clarificationAnswer: "Tu respuesta",
    suggestedAnswers: "Respuestas sugeridas",
    useSuggestion: "Usar sugerencia",
    submitClarification: "Enviar aclaraciones",
    submittingClarification: "Evaluando aclaraciones...",
    clarificationDoneViable: "Aclaracion procesada. La idea paso a validacion tecnica.",
    clarificationDoneRejected: "Aclaracion procesada. La idea fue rechazada con trazabilidad.",
    clarificationStillNeeded: "Aclaracion procesada. Aun se requiere mas informacion antes de pasar a validacion tecnica.",
    noIdeas: "Aun no tienes ideas registradas.",
    language: "Idioma UI",
    welcomeTitle: "Bienvenido al AI Value Hub",
    welcomeBody: "Impulsa decisiones con evidencia, prioriza iniciativas de mayor impacto y alinea innovacion con contexto real de negocio.",
    continue: "Continuar",
    adminOnlyContext: "El contexto empresarial solo puede ser administrado por el perfil admin.",
    uploadSection: "Carga opcional de archivos de contexto",
    uploadHint: "Puedes subir PDF, PPT, Word o MD para enriquecer el Context Engine.",
    selectFiles: "Seleccionar archivos",
    uploadFiles: "Subir archivos",
    uploadingFiles: "Subiendo archivos...",
    uploadOk: "Archivos cargados correctamente.",
    technicalPanelTitle: "Validacion tecnica",
    runTechnicalValidation: "Iniciar chat tecnico con agente",
    validatingTechnical: "Validando tecnica...",
    loadingTechnicalQuestions: "Cargando preguntas tecnicas...",
    technicalChatIntro: "Responde estas preguntas tecnicas para evaluar factibilidad con soporte de respuestas sugeridas.",
    technicalChatWelcome: "Hola, soy tu agente tecnico. Vamos a revisar este caso en una conversacion breve para estimar factibilidad.",
    technicalChatRationale: "Contexto de esta pregunta",
    technicalChatSend: "Enviar mensaje",
    technicalChatPending: "Pregunta pendiente",
    technicalChatReady: "Listo para evaluar",
    technicalChatComplete: "Perfecto. Ya tengo toda la informacion tecnica necesaria. Cuando quieras, ejecuto la validacion.",
    technicalChatNeedMore: "Necesito una respuesta un poco mas detallada (minimo 5 caracteres).",
    submitTechnicalChat: "Enviar respuestas tecnicas",
    technicalAnswer: "Tu respuesta tecnica",
    generateArchitecture: "Generar paquete de arquitectura",
    generatingArchitecture: "Generando arquitectura...",
    technicalResult: "Resultado tecnico",
    feasibilityScore: "Factibilidad",
    technicalAgentTrace: "Validacion tecnica (agente)",
    integrationComplexity: "Complejidad de integracion",
    securityRisk: "Riesgo de seguridad",
    dataReadiness: "Madurez de datos",
    technicalBlockers: "Bloqueadores",
    packageGenerated: "Paquete de arquitectura generado",
    packageGeneratedAt: "Generado",
    downloadPackage: "Descargar paquete (HTML)",
    viewPackage: "Ver reporte HTML",
    closePreview: "Cerrar vista",
    possibleDuplicate: "Posible duplicada de",
    architectureSummary: "Resumen arquitectura",
    nextActions: "Siguientes acciones",
    adminPanelTitle: "Panel de administracion",
    adminPanelSubtitle: "Vista de casos de uso aprobados, consumo estimado de tokens/costo y metricas del portafolio.",
    adminTabUseCases: "Casos de uso",
    adminTabTokenCost: "Tokens y costo",
    adminTabMetrics: "Metricas",
    adminUseCaseList: "Listado de casos de uso aprobados",
    adminUseCaseNone: "Aun no hay casos de uso que hayan completado todas las validaciones.",
    adminGeneratedAt: "Generado",
    adminEstimatedTokens: "Tokens estimados",
    adminEstimatedCost: "Costo estimado (USD)",
    adminProjectsInProduction: "Proyectos en produccion",
    adminPromptTokens: "Prompt tokens",
    adminCompletionTokens: "Completion tokens",
    adminQuotaTotal: "Cuota total mensual (tokens)",
    adminQuotaConsumed: "Consumo mensual (tokens)",
    adminQuotaRemaining: "Cuota restante (tokens)",
    adminQuotaTotalUsd: "Equivalente cuota total (USD)",
    adminQuotaConsumedUsd: "Consumo estimado (USD)",
    adminQuotaRemainingUsd: "Saldo estimado (USD)",
    adminQuotaUsdHint: "Supuesto para cuota: 3000 tokens input + 1000 tokens output por interaccion, GPT-5.5 Instant (input $2.50/1M, output $10/1M). Costo por interaccion: $0.0175.",
    adminQuotaMonth: "Mes de cuota",
    adminQuotaBase: "Cuota base",
    adminQuotaExtra: "Cuota extra",
    adminQuotaSet: "Asignar cuota base",
    adminQuotaAddExtra: "Agregar cuota extra",
    adminQuotaReason: "Motivo",
    adminQuotaUsageClock: "Reloj de consumo",
    adminNoProductionApps: "No hay apps en produccion para controlar cuota.",
    adminQuotaUpdated: "Cuota base actualizada.",
    adminQuotaExtraAdded: "Cuota extra agregada.",
    errorUpdateQuota: "No fue posible actualizar la cuota",
    errorAddQuotaExtra: "No fue posible agregar cuota extra",
    adminTotalIdeas: "Ideas totales",
    adminApprovalRate: "Tasa de aprobacion",
    adminTechnicalPassRate: "Tasa de aprobacion tecnica",
    adminAvgFeasibility: "Factibilidad promedio",
    adminAvgCycleHours: "Ciclo promedio (horas)",
    adminTopComponents: "Componentes mas frecuentes",
    adminNoComponentData: "Sin datos de componentes aun",
    adminMetricHintTotalIdeas: "Conteo total de ideas del tenant (todas las etapas y estados).",
    adminMetricHintApprovalRate: "(Ideas business_viable / ideas totales) x 100. Fuente: portfolio_metrics.approval_rate_pct.",
    adminMetricHintTechnicalPassRate: "(Ideas viables con validacion tecnica aprobada / ideas business_viable) x 100.",
    adminMetricHintAvgFeasibility: "Promedio del feasibility_score de ideas con validacion tecnica.",
    adminMetricHintAvgCycleHours: "Promedio de horas entre fecha de creacion y ultima actualizacion de la idea.",
    productionCatalogTitle: "Catalogo productivo disponible",
    productionCatalogSubtitle: "Herramientas listas para uso por usuarios internos, con alcance y contacto simulado.",
    productionStatus: "En productivo",
    productionScope: "Alcance",
    productionContact: "Contacto",
    demoIdeasTitle: "Ideas demo para mostrar flujo",
    demoIdeasSubtitle: "Carga una idea ejemplo, ejecútala en el flujo y elimínala para volver a usarla.",
    demoIdeaPrefill: "Cargar en formulario",
    demoIdeaCreate: "Crear ejemplo",
    deletingIdea: "Eliminando idea...",
    deleteOwnIdea: "Eliminar idea",
    deleteOwnIdeaConfirm: "Confirmar eliminacion de esta idea",
    technicalHubTitle: "Bandeja equipo tecnico",
    technicalHubSubtitle: "Ideas viables de negocio para revision tecnica asistida por agente.",
    technicalHub: "Equipo tecnico",
    technicalQueueEmpty: "No hay ideas viables pendientes para revision tecnica.",
    technicalOpen: "Abrir revision tecnica",
    technicalRequestMoreInfo: "Si falta informacion, usa el chat para pedir detalles adicionales al equipo funcional.",
    demoTechnical: "Demo tecnico: tecnico.platform / Demo1234!",
    adminDeploymentStatus: "Estado de despliegue",
    adminDeploymentDevelopment: "Desarrollo",
    adminDeploymentFunding: "Funding",
    adminDeploymentProduction: "Produccion",
    adminDeploymentDemoNote: "Vista demo: algunos casos se muestran como ya desplegados en produccion para ilustrar el portafolio.",
    adminDeleteIdea: "Eliminar",
    adminDeleteIdeaConfirm: "Confirmar eliminacion",
    adminDeleteingIdea: "Eliminando...",
    adminIdeaDeleted: "Idea eliminada exitosamente.",
    errorDeleteIdea: "No fue posible eliminar la idea",
    focusedIdeaTitle: "Idea en primer plano",
    removeFocus: "Quitar foco",
    viewInFocus: "Ver en primer plano",
    componentsLabel: "Componentes",
    demoUser1: "Demo usuario 1: analista.finanzas / Demo1234!",
    demoUser2: "Demo usuario 2: analista.riesgo / Demo1234!",
    demoAdmin: "Demo admin: admin.valuehub / Demo1234!",
    noFilesSelected: "No hay archivos seleccionados.",
    tenantNoContext: "Este tenant aun no tiene contexto base. Completa el formulario y guarda.",
    errorSessionExpired: "Sesion expirada. Inicia sesion nuevamente.",
    errorLoadProfile: "No fue posible recuperar el perfil de usuario",
    errorLoadContext: "No se pudo cargar el contexto base del tenant",
    errorLoadIdeas: "No se pudieron cargar tus ideas",
    errorUnexpected: "Error inesperado",
    errorLogin: "No fue posible iniciar sesion",
    errorLoadTechnicalQuestions: "No fue posible cargar preguntas tecnicas",
    errorLoadingTechnical: "Error cargando chat tecnico",
    errorRunTechnical: "No fue posible ejecutar validacion tecnica",
    errorTechnicalValidation: "Error validando tecnica",
    errorGenerateArchitecture: "No fue posible generar arquitectura",
    errorGeneratingArchitecture: "Error generando arquitectura",
    errorLoadClarificationQuestions: "No fue posible cargar preguntas de aclaracion",
    errorLoadingClarifications: "Error cargando aclaraciones",
    errorProcessClarifications: "No fue posible procesar aclaraciones",
    errorProcessingClarifications: "Error procesando aclaraciones",
    errorLoadingContext: "Error cargando contexto",
    errorSaveContext: "No fue posible guardar el contexto",
    errorContextFiles: "Error cargando archivos de contexto",
    errorMustRegisterContext: "Primero debes registrar el contexto base del tenant para evaluar la idea.",
    errorCreateIdea: "No fue posible crear la idea",
    riskLow: "baja",
    riskMedium: "media",
    riskHigh: "alta",
  },
  en: {
    demoAccess: "Demo Access",
    loginDescription: "Sign in with a test user. This layer is ready for Entra ID integration in upcoming phases.",
    username: "Username",
    password: "Password",
    login: "Sign in",
    loggingIn: "Signing in...",
    session: "Session",
    home: "Home",
    myIdeas: "My ideas",
    logout: "Sign out",
    heroTitle: "Business + Technical Studio",
    heroCopy: "Capture ideas, validate business, run technical validation, and generate architecture package per case.",
    tenant: "Tenant",
    authReady: "Demo auth ready for Entra",
    stages: "Stages: business and technical",
    viable: "Viable",
    rejected: "Rejected",
    clarification: "Clarification",
    contextTitle: "Tenant baseline context",
    contextSubtitle: "Registered once and used as baseline for idea viability scoring.",
    loadContext: "Load context",
    company: "Company",
    industry: "Industry",
    strategicPriorities: "Strategic priorities (comma-separated)",
    prohibitedDomains: "Prohibited domains (comma-separated)",
    regulatoryConstraints: "Regulatory constraints (comma-separated)",
    operatingSummary: "Operating summary",
    riskTolerance: "Risk tolerance",
    saveContext: "Save context",
    editContext: "Edit context",
    savingContext: "Saving context...",
    contextStatusLoaded: "Context status: loaded",
    contextStatusPending: "Context status: pending",
    contextRegistered: "Business context registered",
    contextRegisteredBody: "Context has been saved and is applied automatically during idea evaluation. Editing will be enabled later for admin profile.",
    newIdea: "New idea",
    newIdeaSubtitle: "Scoring uses business context plus a technical feasibility filter.",
    title: "Title",
    problem: "Problem",
    expectedValue: "Expected value",
    affectedUsers: "Affected users (comma-separated)",
    sourceLanguage: "Source language",
    saveIdea: "Create and validate",
    savingIdea: "Saving...",
    myIdeasSubtitle: "You only see ideas created in your session. Includes rejection phase and reason. Ideas in Spanish, English, and Portuguese are shown regardless of UI language.",
    statusDetail: "Status",
    stageIdeaIntake: "Idea intake",
    stageBusinessValidation: "Business validation",
    stageTechnicalValidation: "Technical validation",
    owner: "Owner",
    currentStage: "Current stage",
    scores: "Scores",
    rejectionInPhase: "Rejected in phase",
    viewDetail: "View detail",
    contextSignals: "Context signals",
    assumptions: "Assumptions",
    openQuestions: "Open questions",
    agentSummary: "Agent summary",
    clarifyWithAgent: "Clarify with agent",
    resubmitForReview: "Resubmit for review",
    submittingResubmit: "Resubmitting for review...",
    resubmitSuccess: "Idea resubmitted. You can provide more information.",
    resubmitFailed: "Could not resubmit the idea.",
    clarificationTitle: "Guided clarification",
    clarificationIntro: "Answer these questions to re-score the idea and decide if it moves to technical validation or is rejected in phase 1.",
    clarificationWhy: "Why this is asked",
    clarificationAnswer: "Your answer",
    suggestedAnswers: "Suggested answers",
    useSuggestion: "Use suggestion",
    submitClarification: "Submit clarifications",
    submittingClarification: "Evaluating clarifications...",
    clarificationDoneViable: "Clarification processed. Idea moved to technical validation.",
    clarificationDoneRejected: "Clarification processed. Idea rejected with traceability.",
    clarificationStillNeeded: "Clarification processed. More information is still required before technical validation.",
    noIdeas: "You have no ideas yet.",
    language: "UI language",
    welcomeTitle: "Welcome to AI Value Hub",
    welcomeBody: "Drive evidence-based decisions, prioritize high-value initiatives, and align innovation with real business context.",
    continue: "Continue",
    adminOnlyContext: "Business context can only be managed by the admin profile.",
    uploadSection: "Optional context file upload",
    uploadHint: "Upload PDF, PPT, Word, or MD files to enrich the Context Engine.",
    selectFiles: "Select files",
    uploadFiles: "Upload files",
    uploadingFiles: "Uploading files...",
    uploadOk: "Files uploaded successfully.",
    technicalPanelTitle: "Technical validation",
    runTechnicalValidation: "Start technical chat with agent",
    validatingTechnical: "Validating technical...",
    loadingTechnicalQuestions: "Loading technical questions...",
    technicalChatIntro: "Answer these technical questions to evaluate feasibility with guided suggestions.",
    technicalChatWelcome: "Hi, I am your technical agent. Let us review this case in a short conversation to estimate feasibility.",
    technicalChatRationale: "Context for this question",
    technicalChatSend: "Send message",
    technicalChatPending: "Pending question",
    technicalChatReady: "Ready to evaluate",
    technicalChatComplete: "Perfect. I now have all the technical information needed. When you are ready, I can run the validation.",
    technicalChatNeedMore: "I need a slightly more detailed answer (minimum 5 characters).",
    submitTechnicalChat: "Submit technical answers",
    technicalAnswer: "Your technical answer",
    generateArchitecture: "Generate architecture package",
    generatingArchitecture: "Generating architecture...",
    technicalResult: "Technical result",
    feasibilityScore: "Feasibility",
    technicalAgentTrace: "Technical validation (agent)",
    integrationComplexity: "Integration complexity",
    securityRisk: "Security risk",
    dataReadiness: "Data readiness",
    technicalBlockers: "Blockers",
    packageGenerated: "Architecture package generated",
    packageGeneratedAt: "Generated",
    downloadPackage: "Download package (HTML)",
    viewPackage: "View HTML report",
    closePreview: "Close preview",
    possibleDuplicate: "Possible duplicate of",
    architectureSummary: "Architecture summary",
    nextActions: "Next actions",
    adminPanelTitle: "Admin panel",
    adminPanelSubtitle: "Approved use cases, estimated token/cost consumption, and portfolio metrics.",
    adminTabUseCases: "Use cases",
    adminTabTokenCost: "Tokens and cost",
    adminTabMetrics: "Metrics",
    adminUseCaseList: "Approved use case list",
    adminUseCaseNone: "No use cases have completed all validations yet.",
    adminGeneratedAt: "Generated",
    adminEstimatedTokens: "Estimated tokens",
    adminEstimatedCost: "Estimated cost (USD)",
    adminProjectsInProduction: "Projects in production",
    adminPromptTokens: "Prompt tokens",
    adminCompletionTokens: "Completion tokens",
    adminQuotaTotal: "Monthly total quota (tokens)",
    adminQuotaConsumed: "Monthly consumption (tokens)",
    adminQuotaRemaining: "Remaining quota (tokens)",
    adminQuotaTotalUsd: "Total quota equivalent (USD)",
    adminQuotaConsumedUsd: "Estimated consumption (USD)",
    adminQuotaRemainingUsd: "Estimated balance (USD)",
    adminQuotaUsdHint: "Quota assumption: 3000 input tokens + 1000 output tokens per interaction, GPT-5.5 Instant (input $2.50/1M, output $10/1M). Cost per interaction: $0.0175.",
    adminQuotaMonth: "Quota month",
    adminQuotaBase: "Base quota",
    adminQuotaExtra: "Extra quota",
    adminQuotaSet: "Set base quota",
    adminQuotaAddExtra: "Add extra quota",
    adminQuotaReason: "Reason",
    adminQuotaUsageClock: "Consumption clock",
    adminNoProductionApps: "No production apps available for quota control.",
    adminQuotaUpdated: "Base quota updated.",
    adminQuotaExtraAdded: "Extra quota added.",
    errorUpdateQuota: "Could not update quota",
    errorAddQuotaExtra: "Could not add extra quota",
    adminTotalIdeas: "Total ideas",
    adminApprovalRate: "Approval rate",
    adminTechnicalPassRate: "Technical pass rate",
    adminAvgFeasibility: "Average feasibility",
    adminAvgCycleHours: "Average cycle (hours)",
    adminTopComponents: "Most frequent components",
    adminNoComponentData: "No component data yet",
    adminMetricHintTotalIdeas: "Total idea count for the tenant (all stages and statuses).",
    adminMetricHintApprovalRate: "(business_viable ideas / total ideas) x 100. Source: portfolio_metrics.approval_rate_pct.",
    adminMetricHintTechnicalPassRate: "(business-viable ideas with approved technical validation / business_viable ideas) x 100.",
    adminMetricHintAvgFeasibility: "Average feasibility_score across ideas with technical validation.",
    adminMetricHintAvgCycleHours: "Average hours between idea creation and latest update timestamps.",
    productionCatalogTitle: "Production catalog",
    productionCatalogSubtitle: "Tools ready for internal users, with scope and simulated contact.",
    productionStatus: "In production",
    productionScope: "Scope",
    productionContact: "Contact",
    demoIdeasTitle: "Demo ideas to showcase flow",
    demoIdeasSubtitle: "Load a sample idea, run it through the flow, and delete it to reuse later.",
    demoIdeaPrefill: "Load into form",
    demoIdeaCreate: "Create sample",
    deletingIdea: "Deleting idea...",
    deleteOwnIdea: "Delete idea",
    deleteOwnIdeaConfirm: "Confirm deletion for this idea",
    technicalHubTitle: "Technical team queue",
    technicalHubSubtitle: "Business-viable ideas ready for technical review with agent support.",
    technicalHub: "Technical team",
    technicalQueueEmpty: "No business-viable ideas pending technical review.",
    technicalOpen: "Open technical review",
    technicalRequestMoreInfo: "If information is missing, use chat to request additional details from the functional team.",
    demoTechnical: "Tech demo: tecnico.platform / Demo1234!",
    adminDeploymentStatus: "Deployment status",
    adminDeploymentDevelopment: "Development",
    adminDeploymentFunding: "Funding",
    adminDeploymentProduction: "Production",
    adminDeploymentDemoNote: "Demo view: some cases are shown as already deployed to illustrate the portfolio.",
    adminDeleteIdea: "Delete",
    adminDeleteIdeaConfirm: "Confirm deletion",
    adminDeleteingIdea: "Deleting...",
    adminIdeaDeleted: "Idea deleted successfully.",
    errorDeleteIdea: "Could not delete the idea",
    focusedIdeaTitle: "Focused idea",
    removeFocus: "Remove focus",
    viewInFocus: "View in focus",
    componentsLabel: "Components",
    demoUser1: "Demo user 1: analista.finanzas / Demo1234!",
    demoUser2: "Demo user 2: analista.riesgo / Demo1234!",
    demoAdmin: "Demo admin: admin.valuehub / Demo1234!",
    noFilesSelected: "No files selected.",
    tenantNoContext: "This tenant has no baseline context yet. Complete and save the form.",
    errorSessionExpired: "Session expired. Sign in again.",
    errorLoadProfile: "Could not retrieve user profile",
    errorLoadContext: "Could not load tenant baseline context",
    errorLoadIdeas: "Could not load your ideas",
    errorUnexpected: "Unexpected error",
    errorLogin: "Could not sign in",
    errorLoadTechnicalQuestions: "Could not load technical questions",
    errorLoadingTechnical: "Error loading technical chat",
    errorRunTechnical: "Could not run technical validation",
    errorTechnicalValidation: "Error validating technical",
    errorGenerateArchitecture: "Could not generate architecture",
    errorGeneratingArchitecture: "Error generating architecture",
    errorLoadClarificationQuestions: "Could not load clarification questions",
    errorLoadingClarifications: "Error loading clarifications",
    errorProcessClarifications: "Could not process clarifications",
    errorProcessingClarifications: "Error processing clarifications",
    errorLoadingContext: "Error loading context",
    errorSaveContext: "Could not save context",
    errorContextFiles: "Error uploading context files",
    errorMustRegisterContext: "You must register tenant baseline context before evaluating an idea.",
    errorCreateIdea: "Could not create idea",
    riskLow: "low",
    riskMedium: "medium",
    riskHigh: "high",
  },
  pt: {
    demoAccess: "Acesso Demo",
    loginDescription: "Entre com um usuario de teste. Esta camada esta pronta para integrar Entra ID nas proximas fases.",
    username: "Usuario",
    password: "Senha",
    login: "Entrar",
    loggingIn: "Entrando...",
    session: "Sessao",
    home: "Inicio",
    myIdeas: "Minhas ideias",
    logout: "Sair",
    heroTitle: "Business + Technical Studio",
    heroCopy: "Capture ideias, valide negocio, execute validacao tecnica e gere pacote de arquitetura por caso.",
    tenant: "Tenant",
    authReady: "Auth demo pronta para Entra",
    stages: "Etapas: negocio e tecnica",
    viable: "Viaveis",
    rejected: "Rejeitadas",
    clarification: "Esclarecimento",
    contextTitle: "Contexto base do tenant",
    contextSubtitle: "Registrado uma vez e usado como base para classificar viabilidade.",
    loadContext: "Carregar contexto",
    company: "Empresa",
    industry: "Industria",
    strategicPriorities: "Prioridades estrategicas (separadas por virgula)",
    prohibitedDomains: "Dominios proibidos (separados por virgula)",
    regulatoryConstraints: "Restricoes regulatorias (separadas por virgula)",
    operatingSummary: "Resumo operacional",
    riskTolerance: "Tolerancia de risco",
    saveContext: "Salvar contexto",
    editContext: "Editar contexto",
    savingContext: "Salvando contexto...",
    contextStatusLoaded: "Status do contexto: carregado",
    contextStatusPending: "Status do contexto: pendente",
    contextRegistered: "Contexto empresarial registrado",
    contextRegisteredBody: "O contexto ja foi salvo e se aplica automaticamente na avaliacao de ideias. A edicao ficara disponivel depois para perfil admin.",
    newIdea: "Nova ideia",
    newIdeaSubtitle: "A classificacao usa contexto de negocio + filtro tecnico de viabilidade.",
    title: "Titulo",
    problem: "Problema",
    expectedValue: "Valor esperado",
    affectedUsers: "Usuarios afetados (separados por virgula)",
    sourceLanguage: "Idioma de origem",
    saveIdea: "Criar e validar",
    savingIdea: "Salvando...",
    myIdeasSubtitle: "Voce so ve ideias criadas na sua sessao. Inclui fase e motivo de rejeicao. Ideias em espanhol, ingles e portugues aparecem sem filtro de idioma da UI.",
    statusDetail: "Status",
    stageIdeaIntake: "Intake da ideia",
    stageBusinessValidation: "Validacao de negocio",
    stageTechnicalValidation: "Validacao tecnica",
    owner: "Proprietario",
    currentStage: "Etapa atual",
    scores: "Pontuacoes",
    rejectionInPhase: "Rejeitada na fase",
    viewDetail: "Ver detalhe",
    contextSignals: "Sinais de contexto",
    assumptions: "Supostos",
    openQuestions: "Perguntas abertas",
    agentSummary: "Resumo do agente",
    clarifyWithAgent: "Esclarecer com agente",
    resubmitForReview: "Reenviar para revisao",
    submittingResubmit: "Reenviando para revisao...",
    resubmitSuccess: "Ideia reenviada. Voce pode fornecer mais informacoes.",
    resubmitFailed: "Nao foi possivel reenviar a ideia.",
    clarificationTitle: "Esclarecimento guiado",
    clarificationIntro: "Responda as perguntas para recalificar a ideia e decidir se vai para validacao tecnica ou rejeicao na fase 1.",
    clarificationWhy: "Por que e perguntado",
    clarificationAnswer: "Sua resposta",
    suggestedAnswers: "Respostas sugeridas",
    useSuggestion: "Usar sugestao",
    submitClarification: "Enviar esclarecimentos",
    submittingClarification: "Avaliando esclarecimentos...",
    clarificationDoneViable: "Esclarecimento processado. A ideia foi para validacao tecnica.",
    clarificationDoneRejected: "Esclarecimento processado. A ideia foi rejeitada com rastreabilidade.",
    clarificationStillNeeded: "Esclarecimento processado. Ainda e necessario mais informacao antes da validacao tecnica.",
    noIdeas: "Ainda nao ha ideias registradas.",
    language: "Idioma UI",
    welcomeTitle: "Bem-vindo ao AI Value Hub",
    welcomeBody: "Impulsione decisoes com evidencia, priorize iniciativas de maior impacto e alinhe inovacao com contexto real de negocio.",
    continue: "Continuar",
    adminOnlyContext: "O contexto empresarial so pode ser gerenciado pelo perfil admin.",
    uploadSection: "Carga opcional de arquivos de contexto",
    uploadHint: "Voce pode enviar PDF, PPT, Word ou MD para enriquecer o Context Engine.",
    selectFiles: "Selecionar arquivos",
    uploadFiles: "Enviar arquivos",
    uploadingFiles: "Enviando arquivos...",
    uploadOk: "Arquivos enviados com sucesso.",
    technicalPanelTitle: "Validacao tecnica",
    runTechnicalValidation: "Iniciar chat tecnico com agente",
    validatingTechnical: "Validando tecnica...",
    loadingTechnicalQuestions: "Carregando perguntas tecnicas...",
    technicalChatIntro: "Responda estas perguntas tecnicas para avaliar factibilidade com sugestoes guiadas.",
    technicalChatWelcome: "Ola, sou seu agente tecnico. Vamos revisar este caso em uma conversa breve para estimar factibilidade.",
    technicalChatRationale: "Contexto desta pergunta",
    technicalChatSend: "Enviar mensagem",
    technicalChatPending: "Pergunta pendente",
    technicalChatReady: "Pronto para avaliar",
    technicalChatComplete: "Perfeito. Ja tenho toda a informacao tecnica necessaria. Quando quiser, executo a validacao.",
    technicalChatNeedMore: "Preciso de uma resposta um pouco mais detalhada (minimo 5 caracteres).",
    submitTechnicalChat: "Enviar respostas tecnicas",
    technicalAnswer: "Sua resposta tecnica",
    generateArchitecture: "Gerar pacote de arquitetura",
    generatingArchitecture: "Gerando arquitetura...",
    technicalResult: "Resultado tecnico",
    feasibilityScore: "Factibilidade",
    technicalAgentTrace: "Validacao tecnica (agente)",
    integrationComplexity: "Complexidade de integracao",
    securityRisk: "Risco de seguranca",
    dataReadiness: "Maturidade de dados",
    technicalBlockers: "Bloqueadores",
    packageGenerated: "Pacote de arquitetura gerado",
    packageGeneratedAt: "Gerado",
    downloadPackage: "Baixar pacote (HTML)",
    viewPackage: "Ver relatorio HTML",
    closePreview: "Fechar visualizacao",
    possibleDuplicate: "Possivel duplicata de",
    architectureSummary: "Resumo da arquitetura",
    nextActions: "Proximas acoes",
    adminPanelTitle: "Painel de administracao",
    adminPanelSubtitle: "Casos de uso aprovados, consumo estimado de tokens/custo e metricas do portifolio.",
    adminTabUseCases: "Casos de uso",
    adminTabTokenCost: "Tokens e custo",
    adminTabMetrics: "Metricas",
    adminUseCaseList: "Lista de casos de uso aprovados",
    adminUseCaseNone: "Ainda nao ha casos de uso que tenham concluido todas as validacoes.",
    adminGeneratedAt: "Gerado",
    adminEstimatedTokens: "Tokens estimados",
    adminEstimatedCost: "Custo estimado (USD)",
    adminProjectsInProduction: "Projetos em producao",
    adminPromptTokens: "Prompt tokens",
    adminCompletionTokens: "Completion tokens",
    adminQuotaTotal: "Cota total mensal (tokens)",
    adminQuotaConsumed: "Consumo mensal (tokens)",
    adminQuotaRemaining: "Cota restante (tokens)",
    adminQuotaTotalUsd: "Equivalente da cota total (USD)",
    adminQuotaConsumedUsd: "Consumo estimado (USD)",
    adminQuotaRemainingUsd: "Saldo estimado (USD)",
    adminQuotaUsdHint: "Suposicao da cota: 3000 tokens de input + 1000 tokens de output por interacao, GPT-5.5 Instant (input $2.50/1M, output $10/1M). Custo por interacao: $0.0175.",
    adminQuotaMonth: "Mes da cota",
    adminQuotaBase: "Cota base",
    adminQuotaExtra: "Cota extra",
    adminQuotaSet: "Definir cota base",
    adminQuotaAddExtra: "Adicionar cota extra",
    adminQuotaReason: "Motivo",
    adminQuotaUsageClock: "Relogio de consumo",
    adminNoProductionApps: "Nao ha apps em producao para controle de cota.",
    adminQuotaUpdated: "Cota base atualizada.",
    adminQuotaExtraAdded: "Cota extra adicionada.",
    errorUpdateQuota: "Nao foi possivel atualizar a cota",
    errorAddQuotaExtra: "Nao foi possivel adicionar cota extra",
    adminTotalIdeas: "Ideias totais",
    adminApprovalRate: "Taxa de aprovacao",
    adminTechnicalPassRate: "Taxa de aprovacao tecnica",
    adminAvgFeasibility: "Factibilidade media",
    adminAvgCycleHours: "Ciclo medio (horas)",
    adminTopComponents: "Componentes mais frequentes",
    adminNoComponentData: "Sem dados de componentes ainda",
    adminMetricHintTotalIdeas: "Contagem total de ideias do tenant (todas as etapas e status).",
    adminMetricHintApprovalRate: "(ideias business_viable / ideias totais) x 100. Fonte: portfolio_metrics.approval_rate_pct.",
    adminMetricHintTechnicalPassRate: "(ideias viaveis com validacao tecnica aprovada / ideias business_viable) x 100.",
    adminMetricHintAvgFeasibility: "Media do feasibility_score das ideias com validacao tecnica.",
    adminMetricHintAvgCycleHours: "Media de horas entre criacao da ideia e ultima atualizacao.",
    productionCatalogTitle: "Catalogo produtivo",
    productionCatalogSubtitle: "Ferramentas prontas para uso interno, com escopo e contato simulado.",
    productionStatus: "Em producao",
    productionScope: "Escopo",
    productionContact: "Contato",
    demoIdeasTitle: "Ideias demo para mostrar fluxo",
    demoIdeasSubtitle: "Carregue uma ideia de exemplo, execute o fluxo e exclua para reutilizar.",
    demoIdeaPrefill: "Carregar no formulario",
    demoIdeaCreate: "Criar exemplo",
    deletingIdea: "Excluindo ideia...",
    deleteOwnIdea: "Excluir ideia",
    deleteOwnIdeaConfirm: "Confirmar exclusao desta ideia",
    technicalHubTitle: "Fila da equipe tecnica",
    technicalHubSubtitle: "Ideias viaveis de negocio para revisao tecnica assistida por agente.",
    technicalHub: "Equipe tecnica",
    technicalQueueEmpty: "Nao ha ideias viaveis pendentes para revisao tecnica.",
    technicalOpen: "Abrir revisao tecnica",
    technicalRequestMoreInfo: "Se faltar informacao, use o chat para pedir detalhes adicionais ao time funcional.",
    demoTechnical: "Demo tecnico: tecnico.platform / Demo1234!",
    adminDeploymentStatus: "Estado de deploy",
    adminDeploymentDevelopment: "Desenvolvimento",
    adminDeploymentFunding: "Funding",
    adminDeploymentProduction: "Producao",
    adminDeploymentDemoNote: "Vista demo: alguns casos aparecem como ja implantados em producao para ilustrar o portifolio.",
    adminDeleteIdea: "Eliminar",
    adminDeleteIdeaConfirm: "Confirmar eliminacao",
    adminDeleteingIdea: "Eliminando...",
    adminIdeaDeleted: "Ideia eliminada com sucesso.",
    errorDeleteIdea: "Nao foi possivel eliminar a ideia",
    errorLoadAdminDashboard: "Nao foi possivel carregar o painel admin",
    focusedIdeaTitle: "Ideia em foco",
    removeFocus: "Remover foco",
    viewInFocus: "Ver em foco",
    componentsLabel: "Componentes",
    demoUser1: "Usuario demo 1: analista.finanzas / Demo1234!",
    demoUser2: "Usuario demo 2: analista.riesgo / Demo1234!",
    demoAdmin: "Admin demo: admin.valuehub / Demo1234!",
    noFilesSelected: "Nao ha arquivos selecionados.",
    tenantNoContext: "Este tenant ainda nao tem contexto base. Complete e salve o formulario.",
    errorSessionExpired: "Sessao expirada. Entre novamente.",
    errorLoadProfile: "Nao foi possivel recuperar o perfil do usuario",
    errorLoadContext: "Nao foi possivel carregar o contexto base do tenant",
    errorLoadIdeas: "Nao foi possivel carregar suas ideias",
    errorUnexpected: "Erro inesperado",
    errorLogin: "Nao foi possivel entrar",
    errorLoadTechnicalQuestions: "Nao foi possivel carregar perguntas tecnicas",
    errorLoadingTechnical: "Erro ao carregar chat tecnico",
    errorRunTechnical: "Nao foi possivel executar validacao tecnica",
    errorTechnicalValidation: "Erro validando tecnico",
    errorGenerateArchitecture: "Nao foi possivel gerar arquitetura",
    errorGeneratingArchitecture: "Erro gerando arquitetura",
    errorLoadClarificationQuestions: "Nao foi possivel carregar perguntas de esclarecimento",
    errorLoadingClarifications: "Erro carregando esclarecimentos",
    errorProcessClarifications: "Nao foi possivel processar esclarecimentos",
    errorProcessingClarifications: "Erro processando esclarecimentos",
    errorLoadingContext: "Erro carregando contexto",
    errorSaveContext: "Nao foi possivel salvar o contexto",
    errorContextFiles: "Erro carregando arquivos de contexto",
    errorMustRegisterContext: "Primeiro voce deve registrar o contexto base do tenant para avaliar a ideia.",
    errorCreateIdea: "Nao foi possivel criar a ideia",
    riskLow: "baixa",
    riskMedium: "media",
    riskHigh: "alta",
  },
};

const architectureReportText = {
  es: {
    htmlLang: "es",
    title: "Paquete de Arquitectura",
    generatedAt: "Documento exportado",
    tabs: {
      scope: "Alcance",
      value: "Valor negocio",
      components: "Arquitectura componentes",
      services: "Servicios sugeridos",
      deployment: "Diagrama despliegue",
    },
    headings: {
      summary: "Resumen",
      suggestedMessage: "Mensaje sugerido",
      functionalScope: "Alcance funcional y tecnico",
      businessValue: "Valor para negocio",
      contextSignals: "Senales de contexto",
      nextActions: "Proximas acciones sugeridas",
        monthlyConsumption: "Consumo mensual estimado en produccion",
      componentArchitecture: "Arquitectura de componentes",
      components: "Componentes",
      componentCatalog: "Catalogo sugerido por caso",
      integrationPoints: "Puntos de integracion",
      risks: "Riesgos",
      suggestedServices: "Servicios sugeridos",
      suggestedStack: "Stack sugerido para despliegue",
      deploymentPlan: "Plan de despliegue",
      deploymentDiagram: "Diagrama de despliegue",
      deploymentFlow: "Flujo de despliegue sugerido",
      strategicKickoff: "Abordaje estrategico para iniciar desarrollo",
    },
    labels: {
      idea: "Idea",
      tenant: "Tenant",
      problem: "Problema",
      expectedValue: "Valor esperado",
      affectedUsers: "Usuarios afectados",
      industry: "Industria",
      riskTolerance: "Tolerancia de riesgo",
      valueScore: "Value score",
      riskScore: "Risk score",
      feasibility: "Factibilidad",
      complexity: "Complejidad",
      securityRisk: "Riesgo Seguridad",
      dataReadiness: "Madurez Datos",
      noData: "-",
      monthlyExecutions: "Ejecuciones mensuales",
      tokensPerExecution: "Tokens por ejecucion",
      monthlyPromptTokens: "Tokens prompt mensuales",
      monthlyCompletionTokens: "Tokens respuesta mensuales",
      estimatedMonthlyCost: "Costo mensual estimado",
      assumptions: "Supuestos",
    },
  },
  en: {
    htmlLang: "en",
    title: "Architecture Package",
    generatedAt: "Document exported",
    tabs: {
      scope: "Scope",
      value: "Business value",
      components: "Component architecture",
      services: "Suggested services",
      deployment: "Deployment diagram",
    },
    headings: {
      summary: "Summary",
      suggestedMessage: "Suggested message",
      functionalScope: "Functional and technical scope",
      businessValue: "Business value",
      contextSignals: "Context signals",
      nextActions: "Suggested next actions",
        monthlyConsumption: "Estimated monthly production consumption",
      componentArchitecture: "Component architecture",
      components: "Components",
      componentCatalog: "Case-based suggested catalog",
      integrationPoints: "Integration points",
      risks: "Risks",
      suggestedServices: "Suggested services",
      suggestedStack: "Suggested deployment stack",
      deploymentPlan: "Deployment plan",
      deploymentDiagram: "Deployment diagram",
      deploymentFlow: "Suggested deployment flow",
      strategicKickoff: "Strategic kickoff approach",
    },
    labels: {
      idea: "Idea",
      tenant: "Tenant",
      problem: "Problem",
      expectedValue: "Expected value",
      affectedUsers: "Affected users",
      industry: "Industry",
      riskTolerance: "Risk tolerance",
      valueScore: "Value score",
      riskScore: "Risk score",
      feasibility: "Feasibility",
      complexity: "Complexity",
      securityRisk: "Security risk",
      dataReadiness: "Data readiness",
      noData: "-",
      monthlyExecutions: "Monthly executions",
      tokensPerExecution: "Tokens per execution",
      monthlyPromptTokens: "Monthly prompt tokens",
      monthlyCompletionTokens: "Monthly completion tokens",
      estimatedMonthlyCost: "Estimated monthly cost",
      assumptions: "Assumptions",
    },
  },
  pt: {
    htmlLang: "pt",
    title: "Pacote de Arquitetura",
    generatedAt: "Documento exportado",
    tabs: {
      scope: "Escopo",
      value: "Valor de negocio",
      components: "Arquitetura de componentes",
      services: "Servicos sugeridos",
      deployment: "Diagrama de deploy",
    },
    headings: {
      summary: "Resumo",
      suggestedMessage: "Mensagem sugerida",
      functionalScope: "Escopo funcional e tecnico",
      businessValue: "Valor para o negocio",
      contextSignals: "Sinais de contexto",
      nextActions: "Proximas acoes sugeridas",
        monthlyConsumption: "Consumo mensal estimado em producao",
      componentArchitecture: "Arquitetura de componentes",
      components: "Componentes",
      componentCatalog: "Catalogo sugerido por caso",
      integrationPoints: "Pontos de integracao",
      risks: "Riscos",
      suggestedServices: "Servicos sugeridos",
      suggestedStack: "Stack sugerido para deploy",
      deploymentPlan: "Plano de deploy",
      deploymentDiagram: "Diagrama de deploy",
      deploymentFlow: "Fluxo de deploy sugerido",
      strategicKickoff: "Abordagem estrategica para iniciar desenvolvimento",
    },
    labels: {
      idea: "Ideia",
      tenant: "Tenant",
      problem: "Problema",
      expectedValue: "Valor esperado",
      affectedUsers: "Usuarios afetados",
      industry: "Industria",
      riskTolerance: "Tolerancia de risco",
      valueScore: "Value score",
      riskScore: "Risk score",
      feasibility: "Factibilidade",
      complexity: "Complexidade",
      securityRisk: "Risco de seguranca",
      dataReadiness: "Maturidade de dados",
      noData: "-",
      monthlyExecutions: "Ejecucoes mensais",
      tokensPerExecution: "Tokens por execucao",
      monthlyPromptTokens: "Tokens prompt mensais",
      monthlyCompletionTokens: "Tokens de resposta mensais",
      estimatedMonthlyCost: "Custo mensal estimado",
      assumptions: "Suposicoes",
    },
  },
};

const statusClass = {
  draft: "pill pill-draft",
  needs_clarification: "pill pill-warning",
  business_viable: "pill pill-success",
  rejected: "pill pill-danger",
};

const toolCatalogByLanguage = {
  es: [
    {
      tool_id: "intake-business-validation",
      name: "Intake + Validacion de Negocio",
      scope: "Registro de ideas, scoring de valor/riesgo y trazabilidad de decisiones en fase de negocio.",
      contact: "Paula Ortega (Product Owner) - paula.ortega@contoso.demo",
    },
    {
      tool_id: "technical-agent-chat",
      name: "Agente de Validacion Tecnica",
      scope: "Cuestionario tecnico guiado con analisis de factibilidad, riesgos y bloqueadores.",
      contact: "Diego Campos (Arquitectura) - diego.campos@contoso.demo",
    },
    {
      tool_id: "architecture-package",
      name: "Generador de Paquete de Arquitectura",
      scope: "Genera HTML con stack sugerido, componentes, riesgos y plan de despliegue.",
      contact: "Marina Solis (Cloud Engineering) - marina.solis@contoso.demo",
    },
    {
      tool_id: "executive-metrics",
      name: "Dashboard Ejecutivo y Metricas",
      scope: "Mide adopcion, ROI, produccion, duplicados y colaboracion por periodo.",
      contact: "Luis Varela (Data & Analytics) - luis.varela@contoso.demo",
    },
  ],
  en: [
    {
      tool_id: "intake-business-validation",
      name: "Intake + Business Validation",
      scope: "Idea intake, business value/risk scoring, and decision traceability for business stage.",
      contact: "Paula Ortega (Product Owner) - paula.ortega@contoso.demo",
    },
    {
      tool_id: "technical-agent-chat",
      name: "Technical Validation Agent",
      scope: "Guided technical questionnaire with feasibility, risk, and blocker analysis.",
      contact: "Diego Campos (Architecture) - diego.campos@contoso.demo",
    },
    {
      tool_id: "architecture-package",
      name: "Architecture Package Generator",
      scope: "Produces HTML package with suggested stack, components, risks, and deployment plan.",
      contact: "Marina Solis (Cloud Engineering) - marina.solis@contoso.demo",
    },
    {
      tool_id: "executive-metrics",
      name: "Executive Metrics Dashboard",
      scope: "Tracks adoption, ROI, production outcomes, duplicates, and collaboration trends.",
      contact: "Luis Varela (Data & Analytics) - luis.varela@contoso.demo",
    },
  ],
  pt: [
    {
      tool_id: "intake-business-validation",
      name: "Intake + Validacao de Negocio",
      scope: "Cadastro de ideias, scoring de valor/risco e rastreabilidade de decisoes na fase de negocio.",
      contact: "Paula Ortega (Product Owner) - paula.ortega@contoso.demo",
    },
    {
      tool_id: "technical-agent-chat",
      name: "Agente de Validacao Tecnica",
      scope: "Questionario tecnico guiado com analise de factibilidade, riscos e bloqueios.",
      contact: "Diego Campos (Arquitetura) - diego.campos@contoso.demo",
    },
    {
      tool_id: "architecture-package",
      name: "Gerador de Pacote de Arquitetura",
      scope: "Gera HTML com stack sugerido, componentes, riscos e plano de deploy.",
      contact: "Marina Solis (Cloud Engineering) - marina.solis@contoso.demo",
    },
    {
      tool_id: "executive-metrics",
      name: "Dashboard Executivo e Metricas",
      scope: "Mede adocao, ROI, producao, duplicidades e colaboracao por periodo.",
      contact: "Luis Varela (Data & Analytics) - luis.varela@contoso.demo",
    },
  ],
};

const demoIdeasByLanguage = {
  es: [
    {
      title: "Asistente de onboarding KYC para banca retail",
      problem_statement: "El proceso de onboarding digital tarda demasiado y genera retrabajo por validaciones manuales en KYC y fraude.",
      expected_value: "Reducir en 30% los tiempos de apertura y en 15% los casos con retrabajo en primer trimestre.",
      affected_users: ["Operacion onboarding", "Analistas de fraude", "Equipo compliance"],
    },
    {
      title: "Copiloto de respuesta para reclamos de clientes",
      problem_statement: "Los equipos de atencion tardan en consolidar politicas y evidencia para responder reclamos regulatorios complejos.",
      expected_value: "Reducir en 25% el tiempo de respuesta y mejorar consistencia de respuestas auditables.",
      affected_users: ["Atencion al cliente", "Calidad", "Riesgo operativo"],
    },
  ],
  en: [
    {
      title: "KYC onboarding assistant for retail banking",
      problem_statement: "Digital onboarding is slow and causes rework because KYC and fraud checks are still heavily manual.",
      expected_value: "Reduce account opening cycle time by 30% and first-pass rework by 15% within one quarter.",
      affected_users: ["Onboarding operations", "Fraud analysts", "Compliance team"],
    },
    {
      title: "Claims response copilot for support teams",
      problem_statement: "Support teams need too much time to consolidate policy and evidence before responding to complex regulatory claims.",
      expected_value: "Cut response turnaround by 25% and increase consistency of auditable responses.",
      affected_users: ["Customer support", "Quality", "Operational risk"],
    },
  ],
  pt: [
    {
      title: "Assistente de onboarding KYC para banco varejista",
      problem_statement: "O onboarding digital esta lento e gera retrabalho por validacoes manuais de KYC e fraude.",
      expected_value: "Reduzir em 30% o tempo de abertura e em 15% o retrabalho no primeiro trimestre.",
      affected_users: ["Operacoes de onboarding", "Analistas de fraude", "Time de compliance"],
    },
    {
      title: "Copiloto para resposta de reclamacoes",
      problem_statement: "Os times de atendimento demoram para consolidar politicas e evidencias antes de responder casos regulatorios complexos.",
      expected_value: "Reduzir em 25% o tempo de resposta e melhorar consistencia de respostas auditaveis.",
      affected_users: ["Atendimento", "Qualidade", "Risco operacional"],
    },
  ],
};

function normalizeIdeaLanguage(idea) {
  const language = (idea?.response_language || idea?.source_language || idea?.detected_language || "es").toLowerCase();
  return ["es", "en", "pt"].includes(language) ? language : "es";
}

function App() {
  const [uiLanguage, setUiLanguage] = useState(localStorage.getItem(LANG_KEY) || "en");
  const [loginForm, setLoginForm] = useState(initialLoginForm);
  const [token, setToken] = useState(localStorage.getItem(AUTH_KEY) || "");
  const [user, setUser] = useState(null);
  const [view, setView] = useState("main");
  const [showInitialWelcome, setShowInitialWelcome] = useState(true);
  const [showAdminWelcome, setShowAdminWelcome] = useState(false);
  const [welcomeLanguageIndex, setWelcomeLanguageIndex] = useState(0);
  const [showProjectInfo, setShowProjectInfo] = useState(false);

  const [form, setForm] = useState(initialForm);
  const [contextForm, setContextForm] = useState(initialContextForm);
  const [contextLoaded, setContextLoaded] = useState(false);
  const [showContextEditor, setShowContextEditor] = useState(true);
  const [selectedContextFiles, setSelectedContextFiles] = useState([]);

  const [myIdeas, setMyIdeas] = useState([]);
  const [technicalQueue, setTechnicalQueue] = useState([]);
  const [selectedIdeaId, setSelectedIdeaId] = useState("");
  const [activeClarificationIdeaId, setActiveClarificationIdeaId] = useState("");
  const [activeTechnicalIdeaId, setActiveTechnicalIdeaId] = useState("");
  const [clarificationQuestions, setClarificationQuestions] = useState([]);
  const [clarificationAnswers, setClarificationAnswers] = useState({});
  const [technicalQuestions, setTechnicalQuestions] = useState([]);
  const [technicalAnswers, setTechnicalAnswers] = useState({});
  const [technicalConversation, setTechnicalConversation] = useState([]);
  const [technicalDraft, setTechnicalDraft] = useState("");

  const [error, setError] = useState("");
  const [clarificationFeedback, setClarificationFeedback] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [seedingExamples, setSeedingExamples] = useState(false);
  const [deletingIdeaId, setDeletingIdeaId] = useState("");
  const [loadingTechnicalQueue, setLoadingTechnicalQueue] = useState(false);
  const [savingContext, setSavingContext] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const [loggingIn, setLoggingIn] = useState(false);
  const [loadingClarification, setLoadingClarification] = useState(false);
  const [loadingTechnicalQuestions, setLoadingTechnicalQuestions] = useState(false);
  const [submittingClarification, setSubmittingClarification] = useState(false);
  const [submittingResubmit, setSubmittingResubmit] = useState(false);
  const [submittingTechnical, setSubmittingTechnical] = useState(false);
  const [generatingArchitecture, setGeneratingArchitecture] = useState(false);
  const [adminDashboard, setAdminDashboard] = useState(null);
  const [adminTab, setAdminTab] = useState("useCases");
  const [baseQuotaDrafts, setBaseQuotaDrafts] = useState({});
  const [extraQuotaDrafts, setExtraQuotaDrafts] = useState({});
  const [extraQuotaReasons, setExtraQuotaReasons] = useState({});
  const [architecturePreview, setArchitecturePreview] = useState({ ideaId: "", html: "" });
  const t = uiText[uiLanguage] || uiText.es;
  const statusLabel = statusLabelByLanguage[uiLanguage] || statusLabelByLanguage.es;
  const rotatingWelcomeLanguage = WELCOME_LANGUAGES[welcomeLanguageIndex] || "es";
  const welcomeText = uiText[rotatingWelcomeLanguage] || uiText.es;
  const filteredMyIdeas = useMemo(
    () => myIdeas,
    [myIdeas],
  );
  const filteredAdminUseCases = useMemo(
    () => (adminDashboard?.approved_use_cases || []),
    [adminDashboard],
  );
  const filteredTechnicalQueue = useMemo(
    () => (technicalQueue || []),
    [technicalQueue],
  );
  const filteredProductionApps = useMemo(
    () => (adminDashboard?.token_cost?.production_apps || []),
    [adminDashboard],
  );
  const toolCatalog = useMemo(
    () => toolCatalogByLanguage[uiLanguage] || toolCatalogByLanguage.es,
    [uiLanguage],
  );
  const demoIdeas = useMemo(
    () => demoIdeasByLanguage[uiLanguage] || demoIdeasByLanguage.es,
    [uiLanguage],
  );
  const quotaUsdTotals = useMemo(
    () => filteredProductionApps.reduce(
      (acc, item) => {
        const usd = estimateQuotaUsd(item);
        acc.total += usd.quotaTotalUsd;
        acc.consumed += usd.quotaConsumedUsd;
        acc.remaining += usd.quotaRemainingUsd;
        return acc;
      },
      { total: 0, consumed: 0, remaining: 0 },
    ),
    [filteredProductionApps],
  );
  const selectedIdea = useMemo(
    () => filteredMyIdeas.find((idea) => idea.idea_id === selectedIdeaId) || null,
    [filteredMyIdeas, selectedIdeaId],
  );
  const selectedTechnicalIdea = useMemo(
    () => technicalQueue.find((idea) => idea.idea_id === selectedIdeaId) || null,
    [technicalQueue, selectedIdeaId],
  );
  const selectedIdeaPanelRef = useRef(null);

  useEffect(() => {
    if (selectedIdeaPanelRef.current) {
      selectedIdeaPanelRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [selectedIdeaId]);

  function authHeaders() {
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...authHeaders(),
      },
    });

    if (response.status === 401) {
      localStorage.removeItem(AUTH_KEY);
      setToken("");
      setUser(null);
      throw new Error(t.errorSessionExpired);
    }

    return response;
  }

  async function loadProfile() {
    const response = await apiFetch("/auth/me");
    if (!response.ok) {
      throw new Error(t.errorLoadProfile);
    }
    const profile = await response.json();
    setUser(profile);
    setForm((prev) => ({ ...prev, tenant_id: profile.tenant_id }));
    return profile;
  }

  function contextSavePath(currentUser) {
    if (currentUser?.role === "admin") {
      return `/admin/context/${currentUser.tenant_id}`;
    }
    return `/context/${currentUser?.tenant_id || ""}`;
  }

  function mapContextToForm(data) {
    return {
      company_name: data.company_name || "",
      industry: data.industry || "",
      strategic_priorities: (data.strategic_priorities || []).join(", "),
      prohibited_domains: (data.prohibited_domains || []).join(", "),
      regulatory_constraints: (data.regulatory_constraints || []).join(", "),
      operating_model_summary: data.operating_model_summary || "",
      risk_tolerance: data.risk_tolerance || "medium",
    };
  }

  async function loadContext(tenantId, role = user?.role) {
    const response = await apiFetch(`/context/${tenantId}`);
    if (response.status === 404) {
      setContextLoaded(false);
      setContextForm(initialContextForm);
      setShowContextEditor(role === "admin");
      return false;
    }
    if (!response.ok) {
      throw new Error(t.errorLoadContext);
    }
    const data = await response.json();
    setContextForm(mapContextToForm(data));
    setContextLoaded(true);
    setShowContextEditor(false);
    return true;
  }

  async function loadMyIdeas() {
    const response = await apiFetch("/ideas/mine");
    if (!response.ok) {
      throw new Error(t.errorLoadIdeas);
    }
    const data = await response.json();
    setMyIdeas(data);
  }

  async function loadTechnicalQueue(profile = user) {
    if (!profile || (profile.role !== "admin" && profile.role !== "technical")) {
      setTechnicalQueue([]);
      return;
    }
    setLoadingTechnicalQueue(true);
    try {
      const response = await apiFetch("/technical/ideas-queue");
      if (!response.ok) {
        throw new Error(t.errorLoadIdeas);
      }
      const data = await response.json();
      setTechnicalQueue(data);
    } finally {
      setLoadingTechnicalQueue(false);
    }
  }

  async function loadAdminDashboard() {
    const response = await apiFetch("/admin/dashboard");
    if (!response.ok) {
      throw new Error(t.errorLoadAdminDashboard);
    }
    const data = await response.json();
    setAdminDashboard(data);
  }

  useEffect(() => {
    const apps = adminDashboard?.token_cost?.production_apps || [];
    if (!apps.length) {
      return;
    }
    setBaseQuotaDrafts((prev) => {
      const next = { ...prev };
      apps.forEach((appItem) => {
        if (!next[appItem.idea_id]) {
          next[appItem.idea_id] = String(appItem.monthly_token_quota_base || 0);
        }
      });
      return next;
    });
    setExtraQuotaDrafts((prev) => {
      const next = { ...prev };
      apps.forEach((appItem) => {
        if (!next[appItem.idea_id]) {
          next[appItem.idea_id] = "";
        }
      });
      return next;
    });
  }, [adminDashboard]);

  async function handleUpdateDeploymentStatus(ideaId, deploymentStatus) {
    if (!ideaId || !deploymentStatus) {
      return;
    }

    setError("");
    try {
      const response = await apiFetch(`/admin/ideas/${ideaId}/deployment-status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ deployment_status: deploymentStatus }),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorLoadAdminDashboard);
      }

      await loadAdminDashboard();
      await loadMyIdeas();
      await loadTechnicalQueue();
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    }
  }

  async function handleDeleteIdea(ideaId) {
    if (!ideaId || !window.confirm(t.adminDeleteIdeaConfirm)) {
      return;
    }

    setError("");
    try {
      const response = await apiFetch(`/admin/ideas/${ideaId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorDeleteIdea);
      }

      setClarificationFeedback(t.adminIdeaDeleted);
      await loadAdminDashboard();
      await loadMyIdeas();
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    }
  }

  async function handleSetBaseQuota(ideaId) {
    const value = Number(baseQuotaDrafts[ideaId] || 0);
    if (!ideaId || !Number.isFinite(value) || value < 1000) {
      setError(t.errorUpdateQuota);
      return;
    }

    setError("");
    try {
      const response = await apiFetch(`/admin/ideas/${ideaId}/token-quota`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ monthly_token_quota_base: Math.round(value) }),
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorUpdateQuota);
      }
      setClarificationFeedback(t.adminQuotaUpdated);
      await loadAdminDashboard();
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    }
  }

  async function handleAddExtraQuota(ideaId) {
    const extraTokens = Number(extraQuotaDrafts[ideaId] || 0);
    const reason = (extraQuotaReasons[ideaId] || "").trim();
    if (!ideaId || !Number.isFinite(extraTokens) || extraTokens <= 0) {
      setError(t.errorAddQuotaExtra);
      return;
    }

    setError("");
    try {
      const response = await apiFetch(`/admin/ideas/${ideaId}/token-quota-extra`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ extra_tokens: Math.round(extraTokens), reason }),
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorAddQuotaExtra);
      }
      setClarificationFeedback(t.adminQuotaExtraAdded);
      setExtraQuotaDrafts((prev) => ({ ...prev, [ideaId]: "" }));
      setExtraQuotaReasons((prev) => ({ ...prev, [ideaId]: "" }));
      await loadAdminDashboard();
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    }
  }

  async function bootstrapSession() {
    const profile = await loadProfile();
    setShowAdminWelcome(false);
    setShowInitialWelcome(false);
    setShowContextEditor(false);
    setView(profile.role === "admin" ? "admin" : "main");
    const requests = [loadContext(profile.tenant_id, profile.role), loadMyIdeas()];
    if (profile.role === "admin") {
      requests.push(loadAdminDashboard());
      requests.push(loadTechnicalQueue(profile));
    } else if (profile.role === "technical") {
      requests.push(loadTechnicalQueue(profile));
    } else {
      setAdminDashboard(null);
      setTechnicalQueue([]);
    }
    await Promise.all(requests);
  }

  useEffect(() => {
    if (!token) {
      return;
    }
    bootstrapSession().catch((err) => setError(err.message));
  }, [token]);

  useEffect(() => {
    localStorage.setItem(LANG_KEY, uiLanguage);
    setForm((prev) => ({ ...prev, source_language: uiLanguage }));
  }, [uiLanguage]);

  useEffect(() => {
    async function handleDemoNavigation(event) {
      const trustedOrigins = ["http://127.0.0.1:5174", "http://localhost:5174", "null"];
      if (!trustedOrigins.includes(event.origin)) {
        return;
      }

      const message = event.data || {};
      if (message.type !== "AIHUB_DEMO_NAVIGATE") {
        return;
      }

      const payload = message.payload || {};

      if (["es", "en", "pt"].includes(payload.uiLanguage)) {
        setUiLanguage(payload.uiLanguage);
      }

      if (typeof payload.showProjectInfo === "boolean") {
        setShowProjectInfo(payload.showProjectInfo);
      }

      if (payload.showLoginScreen === true) {
        setShowInitialWelcome(false);
        setShowAdminWelcome(false);
      }

      if (Array.isArray(payload.demoActions) && payload.demoActions.length > 0) {
        for (const action of payload.demoActions) {
          if (!action || typeof action !== "object") {
            continue;
          }

          if (action.type === "logout") {
            handleLogout();
            continue;
          }

          if (action.type === "login") {
            const username = String(action.username || "").trim();
            const password = String(action.password || "").trim();
            if (!username || !password) {
              continue;
            }

            setLoggingIn(true);
            setError("");
            try {
              await performLogin(username, password);
            } catch (err) {
              setError(err.message || t.errorUnexpected);
            } finally {
              setLoggingIn(false);
            }
          }
        }
      }

      if (!user) {
        return;
      }

      if (payload.view === "main" || payload.view === "myIdeas" || payload.view === "technicalHub") {
        setView(payload.view);
      }

      if (user.role === "admin") {
        if (payload.view === "admin" || payload.view === "executiveDashboard") {
          setView(payload.view);
        }

        if (["useCases", "tokenCost", "metrics"].includes(payload.adminTab)) {
          setAdminTab(payload.adminTab);
          setView("admin");
        }
      }
    }

    window.addEventListener("message", handleDemoNavigation);
    return () => window.removeEventListener("message", handleDemoNavigation);
  }, [user]);

  useEffect(() => {
    if (!(showInitialWelcome || showAdminWelcome)) {
      return;
    }

    const timer = setInterval(() => {
      setWelcomeLanguageIndex((prev) => (prev + 1) % WELCOME_LANGUAGES.length);
    }, 2500);

    return () => clearInterval(timer);
  }, [showInitialWelcome, showAdminWelcome]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleContextChange(event) {
    const { name, value } = event.target;
    setContextForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleLoginChange(event) {
    const { name, value } = event.target;
    setLoginForm((prev) => ({ ...prev, [name]: value }));
  }

  async function performLogin(username, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const body = await response.json();
      throw new Error(body.detail || t.errorLogin);
    }

    const session = await response.json();
    localStorage.setItem(AUTH_KEY, session.access_token);
    setToken(session.access_token);
    setShowInitialWelcome(false);
    setShowAdminWelcome(false);
    setLoginForm(initialLoginForm);
    return session;
  }

  async function handleLoginSubmit(event) {
    event.preventDefault();
    setLoggingIn(true);
    setError("");

    try {
      await performLogin(loginForm.username, loginForm.password);
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    } finally {
      setLoggingIn(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(AUTH_KEY);
    setToken("");
    setUser(null);
    setView("main");
    setMyIdeas([]);
    setTechnicalQueue([]);
    setSelectedIdeaId("");
    setActiveClarificationIdeaId("");
    setActiveTechnicalIdeaId("");
    setClarificationQuestions([]);
    setClarificationAnswers({});
    setTechnicalQuestions([]);
    setTechnicalAnswers({});
    setTechnicalConversation([]);
    setTechnicalDraft("");
    setContextLoaded(false);
    setContextForm(initialContextForm);
    setForm(initialForm);
    setShowContextEditor(false);
    setShowAdminWelcome(false);
    setShowInitialWelcome(true);
    setSelectedContextFiles([]);
    setClarificationFeedback("");
    setUploadMessage("");
    setWelcomeLanguageIndex(0);
    setAdminDashboard(null);
    setAdminTab("useCases");
  }

  function stageLabel(stage) {
    if (stage === "idea_intake") {
      return t.stageIdeaIntake;
    }
    if (stage === "business_validation") {
      return t.stageBusinessValidation;
    }
    if (stage === "technical_validation") {
      return t.stageTechnicalValidation;
    }
    return stage;
  }

  function handleClarificationAnswerChange(questionId, value) {
    setClarificationAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  async function openTechnicalPanel(idea) {
    const ideaId = idea.idea_id;
    setLoadingTechnicalQuestions(true);
    setError("");
    setActiveTechnicalIdeaId("");
    try {
      const response = await apiFetch(`/ideas/${ideaId}/technical-questions`);
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorLoadTechnicalQuestions);
      }
      const data = await response.json();
      const initialAnswers = {};
      (data.questions || []).forEach((question) => {
        initialAnswers[question.question_id] = "";
      });
      setSelectedIdeaId(ideaId);
      setTechnicalQuestions(data.questions || []);
      setTechnicalAnswers(initialAnswers);
      const firstQuestion = (data.questions || [])[0];
      const initialConversation = [
        { role: "agent", text: t.technicalChatWelcome },
      ];
      if (firstQuestion) {
        initialConversation.push({
          role: "agent",
          text: `${firstQuestion.prompt}\n${t.technicalChatRationale}: ${firstQuestion.rationale}`,
        });
      }
      setTechnicalConversation(initialConversation);
      setTechnicalDraft("");
      setActiveTechnicalIdeaId(ideaId);
    } catch (err) {
      setError(err.message || t.errorLoadingTechnical);
    } finally {
      setLoadingTechnicalQuestions(false);
    }
  }

  function handleTechnicalAnswerChange(questionId, value) {
    setTechnicalAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  function pendingTechnicalQuestion() {
    return technicalQuestions.find((question) => !(technicalAnswers[question.question_id] || "").trim()) || null;
  }

  function handleTechnicalMessageSubmit(event) {
    event.preventDefault();
    const question = pendingTechnicalQuestion();
    if (!question) {
      return;
    }

    const answer = technicalDraft.trim();
    if (answer.length < 5) {
      setError(t.technicalChatNeedMore);
      return;
    }

    setError("");
    setTechnicalAnswers((prev) => ({ ...prev, [question.question_id]: answer }));
    setTechnicalConversation((prev) => {
      const updated = [...prev, { role: "user", text: answer }];
      const nextQuestion = technicalQuestions.find((item) => {
        if (item.question_id === question.question_id) {
          return false;
        }
        return !(technicalAnswers[item.question_id] || "").trim();
      });
      if (nextQuestion) {
        updated.push({
          role: "agent",
          text: `${nextQuestion.prompt}\n${t.technicalChatRationale}: ${nextQuestion.rationale}`,
        });
      } else {
        updated.push({ role: "agent", text: t.technicalChatComplete });
      }
      return updated;
    });
    setTechnicalDraft("");
  }

  function hasTechnicalValidation(idea) {
    const hasScore = Number.isFinite(Number(idea?.technical_validation?.feasibility_score));
    const hasChat = (idea?.technical_interactions || []).length > 0;
    return hasScore && (hasChat || Boolean(idea?.architecture_package));
  }

  function normalizeForSimilarity(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function tokenSet(value) {
    const stop = new Set(["para", "con", "por", "una", "uno", "las", "los", "que", "del", "de", "and", "the", "for", "with"]);
    return new Set(
      normalizeForSimilarity(value)
        .split(" ")
        .filter((item) => item.length > 3 && !stop.has(item)),
    );
  }

  function jaccard(left, right) {
    if (!left.size || !right.size) {
      return 0;
    }
    let intersection = 0;
    left.forEach((item) => {
      if (right.has(item)) {
        intersection += 1;
      }
    });
    const union = new Set([...left, ...right]).size;
    return union ? intersection / union : 0;
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatUsd(value) {
    const numeric = Number(value || 0);
    return new Intl.NumberFormat(uiLanguage === "es" ? "es-ES" : uiLanguage === "pt" ? "pt-BR" : "en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(Number.isFinite(numeric) ? numeric : 0);
  }

  function formatInt(value) {
    const numeric = Number(value || 0);
    return new Intl.NumberFormat(uiLanguage === "es" ? "es-ES" : uiLanguage === "pt" ? "pt-BR" : "en-US", {
      maximumFractionDigits: 0,
    }).format(Number.isFinite(numeric) ? numeric : 0);
  }

  function estimateQuotaUsd(item) {
    const quotaTotalTokens = Math.max(0, Number(item?.quota_total_tokens || 0));
    const consumedTokens = Math.max(0, Number(item?.consumed_month_tokens || 0));
    const quotaRemainingTokens = Math.max(0, Number(item?.quota_remaining_tokens || 0));

    const quotaTotalUsd = (quotaTotalTokens / QUOTA_TOKENS_PER_INTERACTION) * QUOTA_COST_PER_INTERACTION_USD;
    const quotaConsumedUsd = (consumedTokens / QUOTA_TOKENS_PER_INTERACTION) * QUOTA_COST_PER_INTERACTION_USD;
    const quotaRemainingUsd = (quotaRemainingTokens / QUOTA_TOKENS_PER_INTERACTION) * QUOTA_COST_PER_INTERACTION_USD;

    return {
      quotaTotalUsd,
      quotaConsumedUsd,
      quotaRemainingUsd,
    };
  }

  function quotaClockIcon(usagePct) {
    const pct = Number(usagePct || 0);
    if (pct < 25) return "🕐";
    if (pct < 50) return "🕓";
    if (pct < 75) return "🕗";
    if (pct < 90) return "🕙";
    return "⏰";
  }

  function buildServiceSuggestions(idea) {
    const notes = String(idea?.technical_validation?.assumptions?.join(" ") || "").toLowerCase();
    const contextSignals = String(idea?.business_validation?.context_signals?.join(" ") || "").toLowerCase();
    const lang = idea?.response_language || uiLanguage;
    const text = {
      es: {
        agnosticTitle: "Ruta agnostica (base portable):",
        azureTitle: "Ruta full Azure (acelerada):",
        optionalTitle: "Ajustes opcionales por caso:",
        agnostic: [
          "Contenedores para API/frontend (Docker + runtime estandar)",
          "Base SQL portable (PostgreSQL compatible)",
          "Object Storage compatible S3",
          "Observabilidad con OpenTelemetry + stack SIEM",
        ],
        azure: [
          "Azure Container Apps para API y frontend",
          "Azure OpenAI Service para orquestacion de prompts y respuestas",
          "Azure AI Search para grounding de contexto empresarial",
          "Azure AI Document Intelligence para parseo de documentos de contexto",
          "Azure API Management para gobierno y seguridad de APIs",
          "Azure Database for PostgreSQL o SQL Database para persistencia",
          "Azure Blob Storage para artefactos de contexto",
          "Azure Key Vault para secretos",
          "Application Insights para observabilidad",
        ],
        entra: "Microsoft Entra ID + RBAC para control de acceso por rol",
        serviceBus: "Azure Service Bus para integraciones asincronas",
        dataFactory: "Azure Data Factory para preparacion e ingesta de datos",
        analytics: "Microsoft Fabric o Synapse para analitica avanzada y trazabilidad",
      },
      en: {
        agnosticTitle: "Agnostic route (portable baseline):",
        azureTitle: "Full Azure route (accelerated):",
        optionalTitle: "Optional case-based adjustments:",
        agnostic: [
          "Containers for API/frontend (Docker + standard runtime)",
          "Portable SQL database (PostgreSQL compatible)",
          "S3-compatible object storage",
          "Observability with OpenTelemetry + SIEM stack",
        ],
        azure: [
          "Azure Container Apps for API and frontend",
          "Azure OpenAI Service for prompt orchestration and response generation",
          "Azure AI Search for enterprise context grounding",
          "Azure AI Document Intelligence for context document parsing",
          "Azure API Management for API governance and security",
          "Azure Database for PostgreSQL or SQL Database for persistence",
          "Azure Blob Storage for context artifacts",
          "Azure Key Vault for secrets",
          "Application Insights for observability",
        ],
        entra: "Microsoft Entra ID + RBAC for role-based access control",
        serviceBus: "Azure Service Bus for asynchronous integrations",
        dataFactory: "Azure Data Factory for data preparation and ingestion",
        analytics: "Microsoft Fabric or Synapse for advanced analytics and traceability",
      },
      pt: {
        agnosticTitle: "Rota agnostica (baseline portavel):",
        azureTitle: "Rota full Azure (acelerada):",
        optionalTitle: "Ajustes opcionais por caso:",
        agnostic: [
          "Containers para API/frontend (Docker + runtime padrao)",
          "Banco SQL portavel (compativel com PostgreSQL)",
          "Object Storage compativel com S3",
          "Observabilidade com OpenTelemetry + stack SIEM",
        ],
        azure: [
          "Azure Container Apps para API e frontend",
          "Azure OpenAI Service para orquestracao de prompts e respostas",
          "Azure AI Search para grounding de contexto empresarial",
          "Azure AI Document Intelligence para parsing de documentos de contexto",
          "Azure API Management para governanca e seguranca de APIs",
          "Azure Database for PostgreSQL ou SQL Database para persistencia",
          "Azure Blob Storage para artefatos de contexto",
          "Azure Key Vault para segredos",
          "Application Insights para observabilidade",
        ],
        entra: "Microsoft Entra ID + RBAC para controle de acesso por papel",
        serviceBus: "Azure Service Bus para integracoes assincronas",
        dataFactory: "Azure Data Factory para preparacao e ingestao de dados",
        analytics: "Microsoft Fabric ou Synapse para analitica avancada e rastreabilidade",
      },
    };

    const s = text[lang] || text.es;
    const services = [
      s.agnosticTitle,
      ...s.agnostic,
      s.azureTitle,
      ...s.azure,
    ];
    const optional = [];

    if ((idea.technical_validation?.security_risk || 0) >= 50) {
      optional.push(s.entra);
    }
    if ((idea.technical_validation?.integration_complexity || 0) >= 55) {
      optional.push(s.serviceBus);
    }
    if ((idea.technical_validation?.data_readiness || 0) < 55 || notes.includes("datos") || notes.includes("data") || contextSignals.includes("data")) {
      optional.push(s.dataFactory);
    }
    if (contextSignals.includes("fraude") || contextSignals.includes("fraud") || contextSignals.includes("riesgo") || contextSignals.includes("risk")) {
      optional.push(s.analytics);
    }

    if (optional.length > 0) {
      services.push(s.optionalTitle, ...optional);
    }

    return services;
  }

  function buildDynamicDeploymentDiagram(idea, rt, labels) {
    const packageData = idea?.architecture_package || {};
    const rawComponents = (packageData.components || []).map((component) => String(component?.name || "").trim()).filter(Boolean);
    const dedupedComponents = Array.from(new Set(rawComponents));

    const baseNodes = [labels.affectedUsers, ...dedupedComponents];
    const fallbackNodes = [
      labels.affectedUsers,
      "Frontend",
      "API",
      "Context Engine",
      "Validation Agent",
    ];
    const primaryNodes = (baseNodes.length > 1 ? baseNodes : fallbackNodes).slice(0, 7);

    const serviceCandidates = buildServiceSuggestions(idea)
      .filter((item) => !item.endsWith(":"))
      .slice(0, 4);

    const columnWidth = 210;
    const nodeWidth = 185;
    const nodeHeight = 66;
    const startX = 36;
    const topY = 38;
    const bottomY = 168;
    const hasServices = serviceCandidates.length > 0;
    const viewWidth = Math.max(980, startX * 2 + columnWidth * Math.max(primaryNodes.length, serviceCandidates.length || 1));
    const viewHeight = hasServices ? 322 : 170;

    const palette = [
      { fill: "#eff6ff", stroke: "#93c5fd", text: "#1e3a8a" },
      { fill: "#ecfeff", stroke: "#67e8f9", text: "#0f766e" },
      { fill: "#f0fdf4", stroke: "#86efac", text: "#166534" },
      { fill: "#fefce8", stroke: "#fde047", text: "#854d0e" },
      { fill: "#fdf4ff", stroke: "#e879f9", text: "#86198f" },
      { fill: "#fff7ed", stroke: "#fdba74", text: "#9a3412" },
      { fill: "#f8fafc", stroke: "#cbd5e1", text: "#334155" },
    ];

    const servicePalette = { fill: "#f1f5f9", stroke: "#cbd5e1", text: "#1e293b" };

    const primaryBoxes = primaryNodes
      .map((label, index) => {
        const color = palette[index % palette.length];
        const x = startX + index * columnWidth;
        const centerX = x + nodeWidth / 2;
        return `
        <g>
          <rect x="${x}" y="${topY}" width="${nodeWidth}" height="${nodeHeight}" rx="10" fill="${color.fill}" stroke="${color.stroke}"/>
          <text x="${centerX}" y="${topY + 38}" text-anchor="middle" font-size="13" fill="${color.text}">${escapeHtml(label)}</text>
        </g>`;
      })
      .join("");

    const primaryLinks = primaryNodes
      .slice(0, -1)
      .map((_, index) => {
        const x1 = startX + index * columnWidth + nodeWidth;
        const x2 = startX + (index + 1) * columnWidth;
        const y = topY + nodeHeight / 2;
        return `<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="#475569" stroke-width="2"/>`;
      })
      .join("");

    const serviceBoxes = serviceCandidates
      .map((label, index) => {
        const x = startX + index * columnWidth;
        const centerX = x + nodeWidth / 2;
        return `
        <g>
          <rect x="${x}" y="${bottomY}" width="${nodeWidth}" height="${nodeHeight}" rx="10" fill="${servicePalette.fill}" stroke="${servicePalette.stroke}"/>
          <text x="${centerX}" y="${bottomY + 38}" text-anchor="middle" font-size="12" fill="${servicePalette.text}">${escapeHtml(label)}</text>
        </g>`;
      })
      .join("");

    const serviceLinks = hasServices
      ? serviceCandidates
        .map((_, index) => {
          const sourceIndex = Math.min(2, primaryNodes.length - 1);
          const x1 = startX + sourceIndex * columnWidth + nodeWidth / 2;
          const y1 = topY + nodeHeight;
          const x2 = startX + index * columnWidth + nodeWidth / 2;
          const y2 = bottomY;
          return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#64748b" stroke-width="1.8"/>`;
        })
        .join("")
      : "";

    return `
      <svg viewBox="0 0 ${viewWidth} ${viewHeight}" role="img" aria-label="${escapeHtml(rt.headings.deploymentDiagram)}" style="width:100%;height:auto;border:1px solid #e2e8f0;border-radius:12px;background:#fff;">
        ${primaryLinks}
        ${serviceLinks}
        ${primaryBoxes}
        ${serviceBoxes}
      </svg>
    `;
  }

  function buildStrategicKickoffPlan(idea, lang) {
    const technical = idea?.technical_validation || {};
    const packageData = idea?.architecture_package || {};
    const hasIntegrations = (packageData.integration_points || []).length > 0;
    const highSecurityRisk = (technical.security_risk || 0) >= 50;
    const lowDataReadiness = (technical.data_readiness || 100) < 55;

    const planByLang = {
      es: [
        "Sprint 0: definir alcance MVP, criterios de exito y matriz de responsables entre negocio, arquitectura y seguridad.",
        "Fundacion tecnica: provisionar entorno base, repositorio, CI/CD, observabilidad y gestion de secretos antes del primer release.",
        hasIntegrations
          ? "Integraciones criticas: priorizar conectores y contratos de API para reducir riesgo de dependencias tempranas."
          : "Integraciones: validar contratos de API principales y establecer mocks para acelerar el primer incremento.",
        lowDataReadiness
          ? "Datos: ejecutar un frente inicial de calidad y disponibilidad de datos para evitar bloqueos en pruebas funcionales."
          : "Datos: confirmar fuentes, periodicidad y reglas de calidad para sostener una validacion estable.",
        highSecurityRisk
          ? "Seguridad desde el inicio: aplicar hardening, identidad (Entra/RBAC), cifrado y revisiones de amenazas desde Sprint 1."
          : "Seguridad operativa: incluir controles de identidad, secretos y telemetria desde el primer entorno.",
        "Primer valor en produccion: entregar un vertical slice end-to-end y medir adopcion, tiempos de ciclo y retrabajo para iterar.",
      ],
      en: [
        "Sprint 0: align MVP scope, success criteria, and ownership across business, architecture, and security.",
        "Technical foundation: establish baseline environment, repository, CI/CD, observability, and secrets management before first release.",
        hasIntegrations
          ? "Critical integrations: prioritize connectors and API contracts early to reduce dependency risk."
          : "Integrations: validate core API contracts and use mocks to accelerate the first increment.",
        lowDataReadiness
          ? "Data readiness: run an early workstream for data quality and availability to avoid test-phase blockers."
          : "Data readiness: confirm data sources, refresh cadence, and quality rules for stable validation.",
        highSecurityRisk
          ? "Security by design: apply hardening, identity controls (Entra/RBAC), encryption, and threat review from Sprint 1."
          : "Operational security: include identity, secrets, and telemetry controls from the first environment.",
        "First production value: deliver one end-to-end vertical slice and measure adoption, cycle time, and rework to guide iteration.",
      ],
      pt: [
        "Sprint 0: alinhar escopo MVP, criterios de sucesso e responsabilidades entre negocio, arquitetura e seguranca.",
        "Fundacao tecnica: preparar ambiente base, repositorio, CI/CD, observabilidade e gestao de segredos antes do primeiro release.",
        hasIntegrations
          ? "Integracoes criticas: priorizar conectores e contratos de API cedo para reduzir risco de dependencias."
          : "Integracoes: validar contratos principais de API e usar mocks para acelerar o primeiro incremento.",
        lowDataReadiness
          ? "Dados: executar uma frente inicial de qualidade e disponibilidade para evitar bloqueios na fase de testes."
          : "Dados: confirmar fontes, frequencia de atualizacao e regras de qualidade para validacao estavel.",
        highSecurityRisk
          ? "Seguranca desde o inicio: aplicar hardening, identidade (Entra/RBAC), criptografia e revisao de ameacas desde Sprint 1."
          : "Seguranca operacional: incluir controles de identidade, segredos e telemetria desde o primeiro ambiente.",
        "Primeiro valor em producao: entregar um vertical slice end-to-end e medir adocao, ciclo e retrabalho para iterar.",
      ],
    };

    return planByLang[lang] || planByLang.es;
  }

  function buildArchitecturePackageHtml(idea) {
    const lang = idea?.response_language || uiLanguage;
    const rt = architectureReportText[lang] || architectureReportText.es;
    const labels = rt.labels;
    const packageData = idea.architecture_package || {};
    const technical = idea.technical_validation || {};
    const response = idea.response_composition || {};
    const business = idea.business_validation || {};
    const context = idea.context_snapshot || {};
    const consumption = packageData.monthly_production_consumption || null;
    const locale = lang === "pt" ? "pt-BR" : lang === "en" ? "en-US" : "es-ES";
    const formatMoney = (value) => new Intl.NumberFormat(locale, {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(Number(value || 0));

    const components = (packageData.components || [])
      .map((component) => `<li><strong>${escapeHtml(component.name)}:</strong> ${escapeHtml(component.purpose)}</li>`)
      .join("");

    const suggestedCatalog = (packageData.suggested_component_catalog || [])
      .map((component) => `<li><strong>${escapeHtml(component.name)}:</strong> ${escapeHtml(component.purpose)}</li>`)
      .join("");

    const integrationPoints = (packageData.integration_points || [])
      .map((item) => `<li>${escapeHtml(item)}</li>`)
      .join("");

    const deploymentSteps = (packageData.deployment_steps || [])
      .map((item) => `<li>${escapeHtml(item)}</li>`)
      .join("");

    const risks = (packageData.risks || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");

    const nextActions = (response.next_actions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    const suggestedServices = buildServiceSuggestions(idea).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    const strategicKickoffPlan = buildStrategicKickoffPlan(idea, lang).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    const monthlyConsumptionAssumptions = (consumption?.assumptions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");

    const strategicPriorities = (context.strategic_priorities || [])
      .map((item) => `<li>${escapeHtml(item)}</li>`)
      .join("");

    const diagram = buildDynamicDeploymentDiagram(idea, rt, labels);

    return `<!doctype html>
<html lang="${escapeHtml(rt.htmlLang)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(rt.title)} - ${escapeHtml(idea.title)}</title>
  <style>
    :root {
      --bg: #f6f8fb;
      --card: #ffffff;
      --ink: #0f172a;
      --muted: #475569;
      --line: #dbe3ef;
      --brand: #0b5fff;
      --brand-soft: #e8f0ff;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); color: var(--ink); }
    .container { max-width: 1100px; margin: 24px auto; padding: 0 16px 28px; }
    .hero { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 20px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); }
    .hero h1 { margin: 0 0 10px; font-size: 1.5rem; }
    .meta { color: var(--muted); margin: 4px 0; }
    .kpis { margin-top: 16px; display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; }
    .kpi { background: var(--brand-soft); border: 1px solid #c9dafd; border-radius: 12px; padding: 10px 12px; }
    .kpi b { display: block; font-size: 1.1rem; margin-top: 4px; }
    .tabs { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 8px; }
    .tab-btn { border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 10px 12px; border-radius: 10px; cursor: pointer; font-weight: 600; }
    .tab-btn.active { background: var(--brand); color: #fff; border-color: var(--brand); }
    .panel { display: none; margin-top: 12px; background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px; }
    .panel.active { display: block; }
    h2 { margin: 0 0 10px; font-size: 1.1rem; }
    ul { margin: 0; padding-left: 20px; }
    li { margin: 6px 0; }
    .two-col { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }
    .note { background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 10px 12px; color: var(--muted); }
  </style>
</head>
<body>
  <div class="container">
    <section class="hero">
      <h1>${escapeHtml(packageData.solution_name || idea.title || rt.title)}</h1>
      <p class="meta"><strong>${escapeHtml(labels.idea)}:</strong> ${escapeHtml(idea.title)} | <strong>${escapeHtml(labels.tenant)}:</strong> ${escapeHtml(idea.tenant_id)}</p>
      <p class="meta"><strong>${escapeHtml(rt.headings.summary)}:</strong> ${escapeHtml(packageData.summary || labels.noData)}</p>
      <p class="meta"><strong>${escapeHtml(rt.headings.suggestedMessage)}:</strong> ${escapeHtml(response.message || labels.noData)}</p>
      <div class="kpis">
        <div class="kpi">${escapeHtml(labels.feasibility)}<b>${escapeHtml(technical.feasibility_score ?? labels.noData)}</b></div>
        <div class="kpi">${escapeHtml(labels.complexity)}<b>${escapeHtml(technical.integration_complexity ?? labels.noData)}</b></div>
        <div class="kpi">${escapeHtml(labels.securityRisk)}<b>${escapeHtml(technical.security_risk ?? labels.noData)}</b></div>
        <div class="kpi">${escapeHtml(labels.dataReadiness)}<b>${escapeHtml(technical.data_readiness ?? labels.noData)}</b></div>
      </div>
      ${consumption ? `
      <div style="margin-top:14px;padding:14px;border:1px solid #dbe3ef;border-radius:14px;background:#f8fafc;">
        <h2 style="margin:0 0 10px;">${escapeHtml(rt.headings.monthlyConsumption)}</h2>
        <div class="two-col">
          <div>
            <ul>
              <li><strong>${escapeHtml(labels.monthlyExecutions)}:</strong> ${escapeHtml(consumption.monthly_executions)}</li>
              <li><strong>${escapeHtml(labels.tokensPerExecution)}:</strong> ${escapeHtml(consumption.prompt_tokens_per_execution)} / ${escapeHtml(consumption.completion_tokens_per_execution)}</li>
            </ul>
          </div>
          <div>
            <ul>
              <li><strong>${escapeHtml(labels.monthlyPromptTokens)}:</strong> ${escapeHtml(consumption.monthly_prompt_tokens)}</li>
              <li><strong>${escapeHtml(labels.monthlyCompletionTokens)}:</strong> ${escapeHtml(consumption.monthly_completion_tokens)}</li>
              <li><strong>${escapeHtml(labels.estimatedMonthlyCost)}:</strong> ${escapeHtml(formatMoney(consumption.estimated_monthly_cost_usd))}</li>
            </ul>
          </div>
        </div>
        <div class="note" style="margin-top:10px;">
          <strong>${escapeHtml(labels.assumptions)}:</strong>
          <ul>${monthlyConsumptionAssumptions || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
        </div>
      </div>
      ` : ""}
    </section>

    <div class="tabs" role="tablist">
      <button class="tab-btn active" data-tab="alcance" type="button">${escapeHtml(rt.tabs.scope)}</button>
      <button class="tab-btn" data-tab="valor" type="button">${escapeHtml(rt.tabs.value)}</button>
      <button class="tab-btn" data-tab="componentes" type="button">${escapeHtml(rt.tabs.components)}</button>
      <button class="tab-btn" data-tab="servicios" type="button">${escapeHtml(rt.tabs.services)}</button>
      <button class="tab-btn" data-tab="despliegue" type="button">${escapeHtml(rt.tabs.deployment)}</button>
    </div>

    <section class="panel active" data-panel="alcance">
      <h2>${escapeHtml(rt.headings.functionalScope)}</h2>
      <div class="two-col">
        <div>
          <p class="meta"><strong>${escapeHtml(labels.problem)}:</strong> ${escapeHtml(idea.problem_statement || labels.noData)}</p>
          <p class="meta"><strong>${escapeHtml(labels.expectedValue)}:</strong> ${escapeHtml(idea.expected_value || labels.noData)}</p>
          <p class="meta"><strong>${escapeHtml(labels.affectedUsers)}:</strong> ${escapeHtml((idea.affected_users || []).join(", ") || labels.noData)}</p>
        </div>
        <div>
          <p class="meta"><strong>${escapeHtml(labels.industry)}:</strong> ${escapeHtml(context.industry || labels.noData)}</p>
          <p class="meta"><strong>${escapeHtml(labels.riskTolerance)}:</strong> ${escapeHtml(context.risk_tolerance || labels.noData)}</p>
          <ul>${strategicPriorities || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
        </div>
      </div>
    </section>

    <section class="panel" data-panel="valor">
      <h2>${escapeHtml(rt.headings.businessValue)}</h2>
      <div class="two-col">
        <div>
          <ul>
            <li><strong>${escapeHtml(labels.valueScore)}:</strong> ${escapeHtml(business.value_score ?? labels.noData)}</li>
            <li><strong>${escapeHtml(labels.riskScore)}:</strong> ${escapeHtml(business.risk_score ?? labels.noData)}</li>
          </ul>
          <h2 style="margin-top:12px;">${escapeHtml(rt.headings.contextSignals)}</h2>
          <ul>${(business.context_signals || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
        </div>
        <div>
          <h2>${escapeHtml(rt.headings.nextActions)}</h2>
          <ul>${nextActions || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
          <div class="note" style="margin-top:10px;">${escapeHtml(rt.generatedAt)}: ${escapeHtml(new Date().toLocaleString())}</div>
        </div>
      </div>
    </section>

    <section class="panel" data-panel="componentes">
      <h2>${escapeHtml(rt.headings.componentArchitecture)}</h2>
      <div class="two-col">
        <div>
          <h2>${escapeHtml(rt.headings.components)}</h2>
          <ul>${components || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
          <h2 style="margin-top:12px;">${escapeHtml(rt.headings.componentCatalog)}</h2>
          <ul>${suggestedCatalog || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
        </div>
        <div>
          <h2>${escapeHtml(rt.headings.integrationPoints)}</h2>
          <ul>${integrationPoints || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
          <h2 style="margin-top:12px;">${escapeHtml(rt.headings.risks)}</h2>
          <ul>${risks || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
        </div>
      </div>
    </section>

    <section class="panel" data-panel="servicios">
      <h2>${escapeHtml(rt.headings.suggestedStack)}</h2>
      <ul>${suggestedServices || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
      <h2 style="margin-top:12px;">${escapeHtml(rt.headings.deploymentPlan)}</h2>
      <ul>${deploymentSteps || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
      <h2 style="margin-top:12px;">${escapeHtml(rt.headings.strategicKickoff)}</h2>
      <ul>${strategicKickoffPlan || `<li>${escapeHtml(labels.noData)}</li>`}</ul>
    </section>

    <section class="panel" data-panel="despliegue">
      <h2>${escapeHtml(rt.headings.deploymentFlow)}</h2>
      <p class="meta">${escapeHtml(rt.headings.deploymentDiagram)}: ${escapeHtml(packageData.solution_name || idea.title || labels.noData)}</p>
      ${diagram}
    </section>
  </div>

  <script>
    const buttons = Array.from(document.querySelectorAll('.tab-btn'));
    const panels = Array.from(document.querySelectorAll('.panel'));
    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const target = button.getAttribute('data-tab');
        buttons.forEach((item) => item.classList.toggle('active', item === button));
        panels.forEach((panel) => panel.classList.toggle('active', panel.getAttribute('data-panel') === target));
      });
    });
  </script>
</body>
</html>`;
  }

  function handleDownloadArchitecturePackage(idea) {
    if (!idea?.architecture_package) {
      return;
    }

    const fileBase = (idea.title || "idea")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
    const filename = `${fileBase || idea.idea_id}-architecture-package.html`;

    const html = buildArchitecturePackageHtml(idea);
    const blob = new Blob([html], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  }

  function handlePreviewArchitecturePackage(idea) {
    if (!idea?.architecture_package) {
      return;
    }
    setArchitecturePreview({
      ideaId: idea.idea_id,
      html: buildArchitecturePackageHtml(idea),
    });
  }

  async function handleTechnicalValidationSubmit(event, ideaId) {
    event?.preventDefault();

    setSubmittingTechnical(true);
    setError("");

    try {
      const payload = {
        answers: technicalQuestions.map((question) => ({
          question_id: question.question_id,
          answer: (technicalAnswers[question.question_id] || "").trim(),
        })),
      };

      const response = await apiFetch(`/ideas/${ideaId}/technical-chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorRunTechnical);
      }

      await loadMyIdeas();
      await loadTechnicalQueue();
      setActiveTechnicalIdeaId("");
      setTechnicalQuestions([]);
      setTechnicalAnswers({});
      setTechnicalConversation([]);
      setTechnicalDraft("");
    } catch (err) {
      setError(err.message || t.errorTechnicalValidation);
    } finally {
      setSubmittingTechnical(false);
    }
  }

  async function handleGenerateArchitecture(ideaId) {
    setGeneratingArchitecture(true);
    setError("");

    try {
      const response = await apiFetch(`/ideas/${ideaId}/architecture-package`, {
        method: "POST",
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorGenerateArchitecture);
      }

      await loadMyIdeas();
      await loadTechnicalQueue();
    } catch (err) {
      setError(err.message || t.errorGeneratingArchitecture);
    } finally {
      setGeneratingArchitecture(false);
    }
  }

  async function openClarificationPanel(ideaId) {
    if (!ideaId) {
      return;
    }
    setLoadingClarification(true);
    setError("");
    setClarificationFeedback("");
    try {
      const response = await apiFetch(`/ideas/${ideaId}/clarification-questions`);
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorLoadClarificationQuestions);
      }

      const data = await response.json();
      const initialAnswers = {};
      (data.questions || []).forEach((question) => {
        initialAnswers[question.question_id] = "";
      });

      setSelectedIdeaId(ideaId);
      setActiveClarificationIdeaId(ideaId);
      setClarificationQuestions(data.questions || []);
      setClarificationAnswers(initialAnswers);
    } catch (err) {
      setError(err.message || t.errorLoadingClarifications);
    } finally {
      setLoadingClarification(false);
    }
  }

  async function handleClarificationSubmit(event, ideaId) {
    event.preventDefault();
    if (!ideaId) {
      return;
    }

    setSubmittingClarification(true);
    setError("");
    setClarificationFeedback("");

    try {
      const answers = clarificationQuestions.map((question) => ({
        question_id: question.question_id,
        answer: (clarificationAnswers[question.question_id] || "").trim(),
      }));

      const response = await apiFetch(`/ideas/${ideaId}/clarify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorProcessClarifications);
      }

      const updatedIdea = await response.json();
      await loadMyIdeas();
      await loadTechnicalQueue();
      setSelectedIdeaId(updatedIdea.idea_id);
      if (updatedIdea.status === "needs_clarification") {
        setActiveClarificationIdeaId(updatedIdea.idea_id);
        setClarificationQuestions(updatedIdea.clarification_questions || []);
        const nextAnswers = {};
        (updatedIdea.clarification_questions || []).forEach((question) => {
          nextAnswers[question.question_id] = "";
        });
        setClarificationAnswers(nextAnswers);
      } else {
        setActiveClarificationIdeaId("");
        setClarificationQuestions([]);
        setClarificationAnswers({});
      }
      if (updatedIdea.status === "business_viable" && !hasTechnicalValidation(updatedIdea)) {
        await openTechnicalPanel(updatedIdea);
      }
      setClarificationFeedback(
        updatedIdea.status === "rejected"
          ? t.clarificationDoneRejected
          : updatedIdea.status === "needs_clarification"
            ? t.clarificationStillNeeded
            : t.clarificationDoneViable,
      );
    } catch (err) {
      setError(err.message || t.errorProcessingClarifications);
    } finally {
      setSubmittingClarification(false);
    }
  }

  async function handleResubmitForReview(ideaId) {
    if (!ideaId) {
      return;
    }

    setSubmittingResubmit(true);
    setError("");
    setClarificationFeedback("");

    try {
      const response = await apiFetch(`/ideas/${ideaId}/resubmit-for-review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.resubmitFailed);
      }

      const updatedIdea = await response.json();
      await loadMyIdeas();
      await loadTechnicalQueue();
      setSelectedIdeaId(updatedIdea.idea_id);
      if (updatedIdea.status === "needs_clarification") {
        setActiveClarificationIdeaId(updatedIdea.idea_id);
        setClarificationQuestions(updatedIdea.clarification_questions || []);
        const nextAnswers = {};
        (updatedIdea.clarification_questions || []).forEach((question) => {
          nextAnswers[question.question_id] = "";
        });
        setClarificationAnswers(nextAnswers);
      }
      setClarificationFeedback(t.resubmitSuccess);
    } catch (err) {
      setError(err.message || t.resubmitFailed);
    } finally {
      setSubmittingResubmit(false);
    }
  }

  async function handleLoadContext() {
    if (!user) {
      return;
    }
    setError("");
    try {
      const found = await loadContext(user.tenant_id);
      if (!found) {
        setError(t.tenantNoContext);
      }
    } catch (err) {
      setError(err.message || t.errorLoadingContext);
    }
  }

  async function handleContextSubmit(event) {
    event.preventDefault();
    if (!user) {
      return;
    }

    setSavingContext(true);
    setError("");

    try {
      const payload = {
        company_name: contextForm.company_name,
        industry: contextForm.industry,
        strategic_priorities: contextForm.strategic_priorities
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        prohibited_domains: contextForm.prohibited_domains
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        regulatory_constraints: contextForm.regulatory_constraints
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        operating_model_summary: contextForm.operating_model_summary,
        risk_tolerance: contextForm.risk_tolerance,
      };

      const response = await apiFetch(contextSavePath(user), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorSaveContext);
      }

      const savedContext = await response.json();
      setContextForm(mapContextToForm(savedContext));
      setContextLoaded(true);
      setShowContextEditor(false);
      setUploadMessage("");
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    } finally {
      setSavingContext(false);
    }
  }

  function handleContextFilesChange(event) {
    const files = Array.from(event.target.files || []);
    setSelectedContextFiles(files);
    setUploadMessage("");
  }

  async function handleUploadContextFiles() {
    if (!user || user.role !== "admin") {
      return;
    }
    if (selectedContextFiles.length === 0) {
      setUploadMessage(t.noFilesSelected);
      return;
    }

    setUploadingFiles(true);
    setError("");

    try {
      for (const file of selectedContextFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await apiFetch(`/admin/context/${user.tenant_id}/files`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const body = await response.json();
          throw new Error(
            body.detail
              || `${t.errorContextFiles}: ${file.name}`,
          );
        }
      }

      setUploadMessage(t.uploadOk);
      setSelectedContextFiles([]);
    } catch (err) {
      setError(err.message || t.errorContextFiles);
    } finally {
      setUploadingFiles(false);
    }
  }

  function handlePrefillDemoIdea(template) {
    setForm((prev) => ({
      ...prev,
      title: template.title,
      problem_statement: template.problem_statement,
      expected_value: template.expected_value,
      affected_users: (template.affected_users || []).join(", "),
      source_language: uiLanguage,
    }));
    setView("main");
  }

  async function handleCreateDemoIdea(template) {
    if (!user) {
      return;
    }

    setSeedingExamples(true);
    setError("");
    try {
      if (!contextLoaded) {
        throw new Error(t.errorMustRegisterContext);
      }

      const payload = {
        tenant_id: user.tenant_id,
        title: template.title,
        problem_statement: template.problem_statement,
        expected_value: template.expected_value,
        affected_users: template.affected_users || [],
        source_language: uiLanguage,
      };

      const response = await apiFetch("/ideas/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorCreateIdea);
      }

      const created = await response.json();
      await loadMyIdeas();
      setSelectedIdeaId(created.idea_id);
      setView("myIdeas");
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    } finally {
      setSeedingExamples(false);
    }
  }

  async function handleDeleteOwnIdea(ideaId) {
    if (!ideaId || !window.confirm(t.deleteOwnIdeaConfirm)) {
      return;
    }

    setDeletingIdeaId(ideaId);
    setError("");
    try {
      const response = await apiFetch(`/ideas/${ideaId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorDeleteIdea);
      }

      if (selectedIdeaId === ideaId) {
        setSelectedIdeaId("");
      }
      await loadMyIdeas();
      await loadTechnicalQueue();
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    } finally {
      setDeletingIdeaId("");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!user) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      if (!contextLoaded) {
        throw new Error(t.errorMustRegisterContext);
      }

      const payload = {
        ...form,
        tenant_id: user.tenant_id,
        affected_users: form.affected_users
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      };

      const response = await apiFetch("/ideas/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || t.errorCreateIdea);
      }

      setForm((prev) => ({ ...initialForm, tenant_id: user.tenant_id }));
      await loadMyIdeas();
    } catch (err) {
      setError(err.message || t.errorUnexpected);
    } finally {
      setLoading(false);
    }
  }

  const summary = useMemo(() => {
    const totalIdeas = filteredMyIdeas.length;
    const viableIdeas = filteredMyIdeas.filter((idea) => idea.status === "business_viable").length;
    const rejectedIdeas = filteredMyIdeas.filter((idea) => idea.status === "rejected").length;
    const needsClarification = filteredMyIdeas.filter((idea) => idea.status === "needs_clarification").length;
    return { totalIdeas, viableIdeas, rejectedIdeas, needsClarification };
  }, [filteredMyIdeas]);

  const similarIdeaMap = useMemo(() => {
    const map = {};
    const viable = filteredMyIdeas.filter((idea) => idea.status === "business_viable");

    for (let i = 0; i < viable.length; i += 1) {
      for (let j = i + 1; j < viable.length; j += 1) {
        const left = viable[i];
        const right = viable[j];
        const leftTokens = tokenSet(`${left.title} ${left.problem_statement}`);
        const rightTokens = tokenSet(`${right.title} ${right.problem_statement}`);
        const similarity = jaccard(leftTokens, rightTokens);

        if (similarity >= 0.7) {
          map[left.idea_id] = right.title;
          map[right.idea_id] = left.title;
        }
      }
    }
    return map;
  }, [filteredMyIdeas]);

  if (!token || !user) {
    if (showInitialWelcome) {
      return (
        <div className="page-shell">
          <div className="ambient ambient-a" aria-hidden="true" />
          <div className="ambient ambient-b" aria-hidden="true" />
          <div className="layout auth-layout">
            <section className="card card-auth">
              <p className="eyebrow">{BRAND_NAME}</p>
              <h1>{welcomeText.welcomeTitle}</h1>
              <p className="hero-copy">{welcomeText.welcomeBody}</p>
              <div className="action-row" style={{ marginTop: 10 }}>
                <button type="button" onClick={() => setWelcomeLanguageIndex(0)}>ES</button>
                <button type="button" onClick={() => setWelcomeLanguageIndex(1)}>EN</button>
                <button type="button" onClick={() => setWelcomeLanguageIndex(2)}>PT</button>
              </div>
              <button type="button" onClick={() => setShowInitialWelcome(false)}>
                {t.continue}
              </button>
            </section>
          </div>
        </div>
      );
    }

    return (
      <div className="page-shell">
        <div className="ambient ambient-a" aria-hidden="true" />
        <div className="ambient ambient-b" aria-hidden="true" />
        <div className="layout auth-layout">
          <section className="card card-auth">
            <p className="eyebrow">{BRAND_NAME}</p>
            <h1>{t.demoAccess}</h1>
            <p className="hero-copy">{t.loginDescription}</p>
            <form onSubmit={handleLoginSubmit}>
              <label>
                {t.username}
                <input name="username" value={loginForm.username} onChange={handleLoginChange} required />
              </label>
              <label>
                {t.password}
                <input name="password" type="password" value={loginForm.password} onChange={handleLoginChange} required />
              </label>
              <label>
                {t.language}
                <select value={uiLanguage} onChange={(event) => setUiLanguage(event.target.value)}>
                  <option value="es">Espanol</option>
                  <option value="en">English</option>
                  <option value="pt">Portugues</option>
                </select>
              </label>
              <button type="submit" disabled={loggingIn}>
                {loggingIn ? t.loggingIn : t.login}
              </button>
            </form>
            <p className="meta">Demo usuario 1: analista.finanzas / Demo1234!</p>
            <p className="meta">Demo usuario 2: analista.riesgo / Demo1234!</p>
            <p className="meta">{t.demoTechnical}</p>
            <p className="meta">Demo admin: admin.valuehub / Demo1234!</p>
            {error && <p className="error">{error}</p>}
          </section>
        </div>
      </div>
    );
  }

  if (showAdminWelcome) {
    return (
      <div className="page-shell">
        <div className="ambient ambient-a" aria-hidden="true" />
        <div className="ambient ambient-b" aria-hidden="true" />
        <div className="layout auth-layout">
          <section className="card card-auth">
            <p className="eyebrow">{BRAND_NAME}</p>
            <h1>{welcomeText.welcomeTitle}</h1>
            <p className="hero-copy">{welcomeText.welcomeBody}</p>
            <div className="action-row" style={{ marginTop: 10 }}>
              <button type="button" onClick={() => setWelcomeLanguageIndex(0)}>ES</button>
              <button type="button" onClick={() => setWelcomeLanguageIndex(1)}>EN</button>
              <button type="button" onClick={() => setWelcomeLanguageIndex(2)}>PT</button>
            </div>
            <button
              type="button"
              onClick={() => {
                setShowAdminWelcome(false);
                setShowContextEditor(false);
                setView("admin");
              }}
            >
              {t.continue}
            </button>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <div className="ambient ambient-a" aria-hidden="true" />
      <div className="ambient ambient-b" aria-hidden="true" />

      <div className="layout">
        <header className="hero">
          <div className="top-actions">
            <div>
              <p className="eyebrow">{BRAND_NAME}</p>
            </div>
            <div className="action-row">
              <label>
                {t.language}
                <select value={uiLanguage} onChange={(event) => setUiLanguage(event.target.value)}>
                  <option value="es">ES</option>
                  <option value="en">EN</option>
                  <option value="pt">PT</option>
                </select>
              </label>
              <button type="button" onClick={() => setShowProjectInfo(!showProjectInfo)} title="Toggle project info" style={{fontSize: "0.8rem", padding: "8px 10px"}}>ℹ️ Info</button>
              {user.role === "admin" && (
                <>
                  <button type="button" onClick={() => setView("executiveDashboard")}>📊 Dashboard</button>
                  <button type="button" onClick={() => setView("admin")}>{t.adminPanelTitle}</button>
                </>
              )}
              {(user.role === "admin" || user.role === "technical") && (
                <button type="button" onClick={() => setView("technicalHub")}>{t.technicalHub}</button>
              )}
              <button type="button" onClick={() => setView("main")}>{t.home}</button>
              {user.role === "analyst" && (
                <button type="button" onClick={() => setView("myIdeas")}>{t.myIdeas}</button>
              )}
              <button type="button" onClick={handleLogout}>{t.logout}</button>
            </div>
          </div>
          {showProjectInfo && (
            <>
              <h1>{t.heroTitle}</h1>
              <p className="hero-copy">{t.heroCopy}</p>
              <div className="tag-row">
                <span className="tag">{t.tenant}: {user.tenant_id}</span>
                <span className="tag">{t.authReady}</span>
                <span className="tag">{t.stages}</span>
                <span className="tag">API: {API_URL}</span>
              </div>
            </>
          )}
        </header>

        {user.role === "analyst" && (
          <section className="kpis" aria-label={t.myIdeas}>
            <article className="kpi-card">
              <p className="kpi-label">{t.myIdeas}</p>
              <p className="kpi-value">{summary.totalIdeas}</p>
            </article>
            <article className="kpi-card">
              <p className="kpi-label">{t.viable}</p>
              <p className="kpi-value">{summary.viableIdeas}</p>
            </article>
            <article className="kpi-card">
              <p className="kpi-label">{t.rejected}</p>
              <p className="kpi-value">{summary.rejectedIdeas}</p>
            </article>
            <article className="kpi-card">
              <p className="kpi-label">{t.clarification}</p>
              <p className="kpi-value">{summary.needsClarification}</p>
            </article>
          </section>
        )}

        {view === "admin" && user.role === "admin" ? (
          <main className="grid grid-single">
            <section className="card card-list admin-panel">
              <div className="admin-header-row">
                <div className="card-header">
                  <h2>{t.adminPanelTitle}</h2>
                  <p>{t.adminPanelSubtitle}</p>
                </div>
                <div className="admin-tabs" role="tablist" aria-label={t.adminPanelTitle}>
                  <button type="button" className={adminTab === "useCases" ? "admin-tab active" : "admin-tab"} onClick={() => setAdminTab("useCases")}>{t.adminTabUseCases}</button>
                  <button type="button" className={adminTab === "tokenCost" ? "admin-tab active" : "admin-tab"} onClick={() => setAdminTab("tokenCost")}>{t.adminTabTokenCost}</button>
                  <button type="button" className={adminTab === "metrics" ? "admin-tab active" : "admin-tab"} onClick={() => setAdminTab("metrics")}>{t.adminTabMetrics}</button>
                </div>
              </div>

              {adminTab === "useCases" && (
                <div className="admin-tab-panel">
                  <p className="meta" style={{ marginBottom: 10 }}>{t.adminUseCaseList}</p>
                  <p className="meta" style={{ marginBottom: 12 }}>{t.adminDeploymentDemoNote}</p>
                  {filteredAdminUseCases.length === 0 ? (
                    <p className="empty">{t.adminUseCaseNone}</p>
                  ) : (
                    <ul className="idea-list">
                      {filteredAdminUseCases.map((item) => (
                        <li key={`admin-use-case-${item.idea_id}`}>
                          <div className="item-top">
                            <h3>{item.title}</h3>
                            <span className="pill pill-success">{t.viable}</span>
                          </div>
                          <p className="meta">{t.owner}: {item.owner_display_name}</p>
                          <p className="meta">{t.feasibilityScore}: {item.feasibility_score}</p>
                          <p className="meta">{t.adminEstimatedTokens}: {item.estimated_tokens}</p>
                          <p className="meta">{t.adminEstimatedCost}: {formatUsd(item.estimated_cost_usd)}</p>
                          <p className="meta">{t.adminGeneratedAt}: {item.generated_at ? new Date(item.generated_at).toLocaleString() : "-"}</p>
                          <p className="meta">
                            {t.adminDeploymentStatus}: <span className={item.deployment_status === "production" ? "pill pill-success" : item.deployment_status === "funding" ? "pill pill-warning" : "pill pill-draft"}>
                              {item.deployment_status === "production"
                                ? t.adminDeploymentProduction
                                : item.deployment_status === "funding"
                                  ? t.adminDeploymentFunding
                                  : t.adminDeploymentDevelopment}
                            </span>
                          </p>
                          <label className="meta" style={{ marginTop: 8 }}>
                            {t.adminDeploymentStatus}
                            <select
                              value={item.deployment_status || "development"}
                              onChange={(event) => handleUpdateDeploymentStatus(item.idea_id, event.target.value)}
                            >
                              <option value="development">{t.adminDeploymentDevelopment}</option>
                              <option value="funding">{t.adminDeploymentFunding}</option>
                              <option value="production">{t.adminDeploymentProduction}</option>
                            </select>
                          </label>
                          <button
                            type="button"
                            className="btn-secondary"
                            style={{ marginTop: 8, marginRight: 4 }}
                            onClick={() => handleDeleteIdea(item.idea_id)}
                          >
                            {t.adminDeleteIdea}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {adminTab === "tokenCost" && (
                <div className="admin-tab-panel">
                  <section className="kpis" aria-label={t.adminTabTokenCost}>
                    <article className="kpi-card">
                      <p className="kpi-label">{t.adminProjectsInProduction}</p>
                      <p className="kpi-value">{filteredProductionApps.length}</p>
                    </article>
                    <article className="kpi-card">
                      <p className="kpi-label">{t.adminQuotaTotal}</p>
                      <p className="kpi-value">{formatInt(adminDashboard?.token_cost?.quota_total_tokens || 0)}</p>
                      <p className="meta">{t.adminQuotaTotalUsd}: {formatUsd(quotaUsdTotals.total)}</p>
                    </article>
                    <article className="kpi-card">
                      <p className="kpi-label">{t.adminQuotaConsumed}</p>
                      <p className="kpi-value">{formatInt(adminDashboard?.token_cost?.quota_consumed_tokens || 0)}</p>
                      <p className="meta">{t.adminQuotaConsumedUsd}: {formatUsd(quotaUsdTotals.consumed)}</p>
                    </article>
                    <article className="kpi-card">
                      <p className="kpi-label">{t.adminQuotaRemaining}</p>
                      <p className="kpi-value">{formatInt(adminDashboard?.token_cost?.quota_remaining_tokens || 0)}</p>
                      <p className="meta">{t.adminQuotaRemainingUsd}: {formatUsd(quotaUsdTotals.remaining)}</p>
                    </article>
                  </section>

                  <p className="meta">
                    {t.adminQuotaMonth}: {adminDashboard?.token_cost?.quota_month || "-"} | {t.adminEstimatedCost}: {formatUsd(adminDashboard?.token_cost?.estimated_cost_usd || 0)}
                  </p>
                  <p className="meta">{t.adminQuotaUsdHint}</p>

                  {filteredProductionApps.length === 0 ? (
                    <p className="empty">{t.adminNoProductionApps}</p>
                  ) : (
                    <ul className="idea-list" style={{ marginTop: 10 }}>
                      {filteredProductionApps.map((item) => {
                        const quotaUsd = estimateQuotaUsd(item);
                        return (
                        <li key={`quota-app-${item.idea_id}`}>
                          <div className="item-top">
                            <h3>{item.title}</h3>
                            <span className={item.usage_pct >= 90 ? "pill pill-danger" : item.usage_pct >= 75 ? "pill pill-warning" : "pill pill-success"}>
                              <span className="quota-clock-icon" aria-hidden="true">{quotaClockIcon(item.usage_pct)}</span>
                              {item.usage_pct}%
                            </span>
                          </div>
                          <p className="meta">{t.owner}: {item.owner_display_name}</p>
                          <p className="meta">{t.adminQuotaUsageClock}: {quotaClockIcon(item.usage_pct)}</p>
                          <p className="meta">{t.adminQuotaTotal}: {formatInt(item.quota_total_tokens)}</p>
                          <p className="meta">{t.adminQuotaTotalUsd}: {formatUsd(quotaUsd.quotaTotalUsd)}</p>
                          <p className="meta">{t.adminQuotaConsumed}: {formatInt(item.consumed_month_tokens)}</p>
                          <p className="meta">{t.adminQuotaConsumedUsd}: {formatUsd(quotaUsd.quotaConsumedUsd)}</p>
                          <p className="meta">{t.adminQuotaRemaining}: {formatInt(item.quota_remaining_tokens)}</p>
                          <p className="meta">{t.adminQuotaRemainingUsd}: {formatUsd(quotaUsd.quotaRemainingUsd)}</p>
                          <p className="meta">{t.adminEstimatedCost}: {formatUsd(item.estimated_monthly_cost_usd || 0)}</p>

                          <label className="meta" style={{ marginTop: 8 }}>
                            {t.adminQuotaBase}
                            <input
                              type="number"
                              min="1000"
                              step="1000"
                              value={baseQuotaDrafts[item.idea_id] || ""}
                              onChange={(event) => setBaseQuotaDrafts((prev) => ({ ...prev, [item.idea_id]: event.target.value }))}
                            />
                          </label>
                          <button type="button" onClick={() => handleSetBaseQuota(item.idea_id)}>{t.adminQuotaSet}</button>

                          <label className="meta" style={{ marginTop: 8 }}>
                            {t.adminQuotaExtra}
                            <input
                              type="number"
                              min="1"
                              step="1000"
                              value={extraQuotaDrafts[item.idea_id] || ""}
                              onChange={(event) => setExtraQuotaDrafts((prev) => ({ ...prev, [item.idea_id]: event.target.value }))}
                            />
                          </label>
                          <label className="meta" style={{ marginTop: 6 }}>
                            {t.adminQuotaReason}
                            <input
                              type="text"
                              maxLength={240}
                              value={extraQuotaReasons[item.idea_id] || ""}
                              onChange={(event) => setExtraQuotaReasons((prev) => ({ ...prev, [item.idea_id]: event.target.value }))}
                            />
                          </label>
                          <button type="button" onClick={() => handleAddExtraQuota(item.idea_id)}>{t.adminQuotaAddExtra}</button>
                        </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              )}

              {adminTab === "metrics" && (
                <div className="admin-tab-panel">
                  <section className="kpis" aria-label={t.adminTabMetrics}>
                    <article className="kpi-card" title={t.adminMetricHintTotalIdeas}>
                      <p className="kpi-label">{t.adminTotalIdeas} <span className="metric-help" title={t.adminMetricHintTotalIdeas}>i</span></p>
                      <p className="kpi-value">{adminDashboard?.portfolio_metrics?.total_ideas || 0}</p>
                    </article>
                    <article className="kpi-card" title={t.adminMetricHintApprovalRate}>
                      <p className="kpi-label">{t.adminApprovalRate} <span className="metric-help" title={t.adminMetricHintApprovalRate}>i</span></p>
                      <p className="kpi-value">{adminDashboard?.portfolio_metrics?.approval_rate_pct || 0}%</p>
                    </article>
                    <article className="kpi-card" title={t.adminMetricHintTechnicalPassRate}>
                      <p className="kpi-label">{t.adminTechnicalPassRate} <span className="metric-help" title={t.adminMetricHintTechnicalPassRate}>i</span></p>
                      <p className="kpi-value">{adminDashboard?.portfolio_metrics?.technical_pass_rate_pct || 0}%</p>
                    </article>
                    <article className="kpi-card" title={t.adminMetricHintAvgFeasibility}>
                      <p className="kpi-label">{t.adminAvgFeasibility} <span className="metric-help" title={t.adminMetricHintAvgFeasibility}>i</span></p>
                      <p className="kpi-value">{adminDashboard?.portfolio_metrics?.avg_feasibility_score || 0}</p>
                    </article>
                  </section>
                  <p className="meta" title={t.adminMetricHintAvgCycleHours}>{t.adminAvgCycleHours}: {adminDashboard?.portfolio_metrics?.avg_cycle_time_hours || 0} <span className="metric-help" title={t.adminMetricHintAvgCycleHours}>i</span></p>
                  <p className="meta" style={{ marginTop: 10 }}>{t.adminTopComponents}</p>
                  {(adminDashboard?.portfolio_metrics?.top_components || []).length === 0 ? (
                    <p className="empty">{t.adminNoComponentData}</p>
                  ) : (
                    <ul className="idea-list">
                      {(adminDashboard?.portfolio_metrics?.top_components || []).map((item) => (
                        <li key={`top-component-${item.component}`}>
                          <p className="meta"><strong>{item.component}</strong></p>
                          <p className="meta">{item.count}</p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </section>
          </main>
        ) : view === "executiveDashboard" && user.role === "admin" ? (
          <main className="grid grid-single">
            <ExecutiveDashboard lang={uiLanguage} />
          </main>
        ) : view === "technicalHub" && (user.role === "admin" || user.role === "technical") ? (
          <main className="grid grid-single">
            <section className="card card-list">
              <div className="card-header">
                <h2>{t.technicalHubTitle}</h2>
                <p>{t.technicalHubSubtitle}</p>
              </div>

              {selectedTechnicalIdea ? (
                <section
                  className="card card-form"
                  ref={selectedIdeaPanelRef}
                  style={{ marginBottom: 18, borderColor: "rgba(14, 116, 144, 0.35)", background: "rgba(255,255,255,0.96)" }}
                >
                  <div className="card-header">
                    <h2>{selectedTechnicalIdea.title}</h2>
                    <p>{t.owner}: {selectedTechnicalIdea.owner_display_name}</p>
                  </div>
                  <p className="meta">{t.statusDetail}: {statusLabel[selectedTechnicalIdea.status] || selectedTechnicalIdea.status}</p>
                  <p className="meta">{t.currentStage}: {stageLabel(selectedTechnicalIdea.current_stage)}</p>
                  <p className="meta">{t.scores}: {selectedTechnicalIdea.business_validation.value_score} | {selectedTechnicalIdea.business_validation.risk_score}</p>

                  <label className="meta" style={{ marginTop: 8 }}>
                    {t.adminDeploymentStatus}
                    <select
                      value={selectedTechnicalIdea.deployment_status || "development"}
                      onChange={(event) => handleUpdateDeploymentStatus(selectedTechnicalIdea.idea_id, event.target.value)}
                    >
                      <option value="development">{t.adminDeploymentDevelopment}</option>
                      <option value="funding">{t.adminDeploymentFunding}</option>
                      <option value="production">{t.adminDeploymentProduction}</option>
                    </select>
                  </label>

                  <div className="action-row" style={{ marginTop: 10 }}>
                    {selectedTechnicalIdea.status === "business_viable" && !hasTechnicalValidation(selectedTechnicalIdea) && (
                      <button
                        type="button"
                        onClick={() => openTechnicalPanel(selectedTechnicalIdea)}
                        disabled={submittingTechnical || generatingArchitecture || loadingTechnicalQuestions}
                      >
                        {t.runTechnicalValidation}
                      </button>
                    )}
                    <button type="button" onClick={() => setSelectedIdeaId("")}>{t.removeFocus}</button>
                  </div>

                  <p className="meta" style={{ marginTop: 8 }}>{t.technicalRequestMoreInfo}</p>

                  {selectedTechnicalIdea.status === "business_viable" && !hasTechnicalValidation(selectedTechnicalIdea) && activeTechnicalIdeaId === selectedTechnicalIdea.idea_id && technicalQuestions.length > 0 && (
                    <div className="clarification-form technical-chat-shell">
                      <div className="card-header">
                        <h2>{t.technicalPanelTitle}</h2>
                        <p>{t.technicalChatIntro}</p>
                      </div>
                      <div className="technical-chat-window">
                        {technicalConversation.map((message, index) => (
                          <div key={`technical-msg-hub-${index}`} className={`technical-chat-bubble ${message.role === "agent" ? "agent" : "user"}`}>
                            {message.text}
                          </div>
                        ))}
                      </div>

                      {pendingTechnicalQuestion() && (
                        <>
                          <p className="meta">
                            {t.technicalChatPending}: {pendingTechnicalQuestion().prompt}
                          </p>
                          {pendingTechnicalQuestion().suggested_answers?.length > 0 && (
                            <div>
                              <span className="meta">{t.suggestedAnswers}:</span>
                              <div className="action-row" style={{ marginTop: 6, marginBottom: 8 }}>
                                {pendingTechnicalQuestion().suggested_answers.map((suggestion, index) => (
                                  <button
                                    key={`${pendingTechnicalQuestion().question_id}-technical-hub-suggestion-${index}`}
                                    type="button"
                                    onClick={() => setTechnicalDraft(suggestion)}
                                  >
                                    {t.useSuggestion} {index + 1}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          <form onSubmit={handleTechnicalMessageSubmit}>
                            <label>
                              {t.technicalAnswer}
                              <textarea
                                minLength={5}
                                required
                                value={technicalDraft}
                                onChange={(event) => setTechnicalDraft(event.target.value)}
                                placeholder={t.technicalAnswer}
                              />
                            </label>
                            <button type="submit">{t.technicalChatSend}</button>
                          </form>
                        </>
                      )}

                      {!pendingTechnicalQuestion() && (
                        <button
                          type="button"
                          onClick={(event) => handleTechnicalValidationSubmit(event, selectedTechnicalIdea.idea_id)}
                          disabled={submittingTechnical}
                        >
                          {submittingTechnical ? t.validatingTechnical : `${t.submitTechnicalChat} (${t.technicalChatReady})`}
                        </button>
                      )}
                    </div>
                  )}

                  {hasTechnicalValidation(selectedTechnicalIdea) && (
                    <>
                      <p className="meta">
                        {t.technicalAgentTrace}: {selectedTechnicalIdea.technical_validation.recommendation} | {t.feasibilityScore}: {selectedTechnicalIdea.technical_validation.feasibility_score}
                      </p>
                      <p className="meta">
                        {t.integrationComplexity}: {selectedTechnicalIdea.technical_validation.integration_complexity} | {t.securityRisk}: {selectedTechnicalIdea.technical_validation.security_risk} | {t.dataReadiness}: {selectedTechnicalIdea.technical_validation.data_readiness}
                      </p>
                    </>
                  )}

                  {selectedTechnicalIdea.status === "business_viable" && hasTechnicalValidation(selectedTechnicalIdea) && !selectedTechnicalIdea.architecture_package && (
                    <button
                      type="button"
                      onClick={() => handleGenerateArchitecture(selectedTechnicalIdea.idea_id)}
                      disabled={generatingArchitecture}
                    >
                      {generatingArchitecture ? t.generatingArchitecture : t.generateArchitecture}
                    </button>
                  )}

                  {selectedTechnicalIdea.architecture_package && (
                    <>
                      <p className="meta">
                        {t.packageGenerated}. {t.packageGeneratedAt}: {new Date(selectedTechnicalIdea.architecture_package.generated_at).toLocaleString()}
                      </p>
                      <div className="action-row">
                        <button
                          type="button"
                          onClick={() => handlePreviewArchitecturePackage(selectedTechnicalIdea)}
                        >
                          {t.viewPackage}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDownloadArchitecturePackage(selectedTechnicalIdea)}
                        >
                          {t.downloadPackage}
                        </button>
                      </div>
                    </>
                  )}
                </section>
              ) : null}

              {loadingTechnicalQueue ? (
                <p className="meta">{t.loadingTechnicalQuestions}</p>
              ) : filteredTechnicalQueue.length === 0 ? (
                <p className="empty">{t.technicalQueueEmpty}</p>
              ) : (
                <ul className="idea-list">
                  {filteredTechnicalQueue.map((idea, index) => (
                    <li key={`technical-${idea.idea_id}`} style={{ "--delay": `${index * 60}ms` }}>
                      <div className="item-top">
                        <h3>{idea.title}</h3>
                        <span className={hasTechnicalValidation(idea) ? "pill pill-success" : "pill pill-warning"}>
                          {hasTechnicalValidation(idea) ? t.technicalResult : t.technicalPanelTitle}
                        </span>
                      </div>
                      <p className="meta">{t.owner}: {idea.owner_display_name}</p>
                      <p className="meta">{t.currentStage}: {stageLabel(idea.current_stage)}</p>
                      <p className="meta">{t.scores}: {idea.business_validation.value_score} | {idea.business_validation.risk_score}</p>
                      <button type="button" onClick={() => setSelectedIdeaId(idea.idea_id)}>{t.technicalOpen}</button>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </main>
        ) : view === "main" ? (
          <main className="grid">
            <section className="card card-list" style={{ gridColumn: "1 / -1" }}>
              <details className="collapsible-card">
                <summary>
                  <span>{t.productionCatalogTitle}</span>
                </summary>
                <div className="card-header" style={{ marginTop: 12 }}>
                  <p>{t.productionCatalogSubtitle}</p>
                </div>
                <ul className="idea-list production-catalog-list">
                  {toolCatalog.map((toolItem) => (
                    <li key={toolItem.tool_id}>
                      <div className="item-top">
                        <h3>{toolItem.name}</h3>
                        <span className="pill pill-success">{t.productionStatus}</span>
                      </div>
                      <p className="meta"><strong>{t.productionScope}:</strong> {toolItem.scope}</p>
                      <p className="meta"><strong>{t.productionContact}:</strong> {toolItem.contact}</p>
                    </li>
                  ))}
                </ul>
              </details>
            </section>

            {user.role !== "admin" && (
              <section className="card card-form" style={{ gridColumn: "1 / -1" }}>
                <details className="collapsible-card">
                  <summary>
                    <span>{t.demoIdeasTitle}</span>
                  </summary>
                  <div className="card-header" style={{ marginTop: 12 }}>
                    <p>{t.demoIdeasSubtitle}</p>
                  </div>
                  <ul className="idea-list production-catalog-list">
                    {demoIdeas.map((sample, index) => (
                      <li key={`demo-idea-${index}`}>
                        <div className="item-top">
                          <h3>{sample.title}</h3>
                        </div>
                        <p className="meta"><strong>{t.problem}:</strong> {sample.problem_statement}</p>
                        <p className="meta"><strong>{t.expectedValue}:</strong> {sample.expected_value}</p>
                        <div className="action-row">
                          <button type="button" onClick={() => handlePrefillDemoIdea(sample)}>{t.demoIdeaPrefill}</button>
                          <button type="button" onClick={() => handleCreateDemoIdea(sample)} disabled={seedingExamples}>
                            {seedingExamples ? t.savingIdea : t.demoIdeaCreate}
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </details>
              </section>
            )}

            {user.role === "analyst" ? (
              <section className="card card-form">
                <div className="card-header">
                  <h2>{t.contextRegistered}</h2>
                  <p>{t.adminOnlyContext}</p>
                </div>
              </section>
            ) : user.role === "technical" ? (
              <section className="card card-form">
                <div className="card-header">
                  <h2>{t.technicalHubTitle}</h2>
                  <p>{t.technicalHubSubtitle}</p>
                </div>
                <button type="button" onClick={() => setView("technicalHub")}>{t.technicalHub}</button>
              </section>
            ) : showContextEditor ? (
              <section className="card card-form">
                <div className="card-header">
                  <h2>{t.contextTitle}</h2>
                  <p>{t.contextSubtitle}</p>
                </div>
                <form onSubmit={handleContextSubmit}>
                  <label>
                    {t.tenant}
                    <input name="tenant_id" value={user.tenant_id} disabled />
                  </label>
                  <button type="button" onClick={handleLoadContext}>{t.loadContext}</button>
                  <label>
                    {t.company}
                    <input
                      name="company_name"
                      value={contextForm.company_name}
                      onChange={handleContextChange}
                      minLength={2}
                      required
                    />
                  </label>
                  <label>
                    {t.industry}
                    <input name="industry" value={contextForm.industry} onChange={handleContextChange} minLength={2} required />
                  </label>
                  <label>
                    {t.strategicPriorities}
                    <input
                      name="strategic_priorities"
                      value={contextForm.strategic_priorities}
                      onChange={handleContextChange}
                    />
                  </label>
                  <label>
                    {t.prohibitedDomains}
                    <input
                      name="prohibited_domains"
                      value={contextForm.prohibited_domains}
                      onChange={handleContextChange}
                    />
                  </label>
                  <label>
                    {t.regulatoryConstraints}
                    <input
                      name="regulatory_constraints"
                      value={contextForm.regulatory_constraints}
                      onChange={handleContextChange}
                    />
                  </label>
                  <label>
                    {t.operatingSummary}
                    <textarea
                      name="operating_model_summary"
                      value={contextForm.operating_model_summary}
                      onChange={handleContextChange}
                      minLength={10}
                      required
                    />
                  </label>
                  <label>
                    {t.riskTolerance}
                    <select name="risk_tolerance" value={contextForm.risk_tolerance} onChange={handleContextChange}>
                      <option value="low">low</option>
                      <option value="medium">medium</option>
                      <option value="high">high</option>
                    </select>
                  </label>
                  <button type="submit" disabled={savingContext}>
                    {savingContext ? t.savingContext : t.saveContext}
                  </button>
                </form>
                <div className="card-header" style={{ marginTop: 14 }}>
                  <h2>{t.uploadSection}</h2>
                  <p>{t.uploadHint}</p>
                </div>
                <label>
                  {t.selectFiles}
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.ppt,.pptx,.doc,.docx,.md"
                    onChange={handleContextFilesChange}
                  />
                </label>
                <button type="button" onClick={handleUploadContextFiles} disabled={uploadingFiles}>
                  {uploadingFiles ? t.uploadingFiles : t.uploadFiles}
                </button>
                {uploadMessage && <p className="meta">{uploadMessage}</p>}
                <p className="meta">{contextLoaded ? t.contextStatusLoaded : t.contextStatusPending}</p>
              </section>
            ) : (
              <section className="card card-form">
                <div className="card-header">
                  <h2>{t.contextRegistered}</h2>
                  <p>{t.contextRegisteredBody}</p>
                </div>
                {user.role === "admin" && (
                  <button type="button" onClick={() => setShowContextEditor(true)}>
                    {t.editContext}
                  </button>
                )}
              </section>
            )}

            {user.role === "analyst" && (
              <section className="card card-form">
                <div className="card-header">
                  <h2>{t.newIdea}</h2>
                  <p>{t.newIdeaSubtitle}</p>
                </div>
                <form onSubmit={handleSubmit}>
                  <label>
                    {t.tenant}
                    <input name="tenant_id" value={user.tenant_id} disabled />
                  </label>
                  <label>
                    {t.title}
                    <input name="title" value={form.title} onChange={handleChange} minLength={3} required />
                  </label>
                  <label>
                    {t.problem}
                    <textarea
                      name="problem_statement"
                      value={form.problem_statement}
                      onChange={handleChange}
                      minLength={10}
                      required
                    />
                  </label>
                  <label>
                    {t.expectedValue}
                    <textarea
                      name="expected_value"
                      value={form.expected_value}
                      onChange={handleChange}
                      minLength={5}
                      required
                    />
                  </label>
                  <label>
                    {t.affectedUsers}
                    <input name="affected_users" value={form.affected_users} onChange={handleChange} />
                  </label>
                  <label>
                    {t.sourceLanguage}
                    <select name="source_language" value={form.source_language} onChange={handleChange}>
                      <option value="es">es</option>
                      <option value="en">en</option>
                      <option value="pt">pt</option>
                    </select>
                  </label>
                  <button type="submit" disabled={loading}>
                    {loading ? t.savingIdea : t.saveIdea}
                  </button>
                </form>
              </section>
            )}

          </main>
        ) : (
          <main className="grid grid-single">
            <section className="card card-list">
              <div className="card-header">
                <h2>{t.myIdeas}</h2>
                <p>{t.myIdeasSubtitle}</p>
              </div>
              {selectedIdea ? (
                <section
                  className="card card-form"
                  ref={selectedIdeaPanelRef}
                  style={{ marginBottom: 18, borderColor: "rgba(99, 102, 241, 0.35)", background: "rgba(255,255,255,0.96)" }}
                >
                  <div className="card-header">
                    <h2>{t.focusedIdeaTitle}</h2>
                    <p>{selectedIdea.title}</p>
                  </div>
                  <p className="meta">{t.statusDetail}: {statusLabel[selectedIdea.status] || selectedIdea.status}</p>
                  <p className="meta">{t.currentStage}: {stageLabel(selectedIdea.current_stage)}</p>
                  <p className="meta">{t.scores}: {selectedIdea.business_validation.value_score} | {selectedIdea.business_validation.risk_score}</p>
                  <div className="action-row" style={{ marginTop: 10 }}>
                    {selectedIdea.status === "needs_clarification" && (
                      <button
                        type="button"
                        onClick={() => openClarificationPanel(selectedIdea.idea_id)}
                        disabled={loadingClarification || submittingClarification}
                      >
                        {t.clarifyWithAgent}
                      </button>
                    )}
                    {selectedIdea.status === "business_viable" && !hasTechnicalValidation(selectedIdea) && (
                      <button
                        type="button"
                        onClick={() => openTechnicalPanel(selectedIdea)}
                        disabled={submittingTechnical || generatingArchitecture || loadingTechnicalQuestions}
                      >
                        {t.runTechnicalValidation}
                      </button>
                    )}
                    {selectedIdea.status === "rejected" && (
                      <button
                        type="button"
                        onClick={() => handleResubmitForReview(selectedIdea.idea_id)}
                        disabled={submittingResubmit}
                      >
                        {submittingResubmit ? t.submittingResubmit : t.resubmitForReview}
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleDeleteOwnIdea(selectedIdea.idea_id)}
                      disabled={deletingIdeaId === selectedIdea.idea_id}
                    >
                      {deletingIdeaId === selectedIdea.idea_id ? t.deletingIdea : t.deleteOwnIdea}
                    </button>
                    <button type="button" onClick={() => setSelectedIdeaId("")}>{t.removeFocus}</button>
                  </div>

                  {selectedIdea.status === "needs_clarification" && activeClarificationIdeaId === selectedIdea.idea_id && clarificationQuestions.length > 0 && (
                    <form className="clarification-form" onSubmit={(event) => handleClarificationSubmit(event, selectedIdea.idea_id)}>
                      <div className="card-header">
                        <h2>{t.clarificationTitle}</h2>
                        <p>{t.clarificationIntro}</p>
                      </div>
                      {clarificationQuestions.map((question) => (
                        <label key={question.question_id}>
                          {question.prompt}
                          <span className="meta">{t.clarificationWhy}: {question.rationale}</span>
                          {question.suggested_answers?.length > 0 && (
                            <div>
                              <span className="meta">{t.suggestedAnswers}:</span>
                              <div className="action-row" style={{ marginTop: 6, marginBottom: 8 }}>
                                {question.suggested_answers.map((suggestion, index) => (
                                  <button
                                    key={`${question.question_id}-suggestion-${index}`}
                                    type="button"
                                    onClick={() => handleClarificationAnswerChange(question.question_id, suggestion)}
                                  >
                                    {t.useSuggestion} {index + 1}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          <textarea
                            minLength={5}
                            required
                            value={clarificationAnswers[question.question_id] || ""}
                            onChange={(event) => handleClarificationAnswerChange(question.question_id, event.target.value)}
                            placeholder={t.clarificationAnswer}
                          />
                        </label>
                      ))}
                      <button type="submit" disabled={submittingClarification}>
                        {submittingClarification ? t.submittingClarification : t.submitClarification}
                      </button>
                    </form>
                  )}

                  {selectedIdea.status === "business_viable" && !hasTechnicalValidation(selectedIdea) && activeTechnicalIdeaId === selectedIdea.idea_id && technicalQuestions.length > 0 && (
                    <div className="clarification-form technical-chat-shell">
                      <div className="card-header">
                        <h2>{t.technicalPanelTitle}</h2>
                        <p>{t.technicalChatIntro}</p>
                      </div>
                      <div className="technical-chat-window">
                        {technicalConversation.map((message, index) => (
                          <div key={`technical-msg-${index}`} className={`technical-chat-bubble ${message.role === "agent" ? "agent" : "user"}`}>
                            {message.text}
                          </div>
                        ))}
                      </div>

                      {pendingTechnicalQuestion() && (
                        <>
                          <p className="meta">
                            {t.technicalChatPending}: {pendingTechnicalQuestion().prompt}
                          </p>
                          {pendingTechnicalQuestion().suggested_answers?.length > 0 && (
                            <div>
                              <span className="meta">{t.suggestedAnswers}:</span>
                              <div className="action-row" style={{ marginTop: 6, marginBottom: 8 }}>
                                {pendingTechnicalQuestion().suggested_answers.map((suggestion, index) => (
                                  <button
                                    key={`${pendingTechnicalQuestion().question_id}-technical-suggestion-${index}`}
                                    type="button"
                                    onClick={() => setTechnicalDraft(suggestion)}
                                  >
                                    {t.useSuggestion} {index + 1}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          <form onSubmit={handleTechnicalMessageSubmit}>
                            <label>
                              {t.technicalAnswer}
                              <textarea
                                minLength={5}
                                required
                                value={technicalDraft}
                                onChange={(event) => setTechnicalDraft(event.target.value)}
                                placeholder={t.technicalAnswer}
                              />
                            </label>
                            <button type="submit">{t.technicalChatSend}</button>
                          </form>
                        </>
                      )}

                      {!pendingTechnicalQuestion() && (
                        <button
                          type="button"
                          onClick={(event) => handleTechnicalValidationSubmit(event, selectedIdea.idea_id)}
                          disabled={submittingTechnical}
                        >
                          {submittingTechnical ? t.validatingTechnical : `${t.submitTechnicalChat} (${t.technicalChatReady})`}
                        </button>
                      )}
                    </div>
                  )}

                  {hasTechnicalValidation(selectedIdea) && (
                    <>
                      <p className="meta">
                        {t.technicalAgentTrace}: {selectedIdea.technical_validation.recommendation} | {t.feasibilityScore}: {selectedIdea.technical_validation.feasibility_score}
                      </p>
                      <p className="meta">
                        {t.integrationComplexity}: {selectedIdea.technical_validation.integration_complexity} | {t.securityRisk}: {selectedIdea.technical_validation.security_risk} | {t.dataReadiness}: {selectedIdea.technical_validation.data_readiness}
                      </p>
                      {selectedIdea.technical_validation.blockers?.length > 0 && (
                        <p className="meta">{t.technicalBlockers}: {selectedIdea.technical_validation.blockers.join(" | ")}</p>
                      )}
                    </>
                  )}

                  <details className="idea-detail" style={{ marginTop: 12 }}>
                    <summary>{t.viewDetail}</summary>
                    <p className="meta">{t.contextSignals}: {selectedIdea.business_validation.context_signals.join(" | ") || "-"}</p>
                    <p className="meta">{t.assumptions}: {selectedIdea.business_validation.assumptions.join(" | ") || "-"}</p>
                    <p className="meta">{t.openQuestions}: {selectedIdea.business_validation.open_questions.join(" | ") || "-"}</p>
                    {selectedIdea.clarification_interactions?.length > 0 && (
                      <p className="meta">
                        {t.agentSummary}: {selectedIdea.clarification_interactions[selectedIdea.clarification_interactions.length - 1].agent_summary}
                      </p>
                    )}
                    {selectedIdea.technical_interactions?.length > 0 && (
                      <p className="meta">
                        {t.technicalAgentTrace}: {selectedIdea.technical_interactions[selectedIdea.technical_interactions.length - 1].agent_summary}
                      </p>
                    )}
                    {selectedIdea.response_composition && (
                      <>
                        <p className="meta">{selectedIdea.response_composition.message}</p>
                        <p className="meta">{t.nextActions}: {(selectedIdea.response_composition.next_actions || []).join(" | ") || "-"}</p>
                      </>
                    )}
                  </details>
                </section>
              ) : filteredMyIdeas.length > 0 ? (
                <ul className="idea-list">
                  {filteredMyIdeas.map((idea, index) => (
                    <li key={idea.idea_id} style={{ "--delay": `${index * 70}ms` }}>
                      <div className="item-top">
                        <h3>{idea.title}</h3>
                        <span className={statusClass[idea.status] || "pill"}>{statusLabel[idea.status] || idea.status}</span>
                      </div>
                      <p className="meta">{t.statusDetail}: {statusLabel[idea.status] || idea.status}</p>
                      <p className="meta">{t.owner}: {idea.owner_display_name}</p>
                      <p className="meta">{t.currentStage}: {stageLabel(idea.current_stage)}</p>
                      <p className="meta">
                        {t.scores}: {idea.business_validation.value_score} | {idea.business_validation.risk_score}
                      </p>
                      <button type="button" onClick={() => setSelectedIdeaId(idea.idea_id)}>
                        {t.viewInFocus}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteOwnIdea(idea.idea_id)}
                        disabled={deletingIdeaId === idea.idea_id}
                      >
                        {deletingIdeaId === idea.idea_id ? t.deletingIdea : t.deleteOwnIdea}
                      </button>
                      {similarIdeaMap[idea.idea_id] && (
                        <p className="meta rejection-detail">
                          {t.possibleDuplicate} "{similarIdeaMap[idea.idea_id]}"
                        </p>
                      )}
                      {idea.status === "rejected" && idea.rejection && (
                        <p className="meta rejection-detail">
                          {t.rejectionInPhase} {idea.rejection.phase}: {idea.rejection.reason}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty">{t.noIdeas}</p>
              )}
              {clarificationFeedback && <p className="meta">{clarificationFeedback}</p>}
            </section>
          </main>
        )}

        {error && <p className="error">{error}</p>}

        {architecturePreview.html && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(15, 23, 42, 0.55)",
              zIndex: 50,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 16,
            }}
          >
            <div
              style={{
                width: "min(1200px, 96vw)",
                height: "min(860px, 92vh)",
                background: "#ffffff",
                borderRadius: 14,
                border: "1px solid #dbe3ef",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "10px 12px",
                  borderBottom: "1px solid #dbe3ef",
                  background: "#f8fafc",
                }}
              >
                <p className="meta" style={{ margin: 0 }}>
                  {t.viewPackage} • {architecturePreview.ideaId}
                </p>
                <button
                  type="button"
                  onClick={() => setArchitecturePreview({ ideaId: "", html: "" })}
                >
                  {t.closePreview}
                </button>
              </div>
              <iframe
                title="architecture-package-preview"
                srcDoc={architecturePreview.html}
                style={{ width: "100%", height: "100%", border: "none" }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
