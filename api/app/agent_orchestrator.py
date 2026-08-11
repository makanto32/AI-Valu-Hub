"""
Orquestador de Agentes No-Deterministas.
Usa Context Engine como DNA para habilitar skills dinámicamente según el contexto.
Soporta múltiples agentes especializados (Architecture, DataScience, Compliance, Business).
"""

import json
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum

from .models import (
    IdeaCase,
    IdeaStage,
    AgentSkill,
    AgentContext,
    AgentExecution,
    TechnicalQuestion,
    ClarificationQuestion,
)


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentType(str, Enum):
    ARCHITECTURE = "architecture"
    DATA_SCIENCE = "data_science"
    COMPLIANCE = "compliance"
    BUSINESS = "business"


class ContextEngine:
    """Motor de contexto empresarial - ADN del sistema de agentes."""
    
    def __init__(self, company_context: AgentContext):
        self.context = company_context
    
    def should_block_domain(self, domain: str) -> bool:
        """Verifica si un dominio está prohibido por contexto."""
        domain_lower = domain.lower()
        return any(
            prohibited.lower() in domain_lower
            for prohibited in self.context.prohibited_domains
        )
    
    def has_strategic_priority(self, keyword: str) -> bool:
        """Verifica si una palabra clave coincide con prioridades estratégicas."""
        keyword_lower = keyword.lower()
        return any(
            keyword_lower in priority.lower()
            for priority in self.context.strategic_priorities
        )
    
    def evaluate_risk_level(self, idea_keywords: List[str]) -> str:
        """Evalúa nivel de riesgo de una idea según contexto."""
        risk_score = 0
        
        # Evaluar si coincide con restricciones regulatorias
        for keyword in idea_keywords:
            if any(
                keyword.lower() in constraint.lower()
                for constraint in self.context.regulatory_constraints
            ):
                risk_score += 2
        
        # Riesgo según tolerancia
        if self.context.risk_tolerance == "low":
            risk_threshold = 1
        elif self.context.risk_tolerance == "medium":
            risk_threshold = 3
        else:  # high
            risk_threshold = 5
        
        if risk_score >= risk_threshold:
            return "high"
        elif risk_score > 0:
            return "medium"
        else:
            return "low"
    
    def get_applicable_skills(self) -> List[AgentSkill]:
        """Retorna skills disponibles según contexto."""
        return self.context.available_skills


