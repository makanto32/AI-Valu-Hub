#!/usr/bin/env python3
"""
Seed expandido: Genera múltiples ideas y iniciativas para demo con métricas ricas.
Crea:
- 12+ ideas en diferentes estados (DRAFT, NEEDS_CLARIFICATION, VIABLE, REJECTED)
- 8+ iniciativas en diferentes etapas de despliegue
- Datos para calcular: costos, adopción, duplicación, despliegues a producción
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.models import (
    IdeaCase,
    IdeaStatus,
    InitiativeRegistry,
    DeploymentStatus,
    ContactPerson,
    ContextSnapshot,
)
from app.store import idea_store

DEMO_TENANT = "contoso-demo"
DEMO_USER = "demo-user-001"

# ==================== IDEAS ====================

IDEAS_TO_SEED = [
    # ========== PRODUCCIÓN (4 ideas = 25% deployment rate) ==========
    {
        "title": "Detección de Fraude en Tiempo Real con ML",
        "description": "Sistema de ML para detectar patrones de fraude en transacciones. Reduce falsos positivos en 45%.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Carlos Mendez",
        "owner_email": "carlos@contoso.com",
        "deployment_status": "production",
        "feasibility_score": 92,
        "hours_saved_monthly": 250,
        "annual_value_usd": 450_000,
        "business_validated": True,
        "technical_validated": True,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=180),
    },
    {
        "title": "KYC Automático con OCR e IA",
        "description": "Automatiza Know Your Customer con OCR + análisis de documentos. Reduce tiempo de onboarding de 3 días a 30 minutos.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Rosa Garcia",
        "owner_email": "rosa@contoso.com",
        "deployment_status": "production",
        "feasibility_score": 88,
        "hours_saved_monthly": 180,
        "annual_value_usd": 380_000,
        "business_validated": True,
        "technical_validated": True,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=150),
    },
    {
        "title": "Chatbot de Soporte con IA Generativa",
        "description": "Asistente virtual basado en LLM para soporte tier-1. Resuelve 60% de tickets sin intervención humana.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Maria Torres",
        "owner_email": "maria@contoso.com",
        "deployment_status": "production",
        "feasibility_score": 85,
        "hours_saved_monthly": 320,
        "annual_value_usd": 520_000,
        "business_validated": True,
        "technical_validated": True,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=120),
    },
    {
        "title": "Scoring de Riesgo Crediticio Predictivo",
        "description": "Modelo de credit scoring que predice default con 89% de precisión. Aprobaciones más rápidas.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Juan Ramirez",
        "owner_email": "juan@contoso.com",
        "deployment_status": "production",
        "feasibility_score": 91,
        "hours_saved_monthly": 200,
        "annual_value_usd": 480_000,
        "business_validated": True,
        "technical_validated": True,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=90),
    },
    
    # ========== DESARROLLO (3 ideas) ==========
    {
        "title": "Análisis de Sentimiento en Calls de Clientes",
        "description": "Procesa grabaciones de soporte para detectar satisfacción y problemas. Feedback automático para QA.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Sofia Romero",
        "owner_email": "sofia@contoso.com",
        "deployment_status": "development",
        "feasibility_score": 78,
        "hours_saved_monthly": 120,
        "annual_value_usd": 250_000,
        "business_validated": True,
        "technical_validated": False,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=45),
    },
    {
        "title": "Recomendaciones de Productos Personalizadas",
        "description": "Sistema colaborativo de recomendaciones para cross-sell. Aumenta ingresos por cliente en 12%.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Pablo Fernandez",
        "owner_email": "pablo@contoso.com",
        "deployment_status": "development",
        "feasibility_score": 82,
        "hours_saved_monthly": 80,
        "annual_value_usd": 320_000,
        "business_validated": True,
        "technical_validated": False,
        "ai_assisted_validation": False,
        "generated_at": datetime.utcnow() - timedelta(days=30),
    },
    {
        "title": "Detección de Anomalías en Transacciones",
        "description": "Modelo unsupervised para detectar comportamientos anómalos. Complementa scoring estándar.",
        "status": IdeaStatus.NEEDS_CLARIFICATION,
        "owner_display_name": "Elena Sánchez",
        "owner_email": "elena@contoso.com",
        "deployment_status": "development",
        "feasibility_score": 72,
        "hours_saved_monthly": 90,
        "annual_value_usd": 200_000,
        "business_validated": False,
        "technical_validated": False,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=25),
    },
    
    # ========== FINANCIAMIENTO (2 ideas) ==========
    {
        "title": "Predicción de Churn de Clientes",
        "description": "Modelo predictivo de abandono. Permite intervención proactiva. Target: reducir churn en 8%.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "David Lopez",
        "owner_email": "david@contoso.com",
        "deployment_status": "funding",
        "feasibility_score": 80,
        "hours_saved_monthly": 110,
        "annual_value_usd": 380_000,
        "business_validated": True,
        "technical_validated": False,
        "ai_assisted_validation": False,
        "generated_at": datetime.utcnow() - timedelta(days=60),
    },
    {
        "title": "NLP para Análisis de Contratos",
        "description": "Extrae términos clave de contratos automáticamente. Reduce revisión manual en 70%.",
        "status": IdeaStatus.VIABLE,
        "owner_display_name": "Ana Gutierrez",
        "owner_email": "ana@contoso.com",
        "deployment_status": "funding",
        "feasibility_score": 76,
        "hours_saved_monthly": 140,
        "annual_value_usd": 300_000,
        "business_validated": True,
        "technical_validated": False,
        "ai_assisted_validation": True,
        "generated_at": datetime.utcnow() - timedelta(days=50),
    },
    
    # ========== DRAFT (2 ideas) ==========
    {
        "title": "Optimización de Rutas de Cobranza",
        "description": "Algoritmo genético para optimizar rutas de cobranzas. Reduce costos operativos.",
        "status": IdeaStatus.DRAFT,
        "owner_display_name": "Ricardo Diaz",
        "owner_email": "ricardo@contoso.com",
        "deployment_status": None,
        "feasibility_score": 60,
        "hours_saved_monthly": 0,
        "annual_value_usd": 0,
        "business_validated": False,
        "technical_validated": False,
        "ai_assisted_validation": False,
        "generated_at": datetime.utcnow() - timedelta(days=10),
    },
    {
        "title": "Generación Automática de Reportes de Cumplimiento",
        "description": "LLM para generar reportes regulatorios. Cumple con normativa AML/CFT.",
        "status": IdeaStatus.DRAFT,
        "owner_display_name": "Carmen Alba",
        "owner_email": "carmen@contoso.com",
        "deployment_status": None,
        "feasibility_score": 55,
        "hours_saved_monthly": 0,
        "annual_value_usd": 0,
        "business_validated": False,
        "technical_validated": False,
        "ai_assisted_validation": False,
        "generated_at": datetime.utcnow() - timedelta(days=5),
    },
    
    # ========== REJECTED (2 ideas) ==========
    {
        "title": "Avatar Virtual para Atención al Cliente",
        "description": "Holograma 3D interactivo. Requiere infraestructura no escalable.",
        "status": IdeaStatus.REJECTED,
        "owner_display_name": "Marcos Vega",
        "owner_email": "marcos@contoso.com",
        "deployment_status": None,
        "feasibility_score": 35,
        "hours_saved_monthly": 0,
        "annual_value_usd": 0,
        "business_validated": False,
        "technical_validated": False,
        "ai_assisted_validation": False,
        "generated_at": datetime.utcnow() - timedelta(days=15),
        "rejection_reason": "Costo de infraestructura prohibitivo. No hay ROI claro.",
    },
    {
        "title": "Blockchain para Auditoría Inmutable",
        "description": "Todos los accesos registrados en blockchain. Pero: compleja, lenta, regulación unclear.",
        "status": IdeaStatus.REJECTED,
        "owner_display_name": "Teresa Ruiz",
        "owner_email": "teresa@contoso.com",
        "deployment_status": None,
        "feasibility_score": 40,
        "hours_saved_monthly": 0,
        "annual_value_usd": 0,
        "business_validated": False,
        "technical_validated": False,
        "ai_assisted_validation": False,
        "generated_at": datetime.utcnow() - timedelta(days=20),
        "rejection_reason": "Regulación unclear. Complejidad técnica no justificada para audit trail.",
    },
]


def seed_ideas():
    """Crea todas las ideas de prueba."""
    print("\n" + "="*70)
    print("SEEDING EXPANDIDO: IDEAS CON MÉTRICAS RICAS")
    print("="*70 + "\n")

    print("[1] Creando ideas en diferentes estados...\n")
    
    for idx, idea_data in enumerate(IDEAS_TO_SEED, 1):
        idea = IdeaCase(
            idea_id=str(uuid4()),
            tenant_id=DEMO_TENANT,
            submitted_by=DEMO_USER,
            title=idea_data["title"],
            description=idea_data["description"],
            status=idea_data["status"],
            owner_display_name=idea_data["owner_display_name"],
            owner_email=idea_data["owner_email"],
            deployment_status=idea_data["deployment_status"],
            feasibility_score=idea_data["feasibility_score"],
            hours_saved_monthly=idea_data["hours_saved_monthly"],
            annual_value_usd=idea_data["annual_value_usd"],
            business_validated=idea_data["business_validated"],
            technical_validated=idea_data["technical_validated"],
            ai_assisted_validation=idea_data["ai_assisted_validation"],
            created_at=idea_data["generated_at"],
            updated_at=idea_data["generated_at"],
        )
        
        if idea_data["status"] == IdeaStatus.REJECTED and "rejection_reason" in idea_data:
            idea.rejection_reason = idea_data["rejection_reason"]
        
        idea_store.create(idea)
        
        status_emoji = {
            IdeaStatus.VIABLE: "✅",
            IdeaStatus.DRAFT: "📝",
            IdeaStatus.NEEDS_CLARIFICATION: "❓",
            IdeaStatus.REJECTED: "❌",
        }
        
        deployment_emoji = {
            "production": "🚀",
            "development": "⚙️",
            "funding": "💰",
            None: "-",
        }
        
        print(f"  {idx:2d}. {status_emoji.get(idea.status, '?')} {deployment_emoji.get(idea.deployment_status, '-')} {idea.title}")
        print(f"       Owner: {idea.owner_display_name} | Score: {idea.feasibility_score}% | Value: ${idea.annual_value_usd:,}")
        print()

    print("\n" + "="*70)
    print("[✓] SEED COMPLETADO")
    print("="*70)
    print(f"\n📊 ESTADÍSTICAS:")
    
    all_ideas = idea_store.list_by_tenant(DEMO_TENANT)
    viable = [i for i in all_ideas if i.status == IdeaStatus.VIABLE]
    draft = [i for i in all_ideas if i.status == IdeaStatus.DRAFT]
    clarification = [i for i in all_ideas if i.status == IdeaStatus.NEEDS_CLARIFICATION]
    rejected = [i for i in all_ideas if i.status == IdeaStatus.REJECTED]
    production = [i for i in all_ideas if i.deployment_status == "production"]
    
    print(f"  📈 Total ideas: {len(all_ideas)}")
    print(f"  ✅ Viable: {len(viable)}")
    print(f"  📝 Draft: {len(draft)}")
    print(f"  ❓ Needs clarification: {len(clarification)}")
    print(f"  ❌ Rejected: {len(rejected)}")
    print(f"  🚀 En producción: {len(production)} ({len(production)*100//len(all_ideas)}%)")
    
    total_value = sum(i.annual_value_usd for i in all_ideas)
    total_hours = sum(i.hours_saved_monthly for i in all_ideas)
    ai_validated = len([i for i in all_ideas if i.ai_assisted_validation])
    
    print(f"\n  💵 Valor anual total: ${total_value:,}")
    print(f"  ⏱️  Horas ahorradas/mes: {total_hours}")
    print(f"  🤖 Ideas validadas con IA: {ai_validated}")
    print(f"  📋 Ideas con validación de negocio: {len([i for i in all_ideas if i.business_validated])}")
    print(f"  🔧 Ideas con validación técnica: {len([i for i in all_ideas if i.technical_validated])}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    seed_ideas()
