#!/usr/bin/env python3
"""
Seed demo ideas into the AIHUB SQLite database.
Genera ideas persistentes de demostración en diferentes etapas del flujo.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.models import (
    ArchitectureComponent,
    ArchitectureConsumptionEstimate,
    ArchitecturePackage,
    BusinessValidation,
    ClarificationAnswerInput,
    ClarificationInteraction,
    ClarificationQuestion,
    ContextSnapshot,
    DeploymentStatus,
    IdeaCase,
    IdeaStage,
    IdeaStatus,
    ResponseComposition,
    TechnicalInteraction,
    TechnicalQuestion,
    TechnicalValidation,
)
from app.store import idea_store, company_context_store, CompanyContext


DEMO_TENANT = "contoso-demo"
DEMO_USER_ID = "demo-user-001"
DEMO_USER_NAME = "Demo User"


def create_context_snapshot() -> ContextSnapshot:
    """Crea un snapshot del contexto empresarial."""
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


def create_demo_idea_1_draft():
    """Idea en estado DRAFT - Recién capturada."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Automatización de Detección de Fraude en Transacciones Retail",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Queremos usar IA para detectar fraudes en tiempo real en nuestras transacciones retail.",
        canonical_summary="Propuesta para implementar sistema de detección de fraude usando ML en transacciones.",
        current_stage=IdeaStage.idea_intake,
        status=IdeaStatus.draft,
        problem_statement="Actualmente detectamos fraude con reglas estáticas que generan muchos falsos positivos. Necesitamos un sistema más inteligente que se adapte a patrones nuevos.",
        expected_value="Reducir pérdidas por fraude en 35% y mejorar experiencia de cliente reduciendo bloqueos incorrectos.",
        affected_users=["equipos-operaciones", "equipos-seguridad", "clientes-retail"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=0,
            risk_score=0,
            assumptions=[],
            open_questions=[],
            context_signals=[],
            score_breakdown=[],
            recommendation="Pendiente de validación inicial",
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
        created_at=datetime.utcnow() - timedelta(days=7),
        updated_at=datetime.utcnow() - timedelta(days=7),
    )


def create_demo_idea_2_needs_clarification():
    """Idea que REQUIERE ACLARACION - En validación de negocio."""
    questions = [
        ClarificationQuestion(
            question_id="q1",
            prompt="¿Cuál es el volumen actual de transacciones que necesitan evaluación diaria?",
            rationale="Necesitamos entender la escala para dimensionar correctamente la solución.",
            suggested_answers=["< 100k transacciones/día", "100k-500k", "500k-1M", "> 1M"],
        ),
        ClarificationQuestion(
            question_id="q2",
            prompt="¿Tienen datos históricos de fraudes etiquetados disponibles para entrenar?",
            rationale="La calidad del modelo depende de la disponibilidad de datos de entrenamiento.",
            suggested_answers=["Si, últimos 2 años", "Si, último año", "Parcialmente", "No"],
        ),
    ]

    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Optimización de Procesos KYC con Análisis de Documentos IA",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Necesitamos acelerar los procesos de verificación Know Your Customer usando visión por computadora.",
        canonical_summary="Propuesta de automatización de validación de documentos KYC con IA.",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.needs_clarification,
        problem_statement="El proceso de KYC toma 2-3 días por cliente. Los agentes deben revisar documentos manualmente, generando cuellos de botella.",
        expected_value="Reducir tiempo de KYC a máximo 2 horas, mejorar precisión a 99.5%, y permitir escalar sin aumentar headcount.",
        affected_users=["onboarding-team", "compliance", "clientes-nuevos"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=75,
            risk_score=40,
            assumptions=["Disponibilidad de datos de documentos históricos"],
            open_questions=["Integración con sistemas de verificación de terceros"],
            context_signals=["Cliente requiere mejora de SLA"],
            score_breakdown=["Alineación: 8/10", "Viabilidad: 7/10", "Impacto: 8/10"],
            recommendation="En evaluación de negocio",
        ),
        clarification_questions=questions,
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
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(days=2),
    )