class Agent:
    """Base para agentes especializados."""
    
    def __init__(self, agent_type: AgentType, context_engine: ContextEngine):
        self.agent_type = agent_type
        self.context = context_engine
        self.name = self._get_agent_name()
    
    def _get_agent_name(self) -> str:
        name_map = {
            AgentType.ARCHITECTURE: "Architecture Expert",
            AgentType.DATA_SCIENCE: "Data Science Specialist",
            AgentType.COMPLIANCE: "Compliance Officer",
            AgentType.BUSINESS: "Business Analyst",
        }
        return name_map.get(self.agent_type, "Agent")
    
    def can_handle_idea(self, idea: IdeaCase) -> bool:
        """Determina si el agente puede procesar esta idea."""
        # Puede procesar si no está bloqueada por contexto
        return not self.context.should_block_domain(idea.problem_domain)
    
    def evaluate_complexity(self, idea: IdeaCase) -> ComplexityLevel:
        """Evalúa complejidad de la idea."""
        complexity_score = 0
        
        # Evaluar por cantidad de preguntas
        complexity_score += len(idea.technical_questions)
        
        # Evaluar por keywords
        complexity_score += len(idea.problem_keywords)
        
        # Evaluar por alineación estratégica
        if any(
            self.context.has_strategic_priority(kw)
            for kw in idea.problem_keywords
        ):
            complexity_score += 1
        
        if complexity_score >= 8:
            return ComplexityLevel.CRITICAL
        elif complexity_score >= 5:
            return ComplexityLevel.HIGH
        elif complexity_score >= 2:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.LOW
    
    def select_skills(
        self, 
        idea: IdeaCase, 
        complexity: ComplexityLevel
    ) -> List[AgentSkill]:
        """Selecciona skills dinámicamente basado en complejidad y contexto."""
        selected_skills = []
        available_skills = self.context.get_applicable_skills()
        
        # Filtrar por dominio de expertise del agente
        domain_filter = self._get_domain_filter()
        
        for skill in available_skills:
            if skill.expertise_domain != domain_filter:
                continue
            
            # Seleccionar skill si:
            # 1. Hay palabras clave en la idea que coinciden
            # 2. Complejidad >= required_for_complexity
            
            required_complexity = skill.required_for_complexity
            if self._meets_complexity_requirement(complexity, required_complexity):
                # Verificar trigger keywords
                if self._has_trigger_keywords(idea, skill):
                    selected_skills.append(skill)
        
        return selected_skills
    
    def _get_domain_filter(self) -> str:
        """Retorna el dominio de expertise del agente."""
        domain_map = {
            AgentType.ARCHITECTURE: "architecture",
            AgentType.DATA_SCIENCE: "data_science",
            AgentType.COMPLIANCE: "compliance",
            AgentType.BUSINESS: "business",
        }
        return domain_map.get(self.agent_type, "general")
    
    def _meets_complexity_requirement(self, actual: ComplexityLevel, required: str) -> bool:
        """Verifica si complejidad actual cumple con requerimiento."""
        complexity_order = {
            ComplexityLevel.LOW: 0,
            ComplexityLevel.MEDIUM: 1,
            ComplexityLevel.HIGH: 2,
            ComplexityLevel.CRITICAL: 3,
        }
        
        required_map = {
            "low": 0,
            "medium": 1,
            "high": 2,
            "critical": 3,
        }
        
        return complexity_order.get(actual, 0) >= required_map.get(required, 0)
    
    def _has_trigger_keywords(self, idea: IdeaCase, skill: AgentSkill) -> bool:
        """Verifica si idea contiene keywords que activan el skill."""
        idea_keywords = {kw.lower() for kw in idea.problem_keywords}
        skill_keywords = {kw.lower() for kw in skill.trigger_keywords}
        
        return bool(idea_keywords & skill_keywords) or len(skill.trigger_keywords) == 0
    
    async def execute(
        self,
        idea: IdeaCase,
        skills: List[AgentSkill],
    ) -> AgentExecution:
        """Ejecuta agente con skills seleccionados."""
        complexity = self.evaluate_complexity(idea)
        questions_to_ask = []
        
        # Recolectar preguntas de todos los skills
        for skill in skills:
            questions_to_ask.extend(skill.questions_to_ask)
        
        # Simular decisiones basadas en contexto
        decisions = self._generate_decisions(idea, skills, complexity)
        
        execution = AgentExecution(
            idea_id=idea.idea_id,
            tenant_id=idea.tenant_id,
            activated_skills=[s.skill_id for s in skills],
            questions_asked=questions_to_ask,
            answers_received=[],  # Se completan después
            decisions_made=decisions,
            complexity_level=complexity.value,
            execution_time_seconds=0.0,
        )
        
        return execution
    
    def _generate_decisions(
        self,
        idea: IdeaCase,
        skills: List[AgentSkill],
        complexity: ComplexityLevel,
    ) -> List[str]:
        """Genera decisiones basadas en análisis de contexto."""
        decisions = []
        
        # Decisión 1: Procedibilidad
        if complexity == ComplexityLevel.CRITICAL:
            decisions.append(
                f"[{self.name}] Requiere escalación a liderazgo - Complejidad crítica"
            )
        else:
            decisions.append(f"[{self.name}] Puede proceder - Complejidad {complexity.value}")
        
        # Decisión 2: Requerimientos de coordinación
        if len(skills) > 2:
            decisions.append(
                f"[{self.name}] Requiere coordinación multi-team ({len(skills)} skills)"
            )
        
        # Decisión 3: Alineación estratégica
        strategic_alignment = any(
            self.context.has_strategic_priority(kw)
            for kw in idea.problem_keywords
        )
        if strategic_alignment:
            decisions.append(f"[{self.name}] Alineada con prioridades estratégicas ✓")
        
        # Decisión 4: Riesgo
        risk_level = self.context.evaluate_risk_level(idea.problem_keywords)
        decisions.append(f"[{self.name}] Nivel de riesgo: {risk_level}")
        
        return decisions


