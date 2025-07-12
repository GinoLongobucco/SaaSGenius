import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re

logger = logging.getLogger(__name__)

class ProjectScale(Enum):
    STARTUP = "startup"
    SMB = "smb"
    ENTERPRISE = "enterprise"
    GLOBAL = "global"

class IndustryType(Enum):
    HEALTHCARE = "healthcare"
    FINTECH = "fintech"
    ECOMMERCE = "ecommerce"
    EDUCATION = "education"
    LOGISTICS = "logistics"
    GENERAL = "general"

@dataclass
class TechRequirement:
    """Requisito técnico específico"""
    name: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'performance', 'security', 'scalability', 'integration'
    description: str
    impact_score: float  # 0-10

@dataclass
class TechnologyOption:
    """Opción tecnológica con evaluación"""
    name: str
    category: str  # 'frontend', 'backend', 'database', 'infrastructure'
    version: str
    pros: List[str]
    cons: List[str]
    learning_curve: str  # 'low', 'medium', 'high'
    community_support: float  # 0-10
    market_adoption: float  # 0-10
    future_viability: float  # 0-10
    cost_factor: str  # 'free', 'low', 'medium', 'high'
    industry_fit: float  # 0-10
    scale_suitability: Dict[str, float]  # scale -> suitability score
    dependencies: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)

@dataclass
class StackRecommendation:
    """Recomendación completa de stack"""
    frontend: TechnologyOption
    backend: TechnologyOption
    database: TechnologyOption
    infrastructure: Dict[str, TechnologyOption]
    additional_tools: Dict[str, TechnologyOption]
    total_score: float
    justification: str
    estimated_cost: str
    development_timeline: str
    team_requirements: Dict[str, int]
    risk_factors: List[str]
    migration_path: List[str]

