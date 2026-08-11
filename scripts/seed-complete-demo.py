#!/usr/bin/env python3
"""
Seed completo: Ideas + Catálogo de Iniciativas + Contactos.
Genera un set realista de ideas en intake y catálogo de iniciativas ya desplegadas/en desarrollo.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.models import (
    ArchitectureComponent,
    ArchitectureConsumptionEstimate,
    ArchitecturePackage,
    BusinessValidation,
    ClarificationQuestion,
    ContactPerson,
    ContextSnapshot,
    DeploymentStatus,
    IdeaCase,
    IdeaStage,
    IdeaStatus,
    InitiativeRegistry,
    TechnicalValidation,
)
from app.store import idea_store, company_context_store, CompanyContext


DEMO_TENANT = "contoso-demo"
DEMO_USER_ID = "demo-user-001"
DEMO_USER_NAME = "Demo User"

# Catálogo global de iniciativas (para matching)
INITIATIVES_REGISTRY = []


# ==================== CONTACTOS ====================

def get_contact_carlos_fraud():
    return ContactPerson(
        contact_id="contact-001",
        name="Carlos Mendez",
        email="carlos.mendez@contoso.com",
        role="Fraud Detection Lead",
        department="Risk & Compliance",
        phone="+34-91-555-0001",
    )


def get_contact_rosa_kyc():
    return ContactPerson(
        contact_id="contact-002",
        name="Rosa Garcia",
        email="rosa.garcia@contoso.com",
        role="KYC Program Manager",
        department="Onboarding",
        phone="+34-91-555-0002",
    )


def get_contact_juan_risk():
    return ContactPerson(
        contact_id="contact-003",
        name="Juan Ramirez",
        email="juan.ramirez@contoso.com",
        role="Credit Risk Officer",
        department="Risk Management",
        phone="+34-91-555-0003",
    )


def get_contact_maria_support():
    return ContactPerson(
        contact_id="contact-004",
        name="Maria Torres",
        email="maria.torres@contoso.com",
        role="Customer Experience Manager",
        department="Support Operations",
        phone="+34-91-555-0004",
    )


def get_contact_luis_arch():
    return ContactPerson(
        contact_id="contact-005",
        name="Luis Martinez",
        email="luis.martinez@contoso.com",
        role="Enterprise Architect",
        department="Technology",
        phone="+34-91-555-0005",
    )


# ==================== CATÁLOGO DE INICIATIVAS ====================

def register_initiative_fraud_detection_production():
    """Iniciativa de detección de fraude ACTIVA EN PRODUCCIÓN."""
    contact = get_contact_carlos_fraud()
    init = InitiativeRegistry(
        initiative_id="init-prod-001",
        tenant_id=DEMO_TENANT,
        title="Fraud Detection Platform v2.0",
        problem_domain="Detección de fraude en tiempo real",
        solution_category="fraud-detection",
        deployment_status="production",
        stage="deployed",
        key_technologies=["Azure Stream Analytics", "ML.NET", "Cosmos DB", "Azure AI"],
        main_contact=contact,
        supporting_contacts=[
            ContactPerson(
                contact_id="contact-005a",
                name="Pedro Lopez",
                email="pedro.lopez@contoso.com",
                role="DevOps Engineer",
                department="Platform",
            )
        ],
        estimated_value="35% reducción de pérdidas por fraude",
        problem_keywords=[
            "fraude",
            "transacciones",
            "detección en tiempo real",
            "machine learning",
            "patrones anómalos",
        ],
        created_at=datetime.utcnow() - timedelta(days=180),
        updated_at=datetime.utcnow() - timedelta(days=30),
        deployment_date=datetime.utcnow() - timedelta(days=120),
    )
    INITIATIVES_REGISTRY.append(init)
    return init


def register_initiative_kyc_automation_development():
    """Iniciativa de automatización KYC EN DESARROLLO."""
    contact = get_contact_rosa_kyc()
    init = InitiativeRegistry(
        initiative_id="init-dev-001",
        tenant_id=DEMO_TENANT,
        title="KYC Document Automation v1.0",
        problem_domain="Automatización de procesos KYC",
        solution_category="document-processing",
        deployment_status="development",
        stage="technical_validation",
        key_technologies=["Azure Computer Vision", "Form Recognizer", "Power Automate"],
        main_contact=contact,
        supporting_contacts=[
            ContactPerson(
                contact_id="contact-002a",
                name="Sofia Gonzalez",
                email="sofia.gonzalez@contoso.com",
                role="Business Analyst",
                department="Onboarding",
            )
        ],
        estimated_value="Reducir tiempo KYC de 2-3 días a 2 horas",
        problem_keywords=[
            "kyc",
            "onboarding",
            "documentos",
            "validación",
            "automatización",
            "visión computadora",
        ],
        created_at=datetime.utcnow() - timedelta(days=90),
        updated_at=datetime.utcnow() - timedelta(days=15),
        deployment_date=None,
    )
    INITIATIVES_REGISTRY.append(init)
    return init


def register_initiative_credit_risk_funding():
    """Iniciativa de riesgo de crédito EN FASE DE FINANCIAMIENTO."""
    contact = get_contact_juan_risk()
    init = InitiativeRegistry(
        initiative_id="init-fund-001",
        tenant_id=DEMO_TENANT,
        title="Predictive Credit Risk Engine",
        problem_domain="Análisis predictivo de riesgo",
        solution_category="risk-prediction",
        deployment_status="funding",
        stage="business_validation",
        key_technologies=["Azure Databricks", "ML Services", "Power BI"],
        main_contact=contact,
        supporting_contacts=[
            ContactPerson(
                contact_id="contact-003a",
                name="Ana Rodriguez",
                email="ana.rodriguez@contoso.com",
                role="Data Scientist",
                department="Analytics",
            )
        ],
        estimated_value="25% mejora en calidad de cartera",
        problem_keywords=[
            "riesgo de crédito",
            "predicción",
            "scoring",
            "machine learning",
            "análisis predictivo",
        ],
        created_at=datetime.utcnow() - timedelta(days=60),
        updated_at=datetime.utcnow() - timedelta(days=10),
        deployment_date=None,
    )
    INITIATIVES_REGISTRY.append(init)
    return init


def register_initiative_support_chatbot_production():
    """Iniciativa de chatbot de soporte EN PRODUCCIÓN."""
    contact = get_contact_maria_support()
    init = InitiativeRegistry(
        initiative_id="init-prod-002",
        tenant_id=DEMO_TENANT,
        title="AI Support Chatbot Platform",
        problem_domain="Soporte al cliente 24/7",
        solution_category="customer-support",
        deployment_status="production",
        stage="deployed",
        key_technologies=["Azure OpenAI", "Bot Framework", "QnA Maker", "Cosmos DB"],
        main_contact=contact,
        supporting_contacts=[
            ContactPerson(
                contact_id="contact-004a",
                name="Miguel Sanchez",
                email="miguel.sanchez@contoso.com",
                role="Support Operations Lead",
                department="Support",
            )
        ],
        estimated_value="50% reducción de carga, CSAT +20%",
        problem_keywords=[
            "soporte",
            "chatbot",
            "ia conversacional",
            "24/7",
            "experiencia cliente",
            "automatización",
        ],
        created_at=datetime.utcnow() - timedelta(days=150),
        updated_at=datetime.utcnow() - timedelta(days=20),
        deployment_date=datetime.utcnow() - timedelta(days=100),
    )
    INITIATIVES_REGISTRY.append(init)
    return init


# ==================== CONTEXTO EMPRESARIAL ====================

def create_context_snapshot() -> ContextSnapshot:
    return ContextSnapshot(
        tenant_id=DEMO_TENANT,
        company_name="Contoso Financial Services",
        industry="Servicios financieros",
        risk_tolerance="low",
        strategic_priorities=[
            "reduccion de fraude",
            "eficiencia operativa en onboarding",
            "experiencia digital para clientes retail",
            "cumplimiento regulatorio",
        ],
        prohibited_domains=[
            "asesoria de inversion automatizada sin supervision",
            "criptomonedas no reguladas",
            "modelos de credito sin explicabilidad",
        ],
        regulatory_constraints=[
            "KYC",
            "AML",
            "proteccion de datos personales",
            "trazabilidad de decisiones",
        ],
        evaluated_at=datetime.utcnow(),
    )


# ==================== IDEAS NUEVAS PARA INTAKE ====================

def create_idea_1_fraud_detection_draft():
    """Idea nueva que COINCIDE CON INICIATIVA EN PRODUCCIÓN."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Detección de Fraude Mejorada con Análisis Behavioral",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Queremos mejorar la detección de fraude añadiendo análisis de comportamiento del usuario con grafos de conexiones.",
        canonical_summary="Mejora de sistema de detección de fraude con análisis behavioral y grafos de conexión.",
        current_stage=IdeaStage.idea_intake,
        status=IdeaStatus.draft,
        problem_statement="Nuestro sistema actual detecta fraude pero genera falsos positivos. Necesitamos análisis más sofisticado de patrones comportamentales y redes de conexión.",
        expected_value="Reducir falsos positivos en 40%, detectar fraude anillo en tiempo real.",
        affected_users=["equipos-operaciones", "equipos-seguridad"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=0,
            risk_score=0,
            assumptions=[],
            open_questions=[],
            context_signals=[],
            score_breakdown=[],
            recommendation="Pendiente validación",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=None,
        architecture_package=None,
        response_composition=None,
        rejection=None,
        deployment_status=DeploymentStatus.development,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(hours=2),
        updated_at=datetime.utcnow() - timedelta(hours=2),
    )