def create_demo_idea_3_business_viable():
    """Idea VIABLE DE NEGOCIO - Pasó validación de negocio."""
    business_val = BusinessValidation(
        value_score=82,
        risk_score=35,
        assumptions=[
            "Disponibilidad de datos históricos de 2+ años",
            "Integración con sistemas de core banking en 8 semanas",
            "Adopción del 80% de los agentes en 3 meses",
        ],
        open_questions=[
            "Arquitectura de gobernanza de datos",
            "Plan de mantenimiento predictivo del modelo",
        ],
        context_signals=[
            "Competencia está usando soluciones similares",
            "Cliente ha expresado urgencia",
            "Presupuesto aprobado para H2",
        ],
        score_breakdown=[
            "Alineación estratégica: 9/10",
            "Viabilidad operativa: 8/10",
            "Impacto financiero: 9/10",
            "Riesgo técnico: 7/10",
        ],
        recommendation="Proceder a validación técnica con arquitectura propuesta.",
    )

    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Chatbot de Soporte al Cliente con Comprensión Conversacional",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Implementar un asistente virtual inteligente para soportar consultas de clientes 24/7.",
        canonical_summary="Chatbot con IA para soporte multiidioma en canales digitales.",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.business_viable,
        problem_statement="Centro de soporte atiende 50k consultas/mes. 60% son consultas repetitivas que pueden automatizarse. Actualmente solo disponible 9-17h.",
        expected_value="Reducir carga en equipo de soporte en 50%, disponibilidad 24/7, mejora CSAT en 20%.",
        affected_users=["customer-support", "clientes-retail", "clientes-pymes"],
        context_snapshot=create_context_snapshot(),
        business_validation=business_val,
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
        created_at=datetime.utcnow() - timedelta(days=14),
        updated_at=datetime.utcnow() - timedelta(days=1),
    )


def create_demo_idea_4_technical_validated():
    """Idea con validación técnica completada."""
    tech_validation = TechnicalValidation(
        feasibility_score=88,
        integration_complexity=65,
        security_risk=25,
        data_readiness=80,
        recommendation="Proceder a implementación. Principales riesgos mitigables.",
        blockers=[],
        assumptions=[
            "APIs de core banking disponibles",
            "Datos de transacción en formato normalizado",
            "Latencia máxima de 500ms aceptable",
        ],
    )

    architecture = ArchitecturePackage(
        solution_name="Plataforma de Análisis de Transacciones en Tiempo Real",
        summary="Arquitectura serverless con stream processing para evaluación de transacciones con latencia < 100ms.",
        components=[
            ArchitectureComponent(
                name="Event Hub",
                purpose="Ingesta de eventos de transacciones desde sistema core",
            ),
            ArchitectureComponent(
                name="Stream Analytics",
                purpose="Procesamiento en tiempo real y enriquecimiento de datos",
            ),
            ArchitectureComponent(
                name="Azure AI Services",
                purpose="Evaluación de riesgo con modelo ML entrenado",
            ),
            ArchitectureComponent(
                name="Cosmos DB",
                purpose="Almacenamiento de decisiones y auditoría",
            ),
        ],
        integration_points=[
            "Integración con Core Banking System vía REST API",
            "Consumo de datos de terceros de verificación de identidad",
            "Webhook para notificaciones de decisiones a sistemas de compliance",
        ],
        deployment_steps=[
            "Configurar infraestructura base (networking, seguridad)",
            "Implementar ingesta y pipelines de datos",
            "Entrenar y validar modelos ML",
            "Testing de carga y disaster recovery",
            "Go-live en producción",
        ],
        risks=[
            "Latencia de base de datos compartida",
            "Costo de procesamiento si no se optimiza",
            "Cambios en formato de datos",
        ],
        monthly_production_consumption=ArchitectureConsumptionEstimate(
            monthly_executions=1_500_000,
            prompt_tokens_per_execution=150,
            completion_tokens_per_execution=50,
            monthly_prompt_tokens=225_000_000,
            monthly_completion_tokens=75_000_000,
            estimated_monthly_cost_usd=2_500,
            assumptions=[
                "Basado en 1.5M transacciones/mes",
                "Tasa de rechazo del 2% requiere revisión",
            ],
        ),
        generated_at=datetime.utcnow() - timedelta(days=1),
    )

    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Análisis Predictivo de Riesgo de Crédito en Onboarding",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Sistema para predecir riesgo de crédito en tiempo real durante onboarding de clientes.",
        canonical_summary="Modelo predictivo de riesgo de crédito integrado en flujo de onboarding.",
        current_stage=IdeaStage.technical_validation,
        status=IdeaStatus.business_viable,
        problem_statement="Actualmente evaluamos riesgo post-onboarding, resultando en colocaciones no óptimas. Necesitamos predicción en tiempo real.",
        expected_value="Mejorar calidad de cartera en 25%, reducir charge-offs, mejorar aprovisionamiento de capital.",
        affected_users=["credit-team", "onboarding", "risk-management"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=85,
            risk_score=40,
            assumptions=[
                "Datos de comportamiento histórico disponibles",
                "Modelos entrenables con datos disponibles",
            ],
            open_questions=[],
            context_signals=[
                "Regulador requiere mayor control de riesgo",
                "Competencia ofrece evaluación inmediata",
            ],
            score_breakdown=["Alineación: 9/10", "Viabilidad: 8/10", "Impacto: 9/10"],
            recommendation="Viable, proceder.",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=tech_validation,
        architecture_package=architecture,
        response_composition=None,
        rejection=None,
        deployment_status=DeploymentStatus.development,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(days=21),
        updated_at=datetime.utcnow() - timedelta(days=1),
    )


