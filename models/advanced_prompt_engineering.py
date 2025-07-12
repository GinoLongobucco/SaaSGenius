import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PromptContext:
    """Contexto estructurado para generación de prompts"""
    role: str
    industry: str
    project_type: str
    user_problems: List[str]
    specific_features: List[str]
    target_users: str
    business_model: str
    scale: str
    web_search_data: Dict[str, Any]
    technical_requirements: List[str]

class AdvancedPromptEngineer:
    """Ingeniero de prompts avanzado para análisis de proyectos SaaS"""
    
    def __init__(self):
        self.role_templates = self._load_role_templates()
        self.industry_contexts = self._load_industry_contexts()
        self.analysis_frameworks = self._load_analysis_frameworks()
    
    def generate_market_analysis_prompt(self, context: PromptContext) -> str:
        """Genera prompt avanzado para análisis de mercado usando técnica PCT y Few-Shot"""
        
        # 1. PERSONA - Asignar rol específico y expertise
        persona = f"""Eres un analista de negocios senior especializado en startups de tecnología SaaS con 15+ años de experiencia. 
Tu expertise incluye análisis de mercado para la industria {context.industry}, evaluación de oportunidades de negocio, 
y estrategias go-to-market para productos digitales. Has trabajado con empresas desde startups hasta Fortune 500."""
        
        # 2. CONTEXTO - Información específica del proyecto
        contexto = f"""
Estoy analizando una idea de negocio SaaS. Los detalles del proyecto son:
- **Industria:** {context.industry}
- **Tipo de Proyecto:** {context.project_type}
- **Usuarios Objetivo:** {context.target_users}
- **Modelo de Negocio:** {context.business_model}
- **Escala Proyectada:** {context.scale}
- **Problemas que resuelve:** {', '.join(context.user_problems) if context.user_problems else 'No especificados'}
- **Características clave:** {', '.join(context.specific_features) if context.specific_features else 'No especificadas'}

**Datos de mercado actualizados:**
{self._format_web_insights(context.web_search_data)}"""
        
        # 3. TAREA - Instrucciones específicas con formato y ejemplos
        tarea = f"""
Basado en la información del proyecto, realiza un análisis de mercado detallado y específico. 
Tu respuesta DEBE seguir esta estructura JSON exacta:

{{
  "market_opportunity": {{
    "market_size": "Tamaño específico del mercado en USD con fuentes",
    "growth_rate": "Tasa de crecimiento anual con porcentaje específico",
    "target_segments": ["Segmento 1", "Segmento 2", "Segmento 3"],
    "unmet_needs": "Necesidades no cubiertas identificadas en el mercado"
  }},
  "competitive_analysis": {{
    "direct_competitors": ["Competidor 1", "Competidor 2", "Competidor 3"],
    "indirect_competitors": ["Alternativa 1", "Alternativa 2"],
    "competitive_gaps": "Oportunidades específicas no cubiertas por competidores",
    "differentiation_strategy": "Estrategia de diferenciación recomendada"
  }},
  "commercial_viability": {{
    "monetization_model": "Modelo de monetización óptimo (SaaS, freemium, etc.)",
    "pricing_strategy": "Rango de precios competitivo con justificación",
    "adoption_timeline": "Proyección de adopción en meses/años",
    "revenue_projections": "Proyecciones de ingresos para años 1-3"
  }},
  "market_trends": {{
    "technology_trends": ["Tendencia tech 1", "Tendencia tech 2"],
    "regulatory_factors": "Factores regulatorios relevantes",
    "consumer_behavior": "Cambios en comportamiento del consumidor"
  }},
  "strategic_recommendations": {{
    "go_to_market": "Estrategia específica de entrada al mercado",
    "feature_prioritization": ["Feature prioritaria 1", "Feature prioritaria 2"],
    "positioning_statement": "Declaración de posicionamiento en una frase",
    "success_metrics": ["Métrica 1", "Métrica 2", "Métrica 3"]
  }}
}}

**EJEMPLO de cómo analizarías 'una plataforma SaaS para gestión de inventario en restaurantes':**

{{
  "market_opportunity": {{
    "market_size": "$3.2B mercado global de software para restaurantes, creciendo 12% anual",
    "growth_rate": "12% CAGR impulsado por digitalización post-COVID",
    "target_segments": ["Restaurantes independientes (50-200 empleados)", "Cadenas regionales", "Food trucks y delivery-only"],
    "unmet_needs": "Integración real-time entre POS, inventario y proveedores con predicción de demanda"
  }},
  "competitive_analysis": {{
    "direct_competitors": ["Toast Inventory", "Resy Platform", "OpenTable Connect"],
    "indirect_competitors": ["Hojas de Excel", "QuickBooks", "Sistemas POS básicos"],
    "competitive_gaps": "Falta de predicción inteligente de inventario y automatización de pedidos",
    "differentiation_strategy": "IA predictiva + integración automática con proveedores + mobile-first"
  }},
  "commercial_viability": {{
    "monetization_model": "SaaS por ubicación: $89/mes base + $15/empleado adicional",
    "pricing_strategy": "$89-299/mes según tamaño, 30% menos que Toast para captar mercado",
    "adoption_timeline": "6-12 meses para PMF, 18-24 meses para escala regional",
    "revenue_projections": "Año 1: $240K, Año 2: $1.2M, Año 3: $4.8M ARR"
  }},
  "market_trends": {{
    "technology_trends": ["IA predictiva en F&B", "Integración IoT sensores", "Pagos contactless"],
    "regulatory_factors": "HACCP compliance, trazabilidad de alimentos, reportes fiscales",
    "consumer_behavior": "Mayor demanda de transparencia en ingredientes y sostenibilidad"
  }},
  "strategic_recommendations": {{
    "go_to_market": "Piloto con 10 restaurantes locales → partnerships con distribuidores → expansión regional",
    "feature_prioritization": ["Predicción de demanda con IA", "Integración POS", "App móvil para managers"],
    "positioning_statement": "La única plataforma que predice qué necesitas antes de que se agote",
    "success_metrics": ["Reducción 25% desperdicio", "Ahorro 15 horas/semana gestión", "ROI 300% primer año"]
  }}
}}

**INSTRUCCIONES CRÍTICAS:**
- Usa DATOS ESPECÍFICOS de los insights web proporcionados
- Incluye NÚMEROS y PORCENTAJES reales cuando sea posible
- Sé ESPECÍFICO sobre competidores, precios y métricas
- Evita generalidades - cada recomendación debe ser ACCIONABLE
- Basa las proyecciones en datos de mercado reales, no estimaciones vagas"""
        
        # Combine everything into the final prompt
        final_prompt = f"{persona}\n\n## CONTEXTO\n{contexto}\n\n## TAREA\n{tarea}"
        
        return final_prompt.strip()
    
    def generate_tech_stack_prompt(self, context: PromptContext) -> str:
        """Genera prompt avanzado para recomendación de stack tecnológico usando técnica PCT"""
        
        # 1. PERSONA - Arquitecto de software senior
        persona = f"""Eres un arquitecto de software senior con 12+ años de experiencia diseñando sistemas SaaS escalables. 
Tu especialidad incluye arquitecturas para la industria {context.industry}, optimización de performance, y selección de tecnologías 
basada en ROI y escalabilidad. Has liderado equipos técnicos en startups unicornio y empresas Fortune 100."""
        
        # 2. CONTEXTO - Información técnica del proyecto
        contexto = f"""
Necesito diseñar el stack tecnológico para un proyecto SaaS con estas características:
- **Industria:** {context.industry}
- **Tipo de Proyecto:** {context.project_type}
- **Escala Proyectada:** {context.scale}
- **Usuarios Concurrentes Estimados:** {self._estimate_concurrent_users(context.scale)}
- **Características Funcionales:** {', '.join(context.specific_features) if context.specific_features else 'No especificadas'}
- **Requisitos Técnicos:** {', '.join(context.technical_requirements) if context.technical_requirements else 'Estándar SaaS'}

**Tendencias tecnológicas actuales relevantes:**
{self._extract_tech_trends(context.web_search_data)}"""
        
        # 3. TAREA - Instrucciones específicas con formato JSON y ejemplo
        tarea = f"""
Diseña un stack tecnológico completo y justificado. Tu respuesta DEBE seguir esta estructura JSON exacta:

{{
  "architecture_pattern": {{
    "type": "Patrón arquitectónico recomendado",
    "justification": "Razón específica basada en escala y requisitos",
    "scalability_approach": "Estrategia de escalamiento"
  }},
  "frontend_stack": {{
    "framework": "Framework específico con versión",
    "ui_library": "Librería de componentes recomendada",
    "state_management": "Solución de manejo de estado",
    "build_tools": ["Tool 1", "Tool 2"],
    "justification": "Razón técnica para estas elecciones"
  }},
  "backend_stack": {{
    "language": "Lenguaje de programación",
    "framework": "Framework específico con versión",
    "api_design": "Estilo de API (REST, GraphQL, etc.)",
    "authentication": "Solución de autenticación",
    "justification": "Razón basada en performance y ecosistema"
  }},
  "database_storage": {{
    "primary_database": "Motor de BD principal con versión",
    "caching_layer": "Solución de caching",
    "file_storage": "Solución para archivos",
    "backup_strategy": "Estrategia de respaldo",
    "justification": "Razón para elección de BD y estrategia"
  }},
  "infrastructure_devops": {{
    "cloud_provider": "Proveedor cloud recomendado",
    "containerization": "Docker/Kubernetes strategy",
    "ci_cd_pipeline": "Herramientas específicas de CI/CD",
    "monitoring": "Stack de monitoreo y observabilidad",
    "estimated_monthly_cost": "Costo estimado mensual para escala inicial"
  }},
  "security_compliance": {{
    "auth_framework": "Framework de autenticación/autorización",
    "data_encryption": "Estrategia de encriptación",
    "compliance_requirements": ["Req 1", "Req 2"],
    "security_tools": ["Tool 1", "Tool 2"]
  }},
  "performance_optimization": {{
    "load_balancing": "Estrategia de load balancing",
    "cdn_strategy": "CDN recomendado",
    "performance_targets": "Métricas objetivo (latencia, throughput)",
    "optimization_techniques": ["Técnica 1", "Técnica 2"]
  }},
  "development_considerations": {{
    "team_size_recommendation": "Tamaño de equipo recomendado",
    "development_timeline": "Timeline estimado para MVP",
    "talent_availability": "Disponibilidad de desarrolladores",
    "learning_curve": "Curva de aprendizaje del stack"
  }}
}}

**EJEMPLO para 'plataforma SaaS de gestión de proyectos para equipos remotos (escala: 10K usuarios)':**

{{
  "architecture_pattern": {{
    "type": "Microservicios con API Gateway",
    "justification": "Permite escalamiento independiente de módulos (chat, files, analytics) y facilita desarrollo en equipo",
    "scalability_approach": "Horizontal scaling con load balancers y auto-scaling groups"
  }},
  "frontend_stack": {{
    "framework": "React 18.2 con TypeScript",
    "ui_library": "Chakra UI para componentes consistentes",
    "state_management": "Zustand para estado global + React Query para server state",
    "build_tools": ["Vite", "ESLint", "Prettier"],
    "justification": "React tiene el mejor ecosistema para SaaS, TypeScript reduce bugs, Vite es más rápido que Webpack"
  }},
  "backend_stack": {{
    "language": "Node.js con TypeScript",
    "framework": "Fastify 4.x para mejor performance que Express",
    "api_design": "REST APIs + WebSockets para real-time features",
    "authentication": "Auth0 para OAuth + JWT tokens",
    "justification": "Node.js permite compartir código con frontend, Fastify es 2x más rápido que Express"
  }},
  "database_storage": {{
    "primary_database": "PostgreSQL 15 para datos relacionales",
    "caching_layer": "Redis 7.x para sessions y cache",
    "file_storage": "AWS S3 con CloudFront CDN",
    "backup_strategy": "Automated daily backups + point-in-time recovery",
    "justification": "PostgreSQL maneja JSON + relacional, Redis es estándar para cache, S3 es cost-effective"
  }},
  "infrastructure_devops": {{
    "cloud_provider": "AWS (mejor ecosistema para startups)",
    "containerization": "Docker + ECS Fargate (serverless containers)",
    "ci_cd_pipeline": "GitHub Actions + AWS CodeDeploy",
    "monitoring": "DataDog para APM + AWS CloudWatch para infraestructura",
    "estimated_monthly_cost": "$800-1200/mes para 10K usuarios activos"
  }},
  "security_compliance": {{
    "auth_framework": "Auth0 + RBAC (Role-Based Access Control)",
    "data_encryption": "AES-256 en reposo + TLS 1.3 en tránsito",
    "compliance_requirements": ["SOC 2 Type II", "GDPR"],
    "security_tools": ["Snyk para vulnerabilidades", "AWS WAF"]
  }},
  "performance_optimization": {{
    "load_balancing": "AWS Application Load Balancer con health checks",
    "cdn_strategy": "CloudFront para assets estáticos + edge caching",
    "performance_targets": "<200ms API response, <2s page load, 99.9% uptime",
    "optimization_techniques": ["Database indexing", "Query optimization", "Image compression"]
  }},
  "development_considerations": {{
    "team_size_recommendation": "4-6 developers (2 frontend, 2 backend, 1 DevOps, 1 full-stack)",
    "development_timeline": "4-6 meses para MVP con features core",
    "talent_availability": "Alta - React/Node.js tienen gran pool de desarrolladores",
    "learning_curve": "Moderada - stack familiar pero requiere conocimiento de microservicios"
  }}
}}

**INSTRUCCIONES CRÍTICAS:**
- Usa tecnologías ESPECÍFICAS con versiones cuando sea relevante
- Justifica CADA elección técnica con razones concretas
- Incluye costos estimados realistas
- Considera la disponibilidad de talento en el mercado
- Basa las recomendaciones en las tendencias tech actuales proporcionadas
- Sé específico sobre métricas de performance y SLAs"""
        
        # Combine everything into the final prompt
        final_prompt = f"{persona}\n\n## CONTEXTO\n{contexto}\n\n## TAREA\n{tarea}"
        
        return final_prompt.strip()
    
    def generate_executive_summary_prompt(self, context: PromptContext) -> str:
        """Genera prompt avanzado para resumen ejecutivo usando técnicas PCT y Few-Shot"""
        
        # 1. PERSONA - Consultor de negocios senior especializado
        persona = f"""Eres un consultor de negocios senior con MBA de Wharton y 15+ años de experiencia en startups SaaS. 
Has ayudado a más de 200 startups a conseguir $500M+ en financiación total y has sido mentor en Y Combinator, Techstars y 500 Startups. 
Tu especialidad incluye análisis de mercado para la industria {context.industry}, business model design, y estrategias de go-to-market."""
        
        # 2. CONTEXTO - Información específica y estructurada del proyecto
        contexto = f"""
INFORMACIÓN DEL PROYECTO:
- **Industria:** {context.industry}
- **Tipo de Proyecto:** {context.project_type}
- **Usuarios Objetivo:** {context.target_users}
- **Modelo de Negocio:** {context.business_model}
- **Escala Proyectada:** {context.scale}
- **Problemas que resuelve:** {', '.join(context.user_problems) if context.user_problems else 'No especificados'}
- **Características clave:** {', '.join(context.specific_features) if context.specific_features else 'No especificadas'}

**INTELIGENCIA DE MERCADO ACTUALIZADA:**
{self._extract_market_insights(context.web_search_data)}

**CONTEXTO COMPETITIVO:**
{self._format_web_insights(context.web_search_data)}"""
        
        # 3. TAREA - Instrucciones específicas con formato JSON y ejemplo
        tarea = f"""
TAREA: Crea un resumen ejecutivo estratégico que siga EXACTAMENTE esta estructura JSON:

{{
  "executive_summary": {{
    "value_proposition": "Propuesta de valor única en 1-2 oraciones que destaque el problema específico y la solución",
    "market_opportunity": {{
      "target_market": "Descripción específica del mercado objetivo con demografía",
      "market_size": "Tamaño de mercado TAM/SAM/SOM con fuentes",
      "growth_drivers": ["Driver 1", "Driver 2", "Driver 3"],
      "urgency_factors": "Por qué es urgente resolver este problema ahora"
    }},
    "business_model": {{
      "revenue_streams": ["Stream 1 con pricing", "Stream 2 con pricing"],
      "unit_economics": "CAC, LTV, y payback period estimados",
      "scalability_model": "Cómo el negocio escala operacional y financieramente",
      "monetization_timeline": "Timeline para alcanzar rentabilidad"
    }},
    "competitive_advantages": {{
      "core_differentiators": ["Diferenciador 1", "Diferenciador 2", "Diferenciador 3"],
      "barriers_to_entry": "Barreras que protegen la ventaja competitiva",
      "intellectual_property": "IP, patents, o know-how propietario",
      "network_effects": "Efectos de red o switching costs"
    }},
    "financial_projections": {{
      "revenue_forecast": "Proyección de ingresos años 1-3 con assumptions",
      "funding_requirements": "Capital necesario y uso de fondos",
      "key_metrics": "Métricas clave de éxito (ARR, churn, etc.)",
      "break_even_timeline": "Timeline para break-even y cash flow positivo"
    }},
    "execution_roadmap": {{
      "critical_milestones": ["Hito 1 (timeline)", "Hito 2 (timeline)", "Hito 3 (timeline)"],
      "go_to_market_strategy": "Estrategia específica de entrada al mercado",
      "team_requirements": "Roles clave necesarios para ejecución",
      "success_metrics": ["Métrica 1", "Métrica 2", "Métrica 3"]
    }},
    "risk_assessment": {{
      "primary_risks": ["Riesgo 1", "Riesgo 2", "Riesgo 3"],
      "mitigation_strategies": ["Estrategia 1", "Estrategia 2", "Estrategia 3"],
      "contingency_plans": "Planes B para riesgos críticos",
      "success_factors": "Factores críticos que determinan el éxito"
    }}
  }}
}}

**EJEMPLO para 'plataforma SaaS de gestión de inventario para restaurantes':**

{{
  "executive_summary": {{
    "value_proposition": "Plataforma SaaS que reduce el desperdicio de alimentos en restaurantes hasta un 35% mediante IA predictiva y automatización de inventario, generando ahorros promedio de $2,400/mes por ubicación.",
    "market_opportunity": {{
      "target_market": "Restaurantes independientes y cadenas regionales (50-500 empleados) en mercados urbanos de LATAM",
      "market_size": "TAM: $8.2B (software restaurantes LATAM), SAM: $1.8B (gestión inventario), SOM: $180M (target específico)",
      "growth_drivers": ["Digitalización post-COVID", "Presión en márgenes", "Regulaciones de desperdicio"],
      "urgency_factors": "Inflación de alimentos del 15% anual hace crítico el control de inventario para supervivencia"
    }},
    "business_model": {{
      "revenue_streams": ["SaaS subscription $149-499/mes por ubicación", "Marketplace comisiones 2% en pedidos automatizados"],
      "unit_economics": "CAC: $450, LTV: $4,200, Payback: 8 meses, LTV/CAC: 9.3x",
      "scalability_model": "Multi-tenant SaaS con costos marginales <5%, expansión geográfica y vertical",
      "monetization_timeline": "Break-even operacional mes 18, cash flow positivo mes 24"
    }},
    "competitive_advantages": {{
      "core_differentiators": ["IA predictiva propietaria con 94% precisión", "Integración nativa con 80+ proveedores LATAM", "ROI demostrable en 90 días"],
      "barriers_to_entry": "Dataset propietario de patrones de consumo, partnerships exclusivos con distribuidores",
      "intellectual_property": "Algoritmos de predicción de demanda, base de datos de productos LATAM",
      "network_effects": "Más restaurantes = mejor predicción, switching cost alto por integración profunda"
    }},
    "financial_projections": {{
      "revenue_forecast": "Año 1: $180K, Año 2: $1.2M, Año 3: $4.8M ARR (assumptions: 50 clientes Y1, 300 Y2, 800 Y3)",
      "funding_requirements": "$800K semilla para desarrollo + $2.5M Serie A para expansión regional",
      "key_metrics": "ARR growth 300%+, Net churn <5%, NPS >50, Gross margin >85%",
      "break_even_timeline": "Unit economics positivas mes 8, break-even operacional mes 18"
    }},
    "execution_roadmap": {{
      "critical_milestones": ["MVP + 10 pilotos (mes 6)", "Product-market fit + $500K ARR (mes 12)", "Expansión regional + $2M ARR (mes 24)"],
      "go_to_market_strategy": "Ventas directas a restaurantes premium → partnerships con consultores F&B → marketplace de distribuidores",
      "team_requirements": "CTO (IA/ML), VP Sales (F&B experience), Customer Success Manager, 4 developers",
      "success_metrics": ["35% reducción desperdicio promedio", "$2,400 ahorro mensual por cliente", "<3 meses time-to-value"]
    }},
    "risk_assessment": {{
      "primary_risks": ["Resistencia al cambio en industria tradicional", "Competencia de incumbentes (Toast, Resy)", "Dependencia de integraciones con proveedores"],
      "mitigation_strategies": ["Programa de change management y training", "Diferenciación por IA y ROI superior", "Partnerships estratégicos y APIs abiertas"],
      "contingency_plans": "Pivot a consultores F&B si adopción lenta, expansión vertical a hoteles si saturación",
      "success_factors": "Calidad de predicción IA, velocidad de onboarding, partnerships estratégicos"
    }}
  }}
}}

**INSTRUCCIONES CRÍTICAS:**
- Usa DATOS ESPECÍFICOS de los market insights proporcionados
- Incluye NÚMEROS y MÉTRICAS concretas en cada sección
- Basa las proyecciones en benchmarks de industria reales
- Cada recomendación debe ser ESPECÍFICA y ACCIONABLE
- El JSON debe ser válido y seguir exactamente la estructura
- Evita generalidades - sé específico sobre competidores, precios, timelines

**RESPUESTA:** Devuelve ÚNICAMENTE el JSON válido, sin texto adicional antes o después."""
        
        # Combine everything into the final prompt
        final_prompt = f"{persona}\n\n## CONTEXTO\n{contexto}\n\n## TAREA\n{tarea}"
        
        return final_prompt.strip()
    
    def generate_roadmap_prompt(self, context: PromptContext) -> str:
        """Genera prompt avanzado para roadmap de desarrollo"""
        
        role_context = self._get_role_context('product_manager', context.industry)
        
        prompt = f"""
{role_context}

## CONTEXTO DEL PRODUCTO
**Tipo de Proyecto:** {context.project_type}
**Industria:** {context.industry}
**Usuarios Objetivo:** {context.target_users}
**Escala:** {context.scale}

## CARACTERÍSTICAS IDENTIFICADAS
{self._format_features_for_roadmap(context.specific_features)}

## PROBLEMAS A RESOLVER
{self._format_problems_for_roadmap(context.user_problems)}

## FRAMEWORK DE ROADMAP
{self._get_analysis_framework('product_roadmap')}

## INSTRUCCIONES PARA ROADMAP DE DESARROLLO

Crea un roadmap de desarrollo DETALLADO y PRIORIZADO que incluya:

1. **Análisis de Priorización:**
   - Framework de priorización (RICE, MoSCoW, etc.)
   - Criterios de evaluación específicos
   - Matriz de impacto vs esfuerzo
   - Dependencies y prerequisitos

2. **Fase 1 - MVP (Meses 1-3):**
   - Core features mínimas viables
   - Criterios de éxito específicos
   - Métricas de validación
   - User stories prioritarias

3. **Fase 2 - Product-Market Fit (Meses 4-8):**
   - Features de diferenciación
   - Optimizaciones basadas en feedback
   - Escalabilidad inicial
   - Métricas de engagement

4. **Fase 3 - Escalamiento (Meses 9-18):**
   - Features avanzadas
   - Integraciones estratégicas
   - Optimización de performance
   - Expansión de mercado

5. **Consideraciones Técnicas:**
   - Debt técnico y refactoring
   - Arquitectura y escalabilidad
   - Security y compliance
   - Testing y quality assurance

6. **Recursos y Timeline:**
   - Estimaciones de esfuerzo
   - Roles y skills requeridos
   - Dependencias externas
   - Riesgos y contingencias

7. **Métricas y KPIs:**
   - Métricas de producto por fase
   - Business metrics
   - Technical metrics
   - User satisfaction metrics

**FORMATO:** Organiza en fases claras con timelines específicos, estimaciones de esfuerzo, y criterios de éxito medibles.
"""
        
        return prompt.strip()
    
    def _load_role_templates(self) -> Dict[str, Dict[str, str]]:
        """Carga plantillas de roles especializados"""
        return {
            'market_analyst': {
                'general': "Eres un analista de mercado senior especializado en SaaS con 15+ años de experiencia. Tu expertise incluye análisis competitivo, sizing de mercado, y estrategias go-to-market. Tienes acceso a datos de mercado actualizados y herramientas de business intelligence.",
                'salud': "Eres un analista de mercado especializado en HealthTech con profundo conocimiento de regulaciones HIPAA, tendencias de telemedicina, y el ecosistema de salud digital. Has trabajado con startups y enterprises en el sector salud.",
                'finanzas': "Eres un analista de mercado FinTech con expertise en regulaciones financieras, compliance, y tendencias de digital banking. Conoces profundamente el ecosistema de pagos, lending, y wealth management.",
                'educación': "Eres un analista de mercado EdTech con experiencia en instituciones educativas, plataformas de e-learning, y tecnologías educativas. Entiendes las necesidades específicas de estudiantes, profesores y administradores."
            },
            'tech_architect': {
                'general': "Eres un arquitecto de software senior con 12+ años diseñando sistemas escalables. Tu expertise incluye microservicios, cloud architecture, y DevOps. Has liderado la arquitectura de múltiples productos SaaS exitosos.",
                'salud': "Eres un arquitecto de software especializado en sistemas de salud con profundo conocimiento de HIPAA compliance, interoperabilidad HL7/FHIR, y security en healthcare. Has diseñado sistemas críticos para hospitales y clínicas.",
                'finanzas': "Eres un arquitecto de software FinTech con expertise en sistemas de alta disponibilidad, PCI compliance, y arquitecturas de trading. Has trabajado en bancos y fintech de alto volumen transaccional."
            },
            'business_analyst': {
                'general': "Eres un analista de negocios senior con MBA y 10+ años en consultoría estratégica. Tu expertise incluye business model design, financial modeling, y strategic planning para startups y enterprises.",
                'salud': "Eres un consultor de negocios especializado en healthcare con profundo entendimiento de los modelos de reembolso, value-based care, y la economía de la salud digital.",
                'finanzas': "Eres un consultor de negocios FinTech con expertise en modelos de monetización financiera, risk management, y regulatory compliance. Has trabajado con bancos digitales y fintechs."
            },
            'product_manager': {
                'general': "Eres un Product Manager senior con 8+ años liderando productos SaaS. Tu expertise incluye product strategy, roadmap planning, y user experience design. Has lanzado múltiples productos exitosos al mercado.",
                'salud': "Eres un Product Manager especializado en productos de salud digital con profundo entendimiento de workflows clínicos, user experience para profesionales de salud, y patient engagement.",
                'finanzas': "Eres un Product Manager FinTech con expertise en productos financieros digitales, user experience en finanzas, y compliance de productos financieros."
            }
        }
    
    def _load_industry_contexts(self) -> Dict[str, str]:
        """Carga contextos específicos por industria"""
        return {
            'salud': "Contexto de salud digital: regulaciones HIPAA/GDPR, interoperabilidad, workflows clínicos, patient engagement, telemedicina, EHR integration.",
            'finanzas': "Contexto FinTech: regulaciones PCI/SOX, compliance bancario, KYC/AML, open banking, digital payments, risk management.",
            'educación': "Contexto EdTech: FERPA compliance, LMS integration, student engagement, assessment tools, accessibility, institutional workflows.",
            'retail': "Contexto RetailTech: omnichannel experience, inventory management, customer analytics, POS integration, supply chain.",
            'logística': "Contexto LogisticsTech: supply chain optimization, tracking systems, warehouse management, last-mile delivery, IoT integration."
        }
    
    def _load_analysis_frameworks(self) -> Dict[str, str]:
        """Carga frameworks de análisis estructurados"""
        return {
            'market_analysis': """
**FRAMEWORK DE ANÁLISIS DE MERCADO:**
- TAM/SAM/SOM Analysis
- Porter's Five Forces
- SWOT Analysis
- Competitive Positioning Map
- Market Segmentation Matrix
- Growth Vector Analysis
""",
            'tech_architecture': """
**FRAMEWORK DE ARQUITECTURA TÉCNICA:**
- Quality Attributes (Performance, Security, Scalability)
- Architecture Decision Records (ADRs)
- Technology Radar Assessment
- Risk-Driven Architecture
- Cost-Benefit Analysis
- Future-Proofing Evaluation
""",
            'executive_summary': """
**FRAMEWORK EJECUTIVO:**
- Problem-Solution Fit
- Market-Product Fit
- Business Model Canvas
- Financial Projections Model
- Risk Assessment Matrix
- Strategic Options Analysis
""",
            'product_roadmap': """
**FRAMEWORK DE ROADMAP:**
- RICE Prioritization (Reach, Impact, Confidence, Effort)
- Kano Model (Must-have, Performance, Delight)
- Story Mapping
- Dependency Analysis
- Risk-Adjusted Timeline
- Success Metrics Definition
"""
        }
    
    def _get_analysis_framework(self, framework_type: str) -> str:
        """Obtiene un framework de análisis específico"""
        return self.analysis_frameworks.get(framework_type, f"**Framework {framework_type}:** No disponible")
    
    def _get_role_context(self, role: str, industry: str) -> str:
        """Obtiene contexto específico del rol e industria"""
        role_template = self.role_templates.get(role, {}).get(industry) or self.role_templates.get(role, {}).get('general', '')
        industry_context = self.industry_contexts.get(industry, '')
        
        return f"**ROL Y EXPERTISE:**\n{role_template}\n\n**CONTEXTO DE INDUSTRIA:**\n{industry_context}"
    
    def _format_web_insights(self, web_data: Dict[str, Any]) -> str:
        """Formatea insights de búsqueda web"""
        if not web_data or not web_data.get('market_data'):
            return "**Datos de mercado:** No disponibles - usar conocimiento base y análisis cualitativo."
        
        market_data = web_data['market_data']
        insights = []
        
        if market_data.get('market_insights'):
            insights.append("**Market Insights:**")
            for insight in market_data['market_insights'][:3]:
                insights.append(f"- {insight.get('insight', '')}")
        
        if market_data.get('growth_indicators'):
            insights.append("\n**Growth Indicators:**")
            for indicator in market_data['growth_indicators'][:3]:
                insights.append(f"- {indicator}")
        
        if market_data.get('technology_trends'):
            insights.append("\n**Technology Trends:**")
            for trend in market_data['technology_trends'][:3]:
                insights.append(f"- {trend}")
        
        confidence = web_data.get('confidence_score', 0)
        insights.append(f"\n**Confianza de datos:** {confidence:.1%}")
        
        return '\n'.join(insights) if insights else "**Datos de mercado:** Análisis basado en conocimiento general."
    
    def _format_problems(self, problems: List[str]) -> str:
        """Formatea problemas identificados"""
        if not problems:
            return "**Problemas:** No especificados - inferir de descripción general."
        
        formatted = []
        for i, problem in enumerate(problems, 1):
            formatted.append(f"{i}. {problem.strip()}")
        
        return '\n'.join(formatted)
    
    def _format_features(self, features: List[str]) -> str:
        """Formatea características técnicas"""
        if not features:
            return "**Características:** No especificadas - recomendar stack estándar SaaS."
        
        formatted = []
        for feature in features:
            formatted.append(f"- {feature}")
        
        return '\n'.join(formatted)
    
    def _format_technical_requirements(self, requirements: List[str]) -> str:
        """Formatea requisitos técnicos"""
        if not requirements:
            return "**Requisitos técnicos:** Estándar SaaS - escalabilidad, seguridad, performance."
        
        formatted = []
        for req in requirements:
            formatted.append(f"- {req}")
        
        return '\n'.join(formatted)
    
    def _extract_tech_trends(self, web_data: Dict[str, Any]) -> str:
        """Extrae tendencias tecnológicas de datos web"""
        if not web_data or not web_data.get('market_data'):
            return "**Tendencias tech:** Cloud-native, AI/ML integration, microservices, serverless."
        
        trends = web_data['market_data'].get('technology_trends', [])
        if trends:
            return "**Tendencias actuales:**\n" + '\n'.join([f"- {trend}" for trend in trends[:5]])
        
        return "**Tendencias tech:** Datos no disponibles - usar mejores prácticas actuales."
    
    def _extract_market_insights(self, web_data: Dict[str, Any]) -> str:
        """Extrae insights de mercado de datos web"""
        if not web_data or not web_data.get('market_data'):
            return "**Inteligencia de mercado:** Análisis basado en conocimiento general del sector."
        
        market_data = web_data['market_data']
        insights = []
        
        if market_data.get('market_insights'):
            insights.extend([insight.get('insight', '') for insight in market_data['market_insights'][:3]])
        
        if market_data.get('competitive_landscape'):
            insights.extend(market_data['competitive_landscape'][:2])
        
        if insights:
            return "**Inteligencia de mercado:**\n" + '\n'.join([f"- {insight}" for insight in insights])
        
        return "**Inteligencia de mercado:** Datos limitados - análisis cualitativo recomendado."
    
    def _estimate_concurrent_users(self, scale: str) -> str:
        """Estima usuarios concurrentes basado en escala"""
        scale_mapping = {
            'pequeña': '100-1,000',
            'mediana': '1,000-10,000',
            'grande': '10,000-100,000',
            'enterprise': '100,000+'
        }
        
        for key, value in scale_mapping.items():
            if key in scale.lower():
                return value
        
        return '1,000-5,000'  # Default
    
    def _format_business_problems(self, problems: List[str]) -> str:
        """Formatea problemas desde perspectiva de negocio"""
        if not problems:
            return "**Problemas de negocio:** Eficiencia operacional, reducción de costos, mejora de productividad."
        
        formatted = []
        for i, problem in enumerate(problems, 1):
            # Enfocar en impacto de negocio
            business_impact = self._translate_to_business_impact(problem)
            formatted.append(f"{i}. {business_impact}")
        
        return '\n'.join(formatted)
    
    def _translate_to_business_impact(self, problem: str) -> str:
        """Traduce problema técnico a impacto de negocio"""
        # Mapeo simple de problemas técnicos a impacto de negocio
        if 'tiempo' in problem.lower() or 'lento' in problem.lower():
            return f"{problem} → Impacto: Pérdida de productividad y costos operacionales elevados"
        elif 'manual' in problem.lower() or 'automati' in problem.lower():
            return f"{problem} → Impacto: Ineficiencia operacional y errores humanos"
        elif 'integra' in problem.lower():
            return f"{problem} → Impacto: Silos de información y decisiones subóptimas"
        else:
            return f"{problem} → Impacto: Reducción de competitividad y satisfacción del cliente"
    
    def _format_solution_overview(self, features: List[str]) -> str:
        """Formatea overview de la solución"""
        if not features:
            return "**Solución:** Plataforma SaaS integral para optimización de procesos empresariales."
        
        # Agrupar features por categoría
        categories = {
            'Core': [],
            'Analytics': [],
            'Integration': [],
            'Advanced': []
        }
        
        for feature in features:
            feature_lower = feature.lower()
            if any(term in feature_lower for term in ['dashboard', 'usuario', 'auth']):
                categories['Core'].append(feature)
            elif any(term in feature_lower for term in ['analytic', 'report', 'metric']):
                categories['Analytics'].append(feature)
            elif any(term in feature_lower for term in ['api', 'integra', 'webhook']):
                categories['Integration'].append(feature)
            else:
                categories['Advanced'].append(feature)
        
        solution_parts = []
        for category, items in categories.items():
            if items:
                solution_parts.append(f"**{category}:** {', '.join(items)}")
        
        return '\n'.join(solution_parts) if solution_parts else "**Solución:** Plataforma SaaS personalizada."
    
    def _format_features_for_roadmap(self, features: List[str]) -> str:
        """Formatea características para roadmap"""
        if not features:
            return "**Características:** Core SaaS features - auth, dashboard, basic analytics."
        
        # Categorizar por complejidad para roadmap
        complexity_map = {
            'MVP': [],
            'Standard': [],
            'Advanced': []
        }
        
        for feature in features:
            feature_lower = feature.lower()
            if any(term in feature_lower for term in ['auth', 'login', 'usuario', 'dashboard']):
                complexity_map['MVP'].append(feature)
            elif any(term in feature_lower for term in ['api', 'integra', 'report', 'analytic']):
                complexity_map['Standard'].append(feature)
            else:
                complexity_map['Advanced'].append(feature)
        
        formatted = []
        for complexity, items in complexity_map.items():
            if items:
                formatted.append(f"**{complexity}:** {', '.join(items)}")
        
        return '\n'.join(formatted)
    
    def _format_problems_for_roadmap(self, problems: List[str]) -> str:
        """Formatea problemas para roadmap con priorización"""
        if not problems:
            return "**Problemas a resolver:** Eficiencia, automatización, escalabilidad."
        
        formatted = []
        for i, problem in enumerate(problems, 1):
            priority = 'Alta' if i <= 2 else 'Media'
            formatted.append(f"**P{i} ({priority}):** {problem.strip()}")
        
        return '\n'.join(formatted)