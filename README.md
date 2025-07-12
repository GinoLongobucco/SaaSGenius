# 🚀 SaaSGenius

**Transforma Ideas en Éxito SaaS con Inteligencia Artificial**

SaaSGenius es una plataforma avanzada de análisis de proyectos SaaS que utiliza inteligencia artificial para convertir conceptos de negocio en planes estratégicos completos. Combina múltiples modelos de IA para proporcionar análisis de mercado, recomendaciones tecnológicas y roadmaps de desarrollo personalizados.

<img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm82bGg2dXQ2M3prcjF1djZ2dGx4bGkwNTExbXpjeHFhMnk2bWdmNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/M5aUBMlZTvSpFCt1aG/giphy.gif" alt="SaaSGenius GIF" width="500"/>

## ✨ Características Principales

### 🧠 Análisis Inteligente con IA
- **Análisis Unificado**: Combina múltiples backends de IA (Groq, Transformers, spaCy, KeyBERT)
- **Procesamiento de Lenguaje Natural**: Extracción automática de características y palabras clave
- **Análisis de Sentimientos**: Evaluación de viabilidad emocional del proyecto
- **Generación de Nombres**: Sugerencias automáticas de nombres para el proyecto

### 📊 Análisis de Mercado Avanzado
- **Evaluación de Viabilidad**: Análisis completo del potencial de mercado
- **Identificación de Competidores**: Mapeo automático del panorama competitivo
- **Estrategias de Monetización**: Recomendaciones de modelos de negocio
- **Análisis de Riesgos**: Identificación proactiva de desafíos potenciales

### 🛠️ Recomendaciones Tecnológicas
- **Stack Tecnológico Dinámico**: Selección automática de tecnologías basada en requisitos
- **Arquitectura Escalable**: Recomendaciones de infraestructura y patrones de diseño
- **Integración de APIs**: Sugerencias de servicios y herramientas complementarias
- **Consideraciones de Seguridad**: Mejores prácticas de seguridad específicas del proyecto

### 📈 Gestión de Proyectos
- **Dashboard Personalizado**: Interfaz intuitiva para gestionar múltiples proyectos
- **Historial de Análisis**: Seguimiento completo de la evolución de ideas
- **Exportación de Datos**: Generación de reportes en PDF y otros formatos
- **Sistema de Favoritos**: Organización eficiente de proyectos prioritarios

### 🔐 Seguridad y Autenticación
- **Autenticación Segura**: Sistema robusto de login con Flask-Login
- **Encriptación de Datos**: Protección completa de información sensible
- **Gestión de Sesiones**: Control avanzado de acceso y permisos
- **Auditoría de Actividad**: Registro detallado de acciones del usuario

## 🏗️ Arquitectura Técnica

### Backend
- **Framework**: Flask 2.3.3 con arquitectura modular
- **Base de Datos**: SQLAlchemy con soporte para SQLite/PostgreSQL
- **IA y ML**: Groq API, Transformers, spaCy, KeyBERT
- **Cache**: Redis para optimización de rendimiento
- **Monitoreo**: Sistema integrado de métricas y health checks

### Frontend
- **UI/UX**: Diseño monochromático moderno y responsive
- **JavaScript**: Vanilla JS con componentes modulares
- **Visualización**: Chart.js para gráficos interactivos
- **Animaciones**: CSS3 con efectos suaves y profesionales

### DevOps y Producción
- **Servidor**: Gunicorn para producción
- **Monitoreo**: Prometheus, Sentry para tracking de errores
- **Testing**: Pytest con cobertura completa
- **CI/CD**: Configuración lista para despliegue automatizado

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes de Python)
- Git

### Instalación Rápida

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/SaaSGenius.git
cd SaaSGenius
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Crear archivo .env
cp .env.example .env

# Editar .env con tus configuraciones
GROQ_API_KEY=tu_clave_groq_api
SECRET_KEY=tu_clave_secreta
DATABASE_URL=sqlite:///saasgenius.db
```

5. **Inicializar base de datos**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Ejecutar la aplicación**
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
# Configuración de la aplicación
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_muy_segura

# Base de datos
DATABASE_URL=sqlite:///saasgenius.db
# Para PostgreSQL: postgresql://usuario:password@localhost/saasgenius

# APIs de IA
GROQ_API_KEY=tu_clave_groq_api

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Monitoreo (opcional)
SENTRY_DSN=tu_sentry_dsn
PROMETHEUS_ENABLED=true

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_app
```

### Configuración de Modelos de IA