def create_demo_idea_5_rejected():
    """Idea RECHAZADA - Completó ciclo pero no aprobada."""
    from app.models import RejectionInfo, RejectionPhase

    rejection = RejectionInfo(
        phase=RejectionPhase.business,
        reason="No alineado con estrategia actual. Prohibido automatizar decisiones de crédito sin supervisión humana en nuestro modelo de riesgo bajo.",
    )

    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Automatización de Asesoría de Inversión Personalizada",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Sistema para generar recomendaciones de inversión automáticas basadas en perfil del cliente.",
        canonical_summary="Recomendador automático de productos de inversión.",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.rejected,
        problem_statement="Agentes de inversión pasan mucho tiempo en consultoría. Podríamos automatizar recomendaciones.",
        expected_value="Reducir tiempo de consultoría, aumentar throughput de asesoría.",
        affected_users=["investment-advisors", "high-net-worth-clients"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=70,
            risk_score=85,
            assumptions=[],
            open_questions=[],
            context_signals=["Presión regulatoria en asesoría automatizada"],
            score_breakdown=[],
            recommendation="Rechazar - Incumple restricciones regulatorias.",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=None,
        architecture_package=None,
        response_composition=None,
        rejection=rejection,
        deployment_status=DeploymentStatus.development,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(days=10),
        updated_at=datetime.utcnow() - timedelta(days=2),
    )


