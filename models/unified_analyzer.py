# Unified SaaS Analyzer - Final Optimized Version
import os
import logging
import time
from typing import Dict, Any, List, Optional, Union
import json
import re
from dataclasses import dataclass
from functools import wraps

# Imports for different analysis backends (lazy loading)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("Groq no disponible")

# Other imports will be done on demand to avoid loading TensorFlow at startup
TRANSFORMERS_AVAILABLE = False
SPACY_AVAILABLE = False
KEYBERT_AVAILABLE = False

def _check_transformers():
    """Verifica si transformers está disponible"""
    global TRANSFORMERS_AVAILABLE
    if not TRANSFORMERS_AVAILABLE:
        try:
            import transformers
            import torch
            TRANSFORMERS_AVAILABLE = True
        except ImportError:
            TRANSFORMERS_AVAILABLE = False
            logging.warning("Transformers no disponible")
    return TRANSFORMERS_AVAILABLE

def _check_spacy():
    """Verifica si spaCy está disponible"""
    global SPACY_AVAILABLE
    if not SPACY_AVAILABLE:
        try:
            import spacy
            SPACY_AVAILABLE = True
        except ImportError:
            SPACY_AVAILABLE = False
            logging.warning("spaCy no disponible")
    return SPACY_AVAILABLE

def _check_keybert():
    """Verifica si KeyBERT está disponible"""
    global KEYBERT_AVAILABLE
    if not KEYBERT_AVAILABLE:
        try:
            from keybert import KeyBERT
            KEYBERT_AVAILABLE = True
        except ImportError:
            KEYBERT_AVAILABLE = False
            logging.warning("KeyBERT no disponible")
    return KEYBERT_AVAILABLE

