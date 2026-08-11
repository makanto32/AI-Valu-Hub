from datetime import datetime
import os
import re
import unicodedata

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .blob_storage import upload_context_file as upload_context_file_blob
from .matching_service import (
    find_related_initiatives,
    create_matching_result,
    build_initiatives_catalog,
)
from .models import (
    ArchitectureComponent,
    ArchitectureConsumptionEstimate,
    ArchitecturePackage,
    ArchitecturePackageResponse,
    AuthResponse,
    BusinessIntakeRequest,
    BusinessValidation,
    ClarificationAnswerInput,
    ClarificationInteraction,
    ClarificationQuestionsResponse,
    ClarificationQuestion,
    ClarificationSubmitRequest,
    CompanyContext,
    ContextSnapshot,
    ContextFileUploadResponse,
    IdeaCase,
    IdeaMatchingResult,
    IdeaStage,
    IdeaStatus,
    DeploymentStatus,
    DeploymentStatusUpdateRequest,
    InitiativeCatalog,
    LoginRequest,
    MessageResponse,
    QuotaAdjustment,
    RejectionInfo,
    RejectionPhase,
    SubmitBusinessValidationRequest,
    TokenQuotaExtraRequest,
    TokenQuotaUpdateRequest,
    TechnicalValidation,
    TechnicalChatSubmitRequest,
    TechnicalInteraction,
    TechnicalQuestion,
    TechnicalQuestionsResponse,
    TechnicalValidationRequest,
    TechnicalValidationResponse,
    UpsertCompanyContextRequest,
    UserProfile,
    new_idea_id,
    # Analytics & Metrics
    ExecutiveDashboardMetrics,
    IdeaDuplicationMetrics,
    AIAdoptionMetrics,
    ProductionMetrics,
    InvestmentROIMetrics,
    CollaboratorMetrics,
    AgentContext,
    AgentExecution,
)
from .store import auth_store, company_context_store, context_file_store, idea_store
from .analytics_service import AnalyticsService
from .agent_orchestrator import MultiAgentOrchestrator
from .metrics_provider import LocalDashboardMetricsProvider, build_dashboard_metrics_provider
from .fabric_medallion import run_medallion_pipeline

app = FastAPI(title="AI Value Hub API", version="0.1.0")
DASHBOARD_METRICS_PROVIDER = build_dashboard_metrics_provider()
LOCAL_DASHBOARD_METRICS_PROVIDER = LocalDashboardMetricsProvider()

CANONICAL_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ["es", "en", "pt"]
AUTO_SEED_CONTEXT = os.getenv("AIHUB_AUTO_SEED_CONTEXT", "true").lower() in {"1", "true", "yes"}
AUTH_PROVIDER = os.getenv("AIHUB_AUTH_PROVIDER", "demo").lower()
DEMO_CONTEXT_BY_TENANT = {
    "contoso-demo": {
        "company_name": "Contoso Financial Services",
        "industry": "Servicios financieros",
        "strategic_priorities": [
            "reduccion de fraude",
            "eficiencia operativa en onboarding",
            "experiencia digital para clientes retail",
            "cumplimiento regulatorio",
        ],
        "prohibited_domains": [
            "asesoria de inversion automatizada sin supervision",
            "criptomonedas no reguladas",
            "modelos de credito sin explicabilidad",
        ],
        "regulatory_constraints": [
            "KYC",
            "AML",
            "proteccion de datos personales",
            "trazabilidad de decisiones",
        ],
        "operating_model_summary": (
            "Banco retail con fuerte escrutinio regulatorio. Se priorizan iniciativas con impacto claro en control de riesgo, "
            "productividad de operaciones y satisfaccion de cliente, evitando decisiones automaticas opacas en procesos criticos."
        ),
        "risk_tolerance": "low",
    }
}


def _default_financial_demo_context(tenant_id: str) -> dict[str, object]:
    return {
        "company_name": f"{tenant_id} Financial Services",
        "industry": "Servicios financieros",
        "strategic_priorities": [
            "reduccion de fraude",
            "eficiencia operativa en onboarding",
            "experiencia digital para clientes retail",
            "cumplimiento regulatorio",
        ],
        "prohibited_domains": [
            "asesoria de inversion automatizada sin supervision",
            "criptomonedas no reguladas",
            "modelos de credito sin explicabilidad",
        ],
        "regulatory_constraints": [
            "KYC",
            "AML",
            "proteccion de datos personales",
            "trazabilidad de decisiones",
        ],
        "operating_model_summary": (
            "Entidad financiera orientada a canales digitales y fuerte cumplimiento regulatorio. "
            "Se priorizan iniciativas con impacto medible en riesgo, productividad operacional y experiencia del cliente."
        ),
        "risk_tolerance": "low",
    }


def _resolve_demo_context_seed(tenant_id: str) -> dict[str, object] | None:
    # Usa mapeo explicito cuando existe; para tenants demo aplica una plantilla financiera.
    if tenant_id in DEMO_CONTEXT_BY_TENANT:
        return DEMO_CONTEXT_BY_TENANT[tenant_id]
    if "demo" in tenant_id.lower():
        return _default_financial_demo_context(tenant_id)
    return None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

ACTIVE_ANALYSIS_STATUSES = {
    IdeaStatus.draft,
    IdeaStatus.needs_clarification,
    IdeaStatus.business_viable,
}
MAX_CLARIFICATION_ROUNDS = int(os.getenv("AIHUB_MAX_CLARIFICATION_ROUNDS", "2"))


def _resolve_language(language: str | None) -> str:
    if language in SUPPORTED_LANGUAGES:
        return str(language)
    return CANONICAL_LANGUAGE


def _msg(language: str, es: str, en: str, pt: str) -> str:
    lang = _resolve_language(language)
    if lang == "en":
        return en
    if lang == "pt":
        return pt
    return es


def _entra_not_configured() -> None:
    raise HTTPException(
        status_code=501,
        detail=(
            "Auth provider configurado en Entra ID, pero la integracion aun no esta habilitada en MVP1. "
            "Mantener AIHUB_AUTH_PROVIDER=demo para la demo local/deploy actual."
        ),
    )


def _build_user_profile(user: dict[str, str]) -> UserProfile:
    return UserProfile(
        user_id=user["user_id"],
        username=user["username"],
        display_name=user["display_name"],
        tenant_id=user["tenant_id"],
        role=user["role"],
    )


def _require_admin(current_user: UserProfile) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operacion permitida solo para admin")


def _require_admin_or_technical(current_user: UserProfile) -> None:
    if current_user.role not in {"admin", "technical"}:
        raise HTTPException(status_code=403, detail="Operacion permitida solo para admin o equipo tecnico")


def _ensure_idea_access(current_user: UserProfile, idea: IdeaCase) -> None:
    if current_user.role in {"admin", "technical"}:
        if idea.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="No puedes operar ideas de otro tenant")
        return
    if idea.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="No puedes operar ideas de otro usuario")