class DynamicTechStackAnalyzer:
    """Analizador dinámico de stack tecnológico"""
    
    def __init__(self):
        self.tech_database = self._initialize_tech_database()
        self.industry_weights = self._initialize_industry_weights()
        self.scale_factors = self._initialize_scale_factors()
        self.trend_multipliers = self._initialize_trend_multipliers()
    
    def analyze_and_recommend(self, 
                            project_context: Dict[str, Any],
                            web_search_data: Dict[str, Any],
                            requirements: List[TechRequirement]) -> StackRecommendation:
        """Analiza contexto y recomienda stack óptimo"""
        
        # Extraer contexto del proyecto
        industry = self._determine_industry(project_context)
        scale = self._determine_scale(project_context)
        
        # Analizar tendencias actuales
        current_trends = self._extract_tech_trends(web_search_data)
        
        # Evaluar requisitos específicos
        requirement_weights = self._calculate_requirement_weights(requirements)
        
        # Generar opciones por categoría
        frontend_options = self._evaluate_frontend_options(industry, scale, requirement_weights, current_trends)
        backend_options = self._evaluate_backend_options(industry, scale, requirement_weights, current_trends)
        database_options = self._evaluate_database_options(industry, scale, requirement_weights, current_trends)
        infrastructure_options = self._evaluate_infrastructure_options(industry, scale, requirement_weights, current_trends)
        
        # Seleccionar combinación óptima
        optimal_stack = self._select_optimal_combination(
            frontend_options, backend_options, database_options, infrastructure_options,
            industry, scale, requirement_weights
        )
        
        # Generar recomendación completa
        recommendation = self._build_recommendation(optimal_stack, project_context, requirements)
        
        return recommendation
    
    def _initialize_tech_database(self) -> Dict[str, Dict[str, TechnologyOption]]:
        """Inicializa base de datos de tecnologías"""
        return {
            'frontend': {
                'react': TechnologyOption(
                    name='React',
                    category='frontend',
                    version='18.x',
                    pros=['Ecosistema maduro', 'Gran comunidad', 'Flexibilidad', 'Performance'],
                    cons=['Curva de aprendizaje', 'Configuración inicial compleja'],
                    learning_curve='medium',
                    community_support=9.5,
                    market_adoption=9.8,
                    future_viability=9.2,
                    cost_factor='free',
                    industry_fit=8.5,
                    scale_suitability={'startup': 9.0, 'smb': 9.5, 'enterprise': 9.8, 'global': 9.5}
                ),
                'vue': TechnologyOption(
                    name='Vue.js',
                    category='frontend',
                    version='3.x',
                    pros=['Fácil aprendizaje', 'Documentación excelente', 'Performance', 'Flexibilidad'],
                    cons=['Ecosistema menor que React', 'Menos oportunidades laborales'],
                    learning_curve='low',
                    community_support=8.5,
                    market_adoption=7.8,
                    future_viability=8.5,
                    cost_factor='free',
                    industry_fit=8.0,
                    scale_suitability={'startup': 9.5, 'smb': 9.0, 'enterprise': 8.0, 'global': 7.5}
                ),
                'angular': TechnologyOption(
                    name='Angular',
                    category='frontend',
                    version='17.x',
                    pros=['Framework completo', 'TypeScript nativo', 'Escalabilidad', 'Estructura'],
                    cons=['Curva de aprendizaje alta', 'Overhead para proyectos pequeños'],
                    learning_curve='high',
                    community_support=8.8,
                    market_adoption=8.2,
                    future_viability=8.8,
                    cost_factor='free',
                    industry_fit=9.0,
                    scale_suitability={'startup': 6.0, 'smb': 7.5, 'enterprise': 9.5, 'global': 9.8}
                ),
                'svelte': TechnologyOption(
                    name='Svelte/SvelteKit',
                    category='frontend',
                    version='4.x',
                    pros=['Performance excepcional', 'Bundle size pequeño', 'Sintaxis simple'],
                    cons=['Ecosistema limitado', 'Comunidad pequeña', 'Menos recursos'],
                    learning_curve='low',
                    community_support=7.0,
                    market_adoption=6.5,
                    future_viability=8.0,
                    cost_factor='free',
                    industry_fit=7.5,
                    scale_suitability={'startup': 8.5, 'smb': 8.0, 'enterprise': 6.5, 'global': 6.0}
                )
            },
            'backend': {
                'nodejs': TechnologyOption(
                    name='Node.js + Express/Fastify',
                    category='backend',
                    version='20.x LTS',
                    pros=['JavaScript full-stack', 'NPM ecosystem', 'Performance I/O', 'Rapid development'],
                    cons=['Single-threaded limitations', 'Callback complexity'],
                    learning_curve='medium',
                    community_support=9.5,
                    market_adoption=9.2,
                    future_viability=9.0,
                    cost_factor='free',
                    industry_fit=8.5,
                    scale_suitability={'startup': 9.5, 'smb': 9.0, 'enterprise': 8.5, 'global': 8.0}
                ),
                'python': TechnologyOption(
                    name='Python + FastAPI/Django',
                    category='backend',
                    version='3.11+',
                    pros=['Sintaxis clara', 'ML/AI integration', 'Rapid prototyping', 'Versatilidad'],
                    cons=['Performance relativa', 'GIL limitations'],
                    learning_curve='low',
                    community_support=9.8,
                    market_adoption=9.5,
                    future_viability=9.5,
                    cost_factor='free',
                    industry_fit=9.0,
                    scale_suitability={'startup': 9.0, 'smb': 9.5, 'enterprise': 9.0, 'global': 8.5}
                ),
                'golang': TechnologyOption(
                    name='Go + Gin/Fiber',
                    category='backend',
                    version='1.21+',
                    pros=['Performance excelente', 'Concurrency nativa', 'Deployment simple', 'Memory efficiency'],
                    cons=['Ecosistema limitado', 'Verbosidad', 'Curva de aprendizaje'],
                    learning_curve='medium',
                    community_support=8.5,
                    market_adoption=8.0,
                    future_viability=9.0,
                    cost_factor='free',
                    industry_fit=8.8,
                    scale_suitability={'startup': 8.0, 'smb': 8.5, 'enterprise': 9.5, 'global': 9.8}
                ),
                'java': TechnologyOption(
                    name='Java + Spring Boot',
                    category='backend',
                    version='21 LTS',
                    pros=['Ecosistema maduro', 'Performance', 'Enterprise features', 'Escalabilidad'],
                    cons=['Verbosidad', 'Complejidad inicial', 'Memory usage'],
                    learning_curve='high',
                    community_support=9.0,
                    market_adoption=8.8,
                    future_viability=8.5,
                    cost_factor='free',
                    industry_fit=9.2,
                    scale_suitability={'startup': 6.5, 'smb': 7.5, 'enterprise': 9.8, 'global': 9.5}
                ),
                'csharp': TechnologyOption(
                    name='C# + .NET Core',
                    category='backend',
                    version='8.0',
                    pros=['Performance excelente', 'Tooling superior', 'Cross-platform', 'Type safety'],
                    cons=['Microsoft ecosystem', 'Licensing considerations'],
                    learning_curve='medium',
                    community_support=8.8,
                    market_adoption=8.5,
                    future_viability=8.8,
                    cost_factor='free',
                    industry_fit=8.8,
                    scale_suitability={'startup': 7.5, 'smb': 8.5, 'enterprise': 9.5, 'global': 9.2}
                )
            },
            'database': {
                'postgresql': TechnologyOption(
                    name='PostgreSQL',
                    category='database',
                    version='16.x',
                    pros=['ACID compliance', 'JSON support', 'Extensibilidad', 'Performance'],
                    cons=['Complejidad de configuración', 'Memory usage'],
                    learning_curve='medium',
                    community_support=9.5,
                    market_adoption=9.0,
                    future_viability=9.5,
                    cost_factor='free',
                    industry_fit=9.2,
                    scale_suitability={'startup': 8.5, 'smb': 9.0, 'enterprise': 9.5, 'global': 9.8}
                ),
                'mysql': TechnologyOption(
                    name='MySQL',
                    category='database',
                    version='8.0',
                    pros=['Simplicidad', 'Performance read-heavy', 'Ecosistema maduro'],
                    cons=['Limitaciones avanzadas', 'Licensing Oracle'],
                    learning_curve='low',
                    community_support=9.0,
                    market_adoption=8.8,
                    future_viability=8.0,
                    cost_factor='free',
                    industry_fit=8.0,
                    scale_suitability={'startup': 9.0, 'smb': 8.5, 'enterprise': 7.5, 'global': 7.0}
                ),
                'mongodb': TechnologyOption(
                    name='MongoDB',
                    category='database',
                    version='7.x',
                    pros=['Flexibilidad schema', 'Horizontal scaling', 'JSON nativo'],
                    cons=['Consistency trade-offs', 'Memory usage', 'Learning curve'],
                    learning_curve='medium',
                    community_support=8.5,
                    market_adoption=8.2,
                    future_viability=8.5,
                    cost_factor='free',
                    industry_fit=7.5,
                    scale_suitability={'startup': 8.5, 'smb': 8.0, 'enterprise': 8.5, 'global': 9.0}
                )
            },
            'infrastructure': {
                'aws': TechnologyOption(
                    name='Amazon Web Services',
                    category='infrastructure',
                    version='current',
                    pros=['Servicios completos', 'Escalabilidad', 'Reliability', 'Global presence'],
                    cons=['Complejidad', 'Costos variables', 'Vendor lock-in'],
                    learning_curve='high',
                    community_support=9.8,
                    market_adoption=9.5,
                    future_viability=9.5,
                    cost_factor='medium',
                    industry_fit=9.0,
                    scale_suitability={'startup': 8.0, 'smb': 8.5, 'enterprise': 9.8, 'global': 9.8}
                ),
                'gcp': TechnologyOption(
                    name='Google Cloud Platform',
                    category='infrastructure',
                    version='current',
                    pros=['AI/ML services', 'Kubernetes nativo', 'Pricing', 'Innovation'],
                    cons=['Menor ecosistema', 'Support limitations'],
                    learning_curve='medium',
                    community_support=8.5,
                    market_adoption=7.8,
                    future_viability=9.0,
                    cost_factor='medium',
                    industry_fit=8.5,
                    scale_suitability={'startup': 8.5, 'smb': 8.8, 'enterprise': 8.5, 'global': 8.8}
                ),
                'azure': TechnologyOption(
                    name='Microsoft Azure',
                    category='infrastructure',
                    version='current',
                    pros=['Enterprise integration', 'Hybrid cloud', '.NET optimization'],
                    cons=['Complejidad', 'Microsoft dependency'],
                    learning_curve='high',
                    community_support=8.8,
                    market_adoption=8.5,
                    future_viability=8.8,
                    cost_factor='medium',
                    industry_fit=9.2,
                    scale_suitability={'startup': 7.0, 'smb': 8.0, 'enterprise': 9.5, 'global': 9.2}
                ),
                'vercel': TechnologyOption(
                    name='Vercel + Serverless',
                    category='infrastructure',
                    version='current',
                    pros=['Deployment simple', 'Performance', 'Developer experience'],
                    cons=['Vendor lock-in', 'Costos escalamiento', 'Limitaciones'],
                    learning_curve='low',
                    community_support=8.0,
                    market_adoption=7.5,
                    future_viability=8.0,
                    cost_factor='low',
                    industry_fit=7.5,
                    scale_suitability={'startup': 9.5, 'smb': 8.5, 'enterprise': 6.5, 'global': 5.0}
                )
            }
        }
    
    def _initialize_industry_weights(self) -> Dict[str, Dict[str, float]]:
        """Pesos específicos por industria"""
        return {
            'healthcare': {
                'security': 10.0,
                'compliance': 10.0,
                'reliability': 9.5,
                'performance': 8.0,
                'cost': 7.0,
                'scalability': 8.5
            },
            'fintech': {
                'security': 10.0,
                'compliance': 10.0,
                'performance': 9.5,
                'reliability': 9.5,
                'cost': 7.5,
                'scalability': 9.0
            },
            'ecommerce': {
                'performance': 9.5,
                'scalability': 9.5,
                'reliability': 9.0,
                'cost': 8.5,
                'security': 8.5,
                'compliance': 7.0
            },
            'education': {
                'cost': 9.0,
                'scalability': 8.5,
                'reliability': 8.0,
                'performance': 8.0,
                'security': 8.5,
                'compliance': 8.0
            },
            'general': {
                'cost': 8.0,
                'performance': 8.0,
                'scalability': 8.0,
                'reliability': 8.0,
                'security': 8.0,
                'compliance': 7.0
            }
        }
    
    def _initialize_scale_factors(self) -> Dict[str, Dict[str, float]]:
        """Factores de escala"""
        return {
            'startup': {
                'speed_to_market': 10.0,
                'cost': 9.5,
                'learning_curve': 9.0,
                'team_size': 8.5,
                'flexibility': 9.0
            },
            'smb': {
                'cost': 8.5,
                'reliability': 8.5,
                'scalability': 8.0,
                'maintenance': 8.0,
                'team_growth': 8.5
            },
            'enterprise': {
                'reliability': 10.0,
                'scalability': 10.0,
                'security': 10.0,
                'compliance': 9.5,
                'integration': 9.5
            },
            'global': {
                'scalability': 10.0,
                'performance': 10.0,
                'reliability': 10.0,
                'global_presence': 10.0,
                'disaster_recovery': 9.5
            }
        }
    
    def _initialize_trend_multipliers(self) -> Dict[str, float]:
        """Multiplicadores de tendencias actuales"""
        return {
            'ai_integration': 1.3,
            'serverless': 1.2,
            'microservices': 1.15,
            'cloud_native': 1.25,
            'typescript': 1.2,
            'jamstack': 1.1,
            'edge_computing': 1.15,
            'container_orchestration': 1.2
        }
    
    def _determine_industry(self, context: Dict[str, Any]) -> str:
        """Determina la industria del proyecto"""
        industry_text = context.get('industry', '').lower()
        
        industry_keywords = {
            'healthcare': ['salud', 'health', 'medical', 'hospital', 'clinic'],
            'fintech': ['fintech', 'financial', 'banking', 'payment', 'finance'],
            'ecommerce': ['ecommerce', 'retail', 'shopping', 'marketplace'],
            'education': ['education', 'learning', 'school', 'university', 'course'],
            'logistics': ['logistics', 'shipping', 'delivery', 'supply']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in industry_text for keyword in keywords):
                return industry
        
        return 'general'
    
    def _determine_scale(self, context: Dict[str, Any]) -> str:
        """Determina la escala del proyecto"""
        scale_text = context.get('scale', '').lower()
        
        if any(term in scale_text for term in ['startup', 'pequeña', 'mvp']):
            return 'startup'
        elif any(term in scale_text for term in ['mediana', 'smb', 'medium']):
            return 'smb'
        elif any(term in scale_text for term in ['enterprise', 'grande', 'corporation']):
            return 'enterprise'
        elif any(term in scale_text for term in ['global', 'multinational', 'worldwide']):
            return 'global'
        
        return 'smb'  # Default
    
    def _extract_tech_trends(self, web_data: Dict[str, Any]) -> Dict[str, float]:
        """Extrae tendencias tecnológicas de datos web"""
        trends = {}
        
        if not web_data or not web_data.get('market_data'):
            # Tendencias por defecto basadas en conocimiento actual
            return {
                'ai_integration': 0.8,
                'cloud_native': 0.9,
                'typescript': 0.7,
                'serverless': 0.6,
                'microservices': 0.7
            }
        
        tech_trends = web_data['market_data'].get('technology_trends', [])
        
        # Analizar tendencias mencionadas
        trend_keywords = {
            'ai_integration': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'serverless': ['serverless', 'lambda', 'functions'],
            'microservices': ['microservices', 'microservice', 'distributed'],
            'cloud_native': ['cloud native', 'kubernetes', 'containers'],
            'typescript': ['typescript', 'type safety'],
            'jamstack': ['jamstack', 'static site', 'headless'],
            'edge_computing': ['edge computing', 'cdn', 'edge functions']
        }
        
        for trend_name, keywords in trend_keywords.items():
            score = 0.0
            for trend_text in tech_trends:
                trend_lower = trend_text.lower()
                if any(keyword in trend_lower for keyword in keywords):
                    score += 0.2
            trends[trend_name] = min(score, 1.0)
        
        return trends
    
    def _calculate_requirement_weights(self, requirements: List[TechRequirement]) -> Dict[str, float]:
        """Calcula pesos basados en requisitos específicos"""
        weights = {
            'performance': 0.0,
            'security': 0.0,
            'scalability': 0.0,
            'integration': 0.0,
            'cost': 0.0,
            'reliability': 0.0
        }
        
        priority_multipliers = {
            'critical': 3.0,
            'high': 2.0,
            'medium': 1.0,
            'low': 0.5
        }
        
        for req in requirements:
            category = req.category.lower()
            if category in weights:
                multiplier = priority_multipliers.get(req.priority.lower(), 1.0)
                weights[category] += req.impact_score * multiplier
        
        # Normalizar pesos
        max_weight = max(weights.values()) if weights.values() else 1.0
        if max_weight > 0:
            weights = {k: v / max_weight for k, v in weights.items()}
        
        return weights
    
    def _evaluate_frontend_options(self, industry: str, scale: str, 
                                 requirement_weights: Dict[str, float],
                                 trends: Dict[str, float]) -> List[Tuple[str, float]]:
        """Evalúa opciones de frontend"""
        options = []
        
        for tech_name, tech_option in self.tech_database['frontend'].items():
            score = self._calculate_technology_score(
                tech_option, industry, scale, requirement_weights, trends
            )
            options.append((tech_name, score))
        
        return sorted(options, key=lambda x: x[1], reverse=True)
    
    def _evaluate_backend_options(self, industry: str, scale: str,
                                requirement_weights: Dict[str, float],
                                trends: Dict[str, float]) -> List[Tuple[str, float]]:
        """Evalúa opciones de backend"""
        options = []
        
        for tech_name, tech_option in self.tech_database['backend'].items():
            score = self._calculate_technology_score(
                tech_option, industry, scale, requirement_weights, trends
            )
            options.append((tech_name, score))
        
        return sorted(options, key=lambda x: x[1], reverse=True)
    
    def _evaluate_database_options(self, industry: str, scale: str,
                                 requirement_weights: Dict[str, float],
                                 trends: Dict[str, float]) -> List[Tuple[str, float]]:
        """Evalúa opciones de base de datos"""
        options = []
        
        for tech_name, tech_option in self.tech_database['database'].items():
            score = self._calculate_technology_score(
                tech_option, industry, scale, requirement_weights, trends
            )
            options.append((tech_name, score))
        
        return sorted(options, key=lambda x: x[1], reverse=True)
    
    def _evaluate_infrastructure_options(self, industry: str, scale: str,
                                       requirement_weights: Dict[str, float],
                                       trends: Dict[str, float]) -> List[Tuple[str, float]]:
        """Evalúa opciones de infraestructura"""
        options = []
        
        for tech_name, tech_option in self.tech_database['infrastructure'].items():
            score = self._calculate_technology_score(
                tech_option, industry, scale, requirement_weights, trends
            )
            options.append((tech_name, score))
        
        return sorted(options, key=lambda x: x[1], reverse=True)
    
    def _calculate_technology_score(self, tech_option: TechnologyOption,
                                  industry: str, scale: str,
                                  requirement_weights: Dict[str, float],
                                  trends: Dict[str, float]) -> float:
        """Calcula score de una tecnología específica"""
        
        # Score base
        base_score = (
            tech_option.community_support * 0.2 +
            tech_option.market_adoption * 0.2 +
            tech_option.future_viability * 0.2 +
            tech_option.industry_fit * 0.2 +
            tech_option.scale_suitability.get(scale, 5.0) * 0.2
        )
        
        # Ajuste por industria
        industry_weights = self.industry_weights.get(industry, self.industry_weights['general'])
        industry_adjustment = 1.0
        
        # Ajuste por escala
        scale_factors = self.scale_factors.get(scale, self.scale_factors['smb'])
        scale_adjustment = 1.0
        
        # Ajuste por learning curve (favorece menor complejidad para startups)
        learning_curve_penalty = {
            'low': 1.0,
            'medium': 0.95 if scale == 'startup' else 1.0,
            'high': 0.85 if scale == 'startup' else 0.95
        }.get(tech_option.learning_curve, 1.0)
        
        # Ajuste por tendencias
        trend_boost = 1.0
        tech_name_lower = tech_option.name.lower()
        
        for trend, multiplier in self.trend_multipliers.items():
            trend_strength = trends.get(trend, 0.0)
            if self._tech_matches_trend(tech_name_lower, trend):
                trend_boost += (multiplier - 1.0) * trend_strength
        
        # Score final
        final_score = (
            base_score * 
            industry_adjustment * 
            scale_adjustment * 
            learning_curve_penalty * 
            trend_boost
        )
        
        return min(final_score, 10.0)  # Cap at 10
    
    def _tech_matches_trend(self, tech_name: str, trend: str) -> bool:
        """Verifica si una tecnología coincide con una tendencia"""
        trend_mappings = {
            'ai_integration': ['python', 'tensorflow', 'pytorch'],
            'serverless': ['vercel', 'netlify', 'lambda'],
            'microservices': ['golang', 'kubernetes', 'docker'],
            'cloud_native': ['kubernetes', 'docker', 'aws', 'gcp', 'azure'],
            'typescript': ['typescript', 'angular', 'nest'],
            'jamstack': ['react', 'vue', 'svelte', 'gatsby', 'next']
        }
        
        keywords = trend_mappings.get(trend, [])
        return any(keyword in tech_name for keyword in keywords)
    
    def _select_optimal_combination(self, frontend_options: List[Tuple[str, float]],
                                  backend_options: List[Tuple[str, float]],
                                  database_options: List[Tuple[str, float]],
                                  infrastructure_options: List[Tuple[str, float]],
                                  industry: str, scale: str,
                                  requirement_weights: Dict[str, float]) -> Dict[str, str]:
        """Selecciona la combinación óptima de tecnologías"""
        
        # Seleccionar top opciones
        frontend = frontend_options[0][0] if frontend_options else 'react'
        backend = backend_options[0][0] if backend_options else 'nodejs'
        database = database_options[0][0] if database_options else 'postgresql'
        infrastructure = infrastructure_options[0][0] if infrastructure_options else 'aws'
        
        # Verificar compatibilidades y ajustar si es necesario
        optimal_stack = {
            'frontend': frontend,
            'backend': backend,
            'database': database,
            'infrastructure': infrastructure
        }
        
        # Aplicar reglas de compatibilidad
        optimal_stack = self._apply_compatibility_rules(optimal_stack, scale)
        
        return optimal_stack
    
    def _apply_compatibility_rules(self, stack: Dict[str, str], scale: str) -> Dict[str, str]:
        """Aplica reglas de compatibilidad entre tecnologías"""
        
        # Regla: Para startups, preferir stacks simples
        if scale == 'startup':
            if stack['infrastructure'] in ['aws', 'azure'] and stack['backend'] in ['nodejs', 'python']:
                stack['infrastructure'] = 'vercel'  # Más simple para startups
        
        # Regla: Java + Azure es una buena combinación
        if stack['backend'] == 'java':
            if stack['infrastructure'] not in ['azure', 'aws']:
                stack['infrastructure'] = 'aws'  # Mejor soporte para Java
        
        # Regla: .NET + Azure
        if stack['backend'] == 'csharp':
            stack['infrastructure'] = 'azure'
        
        return stack
    
    def _build_recommendation(self, optimal_stack: Dict[str, str],
                            project_context: Dict[str, Any],
                            requirements: List[TechRequirement]) -> StackRecommendation:
        """Construye recomendación completa"""
        
        # Obtener objetos de tecnología
        frontend_tech = self.tech_database['frontend'][optimal_stack['frontend']]
        backend_tech = self.tech_database['backend'][optimal_stack['backend']]
        database_tech = self.tech_database['database'][optimal_stack['database']]
        infrastructure_tech = self.tech_database['infrastructure'][optimal_stack['infrastructure']]
        
        # Calcular score total
        total_score = (
            frontend_tech.market_adoption +
            backend_tech.market_adoption +
            database_tech.market_adoption +
            infrastructure_tech.market_adoption
        ) / 4.0
        
        # Generar justificación
        justification = self._generate_justification(optimal_stack, project_context, requirements)
        
        # Estimar costos y timeline
        estimated_cost = self._estimate_costs(optimal_stack)
        development_timeline = self._estimate_timeline(optimal_stack, project_context)
        
        # Requisitos de equipo
        team_requirements = self._calculate_team_requirements(optimal_stack)
        
        # Factores de riesgo
        risk_factors = self._identify_risk_factors(optimal_stack, requirements)
        
        # Path de migración
        migration_path = self._generate_migration_path(optimal_stack)
        
        return StackRecommendation(
            frontend=frontend_tech,
            backend=backend_tech,
            database=database_tech,
            infrastructure={'primary': infrastructure_tech},
            additional_tools={},
            total_score=total_score,
            justification=justification,
            estimated_cost=estimated_cost,
            development_timeline=development_timeline,
            team_requirements=team_requirements,
            risk_factors=risk_factors,
            migration_path=migration_path
        )
    
    def _generate_justification(self, stack: Dict[str, str],
                              context: Dict[str, Any],
                              requirements: List[TechRequirement]) -> str:
        """Genera justificación detallada del stack"""
        
        justifications = []
        
        # Frontend justification
        frontend = self.tech_database['frontend'][stack['frontend']]
        justifications.append(
            f"**Frontend ({frontend.name}):** Seleccionado por {', '.join(frontend.pros[:2])}. "
            f"Ideal para {context.get('scale', 'proyecto')} con learning curve {frontend.learning_curve}."
        )
        
        # Backend justification
        backend = self.tech_database['backend'][stack['backend']]
        justifications.append(
            f"**Backend ({backend.name}):** Elegido por {', '.join(backend.pros[:2])}. "
            f"Excelente para {context.get('industry', 'aplicaciones generales')}."
        )
        
        # Database justification
        database = self.tech_database['database'][stack['database']]
        justifications.append(
            f"**Database ({database.name}):** Recomendado por {', '.join(database.pros[:2])}. "
            f"Soporta los requisitos de escalabilidad del proyecto."
        )
        
        # Infrastructure justification
        infrastructure = self.tech_database['infrastructure'][stack['infrastructure']]
        justifications.append(
            f"**Infrastructure ({infrastructure.name}):** Seleccionado por {', '.join(infrastructure.pros[:2])}. "
            f"Apropiado para escala {context.get('scale', 'mediana')}."
        )
        
        return '\n\n'.join(justifications)
    
    def _estimate_costs(self, stack: Dict[str, str]) -> str:
        """Estima costos del stack"""
        cost_factors = []
        
        for category, tech_name in stack.items():
            if category in self.tech_database:
                tech = self.tech_database[category][tech_name]
                cost_factors.append(tech.cost_factor)
        
        if all(cost == 'free' for cost in cost_factors):
            return "$0-500/mes (solo infraestructura)"
        elif any(cost == 'high' for cost in cost_factors):
            return "$2000-5000/mes"
        elif any(cost == 'medium' for cost in cost_factors):
            return "$500-2000/mes"
        else:
            return "$100-500/mes"
    
    def _estimate_timeline(self, stack: Dict[str, str], context: Dict[str, Any]) -> str:
        """Estima timeline de desarrollo"""
        base_timeline = {
            'startup': "3-6 meses",
            'smb': "6-12 meses",
            'enterprise': "12-18 meses",
            'global': "18-24 meses"
        }
        
        scale = context.get('scale', 'smb')
        return base_timeline.get(scale, "6-12 meses")
    
    def _calculate_team_requirements(self, stack: Dict[str, str]) -> Dict[str, int]:
        """Calcula requisitos de equipo"""
        team = {
            'frontend_developers': 1,
            'backend_developers': 1,
            'devops_engineers': 1,
            'ui_ux_designers': 1
        }
        
        # Ajustar basado en complejidad del stack
        complex_techs = ['angular', 'java', 'golang']
        if any(tech in stack.values() for tech in complex_techs):
            team['senior_developers'] = 1
        
        return team
    
    def _identify_risk_factors(self, stack: Dict[str, str],
                             requirements: List[TechRequirement]) -> List[str]:
        """Identifica factores de riesgo"""
        risks = []
        
        # Riesgos por tecnología
        for category, tech_name in stack.items():
            if category in self.tech_database:
                tech = self.tech_database[category][tech_name]
                if tech.learning_curve == 'high':
                    risks.append(f"Curva de aprendizaje alta para {tech.name}")
                if tech.community_support < 8.0:
                    risks.append(f"Soporte de comunidad limitado para {tech.name}")
        
        # Riesgos por requisitos críticos
        critical_reqs = [req for req in requirements if req.priority == 'critical']
        if len(critical_reqs) > 3:
            risks.append("Múltiples requisitos críticos pueden aumentar complejidad")
        
        return risks
    
    def _generate_migration_path(self, stack: Dict[str, str]) -> List[str]:
        """Genera path de migración/implementación"""
        path = [
            "1. Setup de infraestructura base",
            "2. Configuración de base de datos",
            "3. Desarrollo de APIs backend",
            "4. Implementación de frontend",
            "5. Integración y testing",
            "6. Deployment y monitoreo"
        ]
        
        return path

# Función de utilidad para crear analizador
def create_tech_stack_analyzer() -> DynamicTechStackAnalyzer:
    """Crea una instancia del analizador de stack tecnológico"""
    return DynamicTechStackAnalyzer()