def create_idea_2_kyc_extension_needs_clarification():
    """Idea nueva que EXTIENDE INICIATIVA EN DESARROLLO."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="KYC Automation con Validación Biométrica",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Expandir el KYC actual agregando validación de identidad biométrica (rostro y huellas).",
        canonical_summary="Extensión de automatización KYC con validación biométrica.",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.needs_clarification,
        problem_statement="El proceso KYC actual solo valida documentos. Necesitamos validación de identidad biométrica para mayor seguridad.",
        expected_value="Mejorar precisión de validación a 99.9%, cumplir AML más estrictamente.",
        affected_users=["onboarding-team", "compliance", "clientes"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=78,
            risk_score=45,
            assumptions=["Acceso a APIs de validación biométrica"],
            open_questions=["Compatibilidad con framework existente"],
            context_signals=["Cliente requiere cumplimiento AML mejorado"],
            score_breakdown=["Alineación: 8/10", "Viabilidad: 7/10"],
            recommendation="En evaluación",
        ),
        clarification_questions=[
            ClarificationQuestion(
                question_id="q1",
                prompt="¿Se integraría con el sistema KYC actual en desarrollo?",
                rationale="Necesitamos entender si es complementaria o sustitutiva.",
                suggested_answers=["Complementaria", "Sustitutiva", "Paralela"],
            ),
            ClarificationQuestion(
                question_id="q2",
                prompt="¿Qué proveedores de validación biométrica prefieres?",
                rationale="Hay varias opciones con diferentes costs y capacidades.",
                suggested_answers=["Microsoft Face API", "AWS Rekognition", "Otro"],
            ),
        ],
        technical_questions=[],
        technical_interactions=[],
        technical_validation=None,
        architecture_package=None,
        response_composition=None,
        rejection=None,
        deployment_status=DeploymentStatus.development,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(hours=4),
        updated_at=datetime.utcnow() - timedelta(hours=1),
    )


def create_idea_3_support_sentiment_analysis():
    """Idea nueva para MEJORAR CHATBOT EN PRODUCCIÓN."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Análisis de Sentimiento en Soporte IA",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Agregar análisis de sentimiento al chatbot para detectar clientes frustrados y escalarlos a humanos.",
        canonical_summary="Mejora del chatbot con análisis de sentimiento y escalamiento inteligente.",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.business_viable,
        problem_statement="El chatbot actual no detecta frustración del cliente. Necesitamos escalar automáticamente casos problemáticos.",
        expected_value="Mejorar CSAT en 15%, reducir escalamientos innecesarios en 30%.",
        affected_users=["customer-support", "clientes"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=85,
            risk_score=20,
            assumptions=["API de sentimiento disponible"],
            open_questions=[],
            context_signals=["Clientes piden mejor experiencia"],
            score_breakdown=["Alineación: 9/10", "Viabilidad: 9/10", "Impacto: 8/10"],
            recommendation="Viable, proceder a técnica",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=None,
        architecture_package=None,
        response_composition=None,
        rejection=None,
        deployment_status=DeploymentStatus.development,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(hours=6),
        updated_at=datetime.utcnow() - timedelta(hours=3),
    )