class ArchitectureAgent(Agent):
    """Agente especializado en arquitectura de soluciones."""
    
    def __init__(self, context_engine: ContextEngine):
        super().__init__(AgentType.ARCHITECTURE, context_engine)
    
    async def suggest_technology_stack(self, idea: IdeaCase) -> Dict:
        """Sugiere stack tecnológico basado en idea y contexto."""
        return {
            "primary_tech": self._select_primary_tech(idea),
            "supporting_services": self._select_supporting_services(idea),
            "estimated_cost_monthly": self._estimate_cost(idea),
            "implementation_timeline_weeks": self._estimate_timeline(idea),
        }
    
    def _select_primary_tech(self, idea: IdeaCase) -> str:
        """Selecciona tecnología primaria."""
        if "AI" in idea.title or "ML" in idea.title:
            return "Azure AI / Cognitive Services"
        elif "integraci" in idea.title.lower():
            return "Azure Integration Services"
        elif "dato" in idea.title.lower():
            return "Azure Synapse Analytics"
        else:
            return "Azure App Service + CosmosDB"
    
    def _select_supporting_services(self, idea: IdeaCase) -> List[str]:
        """Selecciona servicios de soporte."""
        services = ["Azure Key Vault", "Azure Monitor", "Azure Log Analytics"]
        
        if any(kw in idea.problem_keywords for kw in ["security", "seguridad", "compliance"]):
            services.append("Azure Defender")
        
        if any(kw in idea.problem_keywords for kw in ["integration", "integracion", "api"]):
            services.append("Azure API Management")
        
        return services
    
    def _estimate_cost(self, idea: IdeaCase) -> float:
        """Estima costo mensual."""
        # Costo base
        base_cost = 500
        
        # Ajuste por complejidad
        complexity = self.evaluate_complexity(idea)
        complexity_multipliers = {
            ComplexityLevel.LOW: 1.0,
            ComplexityLevel.MEDIUM: 1.5,
            ComplexityLevel.HIGH: 2.5,
            ComplexityLevel.CRITICAL: 4.0,
        }
        
        return base_cost * complexity_multipliers.get(complexity, 1.0)
    
    def _estimate_timeline(self, idea: IdeaCase) -> int:
        """Estima timeline de implementación en semanas."""
        base_timeline = 4
        
        complexity = self.evaluate_complexity(idea)
        complexity_timeline = {
            ComplexityLevel.LOW: 4,
            ComplexityLevel.MEDIUM: 8,
            ComplexityLevel.HIGH: 12,
            ComplexityLevel.CRITICAL: 16,
        }
        
        return complexity_timeline.get(complexity, 4)


