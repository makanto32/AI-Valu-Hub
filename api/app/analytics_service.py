"""
Servicio de Analytics y Métricas Ejecutivas.
Calcula KPIs, ROI, adopción de IA, reducción de duplicación, etc.
"""

from datetime import datetime, timedelta
from typing import List, Dict
from collections import Counter

from .models import (
    IdeaCase,
    IdeaStatus,
    DeploymentStatus,
    IdeaDuplicationMetrics,
    AIAdoptionMetrics,
    ProductionMetrics,
    InvestmentROIMetrics,
    CollaboratorMetrics,
    ExecutiveDashboardMetrics,
)


class AnalyticsService:
    """Servicio para calcular métricas ejecutivas."""

    # Costos estimados (USD)
    COST_PER_DUPLICATE_AVOIDED = 2_000  # Ahorro por duplicado evitado (tiempo de análisis)
    HOURS_PER_VALIDATION_MANUAL = 8  # Horas manuales de validación técnica
    HOURLY_RATE = 150  # Tarifa promedio USD/hora
    MONTHLY_PLATFORM_COST = 850  # Costo mensual del sistema
    AI_CONSULTING_PER_VALIDATION = 2_000  # Costo si fuera consulting externo

    def __init__(self, all_ideas: List[IdeaCase]):
        self.all_ideas = all_ideas

    def calculate_duplication_metrics(self) -> IdeaDuplicationMetrics:
        """Calcula métricas de detección y reducción de duplicación."""
        total = len(self.all_ideas)
        
        # Contar ideas que tienen iniciativas relacionadas (detectadas como potencial duplicado)
        duplicates_detected = 0
        total_similarity = 0
        domain_duplicates = {}

        for idea in self.all_ideas:
            # Simulación: si hay múltiples ideas similares, contar como duplicado evitado
            similar_count = sum(
                1 for other in self.all_ideas
                if (other.idea_id != idea.idea_id and 
                    self._calculate_idea_similarity(idea, other) > 60)
            )
            if similar_count > 0:
                duplicates_detected += 1
                # Capturar domain
                domain = idea.title.split()[0:2]
                domain_key = " ".join(domain)
                domain_duplicates[domain_key] = domain_duplicates.get(domain_key, 0) + 1

        # Calcular métrica de detección
        duplicate_detection_rate = (duplicates_detected / total * 100) if total > 0 else 0
        
        # Calcular similitud promedio
        avg_similarity = 0
        if duplicates_detected > 0:
            similarity_sum = 0
            count = 0
            for idea in self.all_ideas:
                for other in self.all_ideas:
                    if idea.idea_id != other.idea_id:
                        sim = self._calculate_idea_similarity(idea, other)
                        if sim > 0:
                            similarity_sum += sim
                            count += 1
            avg_similarity = (similarity_sum / count) if count > 0 else 0

        return IdeaDuplicationMetrics(
            total_ideas_submitted=total,
            duplicates_detected=duplicates_detected,
            duplicates_avoided_cost=duplicates_detected * self.COST_PER_DUPLICATE_AVOIDED,
            duplicate_detection_rate=duplicate_detection_rate,
            avg_similarity_score=min(avg_similarity, 100.0),
            duplicates_by_domain=domain_duplicates,
        )

    def calculate_ai_adoption_metrics(self) -> AIAdoptionMetrics:
        """Calcula métricas de adopción de IA."""
        total = len(self.all_ideas)
        
        # Ideas que usaron validación técnica (indicador de IA usage)
        ai_validated = sum(
            1 for idea in self.all_ideas
            if idea.technical_validation is not None or 
               len(idea.technical_questions) > 0
        )
        
        # Ideas con interacciones de agentes
        agent_assisted = sum(
            1 for idea in self.all_ideas
            if len(idea.clarification_interactions) > 0
        )
        
        # Promedio de preguntas por idea (indicador de profundidad)
        total_questions = sum(
            len(idea.clarification_questions) + len(idea.technical_questions)
            for idea in self.all_ideas
        )
        avg_questions = (total_questions / total) if total > 0 else 0

        adoption_rate = (ai_validated / total * 100) if total > 0 else 0

        return AIAdoptionMetrics(
            ideas_using_ai_validation=ai_validated,
            ideas_total=total,
            ai_adoption_rate=adoption_rate,
            agent_assisted_validations=agent_assisted,
            avg_agent_questions_per_idea=avg_questions,
            common_validation_patterns=self._identify_validation_patterns(),
        )

    def calculate_production_metrics(self) -> ProductionMetrics:
        """Calcula métricas de ideas en producción."""
        production_ideas = [
            idea for idea in self.all_ideas
            if idea.deployment_status == DeploymentStatus.production
        ]
        
        # Estimar valor por idea
        total_estimated_value = 0
        top_performers = []
        
        for idea in production_ideas:
            # Estimar valor basado en scoring de negocio
            if idea.business_validation:
                value_score = idea.business_validation.value_score
                # Rango de $20k a $80k basado en score (estimación realista primer año)
                estimated_value = (value_score / 100) * 80_000
                total_estimated_value += estimated_value
                top_performers.append({
                    "idea_id": idea.idea_id,
                    "title": idea.title,
                    "estimated_annual_value": estimated_value,
                    "deployment_status": idea.deployment_status,
                })

        # Ordenar top performers
        top_performers.sort(key=lambda x: x["estimated_annual_value"], reverse=True)
        
        # Calcular horas ahorradas (asumir 8 horas/validación * ideas con validación técnica)
        ideas_with_tech_validation = sum(
            1 for idea in self.all_ideas
            if idea.technical_validation is not None
        )
        hours_saved_annually = ideas_with_tech_validation * self.HOURS_PER_VALIDATION_MANUAL * 12

        success_rate = (len(production_ideas) / len(self.all_ideas) * 100) if self.all_ideas else 0

        return ProductionMetrics(
            ideas_in_production=len(production_ideas),
            estimated_annual_value=total_estimated_value,
            estimated_annual_savings=hours_saved_annually * self.HOURLY_RATE,
            estimated_hours_saved_annually=hours_saved_annually,
            top_performing_ideas=top_performers[:5],
            deployment_success_rate=success_rate,
        )

    def calculate_roi_metrics(self, annual_ai_investment: float = 100_000) -> InvestmentROIMetrics:
        """Calcula métricas de ROI."""
        prod_metrics = self.calculate_production_metrics()
        dup_metrics = self.calculate_duplication_metrics()
        
        # Total value generated
        total_value = (
            prod_metrics.estimated_annual_savings +  # Horas ahorradas
            dup_metrics.duplicates_avoided_cost +  # Duplicados evitados
            prod_metrics.estimated_annual_value  # Valor de ideas en producción
        )
        
        # Calcular ROI
        net_value = total_value - annual_ai_investment
        roi_percentage = (net_value / annual_ai_investment * 100) if annual_ai_investment > 0 else 0
        
        # Calcular payback period
        monthly_value = total_value / 12
        payback_months = (annual_ai_investment / monthly_value) if monthly_value > 0 else 12
        
        # Breakdown de inversión
        investment_breakdown = {
            "platform_annual": self.MONTHLY_PLATFORM_COST * 12,
            "consulting_equivalent": annual_ai_investment - (self.MONTHLY_PLATFORM_COST * 12),
        }

        # Trend mensual (simulado)
        monthly_trend = [
            (total_value / 12) * ((i + 1) / 12)  # Crecimiento lineal en el año
            for i in range(12)
        ]

        return InvestmentROIMetrics(
            total_ai_investment_usd=annual_ai_investment,
            monthly_ai_platform_cost=self.MONTHLY_PLATFORM_COST,
            estimated_annual_value_generated=total_value,
            roi_percentage=roi_percentage,
            payback_period_months=payback_months,
            investment_breakdown=investment_breakdown,
            value_trend_12_months=monthly_trend,
        )

    def calculate_collaborator_participation(self) -> List[CollaboratorMetrics]:
        """Calcula métricas de participación de colaboradores."""
        # Agrupar ideas por owner
        owner_ideas = {}
        for idea in self.all_ideas:
            owner_key = f"{idea.owner_user_id}|{idea.owner_display_name}"
            if owner_key not in owner_ideas:
                owner_ideas[owner_key] = []
            owner_ideas[owner_key].append(idea)

        collaborator_metrics = []
        total_ideas = len(self.all_ideas)

        for owner_key, ideas in owner_ideas.items():
            user_id, display_name = owner_key.split("|")
            
            # Contar aprobadas
            approved = sum(
                1 for idea in ideas
                if idea.status == IdeaStatus.business_viable
            )
            
            # Calcular días promedio a aprobación
            approval_times = []
            for idea in ideas:
                if idea.status == IdeaStatus.business_viable:
                    days_to_approval = (idea.updated_at - idea.created_at).days
                    approval_times.append(days_to_approval)
            
            avg_days = sum(approval_times) / len(approval_times) if approval_times else 0
            
            # Participation rate
            participation_rate = (len(ideas) / total_ideas * 100) if total_ideas > 0 else 0
            
            # Last submission
            last_submission = max(idea.created_at for idea in ideas)

            collaborator_metrics.append(
                CollaboratorMetrics(
                    user_id=user_id,
                    display_name=display_name,
                    ideas_submitted=len(ideas),
                    ideas_approved=approved,
                    avg_days_to_approval=avg_days,
                    participation_rate=participation_rate,
                    last_submission=last_submission,
                )
            )

        # Ordenar por participación
        collaborator_metrics.sort(key=lambda x: x.participation_rate, reverse=True)
        return collaborator_metrics

    def calculate_executive_dashboard(
        self, 
        tenant_id: str,
        annual_ai_investment: float = 100_000,
        period: str = "current"
    ) -> ExecutiveDashboardMetrics:
        """Calcula dashboard consolidado de métricas ejecutivas."""
        
        dup_metrics = self.calculate_duplication_metrics()
        adoption_metrics = self.calculate_ai_adoption_metrics()
        prod_metrics = self.calculate_production_metrics()
        roi_metrics = self.calculate_roi_metrics(annual_ai_investment)
        collaborators = self.calculate_collaborator_participation()
        
        # Retwork reduction = 100% - (duplicates / ideas submitted)
        retwork_reduction = 100 - (dup_metrics.duplicate_detection_rate / 2)  # Ajuste
        
        # Monthly trends
        monthly_submitted = self._get_monthly_trends("submitted")
        monthly_approved = self._get_monthly_trends("approved")
        monthly_costs = [self.MONTHLY_PLATFORM_COST for _ in range(12)]

        return ExecutiveDashboardMetrics(
            tenant_id=tenant_id,
            period=period,
            duplicates_avoided_percentage=min(dup_metrics.duplicate_detection_rate, 100),
            retwork_reduction_percentage=retwork_reduction,
            collaborator_participation_rate=sum(
                c.participation_rate for c in collaborators[:5]
            ) / 5 if collaborators else 0,
            ai_adoption_rate=adoption_metrics.ai_adoption_rate,
            duplication_metrics=dup_metrics,
            adoption_metrics=adoption_metrics,
            production_metrics=prod_metrics,
            roi_metrics=roi_metrics,
            top_collaborators=collaborators[:5],
            monthly_ideas_submitted=monthly_submitted,
            monthly_ideas_approved=monthly_approved,
            monthly_ai_cost=monthly_costs,
            generated_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
        )

    # ================ HELPER METHODS ================

    def _calculate_idea_similarity(self, idea1: IdeaCase, idea2: IdeaCase) -> float:
        """Calcula similitud entre dos ideas (0-100)."""
        if not idea1.title or not idea2.title:
            return 0.0
        
        words1 = set(idea1.title.lower().split())
        words2 = set(idea2.title.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return (intersection / union * 100) if union > 0 else 0.0

    def _identify_validation_patterns(self) -> List[str]:
        """Identifica patrones comunes de validación."""
        patterns = []
        
        # Contar dominios de preguntas técnicas
        domains = Counter()
        for idea in self.all_ideas:
            if idea.technical_questions:
                for q in idea.technical_questions:
                    # Extraer dominio de la pregunta
                    if "arquitectura" in q.prompt.lower():
                        domains["architecture"] += 1
                    elif "dato" in q.prompt.lower():
                        domains["data_science"] += 1
                    elif "regulat" in q.prompt.lower() or "compli" in q.prompt.lower():
                        domains["compliance"] += 1
                    elif "integra" in q.prompt.lower():
                        domains["integration"] += 1
        
        # Top patterns
        for domain, count in domains.most_common(3):
            patterns.append(f"{domain}: {count} ideas")
        
        return patterns if patterns else ["No patterns yet"]

    def _get_monthly_trends(self, metric_type: str) -> List[int]:
        """Genera tendencia mensual (últimos 12 meses)."""
        monthly_counts = [0] * 12
        now = datetime.utcnow()
        
        for idea in self.all_ideas:
            # Calcular mes del idea
            if metric_type == "submitted":
                ref_date = idea.created_at
            elif metric_type == "approved":
                if idea.status == IdeaStatus.business_viable:
                    ref_date = idea.updated_at
                else:
                    continue
            else:
                continue
            
            # Calcular offset desde ahora
            months_ago = (now - ref_date).days // 30
            if 0 <= months_ago < 12:
                monthly_counts[11 - months_ago] += 1
        
        return monthly_counts