# ==================== SEED COMPLETO ====================

def seed_complete():
    """Puebla BD con catálogo + ideas nuevas."""
    print("\n" + "=" * 70)
    print("SEEDING COMPLETO: CATÁLOGO DE INICIATIVAS + IDEAS DE INTAKE")
    print("=" * 70 + "\n")

    # 1. Registrar iniciativas en catálogo
    print("[1] Registrando iniciativas en catalogo...\n")

    init1 = register_initiative_fraud_detection_production()
    print(f"  [OK] PRODUCCION: {init1.title}")
    print(f"    Contacto: {init1.main_contact.name} ({init1.main_contact.email})")

    init2 = register_initiative_kyc_automation_development()
    print(f"  [OK] EN DESARROLLO: {init2.title}")
    print(f"    Contacto: {init2.main_contact.name} ({init2.main_contact.email})")

    init3 = register_initiative_credit_risk_funding()
    print(f"  [OK] EN FINANCIAMIENTO: {init3.title}")
    print(f"    Contacto: {init3.main_contact.name} ({init3.main_contact.email})")

    init4 = register_initiative_support_chatbot_production()
    print(f"  [OK] PRODUCCION: {init4.title}")
    print(f"    Contacto: {init4.main_contact.name} ({init4.main_contact.email})\n")

    # 2. Crear ideas de intake
    print("[2] Creando ideas nuevas para intake...\n")

    ideas = [
        create_idea_1_fraud_detection_draft(),
        create_idea_2_kyc_extension_needs_clarification(),
        create_idea_3_support_sentiment_analysis(),
    ]

    for i, idea in enumerate(ideas, 1):
        idea_store.save(idea)
        status_label = {
            IdeaStatus.draft: "[DRAFT]",
            IdeaStatus.needs_clarification: "[?]",
            IdeaStatus.business_viable: "[VIABLE]",
        }.get(idea.status, str(idea.status))
        print(f"  {i}. {status_label} {idea.title}")

    print(f"\n" + "=" * 70)
    print(f"[+] CATALOGO: {len(INITIATIVES_REGISTRY)} iniciativas registradas")
    print(f"[+] IDEAS: {len(ideas)} ideas nuevas para intake")
    print("=" * 70)
    print("\nNOTA: El matching se ejecuta en API cuando se ingresa una idea nueva.\n")

    return INITIATIVES_REGISTRY, ideas


if __name__ == "__main__":
    registry, ideas = seed_complete()