class DataScienceAgent(Agent):
    """Agente especializado en viabilidad de datos y ML."""
    
    def __init__(self, context_engine: ContextEngine):
        super().__init__(AgentType.DATA_SCIENCE, context_engine)
    
    async def evaluate_data_readiness(self, idea: IdeaCase) -> Dict:
        """Evalúa disponibilidad y calidad de datos."""
        return {
            "data_availability": self._assess_data_availability(idea),
            "estimated_data_preparation_weeks": self._estimate_data_prep(idea),
            "ml_model_recommendation": self._recommend_model(idea),
            "data_quality_risks": self._identify_data_risks(idea),
        }
    
    def _assess_data_availability(self, idea: IdeaCase) -> str:
        """Evalúa disponibilidad de datos."""
        if any(kw in idea.problem_keywords for kw in ["historical", "histórico"]):
            return "high"
        elif any(kw in idea.problem_keywords for kw in ["real-time", "en-tiempo-real"]):
            return "medium"
        else:
            return "low"
    
    def _estimate_data_prep(self, idea: IdeaCase) -> int:
        """Estima semanas de preparación de datos."""
        complexity = self.evaluate_complexity(idea)
        
        prep_weeks = {
            ComplexityLevel.LOW: 2,
            ComplexityLevel.MEDIUM: 4,
            ComplexityLevel.HIGH: 6,
            ComplexityLevel.CRITICAL: 8,
        }
        
        return prep_weeks.get(complexity, 2)
    
    def _recommend_model(self, idea: IdeaCase) -> str:
        """Recomienda tipo de modelo."""
        if "fraud" in idea.title.lower() or "detección" in idea.title.lower():
            return "Anomaly Detection (Isolation Forest, Autoencoders)"
        elif "predict" in idea.title.lower() or "pronóstico" in idea.title.lower():
            return "Time Series Forecasting (ARIMA, Prophet, LSTM)"
        elif "sentiment" in idea.title.lower() or "sentimiento" in idea.title.lower():
            return "NLP - Sentiment Analysis (BERT, GPT-based)"
        else:
            return "Classification (Random Forest, XGBoost, Neural Networks)"
    
    def _identify_data_risks(self, idea: IdeaCase) -> List[str]:
        """Identifica riesgos de datos."""
        risks = []
        
        if len(idea.problem_keywords) < 3:
            risks.append("Especificación de datos insuficiente")
        
        if any(kw in idea.problem_keywords for kw in ["sensitive", "confidential", "pii"]):
            risks.append("Requiere anonimización y cumplimiento de privacidad")
        
        if not any(kw in idea.problem_keywords for kw in ["data", "datos", "histórico"]):
            risks.append("Fuente de datos no clara")
        
        return risks if risks else ["Riesgos bajos de datos"]


class ComplianceAgent(Agent):
    """Agente especializado en cumplimiento regulatorio."""
    
    def __init__(self, context_engine: ContextEngine):
        super().__init__(AgentType.COMPLIANCE, context_engine)
    
    async def evaluate_regulatory_fit(self, idea: IdeaCase) -> Dict:
        """Evalúa cumplimiento regulatorio."""
        return {
            "regulatory_status": self._check_regulatory_fit(idea),
            "required_approvals": self._identify_required_approvals(idea),
            "compliance_risks": self._identify_compliance_risks(idea),
            "data_residency_requirements": self._check_data_residency(idea),
        }
    
    def _check_regulatory_fit(self, idea: IdeaCase) -> str:
        """Verifica alineación regulatoria."""
        idea_keywords_lower = {kw.lower() for kw in idea.problem_keywords}
        regulatory_keywords = {
            kw.lower() for kw in self.context.context.regulatory_constraints
        }
        
        if idea_keywords_lower & regulatory_keywords:
            return "requires_review"
        else:
            return "compliant"
    
    def _identify_required_approvals(self, idea: IdeaCase) -> List[str]:
        """Identifica aprobaciones requeridas."""
        approvals = []
        
        if any(kw in idea.problem_keywords for kw in ["data", "datos", "pii"]):
            approvals.append("Data Privacy Officer")
        
        if any(kw in idea.problem_keywords for kw in ["security", "seguridad"]):
            approvals.append("Information Security")
        
        if self.context.evaluate_risk_level(idea.problem_keywords) == "high":
            approvals.append("Leadership")
        
        return approvals if approvals else ["Standard Review"]
    
    def _identify_compliance_risks(self, idea: IdeaCase) -> List[str]:
        """Identifica riesgos de cumplimiento."""
        risks = []
        
        for constraint in self.context.context.regulatory_constraints:
            if any(
                constraint.lower() in kw.lower()
                for kw in idea.problem_keywords
            ):
                risks.append(f"Potencial conflicto con: {constraint}")
        
        return risks if risks else ["Sin riesgos identificados"]
    
    def _check_data_residency(self, idea: IdeaCase) -> str:
        """Verifica requerimientos de residencia de datos."""
        # Lógica simplificada
        return "Azure regions - EU compliant"


