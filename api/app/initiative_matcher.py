"""
Servicio de matching de iniciativas.
Detecta iniciativas similares basadas en contexto y problema.
"""

from typing import List
from difflib import SequenceMatcher

from .models import (
    ContactPerson,
    InitiativeRegistry,
    IdeaMatchingResult,
    RelatedInitiative,
)


class InitiativeMatcher:
    """
    Servicio que detecta iniciativas relacionadas/similares.
    Utiliza:
    - Análisis de keywords de problema
    - Similitud textual del problema/solución
    - Categorización de dominio
    """

    def __init__(self, initiatives_registry: List[InitiativeRegistry]):
        """
        Args:
            initiatives_registry: Lista de iniciativas conocidas en el catálogo
        """
        self.initiatives = initiatives_registry

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud entre dos textos (0-100)."""
        ratio = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return ratio * 100

    def _keyword_overlap(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Calcula solapamiento de keywords (0-100)."""
        if not keywords1 or not keywords2:
            return 0
        set1 = set(kw.lower() for kw in keywords1)
        set2 = set(kw.lower() for kw in keywords2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        if union == 0:
            return 0
        return (intersection / union) * 100

    def find_related_initiatives(
        self,
        idea_id: str,
        problem_statement: str,
        problem_domain: str,
        problem_keywords: List[str],
        similarity_threshold: float = 40.0,
    ) -> IdeaMatchingResult:
        """
        Encuentra iniciativas relacionadas a una idea nueva.

        Args:
            idea_id: ID de la idea
            problem_statement: Descripción del problema
            problem_domain: Dominio del problema (e.g., "fraud-detection", "kyc")
            problem_keywords: Keywords del problema
            similarity_threshold: Score mínimo para considerar similar (0-100)

        Returns:
            IdeaMatchingResult con iniciativas relacionadas
        """
        related_initiatives = []
        suggested_contacts = set()

        for initiative in self.initiatives:
            # Calcular similitud por múltiples factores
            scores = []

            # Factor 1: Keywords overlap (peso: 40%)
            keyword_sim = self._keyword_overlap(problem_keywords, initiative.problem_keywords)
            scores.append(keyword_sim * 0.4)

            # Factor 2: Similitud textual del problema (peso: 35%)
            text_sim = self._text_similarity(problem_statement, initiative.title)
            scores.append(text_sim * 0.35)

            # Factor 3: Dominio similar (peso: 25%)
            domain_sim = (
                100 if problem_domain == initiative.solution_category else
                50 if problem_domain in initiative.solution_category else
                0
            )
            scores.append(domain_sim * 0.25)

            # Score final
            final_score = sum(scores)

            # Si supera threshold, agregar como relacionada
            if final_score >= similarity_threshold:
                related_init = RelatedInitiative(
                    initiative_id=initiative.initiative_id,
                    title=initiative.title,
                    status=initiative.deployment_status,
                    stage=initiative.stage,
                    similarity_score=final_score,
                    reason=self._generate_similarity_reason(
                        keyword_sim, text_sim, domain_sim, initiative
                    ),
                    main_contact=initiative.main_contact,
                    created_at=initiative.created_at,
                    deployment_date=initiative.deployment_date,
                )
                related_initiatives.append(related_init)
                suggested_contacts.add(initiative.main_contact)
                for contact in initiative.supporting_contacts:
                    suggested_contacts.add(contact)

        # Ordenar por similitud descendente
        related_initiatives.sort(key=lambda x: x.similarity_score, reverse=True)

        # Determinar recomendación
        can_proceed = len(related_initiatives) == 0
        recommendation = self._generate_recommendation(related_initiatives, can_proceed)
        next_actions = self._generate_next_actions(
            related_initiatives, can_proceed
        )

        return IdeaMatchingResult(
            idea_id=idea_id,
            has_related_initiatives=len(related_initiatives) > 0,
            related_initiatives=related_initiatives[:5],  # Top 5
            can_proceed_independently=can_proceed,
            recommendation=recommendation,
            next_actions=next_actions,
            suggested_contacts=list(suggested_contacts)[:5],  # Top 5
        )

    def _generate_similarity_reason(
        self,
        keyword_sim: float,
        text_sim: float,
        domain_sim: float,
        initiative: InitiativeRegistry,
    ) -> str:
        """Genera una explicación de por qué son similares."""
        reasons = []
        if keyword_sim > 60:
            reasons.append(f"Comparten keywords clave (similitud: {keyword_sim:.0f}%)")
        if text_sim > 50:
            reasons.append(f"Problema similar (similitud textual: {text_sim:.0f}%)")
        if domain_sim > 0:
            reasons.append(f"Mismo dominio de solución")

        base = f"Relacionada con iniciativa '{initiative.title}' - " + " | ".join(
            reasons
        )
        return base

    def _generate_recommendation(
        self, related_initiatives: List[RelatedInitiative], can_proceed: bool
    ) -> str:
        """Genera recomendación basada en iniciativas relacionadas."""
        if can_proceed:
            return "Proceder con nuevo intake. No hay iniciativas relacionadas identificadas."

        # Analizar estado de iniciativas relacionadas
        in_production = [
            i for i in related_initiatives if i.status == "production"
        ]
        in_development = [
            i for i in related_initiatives if i.status == "development"
        ]
        in_funding = [i for i in related_initiatives if i.status == "funding"]

        if in_production:
            count = len(in_production)
            return f"⚠️  Se encontraron {count} soluciones SIMILARES EN PRODUCCIÓN. Evaluar si esta idea complementa o sustituye la solución existente. Recomendado: Contactar a propietarios de iniciativas existentes."

        if in_development:
            count = len(in_development)
            return f"⚠️  Se encontraron {count} iniciativas SIMILARES EN DESARROLLO. Recomendado: Coordinar con equipos en desarrollo para evitar duplicación de esfuerzo."

        if in_funding:
            count = len(in_funding)
            return f"ℹ️  Se encontraron {count} iniciativas SIMILARES EN FASE DE FINANCIAMIENTO. Considerar colaboración o consolidación de propuestas."

        return "Revisar iniciativas relacionadas detectadas."

    def _generate_next_actions(
        self, related_initiatives: List[RelatedInitiative], can_proceed: bool
    ) -> List[str]:
        """Genera acciones recomendadas."""
        actions = []

        if can_proceed:
            actions = [
                "Proceder con captura detallada de la idea",
                "Iniciar validación de negocio",
                "Programar sesión de aclaración si es necesario",
            ]
        else:
            actions.append(
                "Revisar iniciativas relacionadas en detalle"
            )

            # Acciones específicas por estado
            if any(i.status == "production" for i in related_initiatives):
                actions.append(
                    "Agendar reunión con propietarios de soluciones en producción"
                )
                actions.append(
                    "Evaluar oportunidades de integración o mejora de solución existente"
                )

            if any(i.status == "development" for i in related_initiatives):
                actions.append(
                    "Contactar equipos en desarrollo para validar scope y evitar duplicación"
                )
                actions.append(
                    "Considerar join a iniciativa existente si hay alineación"
                )

            if any(i.status == "funding" for i in related_initiatives):
                actions.append(
                    "Evaluar consolidación de propuestas complementarias"
                )

            actions.append("Documentar decisión de proceder o consolidar")

        return actions
