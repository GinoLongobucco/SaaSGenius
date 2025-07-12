// Sistema de visualización de datos para SaaSGenius
// Utiliza Chart.js para gráficos interactivos

class DataVisualization {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#3B82F6',
            secondary: '#10B981',
            accent: '#F59E0B',
            danger: '#EF4444',
            info: '#06B6D4',
            success: '#22C55E',
            warning: '#F97316'
        };
    }

    // Crear gráfico de análisis de sentimientos
    createSentimentChart(containerId, sentimentData) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        const sentiment = sentimentData.sentiment || 'neutral';
        const confidence = sentimentData.confidence || 0.5;

        const data = {
            labels: ['Positivo', 'Neutral', 'Negativo'],
            datasets: [{
                data: sentiment === 'positive' ? [confidence * 100, (1-confidence) * 50, (1-confidence) * 50] :
                      sentiment === 'negative' ? [(1-confidence) * 50, (1-confidence) * 50, confidence * 100] :
                      [33, 34, 33],
                backgroundColor: [this.colors.success, '#E5E7EB', this.colors.danger],
                borderWidth: 2,
                borderColor: '#FFFFFF'
            }]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toFixed(1) + '%';
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    // Crear gráfico de análisis de mercado
    createMarketAnalysisChart(containerId, marketData) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        const viability = marketData.market_viability || {};
        const competition = marketData.competition_analysis || {};

        const data = {
            labels: ['Viabilidad', 'Demanda', 'Competencia', 'Innovación', 'Escalabilidad'],
            datasets: [{
                label: 'Puntuación de Mercado',
                data: [
                    this.extractScore(viability.score) * 20,
                    this.extractScore(viability.demand_level) * 20,
                    (5 - this.extractScore(competition.level)) * 20, // Invertir competencia
                    this.extractScore(viability.innovation_potential) * 20,
                    this.extractScore(viability.scalability) * 20
                ],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: this.colors.primary,
                borderWidth: 2,
                pointBackgroundColor: this.colors.primary,
                pointBorderColor: '#FFFFFF',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }

    // Crear timeline del roadmap
    createRoadmapTimeline(containerId, roadmapData) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const phases = roadmapData.phases || [];
        
        container.innerHTML = '';
        container.className = 'roadmap-timeline';

        phases.forEach((phase, index) => {
            const phaseElement = document.createElement('div');
            phaseElement.className = 'timeline-phase';
            
            const markerClass = index === 0 ? 'primary' : index === 1 ? 'secondary' : 'accent';
            const priorityClass = phase.priority === 'Alta' ? 'high' : phase.priority === 'Media' ? 'medium' : 'low';
            
            phaseElement.innerHTML = `
                <div class="timeline-marker ${markerClass}"></div>
                <div class="timeline-content">
                    <h4 class="phase-title">${phase.name}</h4>
                    <p class="phase-duration">${phase.duration}</p>
                    <div class="phase-features">
                        ${phase.features.map(feature => 
                            `<span class="feature-tag">${feature}</span>`
                        ).join('')}
                    </div>
                    <div class="phase-progress">
                        <div class="progress-bar">
                            <div class="progress-fill ${priorityClass}"></div>
                        </div>
                        <span class="priority-label">Prioridad: ${phase.priority}</span>
                    </div>
                </div>
            `;

            container.appendChild(phaseElement);
        });
    }

    // Crear gráfico de stack tecnológico
    createTechStackChart(containerId, techData) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        const categories = techData.categories || {};
        const labels = Object.keys(categories);
        const data = labels.map(label => categories[label].length);

        const chartData = {
            labels: labels.map(label => this.formatLabel(label)),
            datasets: [{
                label: 'Tecnologías Recomendadas',
                data: data,
                backgroundColor: [
                    this.colors.primary,
                    this.colors.secondary,
                    this.colors.accent,
                    this.colors.info,
                    this.colors.warning
                ].slice(0, labels.length),
                borderWidth: 0,
                borderRadius: 8
            }]
        };

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const category = labels[context.dataIndex];
                                const techs = categories[category] || [];
                                return techs.join(', ');
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Crear indicadores de rendimiento
    createPerformanceIndicators(containerId, performanceData) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const metrics = [
            {
                label: 'Tiempo de Análisis',
                value: `${(performanceData.execution_time || 0).toFixed(2)}s`,
                icon: '⏱️',
                colorClass: 'primary'
            },
            {
                label: 'Precisión',
                value: `${((performanceData.confidence || 0.8) * 100).toFixed(1)}%`,
                icon: '🎯',
                colorClass: 'success'
            },
            {
                label: 'Palabras Clave',
                value: (performanceData.keywords_count || 0).toString(),
                icon: '🔑',
                colorClass: 'accent'
            },
            {
                label: 'Características',
                value: (performanceData.features_count || 0).toString(),
                icon: '⚡',
                colorClass: 'info'
            }
        ];

        container.innerHTML = metrics.map(metric => `
            <div class="performance-indicator">
                <div class="indicator-icon ${metric.colorClass}">${metric.icon}</div>
                <div class="indicator-content">
                    <div class="indicator-value ${metric.colorClass}">${metric.value}</div>
                    <div class="indicator-label">${metric.label}</div>
                </div>
            </div>
        `).join('');
    }

    // Funciones auxiliares
    extractScore(value) {
        if (typeof value === 'number') return Math.min(Math.max(value, 0), 5);
        if (typeof value === 'string') {
            const match = value.match(/\d+/);
            return match ? Math.min(Math.max(parseInt(match[0]), 0), 5) : 3;
        }
        return 3; // Valor por defecto
    }

    formatLabel(label) {
        return label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    // Limpiar gráficos
    destroyChart(containerId) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
            delete this.charts[containerId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }

    // Actualizar gráficos con nuevos datos
    updateCharts(analysisData) {
        // Limpiar gráficos existentes
        this.destroyAllCharts();

        // Crear nuevos gráficos
        if (analysisData.sentiment) {
            this.createSentimentChart('sentimentChart', analysisData.sentiment);
        }

        if (analysisData.market_analysis) {
            this.createMarketAnalysisChart('marketChart', analysisData.market_analysis);
        }

        if (analysisData.development_roadmap) {
            this.createRoadmapTimeline('roadmapTimeline', analysisData.development_roadmap);
        }

        if (analysisData.tech_stack) {
            this.createTechStackChart('techStackChart', analysisData.tech_stack);
        }

        // Crear indicadores de rendimiento
        const performanceData = {
            execution_time: analysisData._metadata?.execution_time,
            confidence: analysisData.sentiment?.confidence,
            keywords_count: analysisData.keywords?.length,
            features_count: analysisData.core_features?.length
        };
        this.createPerformanceIndicators('performanceIndicators', performanceData);
    }
}

// Instancia global
const dataViz = new DataVisualization();

// Exportar para uso global
window.DataVisualization = DataVisualization;
window.dataViz = dataViz;