# Local imports
from app.utils.cache_manager import cached_analysis
from app.utils.monitoring import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuración para el análisis unificado"""
    use_groq: bool = True
    use_transformers: bool = False  # Disabled by default to avoid startup issues
    use_spacy: bool = False  # Disabled by default to avoid startup issues
    use_keybert: bool = False  # Disabled by default to avoid startup issues
    groq_model: str = "llama-3.1-70b-versatile"
    max_tokens: int = 2000
    temperature: float = 0.3
    cache_ttl: int = 1800  # 30 minutos
    enable_monitoring: bool = True

class UnifiedSaaSAnalyzer:
    """Analizador unificado que combina múltiples backends de IA"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.groq_client = None
        self.sentiment_pipeline = None
        self.summarizer_pipeline = None
        self.nlp = None
        self.keybert_model = None
        
        # Configure logging first
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize available backends
        self._initialize_backends()
        
    def _initialize_backends(self):
        """Inicializa los diferentes backends de análisis con lazy loading"""
        # Initialize only Groq API immediately (lightweight)
        if GROQ_AVAILABLE and self.config.use_groq:
            try:
                groq_api_key = os.getenv('GROQ_API_KEY')
                if groq_api_key:
                    self.groq_client = Groq(api_key=groq_api_key)
                    self.logger.info("Groq API inicializado")
                else:
                    self.logger.warning("GROQ_API_KEY no encontrada")
            except Exception as e:
                self.logger.error(f"Error inicializando Groq: {e}")
        
        # Other backends will be initialized on demand
        self.logger.info("Backends configurados para lazy loading")
    
    def _ensure_transformers_loaded(self):
        """Carga los pipelines de Transformers bajo demanda"""
        if _check_transformers() and self.config.use_transformers and not self.sentiment_pipeline:
            try:
                from transformers import pipeline
                self.logger.info("Cargando pipelines de Transformers...")
                # Sentiment Analysis
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment",
                    return_all_scores=True
                )
                
                # Summarization
                self.summarizer_pipeline = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    max_length=150,
                    min_length=50
                )
                
                self.logger.info("Transformers pipelines cargados")
            except Exception as e:
                self.logger.error(f"Error cargando Transformers: {e}")
    
    def _ensure_spacy_loaded(self):
        """Carga spaCy bajo demanda"""
        if _check_spacy() and self.config.use_spacy and not self.nlp:
            try:
                import spacy
                from spacy.lang.es import Spanish
                self.logger.info("Cargando modelo spaCy...")
                # Intentar cargar modelo en español
                try:
                    self.nlp = spacy.load("es_core_news_sm")
                except OSError:
                    # Fallback a modelo básico
                    self.nlp = Spanish()
                    self.logger.warning("Usando modelo spaCy básico")
                
                self.logger.info("spaCy cargado")
            except Exception as e:
                self.logger.error(f"Error cargando spaCy: {e}")
    
    def _ensure_keybert_loaded(self):
        """Carga KeyBERT bajo demanda"""
        if _check_keybert() and self.config.use_keybert and not self.keybert_model:
            try:
                from keybert import KeyBERT
                self.logger.info("Cargando KeyBERT...")
                self.keybert_model = KeyBERT()
                self.logger.info("KeyBERT cargado")
            except Exception as e:
                self.logger.error(f"Error cargando KeyBERT: {e}")
    
    @cached_analysis(ttl=1800)
    @performance_monitor.monitor_function("unified_analysis")
    def analyze_project(self, project_description: str, analysis_type: str = "complete") -> Dict[str, Any]:
        """Análisis completo del proyecto usando múltiples backends"""
        start_time = time.time()
        
        try:
            # Primary analysis with Groq (more advanced)
            if self.groq_client:
                primary_analysis = self._analyze_with_groq(project_description)
            else:
                primary_analysis = self._analyze_with_transformers(project_description)
            
            # Complementary NLP analysis
            nlp_analysis = self._analyze_with_nlp(project_description)
            
            # Market analysis
            market_analysis = self._analyze_market_viability(project_description)
            
            # Combine results
            unified_result = self._combine_analyses(
                primary_analysis, nlp_analysis, market_analysis
            )
            
            # Add metadata
            unified_result['_metadata'] = {
                'analysis_time': time.time() - start_time,
                'backends_used': self._get_active_backends(),
                'analysis_type': analysis_type,
                'timestamp': time.time(),
                'version': '2.0.0'
            }
            
            self.logger.info(f"Análisis completado en {time.time() - start_time:.2f}s")
            return unified_result
            
        except Exception as e:
            self.logger.error(f"Error en análisis: {e}")
            return self._generate_fallback_analysis(project_description)
    
    def _analyze_with_groq(self, description: str) -> Dict[str, Any]:
        """Análisis usando Groq API"""
        try:
            prompt = self._build_groq_prompt(description)
            
            response = self.groq_client.chat.completions.create(
                model=self.config.groq_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_groq_response(analysis_text)
            
        except Exception as e:
            self.logger.error(f"Error en análisis Groq: {e}")
            raise
    
    def _build_groq_prompt(self, description: str) -> str:
        """Construye el prompt optimizado para Groq"""
        return f"""
Analiza el siguiente proyecto SaaS y proporciona un análisis estructurado:

DESCRIPCIÓN DEL PROYECTO:
{description}

Proporciona un análisis completo en el siguiente formato:

SUGGESTED NAME:
[Nombre sugerido para el proyecto]

EXECUTIVE SUMMARY:
[Resumen ejecutivo del proyecto]

MARKET ANALYSIS:
[Análisis del mercado objetivo, competencia y oportunidades]

CORE FEATURES:
[Características principales y funcionalidades clave]

RECOMMENDED TECH STACK:
[Stack tecnológico recomendado con justificación]

DEVELOPMENT METHODOLOGY:
[Metodología de desarrollo recomendada]

DEVELOPMENT ROADMAP:
[Roadmap de desarrollo con fases y timeline]

KEYWORDS:
[Palabras clave relevantes separadas por comas]

Por favor, sé específico y detallado en cada sección.
"""
    
    def _parse_groq_response(self, response_text: str) -> Dict[str, Any]:
        """Parsea la respuesta de Groq en estructura de datos"""
        analysis = {
            'executive_summary': '',
            'market_analysis': '',
            'core_features': [],
            'tech_stack': [],
            'development_roadmap': [],
            'keywords': [],
            'methodology_analysis': ''
        }
        
        analysis_metadata = {
            'suggested_name': '',
            'confidence_score': 0.85,
            'analysis_source': 'groq'
        }
        
        # Patrones para extraer secciones
        sections = {
            'suggested_name': r'SUGGESTED NAME:\s*([^\n]+)',
            'executive_summary': r'EXECUTIVE SUMMARY:\s*([\s\S]*?)(?=\n[A-Z]|$)',
            'market_analysis': r'MARKET ANALYSIS:\s*([\s\S]*?)(?=\n[A-Z]|$)',
            'core_features': r'CORE FEATURES:\s*([\s\S]*?)(?=\n[A-Z]|$)',
            'tech_stack': r'RECOMMENDED TECH STACK:\s*([\s\S]*?)(?=\n[A-Z]|$)',
            'methodology_analysis': r'DEVELOPMENT METHODOLOGY:\s*([\s\S]*?)(?=\n[A-Z]|$)',
            'development_roadmap': r'DEVELOPMENT ROADMAP:\s*([\s\S]*?)(?=\n[A-Z]|$)',
            'keywords': r'KEYWORDS:\s*([^\n]+)'
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, response_text, re.IGNORECASE | re.MULTILINE)
            if match:
                content = match.group(1).strip()
                
                if key == 'suggested_name':
                    analysis_metadata['suggested_name'] = content
                elif key in ['core_features', 'tech_stack', 'development_roadmap']:
                    # Convertir a lista
                    items = [item.strip() for item in re.split(r'[\n•-]', content) if item.strip()]
                    analysis[key] = items
                elif key == 'keywords':
                    analysis[key] = [kw.strip() for kw in content.split(',') if kw.strip()]
                else:
                    analysis[key] = content
        
        return {'analysis': analysis, 'analysis_metadata': analysis_metadata}
    
    def _analyze_with_transformers(self, description: str) -> Dict[str, Any]:
        """Análisis usando Transformers como fallback"""
        # Asegurar que los pipelines estén cargados
        self._ensure_transformers_loaded()
        
        analysis = {
            'executive_summary': '',
            'market_analysis': 'Análisis de mercado básico generado por Transformers',
            'core_features': [],
            'tech_stack': ['Python', 'Flask', 'PostgreSQL', 'React'],
            'development_roadmap': ['Fase 1: MVP', 'Fase 2: Beta', 'Fase 3: Producción'],
            'keywords': [],
            'methodology_analysis': 'Metodología Agile recomendada'
        }
        
        analysis_metadata = {
            'suggested_name': 'SaaS Project',
            'confidence_score': 0.65,
            'analysis_source': 'transformers'
        }
        
        try:
            # Generar resumen si está disponible
            if self.summarizer_pipeline:
                summary = self.summarizer_pipeline(description, max_length=150, min_length=50)
                analysis['executive_summary'] = summary[0]['summary_text']
            
            # Extraer características básicas
            features = self._extract_basic_features(description)
            analysis['core_features'] = features
            
        except Exception as e:
            self.logger.error(f"Error en análisis Transformers: {e}")
        
        return {'analysis': analysis, 'analysis_metadata': analysis_metadata}
    
    def _analyze_with_nlp(self, description: str) -> Dict[str, Any]:
        """Análisis complementario con NLP"""
        # Asegurar que los modelos estén cargados
        self._ensure_transformers_loaded()
        self._ensure_spacy_loaded()
        self._ensure_keybert_loaded()
        
        nlp_results = {
            'sentiment': 'neutral',
            'entities': [],
            'keywords_nlp': [],
            'language': 'es',
            'readability_score': 0.5
        }
        
        try:
            # Análisis de sentimientos
            if self.sentiment_pipeline:
                sentiment_result = self.sentiment_pipeline(description)
                nlp_results['sentiment'] = sentiment_result[0][0]['label'].lower()
            
            # Extracción de entidades con spaCy
            if self.nlp:
                doc = self.nlp(description)
                nlp_results['entities'] = [
                    {'text': ent.text, 'label': ent.label_} 
                    for ent in doc.ents
                ]
            
            # Extracción de palabras clave con KeyBERT
            if self.keybert_model:
                keywords = self.keybert_model.extract_keywords(
                    description, 
                    keyphrase_ngram_range=(1, 2), 
                    stop_words='spanish',
                    top_k=10
                )
                nlp_results['keywords_nlp'] = [kw[0] for kw in keywords]
            
        except Exception as e:
            self.logger.error(f"Error en análisis NLP: {e}")
        
        return nlp_results
    
    def _analyze_market_viability(self, description: str) -> Dict[str, Any]:
        """Análisis de viabilidad de mercado"""
        # Palabras clave para diferentes sectores
        market_indicators = {
            'fintech': ['pago', 'banco', 'financiero', 'dinero', 'transacción'],
            'ecommerce': ['tienda', 'venta', 'producto', 'compra', 'marketplace'],
            'edtech': ['educación', 'aprendizaje', 'curso', 'estudiante', 'enseñanza'],
            'healthtech': ['salud', 'médico', 'paciente', 'hospital', 'clínica'],
            'productivity': ['gestión', 'productividad', 'organización', 'tarea', 'proyecto']
        }
        
        description_lower = description.lower()
        market_scores = {}
        
        for sector, keywords in market_indicators.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            market_scores[sector] = score / len(keywords)
        
        primary_market = max(market_scores, key=market_scores.get)
        market_confidence = market_scores[primary_market]
        
        return {
            'primary_market': primary_market,
            'market_confidence': market_confidence,
            'market_scores': market_scores,
            'competition_level': 'medium',  # Análisis básico
            'market_size': 'large' if market_confidence > 0.3 else 'medium'
        }
    
    def _combine_analyses(self, primary: Dict, nlp: Dict, market: Dict) -> Dict[str, Any]:
        """Combina los resultados de diferentes análisis"""
        combined = primary.copy()
        
        # Enriquecer con datos de NLP
        if 'analysis' in combined:
            combined['analysis']['sentiment_analysis'] = nlp.get('sentiment', 'neutral')
            combined['analysis']['entities'] = nlp.get('entities', [])
            
            # Combinar palabras clave
            existing_keywords = combined['analysis'].get('keywords', [])
            nlp_keywords = nlp.get('keywords_nlp', [])
            combined['analysis']['keywords'] = list(set(existing_keywords + nlp_keywords))
        
        # Agregar análisis de mercado
        combined['market_analysis_detailed'] = market
        
        # Mejorar confianza basada en múltiples fuentes
        if 'analysis_metadata' in combined:
            base_confidence = combined['analysis_metadata'].get('confidence_score', 0.5)
            nlp_boost = 0.1 if nlp.get('sentiment') == 'positive' else 0
            market_boost = market.get('market_confidence', 0) * 0.2
            
            combined['analysis_metadata']['confidence_score'] = min(
                base_confidence + nlp_boost + market_boost, 1.0
            )
        
        return combined
    
    def _extract_basic_features(self, description: str) -> List[str]:
        """Extrae características básicas del texto"""
        feature_keywords = {
            'autenticación': ['login', 'usuario', 'autenticación', 'registro'],
            'dashboard': ['dashboard', 'panel', 'tablero', 'métricas'],
            'api': ['api', 'integración', 'webhook', 'endpoint'],
            'notificaciones': ['notificación', 'email', 'alerta', 'aviso'],
            'reportes': ['reporte', 'informe', 'estadística', 'análisis'],
            'pagos': ['pago', 'facturación', 'suscripción', 'precio']
        }
        
        description_lower = description.lower()
        features = []
        
        for feature, keywords in feature_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                features.append(feature.title())
        
        return features
    
    def _generate_fallback_analysis(self, description: str) -> Dict[str, Any]:
        """Genera análisis básico como fallback"""
        return {
            'analysis': {
                'executive_summary': 'Análisis básico generado como fallback',
                'market_analysis': 'Requiere análisis manual adicional',
                'core_features': self._extract_basic_features(description),
                'tech_stack': ['Python', 'Flask', 'PostgreSQL'],
                'development_roadmap': ['Fase 1: Planificación', 'Fase 2: Desarrollo', 'Fase 3: Lanzamiento'],
                'keywords': ['saas', 'software', 'aplicación'],
                'methodology_analysis': 'Metodología Agile recomendada'
            },
            'analysis_metadata': {
                'suggested_name': 'Proyecto SaaS',
                'confidence_score': 0.3,
                'analysis_source': 'fallback'
            },
            '_metadata': {
                'analysis_time': 0.1,
                'backends_used': ['fallback'],
                'version': '2.0.0'
            }
        }
    
    def _get_active_backends(self) -> List[str]:
        """Obtiene lista de backends activos"""
        backends = []
        if self.groq_client:
            backends.append('groq')
        if self.sentiment_pipeline:
            backends.append('transformers')
        if self.nlp:
            backends.append('spacy')
        if self.keybert_model:
            backends.append('keybert')
        return backends
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene estado de salud del analizador"""
        return {
            'status': 'healthy',
            'backends': {
                'groq': self.groq_client is not None,
                'transformers': self.sentiment_pipeline is not None,
                'spacy': self.nlp is not None,
                'keybert': self.keybert_model is not None
            },
            'config': {
                'groq_model': self.config.groq_model,
                'cache_ttl': self.config.cache_ttl,
                'monitoring_enabled': self.config.enable_monitoring
            }
        }

# Instancia global del analizador unificado
unified_analyzer = UnifiedSaaSAnalyzer()

# Función de compatibilidad para mantener API existente
def analyze_project_description(description: str, analysis_type: str = "complete") -> Dict[str, Any]:
    """Función de compatibilidad para mantener API existente"""
    return unified_analyzer.analyze_project(description, analysis_type)