def _upload_context_file_to_blob(tenant_id: str, upload: UploadFile, uploaded_by_user_id: str) -> ContextFileUploadResponse:
    blob_result = upload_context_file_blob(tenant_id, upload)
    context_file_store.record_upload(
        tenant_id=tenant_id,
        filename=blob_result.filename,
        content_type=blob_result.content_type,
        blob_path=blob_result.blob_path,
        blob_url=blob_result.blob_url,
        uploaded_by_user_id=uploaded_by_user_id,
    )
    return ContextFileUploadResponse(
        filename=blob_result.filename,
        content_type=blob_result.content_type,
        blob_path=blob_result.blob_path,
        blob_url=blob_result.blob_url,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserProfile:
    if AUTH_PROVIDER == "entra":
        _entra_not_configured()

    if credentials is None:
        raise HTTPException(status_code=401, detail="Falta token de autenticacion")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Esquema de autenticacion invalido")

    user = auth_store.get_user_by_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Sesion invalida o expirada")

    return _build_user_profile(user)


def _build_company_context(tenant_id: str, request: UpsertCompanyContextRequest) -> CompanyContext:
    now = datetime.utcnow()
    existing = company_context_store.get(tenant_id)
    created_at = existing.created_at if existing else now
    return CompanyContext(
        tenant_id=tenant_id,
        company_name=request.company_name,
        industry=request.industry,
        strategic_priorities=request.strategic_priorities,
        prohibited_domains=request.prohibited_domains,
        regulatory_constraints=request.regulatory_constraints,
        operating_model_summary=request.operating_model_summary,
        risk_tolerance=request.risk_tolerance,
        created_at=created_at,
        updated_at=now,
    )


def _seed_demo_context_if_needed(tenant_id: str) -> None:
    if not AUTO_SEED_CONTEXT:
        return
    if company_context_store.get(tenant_id) is not None:
        return

    demo = _resolve_demo_context_seed(tenant_id)
    if demo is None:
        return

    context = CompanyContext(
        tenant_id=tenant_id,
        company_name=demo["company_name"],
        industry=demo["industry"],
        strategic_priorities=demo["strategic_priorities"],
        prohibited_domains=demo["prohibited_domains"],
        regulatory_constraints=demo["regulatory_constraints"],
        operating_model_summary=demo["operating_model_summary"],
        risk_tolerance=demo["risk_tolerance"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    company_context_store.save(context)


def _evaluate_idea_with_context(request: BusinessIntakeRequest, context: CompanyContext) -> BusinessValidation:
    lang = _resolve_language(request.source_language)
    text = f"{request.title} {request.problem_statement} {request.expected_value}".lower()
    value_score = 35
    risk_score = 30
    context_signals: list[str] = []
    score_breakdown: list[str] = [
        "Base value score: 35",
        "Base risk score: 30",
    ]
    blocked = False

    for priority in context.strategic_priorities:
        tokens = [token for token in priority.lower().split() if len(token) > 3]
        if any(token in text for token in tokens):
            value_score += 12
            context_signals.append(
                _msg(
                    lang,
                    f"Alineada con prioridad estrategica: {priority}",
                    f"Aligned with strategic priority: {priority}",
                    f"Alinhada com prioridade estrategica: {priority}",
                )
            )
            score_breakdown.append(f"+12 value por prioridad alineada: {priority}")

    for forbidden in context.prohibited_domains:
        tokens = [token for token in forbidden.lower().split() if len(token) > 4]
        if any(token in text for token in tokens):
            risk_score += 35
            blocked = True
            context_signals.append(
                _msg(
                    lang,
                    f"Coincide con dominio restringido: {forbidden}",
                    f"Matches restricted domain: {forbidden}",
                    f"Coincide com dominio restrito: {forbidden}",
                )
            )
            score_breakdown.append(f"+35 risk por dominio restringido: {forbidden}")

    if any(token in text for token in ["fraude", "fraud", "onboarding", "kyc"]):
        value_score += 10
        context_signals.append(
            _msg(
                lang,
                "Caso de uso frecuente en banca retail regulada",
                "Common use case in regulated retail banking",
                "Caso de uso frequente em banco de varejo regulado",
            )
        )
        score_breakdown.append("+10 value por match fraude/onboarding/kyc")

    if any(token in text for token in ["credito", "credit"]) and not any(
        token in text for token in ["explicable", "explainable", "explicavel"]
    ):
        risk_score += 20
        context_signals.append(
            _msg(
                lang,
                "Riesgo de explicabilidad para decisiones de credito",
                "Explainability risk for credit decisions",
                "Risco de explicabilidade para decisoes de credito",
            )
        )
        score_breakdown.append("+20 risk por credito sin explicabilidad")

    if context.risk_tolerance.lower() == "low":
        risk_score += 10
        context_signals.append(
            _msg(
                lang,
                "Tenant con tolerancia de riesgo baja",
                "Tenant with low risk tolerance",
                "Tenant com baixa tolerancia a risco",
            )
        )
        score_breakdown.append("+10 risk por tolerancia low")

    # Criterios concretos para reducir ambiguedad en intake.
    if len(request.affected_users) == 0:
        value_score -= 8
        score_breakdown.append("-8 value por no declarar usuarios afectados")

    if not any(char.isdigit() for char in request.expected_value):
        value_score -= 10
        score_breakdown.append("-10 value por expected_value sin metrica numerica")

    value_score = max(0, min(100, value_score))
    risk_score = max(0, min(100, risk_score))

    recommendation = "continue"
    if blocked:
        recommendation = "stop"
    elif value_score < 60 or risk_score > 60:
        recommendation = "clarify"

    assumptions = [
        _msg(
            lang,
            f"La idea se evalua contra el contexto base de {context.company_name} ({context.industry}).",
            f"The idea is evaluated against the tenant baseline context of {context.company_name} ({context.industry}).",
            f"A ideia e avaliada contra o contexto base do tenant {context.company_name} ({context.industry}).",
        ),
        _msg(
            lang,
            "El contexto del tenant se considera vigente para esta revision inicial.",
            "Tenant context is considered valid for this initial review.",
            "O contexto do tenant e considerado vigente para esta revisao inicial.",
        ),
    ]
    open_questions = [
        _msg(
            lang,
            "Que metrica de negocio confirmara impacto en 30-60 dias?",
            "Which business metric will confirm impact in 30-60 days?",
            "Qual metrica de negocio confirmara impacto em 30-60 dias?",
        ),
        _msg(
            lang,
            "Existe data suficiente para una prueba controlada?",
            "Is there enough data for a controlled pilot?",
            "Existe dado suficiente para um piloto controlado?",
        ),
    ]

    if recommendation == "stop":
        open_questions.insert(
            0,
            _msg(
                lang,
                "La propuesta entra en un dominio restringido. Se requiere rediseno del alcance.",
                "The proposal falls into a restricted domain. Scope redesign is required.",
                "A proposta entra em um dominio restrito. E necessario redesenhar o escopo.",
            ),
        )

    return BusinessValidation(
        value_score=value_score,
        risk_score=risk_score,
        assumptions=assumptions,
        open_questions=open_questions,
        context_signals=context_signals,
        score_breakdown=score_breakdown,
        recommendation=recommendation,
    )


def _normalize_for_duplicate(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _token_set(text: str) -> set[str]:
    normalized = _normalize_for_duplicate(text)
    stopwords = {
        "para", "con", "por", "una", "uno", "las", "los", "que", "del", "de", "and", "the", "for", "with",
    }
    return {token for token in normalized.split() if len(token) > 3 and token not in stopwords}


def _jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left.intersection(right))
    union = len(left.union(right))
    return intersection / union if union else 0.0


def _find_active_duplicate_idea(request: BusinessIntakeRequest) -> IdeaCase | None:
    title_tokens = _token_set(request.title)
    problem_tokens = _token_set(request.problem_statement)
    combined_tokens = _token_set(f"{request.title} {request.problem_statement}")

    for existing in idea_store.list_by_tenant(request.tenant_id):
        if existing.status not in ACTIVE_ANALYSIS_STATUSES:
            continue

        if existing.current_stage == IdeaStage.technical_validation and existing.status != IdeaStatus.business_viable:
            continue

        existing_title = _normalize_for_duplicate(existing.title)
        incoming_title = _normalize_for_duplicate(request.title)
        if incoming_title and incoming_title == existing_title:
            return existing

        if incoming_title and existing_title and (incoming_title in existing_title or existing_title in incoming_title):
            return existing

        title_similarity = _jaccard_similarity(title_tokens, _token_set(existing.title))
        problem_similarity = _jaccard_similarity(problem_tokens, _token_set(existing.problem_statement))
        combined_similarity = _jaccard_similarity(
            combined_tokens,
            _token_set(f"{existing.title} {existing.problem_statement}"),
        )

        if (title_similarity >= 0.72 and problem_similarity >= 0.62) or combined_similarity >= 0.68:
            return existing

    return None


def _localized_status_label(status: IdeaStatus, language: str) -> str:
    status_map = {
        "es": {
            IdeaStatus.draft: "Borrador",
            IdeaStatus.needs_clarification: "Requiere aclaracion",
            IdeaStatus.business_viable: "Viable negocio",
            IdeaStatus.rejected: "Rechazada",
        },
        "en": {
            IdeaStatus.draft: "Draft",
            IdeaStatus.needs_clarification: "Needs clarification",
            IdeaStatus.business_viable: "Business viable",
            IdeaStatus.rejected: "Rejected",
        },
        "pt": {
            IdeaStatus.draft: "Rascunho",
            IdeaStatus.needs_clarification: "Requer esclarecimento",
            IdeaStatus.business_viable: "Viavel negocio",
            IdeaStatus.rejected: "Rejeitada",
        },
    }
    lang = _resolve_language(language)
    return status_map.get(lang, status_map["es"]).get(status, status.value)


def _localized_stage_label(stage: IdeaStage, language: str) -> str:
    stage_map = {
        "es": {
            IdeaStage.idea_intake: "Intake de idea",
            IdeaStage.business_validation: "Validacion de negocio",
            IdeaStage.technical_validation: "Validacion tecnica",
        },
        "en": {
            IdeaStage.idea_intake: "Idea intake",
            IdeaStage.business_validation: "Business validation",
            IdeaStage.technical_validation: "Technical validation",
        },
        "pt": {
            IdeaStage.idea_intake: "Intake da ideia",
            IdeaStage.business_validation: "Validacao de negocio",
            IdeaStage.technical_validation: "Validacao tecnica",
        },
    }
    lang = _resolve_language(language)
    return stage_map.get(lang, stage_map["es"]).get(stage, stage.value)


def _localized_deployment_label(status: DeploymentStatus, language: str) -> str:
    deployment_map = {
        "es": {
            DeploymentStatus.development: "Desarrollo",
            DeploymentStatus.funding: "Funding",
            DeploymentStatus.production: "Produccion",
        },
        "en": {
            DeploymentStatus.development: "Development",
            DeploymentStatus.funding: "Funding",
            DeploymentStatus.production: "Production",
        },
        "pt": {
            DeploymentStatus.development: "Desenvolvimento",
            DeploymentStatus.funding: "Funding",
            DeploymentStatus.production: "Producao",
        },
    }
    lang = _resolve_language(language)
    return deployment_map.get(lang, deployment_map["es"]).get(status, status.value)


def _build_duplicate_detail(duplicate: IdeaCase, language: str) -> str:
    lang = _resolve_language(language)
    title = duplicate.title

    if duplicate.deployment_status == DeploymentStatus.production:
        return _msg(
            lang,
            f"Se detecto una idea similar: '{title}'. Ya esta en productivo. Revisa el catalogo de ideas en produccion para mas detalles.",
            f"A similar idea was detected: '{title}'. It is already in production. Review the production ideas catalog for more details.",
            f"Foi detectada uma ideia similar: '{title}'. Ela ja esta em producao. Revise o catalogo de ideias em producao para mais detalhes.",
        )

    status_label = _localized_status_label(duplicate.status, lang)
    stage_label = _localized_stage_label(duplicate.current_stage, lang)
    deployment_label = _localized_deployment_label(duplicate.deployment_status, lang)

    return _msg(
        lang,
        (
            f"Se detecto una idea similar en curso: '{title}' (ID: {duplicate.idea_id}). "
            f"Estado: {status_label}. Etapa: {stage_label}. Deployment: {deployment_label}. "
            f"Contacto: {duplicate.owner_display_name}."
        ),
        (
            f"A similar active idea was detected: '{title}' (ID: {duplicate.idea_id}). "
            f"Status: {status_label}. Stage: {stage_label}. Deployment: {deployment_label}. "
            f"Contact: {duplicate.owner_display_name}."
        ),
        (
            f"Uma ideia similar em andamento foi detectada: '{title}' (ID: {duplicate.idea_id}). "
            f"Status: {status_label}. Etapa: {stage_label}. Deploy: {deployment_label}. "
            f"Contato: {duplicate.owner_display_name}."
        ),
    )


def _build_context_snapshot(context: CompanyContext) -> ContextSnapshot:
    return ContextSnapshot(
        tenant_id=context.tenant_id,
        company_name=context.company_name,
        industry=context.industry,
        risk_tolerance=context.risk_tolerance,
        strategic_priorities=context.strategic_priorities,
        prohibited_domains=context.prohibited_domains,
        regulatory_constraints=context.regulatory_constraints,
        evaluated_at=datetime.utcnow(),
    )


def _apply_business_decision(idea: IdeaCase, request: BusinessIntakeRequest, context: CompanyContext) -> IdeaCase:
    validation = _evaluate_idea_with_context(request, context)
    rejection: RejectionInfo | None = None
    clarification_questions: list[ClarificationQuestion] = []

    if validation.recommendation == "continue":
        status = IdeaStatus.business_viable
        current_stage = IdeaStage.technical_validation
    elif validation.recommendation == "stop":
        lang = _resolve_language(idea.response_language)
        status = IdeaStatus.rejected
        current_stage = IdeaStage.business_validation
        rejection = RejectionInfo(
            phase=RejectionPhase.business,
            reason=_msg(
                lang,
                "No alineada al contexto de negocio o cae en un dominio restringido del tenant.",
                "Not aligned with business context or falls into a restricted tenant domain.",
                "Nao alinhada ao contexto de negocio ou cai em um dominio restrito do tenant.",
            ),
        )
    else:
        status = IdeaStatus.needs_clarification
        current_stage = IdeaStage.business_validation
        clarification_questions = _build_clarification_questions(request, context, validation)

    idea.business_validation = validation
    idea.status = status
    idea.current_stage = current_stage
    idea.rejection = rejection
    idea.clarification_questions = clarification_questions
    idea.context_snapshot = _build_context_snapshot(context)

    # Business reevaluation invalidates downstream artifacts so state remains consistent.
    idea.technical_questions = []
    idea.technical_interactions = []
    idea.technical_validation = None
    idea.architecture_package = None
    idea.response_composition = None
    return idea


def _ensure_technical_chat_ready(idea: IdeaCase) -> tuple[IdeaCase, bool]:
    if idea.status != IdeaStatus.business_viable:
        return (idea, False)

    # Legacy compatibility: if idea was technically validated without chat and no architecture exists,
    # force the guided technical chat flow before architecture generation.
    if idea.technical_validation is not None and len(idea.technical_interactions) == 0 and idea.architecture_package is None:
        idea.technical_validation = None
        idea.rejection = None
        idea.technical_questions = _build_technical_questions(idea)
        return (idea, True)

    if idea.technical_validation is not None:
        return (idea, False)

    if not idea.technical_questions:
        idea.technical_questions = _build_technical_questions(idea)
        return (idea, True)

    return (idea, False)


def _evaluate_technical_feasibility(request: BusinessIntakeRequest) -> tuple[bool, str]:
    text = f"{request.title} {request.problem_statement} {request.expected_value}".lower()

    blocked_patterns = [
        "sin api",
        "mainframe",
        "reemplazar core",
        "en 1 mes",
        "criptomonedas",
    ]

    for pattern in blocked_patterns:
        if pattern in text:
            return (
                False,
                "Riesgo tecnico alto para MVP: dependencias de integracion o alcance no viable en ventana inicial.",
            )

    return (True, "Viable tecnicamente para pasar a diseno de solucion.")


def _run_technical_validation(idea: IdeaCase, request: TechnicalValidationRequest) -> TechnicalValidation:
    lang = _resolve_language(idea.response_language)
    integration_complexity = min(100, 20 + len(request.systems_in_scope) * 10 + len(request.integration_constraints) * 8)
    security_risk = min(100, 20 + len(request.security_requirements) * 10)
    if any("pii" in item.lower() or "financ" in item.lower() for item in request.data_sources):
        security_risk = min(100, security_risk + 10)

    data_readiness = max(0, min(100, 40 + len(request.data_sources) * 12 - len(request.integration_constraints) * 5))

    timeline_penalty = 20 if request.timeline_weeks <= 4 else 0
    feasibility_score = max(
        0,
        min(
            100,
            100 - int(integration_complexity * 0.35) - int(security_risk * 0.25) + int(data_readiness * 0.30) - timeline_penalty,
        ),
    )

    blockers: list[str] = []
    if request.timeline_weeks <= 4 and integration_complexity > 50:
        blockers.append(
            _msg(
                lang,
                "La ventana de entrega es agresiva para el nivel de integraciones solicitado.",
                "The delivery window is aggressive for the requested integration level.",
                "A janela de entrega e agressiva para o nivel de integracoes solicitado.",
            )
        )
    if data_readiness < 45:
        blockers.append(
            _msg(
                lang,
                "Madurez de datos insuficiente para un piloto confiable.",
                "Data maturity is insufficient for a reliable pilot.",
                "A maturidade de dados e insuficiente para um piloto confiavel.",
            )
        )
    if security_risk > 65:
        blockers.append(
            _msg(
                lang,
                "Riesgo de seguridad/compliance por encima de umbral recomendado para MVP2.",
                "Security/compliance risk is above the recommended MVP2 threshold.",
                "O risco de seguranca/compliance esta acima do limite recomendado para o MVP2.",
            )
        )

    recommendation = "continue"
    if feasibility_score < 45 or blockers:
        recommendation = "stop"
    elif feasibility_score < 65:
        recommendation = "clarify"

    assumptions = [
        _msg(
            lang,
            "La validacion tecnica se realiza con supuestos iniciales y debe confirmarse con arquitectura detallada.",
            "Technical validation is based on initial assumptions and must be confirmed with detailed architecture.",
            "A validacao tecnica considera suposicoes iniciais e deve ser confirmada com arquitetura detalhada.",
        ),
        _msg(
            lang,
            "Se requiere al menos un entorno de datos controlado para pruebas de integracion.",
            "At least one controlled data environment is required for integration testing.",
            "E necessario ao menos um ambiente de dados controlado para testes de integracao.",
        ),
    ]

    return TechnicalValidation(
        feasibility_score=feasibility_score,
        integration_complexity=integration_complexity,
        security_risk=security_risk,
        data_readiness=data_readiness,
        recommendation=recommendation,
        blockers=blockers,
        assumptions=assumptions,
    )


def _build_technical_questions(idea: IdeaCase) -> list[TechnicalQuestion]:
    lang = _resolve_language(idea.response_language)
    return [
        TechnicalQuestion(
            question_id="systems_scope",
            prompt=_msg(
                lang,
                "Que sistemas concretos participan en el flujo y cual es el sistema de registro?",
                "Which concrete systems are part of the flow, and which one is the system of record?",
                "Quais sistemas concretos participam do fluxo e qual e o sistema de registro?",
            ),
            rationale=_msg(
                lang,
                "Definir alcance de integracion evita subestimar complejidad y dependencias.",
                "Defining integration scope avoids underestimating complexity and dependencies.",
                "Definir o escopo de integracao evita subestimar complexidade e dependencias.",
            ),
            suggested_answers=[
                _msg(
                    lang,
                    "CRM y Core Banking participan; Core Banking es sistema de registro.",
                    "CRM and Core Banking are involved; Core Banking is the system of record.",
                    "CRM e Core Banking participam; Core Banking e o sistema de registro.",
                ),
                _msg(
                    lang,
                    "Canal digital, motor de reglas y data lake; data lake concentra historico para analitica.",
                    "Digital channel, rules engine, and data lake; the data lake centralizes historical analytics.",
                    "Canal digital, motor de regras e data lake; o data lake concentra historico para analitica.",
                ),
                _msg(
                    lang,
                    "BPM de onboarding, KYC externo y bus de eventos; BPM orquesta el flujo principal.",
                    "Onboarding BPM, external KYC, and event bus; BPM orchestrates the main flow.",
                    "BPM de onboarding, KYC externo e barramento de eventos; o BPM orquestra o fluxo principal.",
                ),
            ],
        ),
        TechnicalQuestion(
            question_id="data_security",
            prompt=_msg(
                lang,
                "Que datos sensibles se usan y que controles de seguridad/compliance se aplicaran?",
                "Which sensitive data is used and which security/compliance controls will be applied?",
                "Quais dados sensiveis sao usados e quais controles de seguranca/compliance serao aplicados?",
            ),
            rationale=_msg(
                lang,
                "El nivel de sensibilidad impacta riesgo de seguridad y requisitos regulatorios.",
                "Sensitivity level impacts security risk and regulatory requirements.",
                "O nivel de sensibilidade impacta o risco de seguranca e os requisitos regulatorios.",
            ),
            suggested_answers=[
                _msg(
                    lang,
                    "Se usaran datos KYC/PII con cifrado en reposo/transito, RBAC y auditoria por evento.",
                    "KYC/PII data will be used with encryption at rest/in transit, RBAC, and event-level auditing.",
                    "Serao usados dados KYC/PII com criptografia em repouso/transito, RBAC e auditoria por evento.",
                ),
                _msg(
                    lang,
                    "Datos transaccionales anonimizados para piloto, con retencion limitada y control de accesos.",
                    "Anonymized transactional data for pilot, with limited retention and access control.",
                    "Dados transacionais anonimizados para piloto, com retencao limitada e controle de acesso.",
                ),
                _msg(
                    lang,
                    "PII y datos financieros con tokenizacion, segregacion de ambientes y revisiones de cumplimiento.",
                    "PII and financial data with tokenization, environment segregation, and compliance reviews.",
                    "PII e dados financeiros com tokenizacao, segregacao de ambientes e revisoes de compliance.",
                ),
            ],
        ),
        TechnicalQuestion(
            question_id="timeline_constraints",
            prompt=_msg(
                lang,
                "Cual es el timeline tecnico y las principales restricciones de integracion?",
                "What is the technical timeline and the main integration constraints?",
                "Qual e o timeline tecnico e as principais restricoes de integracao?",
            ),
            rationale=_msg(
                lang,
                "El tiempo y las restricciones definen factibilidad real para MVP2.",
                "Time and constraints define real MVP2 feasibility.",
                "Tempo e restricoes definem a viabilidade real do MVP2.",
            ),
            suggested_answers=[
                _msg(
                    lang,
                    "Piloto en 8 semanas; restriccion principal: dependencia con API legacy sin sandbox completo.",
                    "Pilot in 8 weeks; main constraint: dependency on a legacy API without full sandbox.",
                    "Piloto em 8 semanas; principal restricao: dependencia de API legada sem sandbox completo.",
                ),
                _msg(
                    lang,
                    "Entrega en 10 semanas; se requiere aprobacion de seguridad y ventana de cambios quincenal.",
                    "Delivery in 10 weeks; security approval and biweekly change window are required.",
                    "Entrega em 10 semanas; aprovacao de seguranca e janela quinzenal de mudancas sao necessarias.",
                ),
                _msg(
                    lang,
                    "Fase 1 en 6 semanas; integracion asincrona por eventos para reducir acoplamiento inicial.",
                    "Phase 1 in 6 weeks; asynchronous event-based integration to reduce initial coupling.",
                    "Fase 1 em 6 semanas; integracao assincrona por eventos para reduzir acoplamento inicial.",
                ),
            ],
        ),
    ]


def _technical_request_from_answers(answers: list[ClarificationAnswerInput]) -> TechnicalValidationRequest:
    by_id = {item.question_id: item.answer.strip() for item in answers}

    systems_text = by_id.get("systems_scope", "")
    security_text = by_id.get("data_security", "")
    timeline_text = by_id.get("timeline_constraints", "")

    systems_in_scope = [systems_text] if systems_text else []
    data_sources = [security_text] if security_text else []
    integration_constraints = [timeline_text] if timeline_text else []

    security_requirements: list[str] = []
    lowered_security = security_text.lower()
    if any(token in lowered_security for token in ["cifrado", "cifrar", "encryption"]):
        security_requirements.append("cifrado")
    if any(token in lowered_security for token in ["auditoria", "audit"]):
        security_requirements.append("auditoria")
    if any(token in lowered_security for token in ["rbac", "acceso", "access"]):
        security_requirements.append("control de acceso")
    if not security_requirements:
        security_requirements.append("controles base por definir")

    weeks = 8
    week_match = re.search(r"(\d{1,2})\s*(semana|semanas|week|weeks)", timeline_text.lower())
    if week_match:
        weeks = max(1, min(52, int(week_match.group(1))))

    return TechnicalValidationRequest(
        systems_in_scope=systems_in_scope,
        data_sources=data_sources,
        integration_constraints=integration_constraints,
        security_requirements=security_requirements,
        timeline_weeks=weeks,
        notes="\n".join([item.answer for item in answers]),
    )


def _build_technical_summary(
    answers: list[ClarificationAnswerInput],
    validation: TechnicalValidation,
    language: str,
) -> str:
    lang = _resolve_language(language)
    return (
        _msg(
            lang,
            f"Se procesaron {len(answers)} respuestas tecnicas. "
            f"Factibilidad={validation.feasibility_score}, complejidad={validation.integration_complexity}, "
            f"riesgo={validation.security_risk}, data_readiness={validation.data_readiness}.",
            f"Processed {len(answers)} technical answers. "
            f"Feasibility={validation.feasibility_score}, complexity={validation.integration_complexity}, "
            f"risk={validation.security_risk}, data_readiness={validation.data_readiness}.",
            f"Foram processadas {len(answers)} respostas tecnicas. "
            f"Factibilidade={validation.feasibility_score}, complexidade={validation.integration_complexity}, "
            f"risco={validation.security_risk}, data_readiness={validation.data_readiness}.",
        )
    )


def _build_architecture_package(idea: IdeaCase) -> ArchitecturePackage:
    lang = _resolve_language(idea.response_language)
    technical = idea.technical_validation
    if technical is None:
        raise HTTPException(
            status_code=400,
            detail=_msg(
                lang,
                "No existe validacion tecnica para generar arquitectura",
                "No technical validation found to generate architecture",
                "Nao existe validacao tecnica para gerar arquitetura",
            ),
        )

    latest_technical_answers = {}
    if idea.technical_interactions:
        latest_technical_answers = {
            item.question_id: item.answer.strip()
            for item in idea.technical_interactions[-1].answers
            if item.answer.strip()
        }

    systems_scope = latest_technical_answers.get("systems_scope", "")
    data_security = latest_technical_answers.get("data_security", "")
    timeline_constraints = latest_technical_answers.get("timeline_constraints", "")

    priority_context = ", ".join((idea.context_snapshot.strategic_priorities[:2] if idea.context_snapshot else []))
    regulatory_context = ", ".join((idea.context_snapshot.regulatory_constraints[:3] if idea.context_snapshot else []))
    affected_users = ", ".join(idea.affected_users[:4]) if idea.affected_users else _msg(
        lang,
        "usuarios por confirmar",
        "users to be confirmed",
        "usuarios a confirmar",
    )

    architecture_track = _msg(
        lang,
        "agnostica con aceleradores Azure",
        "agnostic with Azure accelerators",
        "agnostica com aceleradores Azure",
    )
    if technical.integration_complexity >= 55 or technical.security_risk >= 50:
        architecture_track = _msg(
            lang,
            "full Azure para acelerar gobierno, integracion y seguridad",
            "full Azure to accelerate governance, integration, and security",
            "full Azure para acelerar governanca, integracao e seguranca",
        )
    elif technical.data_readiness < 55:
        architecture_track = _msg(
            lang,
            "agnostica priorizando capa de datos portable",
            "agnostic prioritizing a portable data layer",
            "agnostica priorizando camada de dados portavel",
        )

    components = [
        ArchitectureComponent(
            name="Business Intake API",
            purpose=(
                _msg(
                    lang,
                    f"Orquesta el caso '{idea.title}' y mantiene estado por tenant para usuarios objetivo: {affected_users}.",
                    f"Orchestrates case '{idea.title}' and maintains tenant state for target users: {affected_users}.",
                    f"Orquestra o caso '{idea.title}' e mantem estado por tenant para usuarios-alvo: {affected_users}.",
                )
            ),
        ),
        ArchitectureComponent(
            name="Technical Validation Agent",
            purpose=(
                _msg(
                    lang,
                    "Evalua factibilidad tecnica y riesgos del caso usando respuestas guiadas del chat tecnico.",
                    "Evaluates technical feasibility and risk using guided technical chat answers.",
                    "Avalia factibilidade tecnica e riscos do caso usando respostas guiadas do chat tecnico.",
                )
            ),
        ),
        ArchitectureComponent(
            name="Context Engine",
            purpose=(
                _msg(
                    lang,
                    "Aplica prioridades y restricciones del tenant para mantener alineacion de negocio y compliance.",
                    "Applies tenant priorities and constraints to keep business and compliance alignment.",
                    "Aplica prioridades e restricoes do tenant para manter alinhamento de negocio e compliance.",
                )
            ),
        ),
        ArchitectureComponent(
            name="Vendor-Agnostic Runtime Layer",
            purpose=_msg(
                lang,
                "Contiene componentes portables (contenedores, API, mensajeria y observabilidad) para despliegue en distintas nubes.",
                "Contains portable components (containers, API, messaging, and observability) for multi-cloud deployment.",
                "Contem componentes portaveis (containers, API, mensageria e observabilidade) para deploy multi-cloud.",
            ),
        ),
        ArchitectureComponent(
            name="Azure Accelerators Layer",
            purpose=_msg(
                lang,
                "Incorpora servicios administrados de Azure cuando se prioriza velocidad y gobierno empresarial.",
                "Adds managed Azure services when speed and enterprise governance are prioritized.",
                "Incorpora servicos gerenciados do Azure quando velocidade e governanca empresarial sao prioridade.",
            ),
        ),
        ArchitectureComponent(
            name="Azure OpenAI Service",
            purpose=_msg(
                lang,
                "Soporta razonamiento asistido para validacion, recomendaciones y composicion de entregables.",
                "Supports assisted reasoning for validation, recommendations, and deliverable composition.",
                "Suporta raciocinio assistido para validacao, recomendacoes e composicao de entregaveis.",
            ),
        ),
    ]

    if systems_scope:
        components.append(
            ArchitectureComponent(
                name="Integration Orchestrator",
                purpose=_msg(
                    lang,
                    f"Coordina integraciones declaradas en alcance tecnico: {systems_scope}",
                    f"Coordinates integrations declared in technical scope: {systems_scope}",
                    f"Coordena integracoes declaradas no escopo tecnico: {systems_scope}",
                ),
            )
        )

    if data_security:
        components.append(
            ArchitectureComponent(
                name="Data Protection Controls",
                purpose=_msg(
                    lang,
                    f"Implementa controles de seguridad/compliance definidos para el caso: {data_security}",
                    f"Implements security/compliance controls defined for this case: {data_security}",
                    f"Implementa controles de seguranca/compliance definidos para o caso: {data_security}",
                ),
            )
        )

    if technical.security_risk >= 50:
        components.append(
            ArchitectureComponent(
                name="Security Control Layer",
                purpose=_msg(
                    lang,
                    "Aplica controles de acceso, auditoria y politicas de compliance por etapa.",
                    "Applies access control, auditing, and compliance policies by stage.",
                    "Aplica controles de acesso, auditoria e politicas de compliance por etapa.",
                ),
            )
        )

    suggested_component_catalog = [
        ArchitectureComponent(
            name="API Gateway",
            purpose=_msg(
                lang,
                "Centraliza autenticacion, cuotas y politicas para consumo seguro de APIs.",
                "Centralizes authentication, throttling, and policies for secure API consumption.",
                "Centraliza autenticacao, limites e politicas para consumo seguro de APIs.",
            ),
        ),
        ArchitectureComponent(
            name="Event Bus",
            purpose=_msg(
                lang,
                "Recomendado cuando hay multiples sistemas y se requiere integracion asincrona desacoplada.",
                "Recommended when multiple systems require decoupled asynchronous integration.",
                "Recomendado quando multiplos sistemas exigem integracao assincrona desacoplada.",
            ),
        ),
        ArchitectureComponent(
            name="Vector Retrieval Layer",
            purpose=_msg(
                lang,
                "Habilita grounding de conocimiento empresarial para respuestas mas precisas del agente.",
                "Enables enterprise knowledge grounding for more accurate agent responses.",
                "Permite grounding de conhecimento empresarial para respostas mais precisas do agente.",
            ),
        ),
        ArchitectureComponent(
            name="Observability & FinOps",
            purpose=_msg(
                lang,
                "Monitorea latencia, costos y calidad para sostener operacion en produccion.",
                "Monitors latency, costs, and quality to sustain production operations.",
                "Monitora latencia, custos e qualidade para sustentar operacao em producao.",
            ),
        ),
    ]

    if technical.security_risk >= 50:
        suggested_component_catalog.append(
            ArchitectureComponent(
                name="Identity & Secrets",
                purpose=_msg(
                    lang,
                    "Agregar federacion de identidad, RBAC y gestion de secretos para reducir riesgo.",
                    "Add identity federation, RBAC, and secrets management to reduce risk.",
                    "Adicionar federacao de identidade, RBAC e gestao de segredos para reduzir risco.",
                ),
            )
        )

    if technical.integration_complexity >= 55:
        suggested_component_catalog.append(
            ArchitectureComponent(
                name="Workflow Orchestrator",
                purpose=_msg(
                    lang,
                    "Coordina dependencias complejas y retries entre procesos de negocio.",
                    "Coordinates complex dependencies and retries across business processes.",
                    "Coordena dependencias complexas e retries entre processos de negocio.",
                ),
            )
        )

    if technical.data_readiness < 55:
        suggested_component_catalog.append(
            ArchitectureComponent(
                name="Data Quality Pipeline",
                purpose=_msg(
                    lang,
                    "Normaliza y valida fuentes antes de exponer datos a los modelos.",
                    "Normalizes and validates sources before exposing data to models.",
                    "Normaliza e valida fontes antes de expor dados aos modelos.",
                ),
            )
        )

    monthly_production_consumption = _estimate_monthly_consumption(idea, latest_technical_answers)

    integration_points = [
        _msg(
            lang,
            "Frontend React consume intake, aclaraciones, chat tecnico y generacion de arquitectura por caso.",
            "React frontend consumes intake, clarification, technical chat, and architecture generation per case.",
            "Frontend React consome intake, esclarecimentos, chat tecnico e geracao de arquitetura por caso.",
        ),
        _msg(
            lang,
            "Camino recomendado (agnostico): API contenedorizada + base SQL portable + object storage compatible S3 + vector store estandar.",
            "Recommended path (agnostic): containerized API + portable SQL database + S3-compatible object storage + standard vector store.",
            "Caminho recomendado (agnostico): API em containers + banco SQL portavel + object storage compativel com S3 + vector store padrao.",
        ),
        _msg(
            lang,
            "Camino acelerado (Azure): Container Apps + PostgreSQL/SQL + Blob Storage + AI Search + API Management.",
            "Accelerated path (Azure): Container Apps + PostgreSQL/SQL + Blob Storage + AI Search + API Management.",
            "Caminho acelerado (Azure): Container Apps + PostgreSQL/SQL + Blob Storage + AI Search + API Management.",
        ),
        _msg(
            lang,
            f"Ruta objetiva sugerida para este caso: {architecture_track}.",
            f"Objective route suggested for this case: {architecture_track}.",
            f"Rota objetiva sugerida para este caso: {architecture_track}.",
        ),
    ]

    if systems_scope:
        integration_points.append(f"Integraciones objetivo del caso: {systems_scope}.")
    if timeline_constraints:
        integration_points.append(f"Restricciones de timeline/integracion declaradas: {timeline_constraints}.")
    if priority_context:
        integration_points.append(f"Alineacion con prioridades estrategicas del tenant: {priority_context}.")
    if regulatory_context:
        integration_points.append(f"Restricciones regulatorias aplicables: {regulatory_context}.")

    ai_and_complementary_services = [
        "Azure OpenAI Service para prompts de negocio/tecnicos y composicion de respuestas",
        "Azure AI Search para recuperar contexto empresarial y evidencia relevante",
        "Azure AI Document Intelligence para extraer contenido estructurado de PDF/PPT/Word",
        "Azure API Management para gobierno y seguridad de APIs",
        "Azure Key Vault para secretos y credenciales",
    ]

    if technical.integration_complexity >= 55:
        ai_and_complementary_services.append(
            _msg(
                lang,
                "Azure Service Bus para desacoplar integraciones complejas",
                "Azure Service Bus to decouple complex integrations",
                "Azure Service Bus para desacoplar integracoes complexas",
            )
        )
    if technical.security_risk >= 50:
        ai_and_complementary_services.append(
            _msg(
                lang,
                "Microsoft Entra ID + RBAC + Managed Identity para acceso seguro",
                "Microsoft Entra ID + RBAC + Managed Identity for secure access",
                "Microsoft Entra ID + RBAC + Managed Identity para acesso seguro",
            )
        )
    if technical.data_readiness < 55:
        ai_and_complementary_services.append(
            _msg(
                lang,
                "Azure Data Factory para preparar y estandarizar fuentes de datos",
                "Azure Data Factory to prepare and standardize data sources",
                "Azure Data Factory para preparar e padronizar fontes de dados",
            )
        )

    deployment_steps = [
        _msg(
            lang,
            "Definir decision de plataforma: agnostica o full Azure segun restricciones del caso.",
            "Define platform decision: agnostic or full Azure based on case constraints.",
            "Definir decisao de plataforma: agnostica ou full Azure segundo as restricoes do caso.",
        ),
        _msg(
            lang,
            f"Implementar baseline portable para el caso '{idea.title}' (API, datos, seguridad y observabilidad).",
            f"Implement portable baseline for case '{idea.title}' (API, data, security, observability).",
            f"Implementar baseline portavel para o caso '{idea.title}' (API, dados, seguranca e observabilidade).",
        ),
        _msg(
            lang,
            "Si se elige Azure acelerado: habilitar Container Apps, APIM, Key Vault, AI Search y servicios de IA.",
            "If Azure accelerated is selected: enable Container Apps, APIM, Key Vault, AI Search, and AI services.",
            "Se Azure acelerado for escolhido: habilitar Container Apps, APIM, Key Vault, AI Search e servicos de IA.",
        ),
        _msg(
            lang,
            "Activar telemetria por etapa y KPI de negocio para seguimiento de valor y riesgo.",
            "Enable stage telemetry and business KPIs for value and risk tracking.",
            "Ativar telemetria por etapa e KPIs de negocio para acompanhar valor e risco.",
        ),
        _msg(
            lang,
            f"Servicios complementarios recomendados: {', '.join(ai_and_complementary_services)}.",
            f"Recommended complementary services: {', '.join(ai_and_complementary_services)}.",
            f"Servicos complementares recomendados: {', '.join(ai_and_complementary_services)}.",
        ),
    ]

    if timeline_constraints:
        deployment_steps.append(f"Planificar release segun restricciones de timeline: {timeline_constraints}.")

    risks = list(technical.blockers)
    if technical.security_risk >= 50 and not any("seguridad" in item.lower() for item in risks):
        risks.append(
            _msg(
                lang,
                "Riesgo de seguridad elevado; reforzar controles de acceso, auditoria y cumplimiento antes de piloto.",
                "Elevated security risk; strengthen access controls, auditing, and compliance before pilot.",
                "Risco de seguranca elevado; reforcar controles de acesso, auditoria e compliance antes do piloto.",
            )
        )
    if technical.data_readiness < 55 and not any("datos" in item.lower() for item in risks):
        risks.append(
            _msg(
                lang,
                "Madurez de datos limitada para el caso; se requiere plan de calidad y disponibilidad de fuentes.",
                "Limited data maturity for this case; a data quality and source availability plan is required.",
                "Maturidade de dados limitada para este caso; e necessario plano de qualidade e disponibilidade de fontes.",
            )
        )
    if not idea.affected_users:
        risks.append(
            _msg(
                lang,
                "Usuarios finales no cerrados; validar adopcion y ownership operativo antes de escalar.",
                "End users are not clearly defined; validate adoption and operational ownership before scaling.",
                "Usuarios finais nao definidos; validar adocao e ownership operacional antes de escalar.",
            )
        )
    if not risks:
        risks.append(
            _msg(
                lang,
                "Validar carga de integraciones en ambiente de preproduccion antes de piloto.",
                "Validate integration load in pre-production before pilot.",
                "Validar carga de integracoes em pre-producao antes do piloto.",
            )
        )

    return ArchitecturePackage(
        solution_name=_msg(
            lang,
            f"{idea.title} - Paquete de Arquitectura MVP2",
            f"{idea.title} - MVP2 Architecture Package",
            f"{idea.title} - Pacote de Arquitetura MVP2",
        ),
        summary=_msg(
            lang,
            f"Paquete de arquitectura para '{idea.title}', alineado al problema '{idea.problem_statement}' y valor esperado '{idea.expected_value}'. "
            f"Incluye rutas agnostica y full Azure, con recomendacion objetiva por complejidad, riesgo y madurez de datos.",
            f"Architecture package for '{idea.title}', aligned with problem '{idea.problem_statement}' and expected value '{idea.expected_value}'. "
            f"Includes agnostic and full Azure paths, with objective recommendation by complexity, risk, and data readiness.",
            f"Pacote de arquitetura para '{idea.title}', alinhado ao problema '{idea.problem_statement}' e ao valor esperado '{idea.expected_value}'. "
            f"Inclui caminhos agnostico e full Azure, com recomendacao objetiva por complexidade, risco e maturidade de dados.",
        ),
        components=components,
        suggested_component_catalog=suggested_component_catalog,
        monthly_production_consumption=monthly_production_consumption,
        integration_points=integration_points,
        deployment_steps=deployment_steps,
        risks=risks,
        generated_at=datetime.utcnow(),
    )


def _estimate_tokens(text: str) -> int:
    words = len((text or "").split())
    # Conservative approximation for multilingual text where token/word ratio varies.
    return max(1, int(words * 1.3))


def _estimate_idea_token_cost(idea: IdeaCase) -> dict[str, float | int]:
    prompt_text_parts = [
        idea.title,
        idea.problem_statement,
        idea.expected_value,
        " ".join(idea.affected_users),
    ]
    completion_text_parts = [
        " ".join(idea.business_validation.assumptions),
        " ".join(idea.business_validation.context_signals),
    ]

    if idea.technical_interactions:
        latest = idea.technical_interactions[-1]
        prompt_text_parts.extend(answer.answer for answer in latest.answers)
        completion_text_parts.append(latest.agent_summary)

    if idea.response_composition is not None:
        completion_text_parts.append(idea.response_composition.message)
        completion_text_parts.extend(idea.response_composition.next_actions)

    if idea.architecture_package is not None:
        completion_text_parts.append(idea.architecture_package.summary)
        completion_text_parts.extend(item.purpose for item in idea.architecture_package.components)

    prompt_tokens = _estimate_tokens("\n".join(prompt_text_parts))
    completion_tokens = _estimate_tokens("\n".join(completion_text_parts))
    total_tokens = prompt_tokens + completion_tokens

    # Estimated rates (USD per 1K tokens) for planning-level portfolio tracking.
    prompt_rate = 0.005
    completion_rate = 0.015
    estimated_cost_usd = round((prompt_tokens / 1000) * prompt_rate + (completion_tokens / 1000) * completion_rate, 4)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost_usd,
    }


def _count_scope_items(value: str) -> int:
    if not value or not value.strip():
        return 0
    parts = [item.strip() for item in re.split(r"[,;/]|\band\b|\by\b|\be\b", value, flags=re.IGNORECASE)]
    return max(1, len([item for item in parts if item]))


def _estimate_monthly_consumption(idea: IdeaCase, latest_technical_answers: dict[str, str]) -> ArchitectureConsumptionEstimate:
    technical = idea.technical_validation
    if technical is None:
        raise HTTPException(status_code=400, detail="No technical validation available to estimate monthly consumption")

    affected_users_count = max(1, len(idea.affected_users))
    systems_count = _count_scope_items(latest_technical_answers.get("systems_scope", ""))
    data_sources_count = _count_scope_items(latest_technical_answers.get("data_security", ""))

    demand_factor = 1.0 + min(0.6, affected_users_count / 20)
    integration_factor = 1.0 + min(0.5, technical.integration_complexity / 200)
    risk_factor = 1.0 + min(0.2, technical.security_risk / 500)

    monthly_executions = max(
        600,
        int((affected_users_count * 140 + systems_count * 120 + data_sources_count * 60) * demand_factor * integration_factor),
    )
    prompt_tokens_per_execution = max(120, int(80 + systems_count * 25 + technical.integration_complexity * 1.1))
    completion_tokens_per_execution = max(90, int(60 + technical.data_readiness * 0.8 + technical.security_risk * 0.6))

    monthly_prompt_tokens = monthly_executions * prompt_tokens_per_execution
    monthly_completion_tokens = monthly_executions * completion_tokens_per_execution

    prompt_rate = 0.005
    completion_rate = 0.015
    estimated_monthly_cost_usd = round(
        (monthly_prompt_tokens / 1000) * prompt_rate * risk_factor
        + (monthly_completion_tokens / 1000) * completion_rate * risk_factor,
        2,
    )

    assumptions = [
        f"Base de usuarios activos aproximada: {affected_users_count}",
        f"Sistemas en alcance aproximados: {systems_count}",
        f"Fuentes/dominios de datos relevantes: {data_sources_count}",
        "La estimacion es de planeacion y no sustituye medicion real en produccion.",
        "Se asume uso estable mensual con picos moderados de adopcion.",
    ]

    return ArchitectureConsumptionEstimate(
        monthly_executions=monthly_executions,
        prompt_tokens_per_execution=prompt_tokens_per_execution,
        completion_tokens_per_execution=completion_tokens_per_execution,
        monthly_prompt_tokens=monthly_prompt_tokens,
        monthly_completion_tokens=monthly_completion_tokens,
        estimated_monthly_cost_usd=estimated_monthly_cost_usd,
        assumptions=assumptions,
    )


def _is_use_case_ready(idea: IdeaCase) -> bool:
    return (
        idea.status == IdeaStatus.business_viable
        and idea.technical_validation is not None
        and idea.technical_validation.recommendation != "stop"
        and idea.architecture_package is not None
    )


def _as_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


def _current_quota_month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def _estimate_monthly_project_tokens(idea: IdeaCase) -> int:
    package = idea.architecture_package
    monthly = package.monthly_production_consumption if package is not None else None
    if monthly is not None:
        return int(monthly.monthly_prompt_tokens + monthly.monthly_completion_tokens)
    token_cost = _estimate_idea_token_cost(idea)
    return int(token_cost["total_tokens"])


def _build_admin_dashboard_payload(tenant_id: str) -> dict:
    ideas = idea_store.list_by_tenant(tenant_id)
    use_cases = [idea for idea in ideas if _is_use_case_ready(idea)]
    production_use_cases = [idea for idea in use_cases if idea.deployment_status == DeploymentStatus.production]
    quota_month = _current_quota_month()

    approved_use_cases = []
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    total_cost = 0.0
    quota_total_tokens = 0
    quota_consumed_tokens = 0
    feasibility_scores: list[int] = []
    cycle_times_hours: list[float] = []
    production_apps = []

    component_counter: dict[str, int] = {}

    for idea in use_cases:
        token_cost = _estimate_idea_token_cost(idea)
        total_prompt_tokens += int(token_cost["prompt_tokens"])
        total_completion_tokens += int(token_cost["completion_tokens"])
        total_tokens += int(token_cost["total_tokens"])
        total_cost += float(token_cost["estimated_cost_usd"])

        feasibility = idea.technical_validation.feasibility_score if idea.technical_validation is not None else 0
        feasibility_scores.append(feasibility)

        if idea.architecture_package is not None:
            for component in idea.architecture_package.components:
                component_counter[component.name] = component_counter.get(component.name, 0) + 1
            for component in idea.architecture_package.suggested_component_catalog:
                component_counter[component.name] = component_counter.get(component.name, 0) + 1

            cycle_time = (idea.architecture_package.generated_at - idea.created_at).total_seconds() / 3600
            if cycle_time > 0:
                cycle_times_hours.append(round(cycle_time, 2))

        approved_use_cases.append(
            {
                "idea_id": idea.idea_id,
                "title": idea.title,
                "owner_display_name": idea.owner_display_name,
                "status": idea.status.value,
                "current_stage": idea.current_stage.value,
                "feasibility_score": feasibility,
                "generated_at": _as_iso(idea.architecture_package.generated_at if idea.architecture_package else None),
                "estimated_tokens": token_cost["total_tokens"],
                "estimated_cost_usd": token_cost["estimated_cost_usd"],
                "deployment_status": idea.deployment_status.value,
                "response_language": idea.response_language,
            }
        )

    for idea in production_use_cases:
        consumed_tokens = _estimate_monthly_project_tokens(idea)
        extra_quota = idea.extra_quota_current_month if idea.quota_month == quota_month else 0
        quota_total = int(idea.monthly_token_quota_base + extra_quota)
        quota_remaining = max(0, quota_total - consumed_tokens)
        usage_pct = round((consumed_tokens / max(1, quota_total)) * 100, 1)
        monthly = idea.architecture_package.monthly_production_consumption if idea.architecture_package is not None else None

        quota_total_tokens += quota_total
        quota_consumed_tokens += consumed_tokens

        production_apps.append(
            {
                "idea_id": idea.idea_id,
                "title": idea.title,
                "owner_display_name": idea.owner_display_name,
                "response_language": idea.response_language,
                "quota_month": quota_month,
                "monthly_token_quota_base": idea.monthly_token_quota_base,
                "extra_quota_current_month": extra_quota,
                "quota_total_tokens": quota_total,
                "consumed_month_tokens": consumed_tokens,
                "quota_remaining_tokens": quota_remaining,
                "usage_pct": usage_pct,
                "estimated_monthly_cost_usd": monthly.estimated_monthly_cost_usd if monthly is not None else float(_estimate_idea_token_cost(idea)["estimated_cost_usd"]),
            }
        )

    technical_ready = [
        idea
        for idea in ideas
        if idea.technical_validation is not None and idea.technical_validation.recommendation != "stop"
    ]
    rejected_total = len([idea for idea in ideas if idea.status == IdeaStatus.rejected])
    approval_rate = round((len(use_cases) / len(ideas)) * 100, 1) if ideas else 0.0
    technical_pass_rate = round((len(technical_ready) / max(1, len([idea for idea in ideas if idea.status == IdeaStatus.business_viable]))) * 100, 1)

    top_components = [
        {"component": name, "count": count}
        for name, count in sorted(component_counter.items(), key=lambda item: item[1], reverse=True)[:5]
    ]

    return {
        "tenant_id": tenant_id,
        "approved_use_cases": approved_use_cases,
        "token_cost": {
            "project_count": len(use_cases),
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "quota_month": quota_month,
            "quota_total_tokens": quota_total_tokens,
            "quota_consumed_tokens": quota_consumed_tokens,
            "quota_remaining_tokens": max(0, quota_total_tokens - quota_consumed_tokens),
            "production_apps": production_apps,
        },
        "portfolio_metrics": {
            "total_ideas": len(ideas),
            "approved_use_cases": len(use_cases),
            "rejected_ideas": rejected_total,
            "approval_rate_pct": approval_rate,
            "technical_pass_rate_pct": technical_pass_rate,
            "avg_feasibility_score": round(sum(feasibility_scores) / len(feasibility_scores), 1) if feasibility_scores else 0.0,
            "avg_cycle_time_hours": round(sum(cycle_times_hours) / len(cycle_times_hours), 1) if cycle_times_hours else 0.0,
            "top_components": top_components,
        },
    }


def _compose_architecture_message(idea: IdeaCase) -> tuple[str, list[str]]:
    lang = _resolve_language(idea.response_language)
    package = idea.architecture_package
    technical = idea.technical_validation
    if package is None or technical is None:
        return (
            _msg(
                lang,
                "No hay artefactos suficientes para componer la respuesta.",
                "There are not enough artifacts to compose the response.",
                "Nao ha artefatos suficientes para compor a resposta.",
            ),
            [],
        )

    message = _msg(
        lang,
        f"La idea '{idea.title}' completo la validacion tecnica con score de factibilidad {technical.feasibility_score}/100. "
        f"Se genero un paquete de arquitectura con {len(package.components)} componentes y rutas agnostica/full Azure.",
        f"Idea '{idea.title}' completed technical validation with feasibility score {technical.feasibility_score}/100. "
        f"An architecture package was generated with {len(package.components)} components and agnostic/full Azure routes.",
        f"A ideia '{idea.title}' concluiu a validacao tecnica com score de factibilidade {technical.feasibility_score}/100. "
        f"Um pacote de arquitetura foi gerado com {len(package.components)} componentes e rotas agnostica/full Azure.",
    )
    next_actions = [
        _msg(
            lang,
            "Revisar el paquete con el equipo tecnico y priorizar integraciones criticas.",
            "Review the package with the technical team and prioritize critical integrations.",
            "Revisar o pacote com o time tecnico e priorizar integracoes criticas.",
        ),
        _msg(
            lang,
            "Confirmar controles de seguridad/compliance antes del piloto.",
            "Confirm security/compliance controls before pilot.",
            "Confirmar controles de seguranca/compliance antes do piloto.",
        ),
        _msg(
            lang,
            "Seleccionar ruta agnostica o full Azure y crear backlog de implementacion.",
            "Select agnostic or full Azure route and create implementation backlog.",
            "Selecionar rota agnostica ou full Azure e criar backlog de implementacao.",
        ),
    ]
    return (message, next_actions)


def _build_clarification_questions(
    request: BusinessIntakeRequest,
    context: CompanyContext,
    validation: BusinessValidation,
) -> list[ClarificationQuestion]:
    lang = _resolve_language(request.source_language)
    questions: list[ClarificationQuestion] = []

    if validation.value_score < 60:
        questions.append(
            ClarificationQuestion(
                question_id="impact_metric",
                prompt=_msg(
                    lang,
                    "Que metrica de negocio vas a mover y cual es la mejora esperada en 30-60 dias?",
                    "Which business metric will you move and what improvement is expected in 30-60 days?",
                    "Qual metrica de negocio voce vai mover e qual melhora e esperada em 30-60 dias?",
                ),
                rationale=_msg(
                    lang,
                    "Sin metrica concreta no se puede priorizar la idea en fase de negocio.",
                    "Without a concrete metric, the idea cannot be prioritized in the business phase.",
                    "Sem metrica concreta, a ideia nao pode ser priorizada na fase de negocio.",
                ),
                suggested_answers=[
                    _msg(
                        lang,
                        "Reducir tiempo de atencion en 25% en 8 semanas, medido contra baseline de ultimo trimestre.",
                        "Reduce handling time by 25% in 8 weeks, measured against last quarter baseline.",
                        "Reduzir tempo de atendimento em 25% em 8 semanas, medido contra baseline do ultimo trimestre.",
                    ),
                    _msg(
                        lang,
                        "Bajar tasa de fraude en onboarding en 15% con control semanal de incidentes confirmados.",
                        "Reduce onboarding fraud rate by 15% with weekly control of confirmed incidents.",
                        "Reduzir taxa de fraude no onboarding em 15% com controle semanal de incidentes confirmados.",
                    ),
                    _msg(
                        lang,
                        "Incrementar aprobaciones en primer contacto en 20% sin elevar riesgo regulatorio.",
                        "Increase first-contact approvals by 20% without increasing regulatory risk.",
                        "Aumentar aprovacoes no primeiro contato em 20% sem elevar risco regulatorio.",
                    ),
                ],
            )
        )

    if validation.risk_score > 55:
        questions.append(
            ClarificationQuestion(
                question_id="risk_controls",
                prompt=_msg(
                    lang,
                    "Que controles de riesgo/compliance aplicaran para evitar incumplimientos?",
                    "Which risk/compliance controls will be applied to prevent non-compliance?",
                    "Quais controles de risco/compliance serao aplicados para evitar nao conformidades?",
                ),
                rationale=_msg(
                    lang,
                    "La idea necesita controles explicitos para disminuir riesgo regulatorio.",
                    "The idea needs explicit controls to reduce regulatory risk.",
                    "A ideia precisa de controles explicitos para reduzir risco regulatorio.",
                ),
                suggested_answers=[
                    _msg(
                        lang,
                        "Implementar validaciones KYC/AML automativas y auditoria completa por transaccion.",
                        "Implement automated KYC/AML checks and full transaction-level auditing.",
                        "Implementar validacoes KYC/AML automaticas e auditoria completa por transacao.",
                    ),
                    _msg(
                        lang,
                        "Agregar revision humana obligatoria para casos de alto riesgo antes de decision final.",
                        "Add mandatory human review for high-risk cases before final decision.",
                        "Adicionar revisao humana obrigatoria para casos de alto risco antes da decisao final.",
                    ),
                    _msg(
                        lang,
                        "Definir reglas de explicabilidad, trazabilidad y retencion de evidencia para compliance.",
                        "Define explainability, traceability, and evidence-retention rules for compliance.",
                        "Definir regras de explicabilidade, rastreabilidade e retencao de evidencias para compliance.",
                    ),
                ],
            )
        )

    if len(request.affected_users) == 0:
        questions.append(
            ClarificationQuestion(
                question_id="target_users",
                prompt=_msg(
                    lang,
                    "Que usuarios o equipos seran impactados directamente por la solucion?",
                    "Which users or teams will be directly impacted by the solution?",
                    "Quais usuarios ou equipes serao impactados diretamente pela solucao?",
                ),
                rationale=_msg(
                    lang,
                    "Definir usuarios afectados mejora foco y factibilidad del MVP.",
                    "Defining impacted users improves MVP focus and feasibility.",
                    "Definir usuarios afetados melhora foco e factibilidade do MVP.",
                ),
                suggested_answers=[
                    _msg(
                        lang,
                        "Equipo de riesgo y operaciones de onboarding como usuarios principales.",
                        "Risk and onboarding operations teams as primary users.",
                        "Equipe de risco e operacoes de onboarding como usuarios principais.",
                    ),
                    _msg(
                        lang,
                        "Analistas de fraude, cumplimiento y lider de canal digital.",
                        "Fraud analysts, compliance team, and digital channel lead.",
                        "Analistas de fraude, compliance e lider do canal digital.",
                    ),
                    _msg(
                        lang,
                        "Backoffice de validacion documental con soporte de seguridad de la informacion.",
                        "Document validation back-office with information security support.",
                        "Backoffice de validacao documental com suporte de seguranca da informacao.",
                    ),
                ],
            )
        )

    if not questions:
        questions.append(
            ClarificationQuestion(
                question_id="scope_fit",
                prompt=(
                    _msg(
                        lang,
                        f"Como aseguras que el alcance se mantiene alineado a prioridades de {context.company_name} y evita dominios restringidos?",
                        f"How do you ensure scope stays aligned with {context.company_name} priorities and avoids restricted domains?",
                        f"Como voce garante que o escopo permanece alinhado as prioridades de {context.company_name} e evita dominios restritos?",
                    )
                ),
                rationale=_msg(
                    lang,
                    "Se requiere confirmar alineacion explicita con el contexto del tenant.",
                    "Explicit alignment with tenant context must be confirmed.",
                    "E necessario confirmar alinhamento explicito com o contexto do tenant.",
                ),
                suggested_answers=[
                    _msg(
                        lang,
                        "Definimos alcance solo para onboarding y excluimos decisiones de credito automatizadas.",
                        "We define scope only for onboarding and exclude automated credit decisions.",
                        "Definimos escopo apenas para onboarding e excluimos decisoes de credito automatizadas.",
                    ),
                    _msg(
                        lang,
                        "Priorizamos casos de fraude en canal digital y mantenemos aprobacion humana en decisiones criticas.",
                        "We prioritize fraud cases in digital channel and keep human approval for critical decisions.",
                        "Priorizamos casos de fraude no canal digital e mantemos aprovacao humana em decisoes criticas.",
                    ),
                    _msg(
                        lang,
                        "Alineamos el piloto a la prioridad de eficiencia operativa y cumplimiento regulatorio vigente.",
                        "We align the pilot to operational efficiency and current regulatory compliance priorities.",
                        "Alinhamos o piloto a prioridade de eficiencia operacional e compliance regulatorio vigente.",
                    ),
                ],
            )
        )

    return questions[:3]


def _questions_missing_suggestions(questions: list[ClarificationQuestion]) -> bool:
    if not questions:
        return True
    return any(len(question.suggested_answers) == 0 for question in questions)


def _clarification_completeness_score(answers: list[ClarificationAnswerInput]) -> int:
    score = 0
    for answer in answers:
        text = answer.answer.strip().lower()
        if len(text) >= 25:
            score += 20
        if any(token in text for token in ["%", "kpi", "margen", "fraude", "cumpl", "control", "sla", "tiempo"]):
            score += 15
        if any(char.isdigit() for char in text):
            score += 10
    return max(0, min(100, score))


def _answer_indicates_missing_information(text: str) -> bool:
    normalized = _normalize_for_duplicate(text)
    if not normalized:
        return True

    missing_info_signals = [
        "no se",
        "no tengo",
        "no contamos",
        "no existe",
        "sin informacion",
        "sin datos",
        "no aplica",
        "desconozco",
        "n a",
        "unknown",
        "dont know",
        "do not know",
        "not available",
        "no data",
        "not sure",
        "nao sei",
        "nao temos",
        "sem informacao",
        "desconheco",
    ]

    if any(signal in normalized for signal in missing_info_signals):
        return True

    # Very short answers without digits or business indicators are treated as missing evidence.
    if len(normalized) < 12 and not any(char.isdigit() for char in normalized):
        weak_tokens = {"no", "ninguno", "none", "na", "n a", "n a", "ninguna"}
        return normalized in weak_tokens

    return False


def _missing_information_answer_ids(answers: list[ClarificationAnswerInput]) -> list[str]:
    missing_ids: list[str] = []
    for item in answers:
        if _answer_indicates_missing_information(item.answer):
            missing_ids.append(item.question_id)
    return missing_ids


def _build_clarification_summary(
    answers: list[ClarificationAnswerInput],
    validation: BusinessValidation,
    language: str,
) -> str:
    lang = _resolve_language(language)
    answer_count = len(answers)
    return _msg(
        lang,
        f"Se procesaron {answer_count} aclaraciones. "
        f"Scores actualizados: valor={validation.value_score}, riesgo={validation.risk_score}.",
        f"Processed {answer_count} clarifications. "
        f"Updated scores: value={validation.value_score}, risk={validation.risk_score}.",
        f"Foram processados {answer_count} esclarecimentos. "
        f"Scores atualizados: valor={validation.value_score}, risco={validation.risk_score}.",
    )


def _is_objective_business_rejection(validation: BusinessValidation) -> bool:
    # Rechazo objetivo: dominio restringido, riesgo extremo o valor muy bajo con evidencia contextual.
    has_restricted_domain_signal = any(
        "dominio restringido" in signal.lower() for signal in validation.context_signals
    )
    has_risk_extreme = validation.risk_score >= 80
    has_low_value = validation.value_score <= 40
    has_evidence = len(validation.context_signals) > 0
    return has_restricted_domain_signal or has_risk_extreme or (has_low_value and has_evidence)


def _build_objective_rejection_reason(validation: BusinessValidation, language: str) -> str:
    lang = _resolve_language(language)
    top_signals = validation.context_signals[:2]
    evidence = " | ".join(top_signals) if top_signals else _msg(
        lang,
        "sin senales contextuales",
        "without contextual signals",
        "sem sinais contextuais",
    )
    return _msg(
        lang,
        "Rechazo objetivo por criterio de Context Engine: "
        f"value_score={validation.value_score}, risk_score={validation.risk_score}. "
        f"Evidencia: {evidence}.",
        "Objective rejection by Context Engine criteria: "
        f"value_score={validation.value_score}, risk_score={validation.risk_score}. "
        f"Evidence: {evidence}.",
        "Rejeicao objetiva por criterio do Context Engine: "
        f"value_score={validation.value_score}, risk_score={validation.risk_score}. "
        f"Evidencia: {evidence}.",
    )


def _business_rejection_reason(validation: BusinessValidation, completeness: int, language: str) -> str:
    lang = _resolve_language(language)
    if completeness < 40:
        return _msg(
            lang,
            "No se aporto informacion suficiente para validar valor y controles de riesgo en fase de negocio.",
            "Not enough information was provided to validate value and risk controls in the business phase.",
            "Nao foram fornecidas informacoes suficientes para validar valor e controles de risco na fase de negocio.",
        )
    if validation.risk_score > 65:
        return _msg(
            lang,
            "Con las aclaraciones recibidas, el riesgo de negocio/regulatorio sigue por encima del umbral aceptable del tenant.",
            "With the clarifications provided, business/regulatory risk remains above the tenant's acceptable threshold.",
            "Com os esclarecimentos fornecidos, o risco de negocio/regulatorio permanece acima do limite aceitavel do tenant.",
        )
    return _msg(
        lang,
        "Con las aclaraciones recibidas, la idea no demuestra impacto de negocio suficiente para pasar a validacion tecnica.",
        "With the clarifications provided, the idea does not show enough business impact to move to technical validation.",
        "Com os esclarecimentos fornecidos, a ideia nao demonstra impacto de negocio suficiente para avancar para validacao tecnica.",
    )


def _extract_affected_users_from_answers(answers: list[ClarificationAnswerInput]) -> list[str]:
    for item in answers:
        if item.question_id != "target_users":
            continue
        text = item.answer.strip()
        if not text:
            continue
        chunks = re.split(r",|;|\by\b|\band\b|\be\b", text, flags=re.IGNORECASE)
        normalized = [chunk.strip() for chunk in chunks if len(chunk.strip()) >= 3]
        if normalized:
            return normalized[:5]
    return []


def _clarification_reliability_score(
    completeness: int,
    answers: list[ClarificationAnswerInput],
    validation: BusinessValidation,
) -> int:
    score = completeness
    # Permite avanzar cuando solo existe una pregunta de aclaracion pero la respuesta es completa.
    if len(answers) == 1 and completeness >= 40:
        score += 25
    if len(answers) >= 3:
        score += 10
    if len(validation.context_signals) >= 2:
        score += 10
    if any(char.isdigit() for item in answers for char in item.answer):
        score += 5
    return max(0, min(100, score))


def _run_clarification_decision(
    idea: IdeaCase,
    context: CompanyContext,
    answers: list[ClarificationAnswerInput],
) -> tuple[BusinessValidation, IdeaStatus, IdeaStage, RejectionInfo | None]:
    lang = _resolve_language(idea.response_language)
    inferred_users = _extract_affected_users_from_answers(answers)
    merged_users = list(dict.fromkeys([*idea.affected_users, *inferred_users]))
    idea.affected_users = merged_users

    enrichment = "\n".join(f"{item.question_id}: {item.answer}" for item in answers)
    enriched_request = BusinessIntakeRequest(
        tenant_id=idea.tenant_id,
        title=idea.title,
        problem_statement=f"{idea.problem_statement}\n\nAclaraciones:\n{enrichment}",
        expected_value=f"{idea.expected_value}\n\nAclaraciones:\n{enrichment}",
        affected_users=merged_users,
        source_language=idea.source_language,
    )

    validation = _evaluate_idea_with_context(enriched_request, context)
    completeness = _clarification_completeness_score(answers)
    reliability = _clarification_reliability_score(completeness, answers, validation)
    missing_info_ids = _missing_information_answer_ids(answers)

    if missing_info_ids:
        total_answers = max(1, len(answers))
        missing_ratio = len(missing_info_ids) / total_answers
        validation.context_signals.append(
            _msg(
                lang,
                f"Respuestas sin evidencia suficiente en: {', '.join(missing_info_ids)}.",
                f"Answers without sufficient evidence in: {', '.join(missing_info_ids)}.",
                f"Respostas sem evidencia suficiente em: {', '.join(missing_info_ids)}.",
            )
        )

        # Contextual policy:
        # - High missing ratio + weak reliability => reject.
        # - Medium missing ratio => keep in clarification.
        # - Low missing ratio + strong evidence may still continue.
        if missing_ratio >= 0.67 and reliability < 80:
            validation.recommendation = "stop"
            validation.value_score = min(validation.value_score, 40)
            validation.risk_score = max(validation.risk_score, 70)
            rejection = RejectionInfo(
                phase=RejectionPhase.business,
                reason=_msg(
                    lang,
                    "No viable en fase de negocio: la falta de informacion en aclaraciones supera el umbral de confianza requerido por el contexto.",
                    "Not viable in business phase: missing clarification information exceeds the confidence threshold required by context.",
                    "Nao viavel na fase de negocio: a falta de informacao nos esclarecimentos excede o limite de confianca exigido pelo contexto.",
                ),
            )
            return (validation, IdeaStatus.rejected, IdeaStage.business_validation, rejection)

        if missing_ratio >= 0.34 and validation.recommendation != "stop":
            validation.recommendation = "clarify"
            validation.open_questions.insert(
                0,
                _msg(
                    lang,
                    "La aclaracion es parcial: hay informacion util, pero aun faltan datos clave para una decision robusta.",
                    "Clarification is partial: there is useful information, but key data is still missing for a robust decision.",
                    "O esclarecimento e parcial: ha informacao util, mas ainda faltam dados chave para uma decisao robusta.",
                ),
            )

    single_question_fast_track = len(answers) == 1 and completeness >= 30 and not missing_info_ids
    if single_question_fast_track and validation.recommendation != "stop":
        validation.value_score = min(100, validation.value_score + 8)
        validation.risk_score = max(0, validation.risk_score - 8)
        validation.recommendation = "continue"
        validation.context_signals.append(
            _msg(
                lang,
                "Aclaraciones suficientes para resolver dudas de negocio.",
                "Clarifications are sufficient to resolve business doubts.",
                "Esclarecimentos suficientes para resolver duvidas de negocio.",
            )
        )

    if validation.recommendation == "continue":
        return (validation, IdeaStatus.business_viable, IdeaStage.technical_validation, None)

    if reliability < 70:
        validation.open_questions.insert(
            0,
            _msg(
                lang,
                "La evidencia aun no es suficiente para una decision confiable. Completa metricas cuantificables y controles de riesgo.",
                "Evidence is still not enough for a reliable decision. Provide quantifiable metrics and risk controls.",
                "A evidencia ainda nao e suficiente para uma decisao confiavel. Complete metricas quantificaveis e controles de risco.",
            ),
        )
        validation.context_signals.append(
            _msg(
                lang,
                f"Confiabilidad de aclaracion insuficiente ({reliability}/100); se mantiene en aclaracion.",
                f"Clarification reliability is insufficient ({reliability}/100); idea remains in clarification.",
                f"Confiabilidade de esclarecimento insuficiente ({reliability}/100); a ideia permanece em esclarecimento.",
            ),
        )
        return (validation, IdeaStatus.needs_clarification, IdeaStage.business_validation, None)

    if validation.recommendation == "clarify":
        if completeness < 45:
            validation.open_questions.insert(
                0,
                _msg(
                    lang,
                    "La informacion sigue siendo insuficiente. Completa metrica de impacto, usuarios afectados y controles de riesgo.",
                    "Information is still insufficient. Add impact metric, affected users, and risk controls.",
                    "A informacao ainda e insuficiente. Complete metrica de impacto, usuarios afetados e controles de risco.",
                ),
            )
            validation.context_signals.append(
                _msg(
                    lang,
                    "Aclaracion incompleta; se mantiene en fase de aclaracion.",
                    "Clarification is incomplete; idea remains in clarification phase.",
                    "Esclarecimento incompleto; a ideia permanece na fase de esclarecimento.",
                )
            )
        else:
            validation.context_signals.append(
                _msg(
                    lang,
                    "Aclaracion parcial; se requiere una iteracion adicional antes de pasar a tecnica.",
                    "Partial clarification; one more iteration is required before moving to technical validation.",
                    "Esclarecimento parcial; e necessaria mais uma iteracao antes da validacao tecnica.",
                )
            )
        return (validation, IdeaStatus.needs_clarification, IdeaStage.business_validation, None)

    if validation.recommendation == "stop" and not _is_objective_business_rejection(validation):
        validation.open_questions.insert(
            0,
            _msg(
                lang,
                "No hay evidencia suficiente para rechazo objetivo. Se requiere una nueva iteracion de aclaracion.",
                "There is not enough evidence for an objective rejection. A new clarification iteration is required.",
                "Nao ha evidencia suficiente para rejeicao objetiva. E necessaria uma nova iteracao de esclarecimento.",
            ),
        )
        validation.context_signals.append(
            _msg(
                lang,
                "Stop no objetivo; se mantiene en aclaracion para mejorar confiabilidad.",
                "Non-objective stop; idea remains in clarification to improve reliability.",
                "Stop nao objetivo; a ideia permanece em esclarecimento para melhorar a confiabilidade.",
            )
        )
        return (validation, IdeaStatus.needs_clarification, IdeaStage.business_validation, None)

    rejection = RejectionInfo(
        phase=RejectionPhase.business,
        reason=(
            _build_objective_rejection_reason(validation, lang)
            if _is_objective_business_rejection(validation)
            else _business_rejection_reason(validation, completeness, lang)
        ),
    )
    return (validation, IdeaStatus.rejected, IdeaStage.business_validation, rejection)


def _insufficient_clarification_rejection(language: str | None) -> RejectionInfo:
    return RejectionInfo(
        phase=RejectionPhase.business,
        reason=_msg(
            language,
            "No viable en fase de negocio: despues de las aclaraciones no se obtuvo evidencia suficiente para sustentar el caso.",
            "Not viable in business phase: after clarifications, there is still not enough evidence to support the case.",
            "Nao viavel na fase de negocio: apos os esclarecimentos, ainda nao ha evidencia suficiente para sustentar o caso.",
        ),
    )


def _question_dependencies() -> dict[str, list[str]]:
    """Define which questions depend on prior ones. Empty list means independent."""
    return {
        "impact_metric": [],  # Always first priority
        "risk_controls": ["impact_metric"],  # Depends on knowing impact
        "target_users": [],  # Independent
        "scope_fit": ["impact_metric"],  # Depends on understanding impact
    }


def _question_is_dependent_on_previous(
    question_id: str,
    answered_question_ids: set[str],
) -> bool:
    """Check if a question depends on prior ones and if those dependencies are met."""
    dependencies = _question_dependencies()
    if question_id not in dependencies:
        return False
    required = dependencies[question_id]
    if not required:
        return False  # No dependencies
    return not all(req_id in answered_question_ids for req_id in required)


def _is_recoverable_business_rejection(validation: BusinessValidation) -> bool:
    """Determine if a rejection can be recovered with better information vs. objective rejection."""
    # Objective rejections (non-recoverable):
    has_restricted_domain = any("dominio restringido" in s.lower() for s in validation.context_signals)
    has_extreme_risk = validation.risk_score >= 85
    has_non_compliance_issue = any(
        keyword in " ".join(validation.context_signals).lower()
        for keyword in ["prohibido", "prohibited", "proibido"]
    )

    # If it's an objective rejection, it's not recoverable
    if has_restricted_domain or has_extreme_risk or has_non_compliance_issue:
        return False

    # Otherwise, if value is low but risk is manageable, it could be recoverable
    # (user may provide better metrics/evidence)
    return validation.value_score < 60 or (validation.risk_score < 85 and validation.value_score < 70)


@app.on_event("startup")
def startup_seed_context() -> None:
    for tenant_id in DEMO_CONTEXT_BY_TENANT:
        _seed_demo_context_if_needed(tenant_id)


@app.get("/health", response_model=MessageResponse)
def health() -> MessageResponse:
    return MessageResponse(message="ok")


@app.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest) -> AuthResponse:
    if AUTH_PROVIDER == "entra":
        _entra_not_configured()

    user = auth_store.authenticate(request.username, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrecta")

    # Garantiza que el contexto base demo quede persistido en BD al iniciar sesion.
    _seed_demo_context_if_needed(user["tenant_id"])

    token = auth_store.issue_token(user["user_id"])
    return AuthResponse(
        access_token=token,
        user_id=user["user_id"],
        display_name=user["display_name"],
        tenant_id=user["tenant_id"],
        role=user["role"],
    )


@app.get("/auth/me", response_model=UserProfile)
def me(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    return current_user


@app.get("/context/{tenant_id}", response_model=CompanyContext)
def get_company_context(tenant_id: str) -> CompanyContext:
    _seed_demo_context_if_needed(tenant_id)
    context = company_context_store.get(tenant_id)
    if context is None:
        raise HTTPException(
            status_code=404,
            detail="No hay contexto base para este tenant. Registra el contexto antes de ingresar ideas.",
        )
    return context


@app.put("/context/{tenant_id}", response_model=CompanyContext)
def upsert_company_context(tenant_id: str, request: UpsertCompanyContextRequest) -> CompanyContext:
    # Backward-compat endpoint kept without auth to avoid breaking existing clients.
    context = _build_company_context(tenant_id, request)
    return company_context_store.save(context)


@app.put("/admin/context/{tenant_id}", response_model=CompanyContext)
def admin_upsert_company_context(
    tenant_id: str,
    request: UpsertCompanyContextRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> CompanyContext:
    _require_admin(current_user)
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes modificar contexto de otro tenant")
    context = _build_company_context(tenant_id, request)
    return company_context_store.save(context)


@app.post("/admin/context/{tenant_id}/files", response_model=ContextFileUploadResponse)
def upload_context_file_endpoint(
    tenant_id: str,
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user),
) -> ContextFileUploadResponse:
    _require_admin(current_user)
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes subir archivos para otro tenant")
    return _upload_context_file_to_blob(tenant_id, file, current_user.user_id)


@app.get("/admin/dashboard")
def get_admin_dashboard(current_user: UserProfile = Depends(get_current_user)) -> dict:
    _require_admin(current_user)
    return _build_admin_dashboard_payload(current_user.tenant_id)


@app.patch("/admin/ideas/{idea_id}/deployment-status", response_model=IdeaCase)
def update_idea_deployment_status(
    idea_id: str,
    request: DeploymentStatusUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaCase:
    _require_admin_or_technical(current_user)
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes modificar proyectos de otro tenant")

    idea.deployment_status = request.deployment_status
    return idea_store.save(idea)


@app.patch("/admin/ideas/{idea_id}/token-quota", response_model=IdeaCase)
def update_idea_token_quota(
    idea_id: str,
    request: TokenQuotaUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaCase:
    _require_admin(current_user)
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes modificar cuotas de otro tenant")

    idea.monthly_token_quota_base = request.monthly_token_quota_base
    idea.quota_adjustments.append(
        QuotaAdjustment(
            adjustment_type="set_base",
            delta_tokens=request.monthly_token_quota_base,
            reason="Quota base update",
            adjusted_by_user_id=current_user.user_id,
            adjusted_by_display_name=current_user.display_name,
            adjusted_at=datetime.utcnow(),
        )
    )
    return idea_store.save(idea)


@app.post("/admin/ideas/{idea_id}/token-quota-extra", response_model=IdeaCase)
def add_idea_token_quota_extra(
    idea_id: str,
    request: TokenQuotaExtraRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaCase:
    _require_admin(current_user)
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes modificar cuotas de otro tenant")

    current_month = _current_quota_month()
    if idea.quota_month != current_month:
        idea.quota_month = current_month
        idea.extra_quota_current_month = 0

    idea.extra_quota_current_month += request.extra_tokens
    idea.quota_adjustments.append(
        QuotaAdjustment(
            adjustment_type="add_extra",
            delta_tokens=request.extra_tokens,
            reason=request.reason.strip(),
            adjusted_by_user_id=current_user.user_id,
            adjusted_by_display_name=current_user.display_name,
            adjusted_at=datetime.utcnow(),
        )
    )
    return idea_store.save(idea)


@app.delete("/admin/ideas/{idea_id}", response_model=MessageResponse)
def delete_idea(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> MessageResponse:
    _require_admin(current_user)
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes eliminar proyectos de otro tenant")

    idea_store.delete(idea_id)
    return MessageResponse(message=f"Idea {idea_id} eliminada exitosamente")


@app.post("/ideas/intake", response_model=IdeaCase)
def create_idea(request: BusinessIntakeRequest, current_user: UserProfile = Depends(get_current_user)) -> IdeaCase:
    if request.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes crear ideas para otro tenant")

    detected_language = request.source_language if request.source_language in SUPPORTED_LANGUAGES else CANONICAL_LANGUAGE
    response_language = detected_language

    _seed_demo_context_if_needed(request.tenant_id)
    context = company_context_store.get(request.tenant_id)
    if context is None:
        raise HTTPException(
            status_code=400,
            detail="Debes registrar el contexto base del tenant antes de evaluar ideas.",
        )

    duplicate = _find_active_duplicate_idea(request)
    if duplicate is not None:
        duplicate_detail = _build_duplicate_detail(duplicate, response_language)
        raise HTTPException(
            status_code=409,
            detail=duplicate_detail,
        )

    validation = _evaluate_idea_with_context(request, context)
    now = datetime.utcnow()

    idea = IdeaCase(
        idea_id=new_idea_id(),
        tenant_id=request.tenant_id,
        owner_user_id=current_user.user_id,
        owner_display_name=current_user.display_name,
        title=request.title,
        canonical_language=CANONICAL_LANGUAGE,
        supported_languages=SUPPORTED_LANGUAGES,
        source_language=request.source_language,
        detected_language=detected_language,
        response_language=response_language,
        original_text=f"{request.problem_statement}\n\n{request.expected_value}",
        canonical_summary=f"Problema: {request.problem_statement} | Valor esperado: {request.expected_value}",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.draft,
        problem_statement=request.problem_statement,
        expected_value=request.expected_value,
        affected_users=request.affected_users,
        business_validation=validation,
        context_snapshot=_build_context_snapshot(context),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=None,
        architecture_package=None,
        response_composition=None,
        rejection=None,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        created_at=now,
        updated_at=now,
    )
    idea = _apply_business_decision(idea, request, context)
    return idea_store.save(idea)


@app.get("/ideas", response_model=list[IdeaCase])
def list_ideas() -> list[IdeaCase]:
    return idea_store.list_all()


@app.get("/ideas/mine", response_model=list[IdeaCase])
def list_my_ideas(current_user: UserProfile = Depends(get_current_user)) -> list[IdeaCase]:
    ideas = idea_store.list_by_owner(current_user.user_id)
    updated = False
    for index, idea in enumerate(ideas):
        ready_idea, changed = _ensure_technical_chat_ready(idea)
        ideas[index] = ready_idea
        if changed:
            idea_store.save(ready_idea)
            updated = True
    if updated:
        return idea_store.list_by_owner(current_user.user_id)
    return ideas


@app.get("/technical/ideas-queue", response_model=list[IdeaCase])
def list_technical_queue(current_user: UserProfile = Depends(get_current_user)) -> list[IdeaCase]:
    _require_admin_or_technical(current_user)
    ideas = [
        idea
        for idea in idea_store.list_by_tenant(current_user.tenant_id)
        if idea.status == IdeaStatus.business_viable
    ]
    ideas.sort(key=lambda item: item.updated_at, reverse=True)
    return ideas


@app.get("/ideas/{idea_id}", response_model=IdeaCase)
def get_idea(idea_id: str, current_user: UserProfile = Depends(get_current_user)) -> IdeaCase:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="No puedes consultar ideas de otro usuario")
    ready_idea, changed = _ensure_technical_chat_ready(idea)
    if changed:
        return idea_store.save(ready_idea)
    return idea


@app.get("/ideas/{idea_id}/clarification-questions", response_model=ClarificationQuestionsResponse)
def get_idea_clarification_questions(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> ClarificationQuestionsResponse:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="No puedes consultar ideas de otro usuario")
    if idea.status != IdeaStatus.needs_clarification:
        raise HTTPException(status_code=400, detail="La idea ya no requiere aclaraciones")

    if _questions_missing_suggestions(idea.clarification_questions):
        context = company_context_store.get(idea.tenant_id)
        if context is None:
            raise HTTPException(status_code=400, detail="No hay contexto base del tenant para generar aclaraciones")
        reconstructed_request = BusinessIntakeRequest(
            tenant_id=idea.tenant_id,
            title=idea.title,
            problem_statement=idea.problem_statement,
            expected_value=idea.expected_value,
            affected_users=idea.affected_users,
            source_language=idea.source_language,
        )
        idea.clarification_questions = _build_clarification_questions(
            reconstructed_request,
            context,
            idea.business_validation,
        )
        idea_store.save(idea)

    return ClarificationQuestionsResponse(idea_id=idea.idea_id, questions=idea.clarification_questions)


@app.post("/ideas/{idea_id}/clarify", response_model=IdeaCase)
def submit_idea_clarification(
    idea_id: str,
    request: ClarificationSubmitRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaCase:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="No puedes actualizar ideas de otro usuario")
    if idea.status != IdeaStatus.needs_clarification:
        raise HTTPException(status_code=400, detail="La idea ya no requiere aclaraciones")

    context = company_context_store.get(idea.tenant_id)
    if context is None:
        raise HTTPException(status_code=400, detail="No hay contexto base del tenant para evaluar aclaraciones")

    required_ids = {item.question_id for item in idea.clarification_questions}
    answer_ids = {item.question_id for item in request.answers}
    missing_ids = sorted(required_ids - answer_ids)
    if missing_ids:
        raise HTTPException(status_code=400, detail=f"Faltan respuestas para: {', '.join(missing_ids)}")

    clarification_round = len(idea.clarification_interactions) + 1
    validation, status, stage, rejection = _run_clarification_decision(idea, context, request.answers)
    summary = _build_clarification_summary(request.answers, validation, idea.response_language)

    enrichment = "\n".join(f"{item.question_id}: {item.answer}" for item in request.answers)
    refreshed_request = BusinessIntakeRequest(
        tenant_id=idea.tenant_id,
        title=idea.title,
        problem_statement=f"{idea.problem_statement}\n\nAclaraciones:\n{enrichment}",
        expected_value=f"{idea.expected_value}\n\nAclaraciones:\n{enrichment}",
        affected_users=idea.affected_users,
        source_language=idea.source_language,
    )

    idea.business_validation = validation
    idea.status = status
    idea.current_stage = stage
    idea.rejection = rejection
    idea.clarification_interactions.append(
        ClarificationInteraction(
            asked_questions=idea.clarification_questions,
            answers=request.answers,
            agent_summary=summary,
            decided_status=status,
            decided_stage=stage,
            created_at=datetime.utcnow(),
        )
    )

    if status == IdeaStatus.needs_clarification:
        next_candidates = _build_clarification_questions(
            refreshed_request,
            context,
            validation,
        )
        asked_question_ids = {
            question.question_id
            for interaction in idea.clarification_interactions
            for question in interaction.asked_questions
        }
        answered_question_ids = {
            item.question_id
            for interaction in idea.clarification_interactions
            for item in interaction.answers
            if not _answer_indicates_missing_information(item.answer)
        }

        next_questions = []
        for question in next_candidates:
            if question.question_id in asked_question_ids:
                continue  # Skip already asked
            if _question_is_dependent_on_previous(question.question_id, answered_question_ids):
                continue  # Skip if dependency not met
            next_questions.append(question)

        if clarification_round >= MAX_CLARIFICATION_ROUNDS or not next_questions:
            is_recoverable = _is_recoverable_business_rejection(validation)
            idea.status = IdeaStatus.rejected
            idea.current_stage = IdeaStage.business_validation
            idea.rejection = _insufficient_clarification_rejection(idea.response_language)
            idea.business_validation.recommendation = "stop"

            if is_recoverable:
                idea.business_validation.open_questions.insert(
                    0,
                    _msg(
                        idea.response_language,
                        "Falta informacion clave. La idea puede ser reenviada con mejor evidencia en iteracion futura.",
                        "Missing key information. The idea can be resubmitted with better evidence in a future iteration.",
                        "Falta informacao chave. A ideia pode ser reenviada com melhor evidencia em iteracao futura.",
                    ),
                )
            else:
                idea.business_validation.open_questions.insert(
                    0,
                    _msg(
                        idea.response_language,
                        "Se alcanzo el maximo de aclaraciones sin evidencia suficiente.",
                        "The maximum clarification rounds were reached without enough evidence.",
                        "Foi atingido o maximo de esclarecimentos sem evidencia suficiente.",
                    ),
                )
            idea.clarification_questions = []
        else:
            idea.clarification_questions = next_questions
    else:
        idea.clarification_questions = []
    return idea_store.save(idea)


@app.post("/ideas/{idea_id}/resubmit-for-review", response_model=IdeaCase)
def resubmit_idea_for_review(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaCase:
    """Allow resubmission of ideas rejected with insufficient information but recoverable."""
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="No puedes actualizar ideas de otro usuario")
    if idea.status != IdeaStatus.rejected or idea.rejection is None:
        raise HTTPException(
            status_code=400,
            detail="Solo ideas rechazadas pueden ser reenviadas para revisión",
        )

    is_recoverable = _is_recoverable_business_rejection(idea.business_validation)
    if not is_recoverable:
        raise HTTPException(
            status_code=400,
            detail="Esta idea fue rechazada por razones objetivas y no puede ser reenviada.",
        )

    # Reset idea to needs_clarification with fresh questions
    context = company_context_store.get(idea.tenant_id)
    if context is None:
        raise HTTPException(status_code=400, detail="No hay contexto base del tenant")

    reconstructed_request = BusinessIntakeRequest(
        tenant_id=idea.tenant_id,
        title=idea.title,
        problem_statement=idea.problem_statement,
        expected_value=idea.expected_value,
        affected_users=idea.affected_users,
        source_language=idea.source_language,
    )

    idea.status = IdeaStatus.needs_clarification
    idea.current_stage = IdeaStage.business_validation
    idea.rejection = None
    idea.clarification_questions = _build_clarification_questions(
        reconstructed_request,
        context,
        idea.business_validation,
    )
    idea.updated_at = datetime.utcnow()
    return idea_store.save(idea)


@app.post("/ideas/business-submit", response_model=IdeaCase)
def submit_business_validation(request: SubmitBusinessValidationRequest) -> IdeaCase:
    idea = idea_store.get(request.idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")

    idea.status = IdeaStatus.business_viable if request.approve else IdeaStatus.rejected
    if request.approve:
        idea.current_stage = IdeaStage.technical_validation
    idea.business_validation.open_questions.append(request.notes or "Decision registrada sin notas.")
    return idea_store.save(idea)


@app.post("/ideas/{idea_id}/reevaluate-business", response_model=IdeaCase)
def reevaluate_business_decision(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> IdeaCase:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="No puedes reevaluar ideas de otro usuario")

    context = company_context_store.get(idea.tenant_id)
    if context is None:
        raise HTTPException(status_code=400, detail="No hay contexto base del tenant para reevaluar")

    request = BusinessIntakeRequest(
        tenant_id=idea.tenant_id,
        title=idea.title,
        problem_statement=idea.problem_statement,
        expected_value=idea.expected_value,
        affected_users=idea.affected_users,
        source_language=idea.source_language,
    )

    updated = _apply_business_decision(idea, request, context)
    return idea_store.save(updated)


@app.post("/ideas/{idea_id}/technical-validate", response_model=TechnicalValidationResponse)
def submit_technical_validation(
    idea_id: str,
    request: TechnicalValidationRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> TechnicalValidationResponse:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    _ensure_idea_access(current_user, idea)
    if idea.status != IdeaStatus.business_viable:
        raise HTTPException(status_code=400, detail="La idea debe estar aprobada en negocio antes de validar tecnica")

    technical = _run_technical_validation(idea, request)
    idea.technical_validation = technical
    idea.current_stage = IdeaStage.technical_validation

    if technical.recommendation == "stop":
        lang = _resolve_language(idea.response_language)
        idea.status = IdeaStatus.rejected
        idea.rejection = RejectionInfo(
            phase=RejectionPhase.technical,
            reason=_msg(
                lang,
                "La idea no supera validacion tecnica: complejidad, riesgo o madurez de datos por encima del umbral permitido.",
                "The idea did not pass technical validation: complexity, risk, or data readiness exceed the allowed threshold.",
                "A ideia nao passou na validacao tecnica: complexidade, risco ou maturidade de dados acima do limite permitido.",
            ),
        )
    else:
        idea.rejection = None

    updated = idea_store.save(idea)
    return TechnicalValidationResponse(
        idea_id=updated.idea_id,
        technical_validation=updated.technical_validation,
        status=updated.status,
        current_stage=updated.current_stage,
        rejection=updated.rejection,
    )


@app.get("/ideas/{idea_id}/technical-questions", response_model=TechnicalQuestionsResponse)
def get_idea_technical_questions(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> TechnicalQuestionsResponse:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    _ensure_idea_access(current_user, idea)
    if idea.status != IdeaStatus.business_viable:
        raise HTTPException(status_code=400, detail="La idea debe estar viable en negocio antes de chat tecnico")
    if idea.technical_validation is not None:
        raise HTTPException(status_code=400, detail="La idea ya cuenta con validacion tecnica")

    if not idea.technical_questions:
        idea.technical_questions = _build_technical_questions(idea)
        idea_store.save(idea)

    return TechnicalQuestionsResponse(idea_id=idea.idea_id, questions=idea.technical_questions)


@app.post("/ideas/{idea_id}/technical-chat", response_model=TechnicalValidationResponse)
def submit_technical_chat(
    idea_id: str,
    request: TechnicalChatSubmitRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> TechnicalValidationResponse:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    _ensure_idea_access(current_user, idea)
    if idea.status != IdeaStatus.business_viable:
        raise HTTPException(status_code=400, detail="La idea debe estar aprobada en negocio antes de validar tecnica")
    if idea.technical_validation is not None:
        raise HTTPException(status_code=400, detail="La idea ya cuenta con validacion tecnica")

    if not idea.technical_questions:
        idea.technical_questions = _build_technical_questions(idea)

    required_ids = {item.question_id for item in idea.technical_questions}
    answer_ids = {item.question_id for item in request.answers}
    missing_ids = sorted(required_ids - answer_ids)
    if missing_ids:
        raise HTTPException(status_code=400, detail=f"Faltan respuestas tecnicas para: {', '.join(missing_ids)}")

    technical_request = _technical_request_from_answers(request.answers)
    technical = _run_technical_validation(idea, technical_request)
    idea.technical_validation = technical
    idea.current_stage = IdeaStage.technical_validation

    if technical.recommendation == "stop":
        lang = _resolve_language(idea.response_language)
        idea.status = IdeaStatus.rejected
        idea.rejection = RejectionInfo(
            phase=RejectionPhase.technical,
            reason=_msg(
                lang,
                "La idea no supera validacion tecnica: complejidad, riesgo o madurez de datos por encima del umbral permitido.",
                "The idea did not pass technical validation: complexity, risk, or data readiness exceed the allowed threshold.",
                "A ideia nao passou na validacao tecnica: complexidade, risco ou maturidade de dados acima do limite permitido.",
            ),
        )
    else:
        idea.rejection = None

    idea.technical_interactions.append(
        TechnicalInteraction(
            asked_questions=idea.technical_questions,
            answers=request.answers,
            agent_summary=_build_technical_summary(request.answers, technical, idea.response_language),
            technical_validation=technical,
            created_at=datetime.utcnow(),
        )
    )
    idea.technical_questions = []

    updated = idea_store.save(idea)
    return TechnicalValidationResponse(
        idea_id=updated.idea_id,
        technical_validation=updated.technical_validation,
        status=updated.status,
        current_stage=updated.current_stage,
        rejection=updated.rejection,
    )


@app.delete("/ideas/{idea_id}", response_model=MessageResponse)
def delete_idea_for_owner_or_technical(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> MessageResponse:
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")

    _ensure_idea_access(current_user, idea)
    idea_store.delete(idea_id)
    return MessageResponse(message=f"Idea {idea_id} eliminada exitosamente")


@app.post("/ideas/{idea_id}/architecture-package", response_model=ArchitecturePackageResponse)
def generate_architecture_package(
    idea_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> ArchitecturePackageResponse:
    _require_admin_or_technical(current_user)
    idea = idea_store.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes generar arquitectura para ideas de otro tenant")
    if idea.status != IdeaStatus.business_viable:
        raise HTTPException(status_code=400, detail="La idea debe estar aprobada en negocio antes de generar arquitectura")
    if idea.status == IdeaStatus.rejected:
        raise HTTPException(status_code=400, detail="No se puede generar arquitectura para ideas rechazadas")
    if idea.technical_validation is None:
        raise HTTPException(status_code=400, detail="Primero debes completar la validacion tecnica")
    if len(idea.technical_interactions) == 0:
        raise HTTPException(status_code=400, detail="Debes completar el chat tecnico guiado antes de generar arquitectura")
    if idea.technical_validation.recommendation == "stop":
        raise HTTPException(status_code=400, detail="La validacion tecnica no fue aprobada para arquitectura")

    idea.architecture_package = _build_architecture_package(idea)
    composed_message, next_actions = _compose_architecture_message(idea)
    idea.response_composition = {
        "language": idea.response_language,
        "message": composed_message,
        "next_actions": next_actions,
        "generated_at": datetime.utcnow().isoformat(),
    }
    updated = idea_store.save(idea)

    return ArchitecturePackageResponse(
        idea_id=updated.idea_id,
        architecture_package=updated.architecture_package,
        response_composition=updated.response_composition,
    )


# ===================== ENDPOINTS EJECUTIVOS & ANALYTICS =====================

@app.get("/admin/metrics/executive-dashboard")
def get_executive_dashboard_metrics(
    period: str = "current",
    current_user: UserProfile = Depends(get_current_user),
) -> ExecutiveDashboardMetrics:
    """
    Retorna dashboard ejecutivo con métricas de valor consolidadas.
    - % Reducción de retrabajo
    - % Duplicados evitados
    - % Participación de colaboradores
    - % Adopción de IA
    """
    _require_admin(current_user)
    return DASHBOARD_METRICS_PROVIDER.get_executive_dashboard(
        tenant_id=current_user.tenant_id,
        period=period,
    )


@app.get("/admin/metrics/executive-dashboard/snapshot")
def get_executive_dashboard_snapshot(
    period: str = "current",
    current_user: UserProfile = Depends(get_current_user),
) -> ExecutiveDashboardMetrics:
    """Always returns local transactional metrics for sync/export jobs."""
    _require_admin(current_user)
    return LOCAL_DASHBOARD_METRICS_PROVIDER.get_executive_dashboard(
        tenant_id=current_user.tenant_id,
        period=period,
    )


@app.post("/admin/metrics/semantic/refresh", response_model=MessageResponse)
def refresh_semantic_metrics(
    current_user: UserProfile = Depends(get_current_user),
) -> MessageResponse:
    """Builds bronze/silver/gold artifacts from transactional DB records."""
    _require_admin(current_user)
    run_medallion_pipeline()
    return MessageResponse(message="Pipeline medallion actualizado")


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
        company_name="AI Value Hub",
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
        available_skills=[],
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
