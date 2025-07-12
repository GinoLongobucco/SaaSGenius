// Analysis page functionality

document.addEventListener('DOMContentLoaded', function() {
    // Get project ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get('id');
    
    if (projectId) {
        loadProjectAnalysis(projectId);
    } else {
        showError('ID de proyecto no encontrado');
    }
});

// Load project analysis data
async function loadProjectAnalysis(projectId) {
    try {
        showLoading('Cargando análisis del proyecto...');
        
        const response = await fetch(`/api/projects/${projectId}`);
        
        if (!response.ok) {
            throw new Error('Error al cargar el proyecto');
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayProjectAnalysis(result.project);
        } else {
            throw new Error(result.error || 'Error al cargar el análisis');
        }
        
    } catch (error) {
        console.error('Error loading analysis:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Display project analysis data
function displayProjectAnalysis(project) {
    // Validate project data
    if (!project || typeof project !== 'object') {
        console.error('Invalid project data received:', project);
        showError('Datos del proyecto no válidos');
        return;
    }
    
    // Update project title and date
    document.getElementById('projectTitle').textContent = project.title || 'Proyecto Sin Título';
    document.getElementById('projectDate').textContent = `Creado el ${formatDate(project.created_at || new Date().toISOString())}`;
    
    // Parse analysis data
    let analysisData = {};
    if (project.analysis_data) {
        try {
            analysisData = typeof project.analysis_data === 'string' 
                ? JSON.parse(project.analysis_data) 
                : project.analysis_data;
        } catch (e) {
            console.warn('Error parsing analysis data:', e);
        }
    }
    
    // Display different sections
    displayExecutiveSummary(analysisData);
    displayKeywords(analysisData);
    displayMarketAnalysis(analysisData);
    displayCoreFeatures(analysisData);
    displayTechStack(analysisData);
    displayMethodology(analysisData);
    displayRoadmap(analysisData);
    displaySpecificContext(analysisData);
    
    // Show analysis content
    document.getElementById('analysisContent').classList.remove('hidden');
}

// Display executive summary
function displayExecutiveSummary(data) {
    const summaryElement = document.getElementById('executiveSummary');
    const summary = data.executive_summary || data.summary || 
        'Este proyecto representa una oportunidad innovadora en el mercado SaaS, con potencial para transformar la experiencia del usuario y generar valor significativo.';
    
    summaryElement.textContent = summary;
}

// Display keywords
function displayKeywords(data) {
    const container = document.getElementById('keywordsContainer');
    const keywords = data.keywords || data.tags || ['SaaS', 'Innovación', 'Tecnología', 'Escalabilidad'];
    
    container.innerHTML = '';
    
    keywords.forEach(keyword => {
        const keywordElement = document.createElement('span');
        keywordElement.className = 'keyword-tag';
        keywordElement.textContent = keyword;
        container.appendChild(keywordElement);
    });
}

// Display market analysis
function displayMarketAnalysis(data) {
    const container = document.getElementById('marketMetrics');
    const marketData = data.market_analysis || {};
    
    const metrics = [
        {
            label: 'Tamaño del Mercado',
            value: marketData.market_size || '$2.5B',
            icon: 'fa-chart-pie'
        },
        {
            label: 'Crecimiento Anual',
            value: marketData.growth_rate || '15%',
            icon: 'fa-trending-up'
        },
        {
            label: 'Competidores',
            value: marketData.competitors || '12+',
            icon: 'fa-users'
        },
        {
            label: 'Oportunidad',
            value: marketData.opportunity || 'Alta',
            icon: 'fa-bullseye'
        }
    ];
    
    container.innerHTML = metrics.map(metric => `
        <div class="metric-card">
            <div class="metric-icon">
                <i class="fas ${metric.icon}"></i>
            </div>
            <div class="metric-content">
                <div class="metric-value">${metric.value}</div>
                <div class="metric-label">${metric.label}</div>
            </div>
        </div>
    `).join('');
}

// Display core features
function displayCoreFeatures(data) {
    const container = document.getElementById('coreFeatures');
    const features = data.core_features || data.features || [
        'Interfaz intuitiva y moderna',
        'Escalabilidad automática',
        'Integración con APIs populares',
        'Dashboard analítico avanzado',
        'Seguridad de nivel empresarial'
    ];
    
    container.innerHTML = features.map(feature => `
        <li class="feature-item">
            <i class="fas fa-check-circle"></i>
            <span>${feature}</span>
        </li>
    `).join('');
}

// Display tech stack
function displayTechStack(data) {
    const container = document.getElementById('techStack');
    const techStack = data.tech_stack || data.technology || {
        frontend: ['React', 'TypeScript', 'Tailwind CSS'],
        backend: ['Node.js', 'Express', 'PostgreSQL'],
        infrastructure: ['AWS', 'Docker', 'Redis'],
        tools: ['Git', 'Jest', 'Webpack']
    };
    
    const categories = [
        { name: 'Frontend', items: techStack.frontend || [], icon: 'fa-desktop' },
        { name: 'Backend', items: techStack.backend || [], icon: 'fa-server' },
        { name: 'Infraestructura', items: techStack.infrastructure || [], icon: 'fa-cloud' },
        { name: 'Herramientas', items: techStack.tools || [], icon: 'fa-tools' }
    ];
    
    container.innerHTML = categories.map(category => `
        <div class="tech-category">
            <div class="tech-category-header">
                <i class="fas ${category.icon}"></i>
                <h4>${category.name}</h4>
            </div>
            <div class="tech-items">
                ${category.items.map(item => `<span class="tech-item">${item}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

// Display methodology
function displayMethodology(data) {
    const container = document.getElementById('methodologyAnalysis');
    const methodology = data.methodology || {
        approach: 'Agile/Scrum',
        phases: ['Planificación', 'Desarrollo', 'Testing', 'Despliegue'],
        duration: '3-6 meses',
        team_size: '4-6 desarrolladores'
    };
    
    container.innerHTML = `
        <div class="methodology-overview">
            <div class="methodology-item">
                <strong>Enfoque:</strong> ${methodology.approach}
            </div>
            <div class="methodology-item">
                <strong>Duración Estimada:</strong> ${methodology.duration}
            </div>
            <div class="methodology-item">
                <strong>Tamaño del Equipo:</strong> ${methodology.team_size}
            </div>
        </div>
        <div class="methodology-phases">
            <h4>Fases del Proyecto:</h4>
            <div class="phases-list">
                ${methodology.phases.map((phase, index) => `
                    <div class="phase-item">
                        <div class="phase-number">${index + 1}</div>
                        <div class="phase-name">${phase}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Display development roadmap
function displayRoadmap(data) {
    const container = document.getElementById('developmentRoadmap');
    const roadmap = data.roadmap || [
        {
            phase: 'Fase 1: Fundación',
            duration: '4-6 semanas',
            tasks: ['Configuración del proyecto', 'Diseño de la arquitectura', 'Prototipo inicial']
        },
        {
            phase: 'Fase 2: Desarrollo Core',
            duration: '8-10 semanas',
            tasks: ['Funcionalidades principales', 'Integración de APIs', 'Testing unitario']
        },
        {
            phase: 'Fase 3: Refinamiento',
            duration: '4-6 semanas',
            tasks: ['Optimización', 'Testing integral', 'Documentación']
        },
        {
            phase: 'Fase 4: Lanzamiento',
            duration: '2-3 semanas',
            tasks: ['Despliegue', 'Monitoreo', 'Soporte inicial']
        }
    ];
    
    container.innerHTML = roadmap.map((phase, index) => `
        <div class="roadmap-phase">
            <div class="roadmap-header">
                <div class="roadmap-number">${index + 1}</div>
                <div class="roadmap-info">
                    <h4>${phase.phase}</h4>
                    <span class="roadmap-duration">${phase.duration}</span>
                </div>
            </div>
            <div class="roadmap-tasks">
                ${phase.tasks.map(task => `
                    <div class="roadmap-task">
                        <i class="fas fa-check"></i>
                        <span>${task}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// Display specific context (if available)
function displaySpecificContext(data) {
    const section = document.getElementById('specificContextSection');
    const container = document.getElementById('specificContextContent');
    
    if (data.specific_context || data.context) {
        const context = data.specific_context || data.context;
        container.innerHTML = `
            <div class="context-content">
                <p>${context}</p>
            </div>
        `;
        section.classList.remove('hidden');
    }
}

// Error handling
function showError(message) {
    const analysisContent = document.getElementById('analysisContent');
    analysisContent.innerHTML = `
        <div class="error-state">
            <div class="error-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <h3>Error al cargar el análisis</h3>
            <p>${message}</p>
            <a href="/dashboard" class="btn btn-primary">
                <i class="fas fa-arrow-left"></i>
                Volver al Dashboard
            </a>
        </div>
    `;
    analysisContent.classList.remove('hidden');
    hideLoading();
}

// Export project analysis
function exportAnalysis() {
    const projectTitle = document.getElementById('projectTitle').textContent;
    const analysisContent = document.getElementById('analysisContent');
    
    // Create a simplified version for export
    const exportData = {
        title: projectTitle,
        date: new Date().toISOString(),
        content: analysisContent.innerText
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `${projectTitle.replace(/\s+/g, '_')}_analysis.json`;
    link.click();
    
    showToast('Análisis exportado exitosamente', 'success');
}