def create_demo_idea_6_funding():
    """Idea en estado FUNDING - Aprobada, buscando financiamiento."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id="team-riesgo",
        owner_display_name="Carlos Mendez (Risk Team Lead)",
        title="Modelo de Scoring de Riesgo Crediticio Avanzado",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Implementar modelo avanzado de ML para evaluación de riesgo en tiempo real.",
        canonical_summary="Modelo ML para evaluación predictiva de riesgo de crédito.",
        current_stage=IdeaStage.technical_validation,
        status=IdeaStatus.business_viable,
        problem_statement="Modelos actuales son lentos y con alta tasa de falsos positivos. Necesitamos predicción en tiempo real.",
        expected_value="Mejorar calidad de cartera, reducir charge-offs en 30%, mejor asignación de capital.",
        affected_users=["risk-team", "credit-officers", "compliance"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=90,
            risk_score=30,
            assumptions=["Datos históricos de 5 años disponibles", "Integración con core sistemas"],
            open_questions=[],
            context_signals=["Regulador incentiva modelos ML transparentes", "Competencia lo hace"],
            score_breakdown=["Alineacion: 10/10", "Viabilidad: 9/10", "Impacto: 10/10"],
            recommendation="Proceder inmediatamente a implementación",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=TechnicalValidation(
            feasibility_score=92,
            integration_complexity=60,
            security_risk=20,
            data_readiness=95,
            recommendation="Excelente candidato para desarrollo inmediato",
            blockers=[],
            assumptions=["APIs disponibles"],
        ),
        architecture_package=ArchitecturePackage(
            solution_name="Plataforma ML de Riesgo Crediticio",
            summary="Pipeline ML con MLOps y governance de datos.",
            components=[
                ArchitectureComponent(name="Azure ML", purpose="Entrenamiento y deployment de modelos"),
                ArchitectureComponent(name="Azure Synapse", purpose="Data warehouse para datos históricos"),
                ArchitectureComponent(name="Azure Data Factory", purpose="ETL de datos"),
            ],
            integration_points=["Core banking", "Data lake", "Compliance systems"],
            deployment_steps=[
                "Setup infraestructura ML",
                "Preparar dataset de entrenamiento",
                "Entrenar modelos",
                "Validación regulatoria",
                "Producción gradual",
            ],
            risks=["Data quality", "Regulatory approval timeline"],
            monthly_production_consumption=ArchitectureConsumptionEstimate(
                monthly_executions=50000,
                prompt_tokens_per_execution=500,
                completion_tokens_per_execution=100,
                monthly_prompt_tokens=25000000,
                monthly_completion_tokens=5000000,
                estimated_monthly_cost_usd=3500,
                assumptions=["50k evaluaciones/mes", "Batch + real-time"],
            ),
            generated_at=datetime.utcnow() - timedelta(days=5),
        ),
        response_composition=None,
        rejection=None,
        deployment_status=DeploymentStatus.funding,
        monthly_token_quota_base=500000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(days=45),
        updated_at=datetime.utcnow() - timedelta(days=3),
    )


def create_demo_idea_7_production():
    """Idea en PRODUCCIÓN - Ya desplegada y operativa."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id="team-operaciones",
        owner_display_name="Maria Rodriguez (Operations Director)",
        title="Automatización de Onboarding Digital con Captura de Documentos",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Sistema de onboarding completamente digital con IA para captura y validacion de documentos.",
        canonical_summary="Plataforma de onboarding digital end-to-end.",
        current_stage=IdeaStage.technical_validation,
        status=IdeaStatus.business_viable,
        problem_statement="Onboarding manual toma 5-7 días. Necesitamos reducir a horas.",
        expected_value="Reducir tiempo a 2-4 horas, mejorar experiencia, escalar sin headcount.",
        affected_users=["onboarding-team", "nuevos-clientes", "customer-success"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=88,
            risk_score=25,
            assumptions=["IA confiable disponible"],
            open_questions=[],
            context_signals=["Clientes piden experiencia digital"],
            score_breakdown=["Alineacion: 9/10", "Viabilidad: 9/10", "Impacto: 9/10"],
            recommendation="Exitoso en producción",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=TechnicalValidation(
            feasibility_score=95,
            integration_complexity=70,
            security_risk=15,
            data_readiness=98,
            recommendation="Excelente desempeño en producción",
            blockers=[],
            assumptions=[],
        ),
        architecture_package=ArchitecturePackage(
            solution_name="Plataforma Digital de Onboarding",
            summary="Solución serverless con OCR e IA para captura y validación de documentos.",
            components=[
                ArchitectureComponent(name="Azure Document Intelligence", purpose="OCR y extracción de datos"),
                ArchitectureComponent(name="Azure Functions", purpose="Orquestación serverless"),
                ArchitectureComponent(name="Azure Cosmos DB", purpose="Almacenamiento de aplicaciones"),
                ArchitectureComponent(name="Azure Blob Storage", purpose="Almacenamiento de documentos"),
            ],
            integration_points=["Core banking", "Compliance", "Payment systems"],
            deployment_steps=[
                "Infraestructura base",
                "Integración con sistemas legacy",
                "Pruebas UAT",
                "Rollout gradual",
                "Soporte 24/7",
            ],
            risks=[
                "Completeness: Al 100%",
                "Uptime: 99.95%",
                "Customer satisfaction: +40%",
            ],
            monthly_production_consumption=ArchitectureConsumptionEstimate(
                monthly_executions=15000,
                prompt_tokens_per_execution=800,
                completion_tokens_per_execution=200,
                monthly_prompt_tokens=12000000,
                monthly_completion_tokens=3000000,
                estimated_monthly_cost_usd=2100,
                assumptions=["15k onboardings/mes", "100% digital"],
            ),
            generated_at=datetime.utcnow() - timedelta(days=180),
        ),
        response_composition=ResponseComposition(
            language="es",
            message="Solución en producción desde hace 6 meses con resultados excepcionales.",
            next_actions=[
                "Expandir a otros tipos de documentos",
                "Integrar con sistema de firmae-lectrónica",
                "Análisis de fraude avanzado",
            ],
            generated_at=datetime.utcnow() - timedelta(days=180),
        ),
        rejection=None,
        deployment_status=DeploymentStatus.production,
        monthly_token_quota_base=1000000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(days=365),
        updated_at=datetime.utcnow() - timedelta(days=30),
    )