class MultiAgentOrchestrator:
    """Orquestador de múltiples agentes no-deterministas."""
    
    def __init__(self, context: AgentContext):
        self.context_engine = ContextEngine(context)
        self.agents = self._initialize_agents()
        self.execution_history: List[AgentExecution] = []
    
    def _initialize_agents(self) -> Dict[AgentType, Agent]:
        """Inicializa todos los agentes disponibles."""
        return {
            AgentType.ARCHITECTURE: ArchitectureAgent(self.context_engine),
            AgentType.DATA_SCIENCE: DataScienceAgent(self.context_engine),
            AgentType.COMPLIANCE: ComplianceAgent(self.context_engine),
            AgentType.BUSINESS: Agent(AgentType.BUSINESS, self.context_engine),
        }
    
    async def orchestrate_validation(self, idea: IdeaCase) -> Dict:
        """Orquesta validación de idea usando múltiples agentes."""
        
        # Determinar qué agentes participan
        eligible_agents = [
            agent for agent in self.agents.values()
            if agent.can_handle_idea(idea)
        ]
        
        # Evaluar complejidad (una sola vez, compartido)
        complexity = eligible_agents[0].evaluate_complexity(idea)
        
        # Ejecutar cada agente
        agent_results = {}
        for agent in eligible_agents:
            # Seleccionar skills
            skills = agent.select_skills(idea, complexity)
            
            # Ejecutar
            execution = await agent.execute(idea, skills)
            self.execution_history.append(execution)
            
            # Almacenar resultados específicos
            if agent.agent_type == AgentType.ARCHITECTURE:
                agent_results["architecture"] = (
                    await agent.suggest_technology_stack(idea)
                )
            elif agent.agent_type == AgentType.DATA_SCIENCE:
                agent_results["data_science"] = (
                    await agent.evaluate_data_readiness(idea)
                )
            elif agent.agent_type == AgentType.COMPLIANCE:
                agent_results["compliance"] = (
                    await agent.evaluate_regulatory_fit(idea)
                )
        
        # Consolidar decisiones
        consolidated_decisions = self._consolidate_decisions(
            eligible_agents, idea, complexity
        )
        
        return {
            "idea_id": idea.idea_id,
            "complexity_level": complexity.value,
            "agents_involved": [a.agent_type.value for a in eligible_agents],
            "agent_results": agent_results,
            "consolidated_recommendation": consolidated_decisions,
            "execution_timestamp": datetime.utcnow().isoformat(),
        }
    
    def _consolidate_decisions(
        self,
        agents: List[Agent],
        idea: IdeaCase,
        complexity: ComplexityLevel,
    ) -> Dict:
        """Consolida decisiones de múltiples agentes."""
        return {
            "go_no_go": "GO" if complexity != ComplexityLevel.CRITICAL else "ESCALATE",
            "next_steps": [
                "Coordinar con todos los agentes involucrados",
                "Validar en contra de prioridades estratégicas",
                "Estimar tiempo total de implementación",
                "Obtener aprobaciones regulatorias",
            ],
            "escalation_required": complexity == ComplexityLevel.CRITICAL,
            "estimated_total_timeline_weeks": self._estimate_total_timeline(agents),
        }
    
    def _estimate_total_timeline(self, agents: List[Agent]) -> int:
        """Estima timeline total considerando todas las fases."""
        # Simplificado: máximo de todos los agentes
        return 12  # Semanas default
    
    def get_execution_summary(self) -> Dict:
        """Resume ejecuciones recientes de agentes."""
        return {
            "total_executions": len(self.execution_history),
            "recent_executions": [
                {
                    "idea_id": ex.idea_id,
                    "complexity": ex.complexity_level,
                    "skills_activated": len(ex.activated_skills),
                    "timestamp": ex.created_at.isoformat(),
                }
                for ex in self.execution_history[-5:]
            ],
        }