El sistema soporta múltiples backends de IA que se pueden habilitar/deshabilitar:

```python
# En config/settings.py
class AnalysisConfig:
    use_groq: bool = True          # Recomendado para mejor calidad
    use_transformers: bool = False  # Para análisis local
    use_spacy: bool = False        # Para NLP avanzado
    use_keybert: bool = False      # Para extracción de keywords
```

## 📖 Uso de la Aplicación

### Análisis Básico

1. **Acceder a la aplicación** en `http://localhost:5000`
2. **Describir tu proyecto** en el área de texto principal
3. **Hacer clic en "Analizar con IA"** para obtener resultados
4. **Revisar el análisis completo** con recomendaciones personalizadas

### Gestión de Proyectos

1. **Crear cuenta** o **iniciar sesión**
2. **Acceder al Dashboard** para ver todos tus proyectos
3. **Organizar proyectos** con favoritos y etiquetas
4. **Exportar análisis** en diferentes formatos

### API Endpoints

```bash
# Análisis de proyecto
POST /analyze_project
Content-Type: application/json
{
  "description": "Tu descripción del proyecto SaaS"
}

# Obtener proyecto
GET /api/projects/{project_id}

# Listar proyectos del usuario
GET /api/projects

# Health check
GET /health
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests unitarios
pytest tests/

# Tests con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_analyzer.py -v
```

### Estructura de Tests

```
tests/
├── conftest.py              # Configuración de pytest
├── test_analyzer.py         # Tests del analizador de IA
├── test_routes.py          # Tests de endpoints
├── test_models.py          # Tests de modelos de datos
└── test_auth.py            # Tests de autenticación
```

## 🚀 Despliegue en Producción

### Docker

```dockerfile
# Dockerfile incluido en el proyecto
docker build -t saasgenius .
docker run -p 5000:5000 saasgenius
```

### Heroku

```bash
# Configuración para Heroku
heroku create tu-app-saasgenius
heroku config:set GROQ_API_KEY=tu_clave
heroku config:set SECRET_KEY=tu_clave_secreta
git push heroku main
```

### VPS/Servidor Dedicado

```bash
# Con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Con Nginx (configuración incluida)
sudo systemctl start nginx
sudo systemctl enable saasgenius
```

## 📊 Monitoreo y Métricas

### Métricas Disponibles
- **Tiempo de análisis**: Duración promedio de procesamiento
- **Uso de APIs**: Consumo de tokens y llamadas
- **Errores del sistema**: Tracking automático de fallos
- **Actividad de usuarios**: Patrones de uso y engagement

### Dashboards
- **Health Check**: `/health` - Estado del sistema
- **Métricas**: `/metrics` - Prometheus metrics
- **Logs**: Integración con Sentry para error tracking

## 🤝 Contribución

### Guía de Contribución

1. **Fork** el repositorio
2. **Crear rama** para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear Pull Request**

### Estándares de Código

```bash
# Formateo de código
black app/ models/ tests/

# Linting
flake8 app/ models/ tests/

# Type checking
mypy app/ models/
```

### Estructura de Commits

```
feat: nueva funcionalidad
fix: corrección de bug
docs: actualización de documentación
style: cambios de formato
refactor: refactorización de código
test: agregar o modificar tests
chore: tareas de mantenimiento
```

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### Documentación
- **Wiki**: [GitHub Wiki](https://github.com/tu-usuario/SaaSGenius/wiki)
- **API Docs**: Disponible en `/docs` cuando la app está ejecutándose
- **Ejemplos**: Directorio `examples/` con casos de uso

### Comunidad
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/SaaSGenius/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/SaaSGenius/discussions)
- **Email**: soporte@saasgenius.com

### FAQ

**P: ¿Necesito una API key de Groq?**
R: Sí, para obtener análisis de alta calidad. Puedes obtener una gratis en [Groq Console](https://console.groq.com).

**P: ¿Funciona sin conexión a internet?**
R: Parcialmente. Los modelos locales (Transformers, spaCy) pueden funcionar offline, pero Groq requiere conexión.

**P: ¿Puedo personalizar los prompts de IA?**
R: Sí, los prompts están en `models/advanced_prompt_engineering.py` y son completamente personalizables.

**P: ¿Hay límites en el número de análisis?**
R: No hay límites técnicos, pero las APIs externas pueden tener rate limits.

---

<div align="center">

**🌟 ¡Dale una estrella si te gusta el proyecto! 🌟**

[⬆ Volver arriba](#-saasgenius)

</div>