def create_demo_idea_8_production():
    """Otra idea en PRODUCCIÓN - Sistema de alertas de fraude."""
    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id="team-seguridad",
        owner_display_name="Roberto Gonzalez (Security Chief)",
        title="Sistema Inteligente de Detección de Fraude en Transacciones",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Red neuronal para detección de fraude en tiempo real en todas las transacciones.",
        canonical_summary="ML system para detección de patrones fraudulentos.",
        current_stage=IdeaStage.technical_validation,
        status=IdeaStatus.business_viable,
        problem_statement="Pérdidas por fraude superiores a 2.5% de volumen. Necesitamos mecanismo inteligente.",
        expected_value="Reducir fraude a 0.5%, mejorar experiencia bloqueando menos transacciones legitimas.",
        affected_users=["fraud-team", "risk-team", "clientes"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=95,
            risk_score=20,
            assumptions=["Datos de fraude disponibles"],
            open_questions=[],
            context_signals=["ROI detectado: $5M anuales"],
            score_breakdown=["Alineacion: 10/10", "Viabilidad: 10/10", "Impacto: 10/10"],
            recommendation="Máxima prioridad",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=TechnicalValidation(
            feasibility_score=96,
            integration_complexity=75,
            security_risk=10,
            data_readiness=99,
            recommendation="Prototipo exitoso en producción",
            blockers=[],
            assumptions=[],
        ),
        architecture_package=ArchitecturePackage(
            solution_name="Fraud Detection Engine en Tiempo Real",
            summary="Sistema de detección en tiempo real con ML y reglas híbridas.",
            components=[
                ArchitectureComponent(name="Azure Stream Analytics", purpose="Procesamiento en tiempo real"),
                ArchitectureComponent(name="Azure Databricks", purpose="Entrenamiento ML"),
                ArchitectureComponent(name="Redis Cache", purpose="Cache de reglas y patrones"),
                ArchitectureComponent(name="Azure App Insights", purpose="Monitoring"),
            ],
            integration_points=["Transaction gateway", "Customer service", "Risk systems"],
            deployment_steps=[
                "Completado",
                "En producción hace 12 meses",
                "Mejora continua de modelos",
                "Expansión a nuevos canales",
            ],
            risks=[
                "Falsos positivos reducidos a 2.1%",
                "Detección real: 94.3%",
                "Latencia promedio: 45ms",
            ],
            monthly_production_consumption=ArchitectureConsumptionEstimate(
                monthly_executions=50000000,
                prompt_tokens_per_execution=100,
                completion_tokens_per_execution=50,
                monthly_prompt_tokens=5000000000,
                monthly_completion_tokens=2500000000,
                estimated_monthly_cost_usd=8500,
                assumptions=["50M transacciones/mes", "Evaluación real-time"],
            ),
            generated_at=datetime.utcnow() - timedelta(days=365),
        ),
        response_composition=ResponseComposition(
            language="es",
            message="Sistema operativo exitosamente desde hace 1 año con mejora constante.",
            next_actions=[
                "Integración con sistemas de terceros",
                "Análisis de comportamiento de cliente",
                "Detección de fraude interno",
            ],
            generated_at=datetime.utcnow() - timedelta(days=365),
        ),
        rejection=None,
        deployment_status=DeploymentStatus.production,
        monthly_token_quota_base=2000000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(days=450),
        updated_at=datetime.utcnow() - timedelta(days=20),
    )

    """Idea RECHAZADA - Completó ciclo pero no aprobada."""
    from app.models import RejectionInfo, RejectionPhase

    rejection = RejectionInfo(
        phase=RejectionPhase.business,
        reason="No alineado con estrategia actual. Prohibido automatizar decisiones de crédito sin supervisión humana en nuestro modelo de riesgo bajo.",
    )

    return IdeaCase(
        idea_id=str(uuid4()),
        tenant_id=DEMO_TENANT,
        owner_user_id=DEMO_USER_ID,
        owner_display_name=DEMO_USER_NAME,
        title="Automatización de Asesoría de Inversión Personalizada",
        canonical_language="es",
        supported_languages=["es", "en"],
        source_language="es",
        detected_language="es",
        response_language="es",
        original_text="Sistema para generar recomendaciones de inversión automáticas basadas en perfil del cliente.",
        canonical_summary="Recomendador automático de productos de inversión.",
        current_stage=IdeaStage.business_validation,
        status=IdeaStatus.rejected,
        problem_statement="Agentes de inversión pasan mucho tiempo en consultoría. Podríamos automatizar recomendaciones.",
        expected_value="Reducir tiempo de consultoría, aumentar throughput de asesoría.",
        affected_users=["investment-advisors", "high-net-worth-clients"],
        context_snapshot=create_context_snapshot(),
        business_validation=BusinessValidation(
            value_score=70,
            risk_score=85,
            assumptions=[],
            open_questions=[],
            context_signals=["Presión regulatoria en asesoría automatizada"],
            score_breakdown=[],
            recommendation="Rechazar - Incumple restricciones regulatorias.",
        ),
        technical_questions=[],
        technical_interactions=[],
        technical_validation=None,
        architecture_package=None,
        response_composition=None,
        rejection=rejection,
        deployment_status=DeploymentStatus.development,
        monthly_token_quota_base=250000,
        extra_quota_current_month=0,
        quota_month="",
        quota_adjustments=[],
        clarification_questions=[],
        clarification_interactions=[],
        created_at=datetime.utcnow() - timedelta(days=10),
        updated_at=datetime.utcnow() - timedelta(days=2),
    )


def seed_demo_ideas():
    """Puebla la base de datos con ideas de demostración."""
    print("[*] Sembrando ideas de demostracion en AIHUB...")

    ideas = [
        create_demo_idea_1_draft(),
        create_demo_idea_2_needs_clarification(),
        create_demo_idea_3_business_viable(),
        create_demo_idea_4_technical_validated(),
        create_demo_idea_5_rejected(),
        create_demo_idea_6_funding(),
        create_demo_idea_7_production(),
        create_demo_idea_8_production(),
    ]

    for i, idea in enumerate(ideas, 1):
        idea_store.save(idea)
        status_label = {
            IdeaStatus.draft: "[DRAFT]",
            IdeaStatus.needs_clarification: "[?]",
            IdeaStatus.business_viable: "[OK]",
            IdeaStatus.rejected: "[X]",
        }.get(idea.status, str(idea.status))
        
        deployment_label = {
            DeploymentStatus.development: "{DEV}",
            DeploymentStatus.funding: "{FUND}",
            DeploymentStatus.production: "{PROD}",
        }.get(idea.deployment_status, "{???}")
        
        print(f"  {i}. {status_label} {deployment_label} - {idea.title}")

    print(f"\n[+] Se crearon {len(ideas)} ideas de demostracion persistentes")
    print("[*] Estados: 1 Draft + 1 Aclaracion + 2 Viable + 1 Rechazada + 1 Funding + 2 Produccion")
    print("[*] Base de datos: data/aihub.db")
    print("[+] Las ideas apareceran en la interfaz de demostracion\n")


if __name__ == "__main__":
    seed_demo_ideas()
