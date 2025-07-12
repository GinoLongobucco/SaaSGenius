// Script corregido para SaaSGenius
console.log("Script v2.0 cargado");

const app = {
  // Estado de la aplicación
  state: {
    analysisData: null,
    isAnalyzing: false,
  },

  // Elementos del DOM cacheados
  elements: {},

  // Inicialización
  init() {
    console.log("DOM cargado - Iniciando configuración de la app");
    this.cacheDOMElements();
    this.setupEventListeners();
    console.log("Configuración completada");
  },

  // Cachear elementos del DOM para reutilización
  cacheDOMElements() {
    this.elements.textarea = document.getElementById("projectDescription");
    this.elements.charCount = document.querySelector(".char-count");
    this.elements.form = document.getElementById("projectForm");
    this.elements.analyzeBtn = document.getElementById("analyzeBtn");
    this.elements.btnText = document.getElementById("btnText");
    this.elements.loadingSpinner = document.getElementById("loadingSpinner");
    this.elements.results = document.getElementById("results");
    // ... agregar otros elementos que se necesiten ...
  },

  // Configurar todos los listeners de eventos
  setupEventListeners() {
    if (this.elements.textarea) {
      this.elements.textarea.addEventListener(
        "input",
        this.handleCharCount.bind(this)
      );
      this.handleCharCount(); // Llamada inicial
    }

    if (this.elements.form) {
      this.elements.form.addEventListener(
        "submit",
        this.handleFormSubmit.bind(this)
      );
    }

    // ... configurar otros listeners ...
  },

  handleCharCount() {
    const { textarea, charCount } = this.elements;
    if (!textarea || !charCount) return;

    const count = textarea.value.length;
    const maxLength = 1000;
    charCount.textContent = `${count} / ${maxLength} caracteres`;

    let color = "#718096";
    if (count > maxLength * 0.9) color = "#e53e3e";
    else if (count > maxLength * 0.7) color = "#dd6b20";
    charCount.style.color = color;
  },

  async handleFormSubmit(e) {
    e.preventDefault();
    if (this.state.isAnalyzing) return;

    const description = this.elements.textarea.value.trim();
    if (!this.validateInput(description)) return;

    this.state.isAnalyzing = true;
    this.toggleLoadingState(true);

    try {
      const data = await SaaSUtils.apiRequest("/analyze_project", {
        method: "POST",
        body: JSON.stringify({ description }),
      });

      this.state.analysisData = data.analysis;
      this.displayResults(data.analysis);
      this.showResults();
      this.saveAnalysisData(data.analysis);
      this.showNotification("¡Análisis completado!", "success");
    } catch (error) {
      console.error("Error en análisis:", error);
      this.showNotification(`Error: ${error.message}`, "error");
    } finally {
      this.state.isAnalyzing = false;
      this.toggleLoadingState(false);
    }
  },

  // Validate project input (using SaaSUtils)
  validateInput(description) {
    const validation = SaaSUtils.validation.isValidProjectDescription(description);
    if (!validation.valid) {
      this.showNotification(validation.message, "error");
      return false;
    }
    return true;
  },

  toggleLoadingState(isLoading) {
    const { analyzeBtn, btnText, loadingSpinner } = this.elements;
    if (!analyzeBtn || !btnText || !loadingSpinner) return;

    analyzeBtn.disabled = isLoading;
    btnText.textContent = isLoading ? "Analizando..." : "Analizar Proyecto";
    if (isLoading) {
      loadingSpinner.classList.remove("hidden");
    } else {
      loadingSpinner.classList.add("hidden");
    }
  },

  showResults() {
    const { results } = this.elements;
    if (results) {
      results.classList.remove("hidden");
      setTimeout(() => {
        results.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    }
  },

  showNotification(message, type = "info", title = null) {
    return SaaSUtils.showNotification(message, type, title);
  },

  // Mostrar resultados del análisis
  displayResults(analysis) {
    console.log("Datos del análisis recibidos:", analysis);

    // Nombre del proyecto
    const projectNameEl = document.getElementById("projectName");
    if (projectNameEl) {
      let projectName = "";
      if (
        analysis.analysis_metadata &&
        analysis.analysis_metadata.suggested_name
      ) {
        projectName = analysis.analysis_metadata.suggested_name;
      } else if (analysis.project_name) {
        projectName = analysis.project_name;
      } else if (analysis.suggested_name) {
        projectName = analysis.suggested_name;
      } else {
        projectName = "Nombre no disponible";
      }
      projectNameEl.textContent = projectName;
    }

    // Resumen ejecutivo
    const summaryEl = document.getElementById("summary");
    if (summaryEl) {
      let executiveSummary = "";
      if (analysis.executive_summary && analysis.executive_summary.summary) {
        executiveSummary = analysis.executive_summary.summary;
      } else if (analysis.executive_summary) {
        executiveSummary = analysis.executive_summary;
      } else if (analysis.summary) {
        executiveSummary = analysis.summary;
      } else {
        executiveSummary = "Resumen no disponible";
      }
      summaryEl.innerHTML = this.formatText(executiveSummary);
    }

    // Palabras clave
    const keywordsContainer = document.getElementById("keywords");
    if (keywordsContainer) {
      keywordsContainer.innerHTML = "";
      let keywords = [];

      // Buscar palabras clave en diferentes ubicaciones
      if (
        analysis.analysis_metadata &&
        analysis.analysis_metadata.keywords_extracted
      ) {
        keywords = analysis.analysis_metadata.keywords_extracted;
      } else if (
        analysis.executive_summary &&
        analysis.executive_summary.keywords
      ) {
        keywords = analysis.executive_summary.keywords;
      } else if (
        analysis.analysis_metadata &&
        analysis.analysis_metadata.keywords
      ) {
        keywords = analysis.analysis_metadata.keywords;
      } else if (
        analysis.market_analysis &&
        analysis.market_analysis.keywords
      ) {
        keywords = analysis.market_analysis.keywords;
      } else if (analysis.keywords) {
        keywords = analysis.keywords;
      }

      if (keywords && keywords.length > 0) {
        keywords.forEach((keyword) => {
          const span = document.createElement("span");
          span.className = "keyword-tag";
          span.textContent = keyword;
          keywordsContainer.appendChild(span);
        });
      } else {
        keywordsContainer.innerHTML = "<p>No se encontraron palabras clave</p>";
      }
    }

    // Características principales
    const featuresEl = document.getElementById("coreFeatures");
    if (featuresEl) {
      let features = null;

      // Buscar características en diferentes ubicaciones
      if (
        analysis.analysis_metadata &&
        analysis.analysis_metadata.key_features
      ) {
        features = analysis.analysis_metadata.key_features;
      } else if (analysis.tech_stack && analysis.tech_stack.core_features) {
        features = analysis.tech_stack.core_features;
      } else if (analysis.tech_stack && analysis.tech_stack.key_features) {
        features = analysis.tech_stack.key_features;
      } else if (
        analysis.executive_summary &&
        analysis.executive_summary.key_features
      ) {
        features = analysis.executive_summary.key_features;
      } else if (analysis.core_features) {
        features = analysis.core_features;
      } else if (analysis.key_features) {
        features = analysis.key_features;
      }

      if (features) {
        if (Array.isArray(features)) {
          featuresEl.innerHTML =
            "<ul class='feature-list'>" +
            features
              .map((feature) => {
                const featureText =
                  typeof feature === "string" ? feature : String(feature);
                return `<li>${featureText}</li>`;
              })
              .join("") +
            "</ul>";
        } else {
          featuresEl.innerHTML = this.formatText(features);
        }
      } else {
        featuresEl.innerHTML = "<p>Características no disponibles</p>";
      }
    }

    // Análisis de mercado
    const marketEl = document.getElementById("marketAnalysis");
    if (marketEl) {
      let marketAnalysis = null;
      if (analysis.market_analysis && analysis.market_analysis.analysis) {
        marketAnalysis = analysis.market_analysis.analysis;
      } else if (analysis.market_analysis) {
        marketAnalysis = analysis.market_analysis;
      }

      if (marketAnalysis) {
        if (typeof marketAnalysis === "string") {
          marketEl.innerHTML = this.formatText(marketAnalysis);
        } else {
          marketEl.innerHTML = this.formatMarketAnalysis(marketAnalysis);
        }
      } else {
        marketEl.innerHTML = "<p>Análisis de mercado no disponible</p>";
      }
    }

    // Stack tecnológico
    const techEl = document.getElementById("techRequirements");
    if (techEl) {
      let techStack = null;
      if (analysis.tech_stack && analysis.tech_stack.detailed_analysis) {
        techStack = analysis.tech_stack.detailed_analysis;
      } else if (analysis.tech_stack) {
        techStack = analysis.tech_stack;
      } else if (analysis.tech_requirements) {
        techStack = analysis.tech_requirements;
      }

      if (techStack) {
        if (typeof techStack === "string") {
          techEl.innerHTML = this.formatText(techStack);
        } else {
          techEl.innerHTML = this.formatTechRequirements(techStack);
        }
      } else {
        techEl.innerHTML = "<p>Stack tecnológico no disponible</p>";
      }
    }

    // Roadmap
    const roadmapEl = document.getElementById("roadmap");
    if (roadmapEl) {
      let roadmap = null;
      if (
        analysis.development_roadmap &&
        analysis.development_roadmap.detailed_roadmap
      ) {
        roadmap = analysis.development_roadmap.detailed_roadmap;
      } else if (analysis.development_roadmap) {
        roadmap = analysis.development_roadmap;
      } else if (analysis.roadmap) {
        roadmap = analysis.roadmap;
      }

      if (roadmap) {
        if (typeof roadmap === "string") {
          roadmapEl.innerHTML = this.formatText(roadmap);
        } else {
          roadmapEl.innerHTML = this.formatRoadmap(roadmap);
        }
      } else {
        roadmapEl.innerHTML = "<p>Roadmap no disponible</p>";
      }
    }
  },

  // Formatear análisis de mercado
  formatMarketAnalysis(marketData) {
    if (!marketData) return "Análisis de mercado no disponible";

    let html = "";
    if (marketData.target_market) {
      const targetMarket =
        typeof marketData.target_market === "string"
          ? marketData.target_market
          : String(marketData.target_market);
      html += `<p><strong>Mercado objetivo:</strong> ${targetMarket}</p>`;
    }
    if (marketData.market_size) {
      const marketSize =
        typeof marketData.market_size === "string"
          ? marketData.market_size
          : String(marketData.market_size);
      html += `<p><strong>Tamaño del mercado:</strong> ${marketSize}</p>`;
    }
    if (marketData.competition) {
      const competition =
        typeof marketData.competition === "string"
          ? marketData.competition
          : String(marketData.competition);
      html += `<p><strong>Competencia:</strong> ${competition}</p>`;
    }
    if (marketData.growth_potential) {
      const growthPotential =
        typeof marketData.growth_potential === "string"
          ? marketData.growth_potential
          : String(marketData.growth_potential);
      html += `<p><strong>Potencial de crecimiento:</strong> ${growthPotential}</p>`;
    }
    if (marketData.trends) {
      const trends =
        typeof marketData.trends === "string"
          ? marketData.trends
          : String(marketData.trends);
      html += `<p><strong>Tendencias:</strong> ${trends}</p>`;
    }

    return html || "Análisis de mercado no disponible";
  },

  // Formatear requisitos técnicos
  formatTechRequirements(techData) {
    if (!techData) return "Requisitos técnicos no disponibles";

    let html = "";
    if (techData.frontend) {
      html += `<p><strong>Frontend:</strong> ${
        Array.isArray(techData.frontend)
          ? techData.frontend
              .map((item) => (typeof item === "string" ? item : String(item)))
              .join(", ")
          : typeof techData.frontend === "string"
          ? techData.frontend
          : String(techData.frontend)
      }</p>`;
    }
    if (techData.backend) {
      html += `<p><strong>Backend:</strong> ${
        Array.isArray(techData.backend)
          ? techData.backend
              .map((item) => (typeof item === "string" ? item : String(item)))
              .join(", ")
          : typeof techData.backend === "string"
          ? techData.backend
          : String(techData.backend)
      }</p>`;
    }
    if (techData.database) {
      html += `<p><strong>Base de datos:</strong> ${
        Array.isArray(techData.database)
          ? techData.database
              .map((item) => (typeof item === "string" ? item : String(item)))
              .join(", ")
          : typeof techData.database === "string"
          ? techData.database
          : String(techData.database)
      }</p>`;
    }

    return html || "Requisitos técnicos no disponibles";
  },

  // Formatear roadmap
  formatRoadmap(roadmapData) {
    if (!roadmapData) return "Roadmap no disponible";

    let html = "";
    if (Array.isArray(roadmapData)) {
      html = "<ul class='feature-list'>";
      roadmapData.forEach((phase) => {
        // Asegurar que phase es un string
        const phaseText = typeof phase === "string" ? phase : String(phase);
        html += `<li>${phaseText}</li>`;
      });
      html += "</ul>";
    } else if (typeof roadmapData === "object") {
      Object.keys(roadmapData).forEach((phase) => {
        // Asegurar que los valores son strings
        const phaseValue =
          typeof roadmapData[phase] === "string"
            ? roadmapData[phase]
            : String(roadmapData[phase]);
        html += `<h4>${phase}</h4><p>${phaseValue}</p>`;
      });
    } else {
      html = this.formatText(roadmapData);
    }

    return html;
  },

  // Formatear texto con saltos de línea y listas
  formatText(text) {
    if (!text) return "";

    // Asegurar que text es un string
    if (typeof text !== "string") {
      text = String(text);
    }

    // Convertir saltos de línea a <br>
    let formatted = text.replace(/\n/g, "<br>");

    // Convertir listas con guiones o asteriscos
    formatted = formatted.replace(/^[-*]\s+(.+)$/gm, "<li>$1</li>");

    // Envolver listas en <ul>
    if (formatted.includes("<li>")) {
      formatted = formatted.replace(
        /(<li>.*<\/li>)/gs,
        '<ul class="feature-list">$1</ul>'
      );
    }

    // Convertir texto en negrita **texto**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Si no hay formato especial, envolver en párrafo
    if (
      !formatted.includes("<br>") &&
      !formatted.includes("<ul>") &&
      !formatted.includes("<li>")
    ) {
      formatted = `<p>${formatted}</p>`;
    }

    return formatted;
  },

  // Configurar botones de acción
  setupActionButtons() {
    // Botón de reset
    const resetBtn = document.getElementById("resetBtn");
    if (resetBtn) {
      resetBtn.addEventListener("click", this.resetForm.bind(this));
    }
  },

  // Resetear formulario
  resetForm() {
    const form = document.getElementById("projectForm");
    const results = document.getElementById("results");
    const charCount = document.querySelector(".char-count");
    const textarea = document.getElementById("projectDescription");

    if (form) form.reset();
    if (results) results.classList.add("hidden");
    if (charCount) {
      charCount.textContent = "0 / 1000 caracteres";
      charCount.style.color = "#718096";
    }
    if (textarea) {
      textarea.focus();
      // Disparar evento para actualizar contador
      textarea.dispatchEvent(new Event("input"));
    }

    this.state.analysisData = null;
    this.showNotification("Formulario reiniciado", "info", "Listo");
  },

  // Guardar datos de análisis
  saveAnalysisData(analysis) {
    try {
      const analysisHistory = JSON.parse(
        localStorage.getItem("analysisHistory") || "[]"
      );
      analysisHistory.unshift({
        ...analysis,
        timestamp: Date.now(),
      });

      // Mantener solo los últimos 10 análisis
      if (analysisHistory.length > 10) {
        analysisHistory.splice(10);
      }

      localStorage.setItem("analysisHistory", JSON.stringify(analysisHistory));
    } catch (error) {
      console.error("Error guardando análisis:", error);
    }
  },
};

// Funciones de utilidad
function exportToPDF() {
  showNotification("Función de exportación próximamente", "info");
}

// Función global para mostrar notificaciones (usando SaaSUtils)
function showNotification(message, type = "info", title = null) {
  return SaaSUtils.showNotification(message, type);
}

// Funciones para el dashboard
function showLoadingOverlay() {
  let overlay = document.getElementById("loadingOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>Analizando proyecto...</p>
        </div>
    `;
    // Los estilos ahora están en el archivo CSS principal
    document.body.appendChild(overlay);
  }
  overlay.classList.remove("hidden");
}

function hideLoadingOverlay() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.classList.add("hidden");
  }
}

// ===== NAVBAR FUNCTIONALITY =====

// Toggle user dropdown menu
function toggleUserMenu() {
  const dropdown = document.getElementById("userDropdown");
  if (dropdown) {
    dropdown.classList.toggle("show");
  }
}

// Toggle mobile menu
function toggleMobileMenu() {
  const navMenu = document.querySelector(".nav-menu");
  const hamburger = document.querySelector(".hamburger");

  if (navMenu) {
    navMenu.classList.toggle("active");
  }

  if (hamburger) {
    hamburger.classList.toggle("active");
  }
}

// Close dropdowns when clicking outside
document.addEventListener("click", function (event) {
  // Close user dropdown
  const userMenu = document.querySelector(".user-menu");
  const userDropdown = document.getElementById("userDropdown");

  if (userMenu && userDropdown && !userMenu.contains(event.target)) {
    userDropdown.classList.remove("show");
  }

  // Close mobile menu when clicking outside
  const navbar = document.querySelector(".navbar");
  const navMenu = document.querySelector(".nav-menu");
  const hamburger = document.querySelector(".hamburger");

  if (
    navbar &&
    navMenu &&
    !navbar.contains(event.target) &&
    navMenu.classList.contains("active")
  ) {
    navMenu.classList.remove("active");
    if (hamburger) {
      hamburger.classList.remove("active");
    }
  }
});

// Handle window resize
window.addEventListener("resize", function () {
  const navMenu = document.querySelector(".nav-menu");
  const hamburger = document.querySelector(".hamburger");

  // Close mobile menu on desktop
  if (
    window.innerWidth > 768 &&
    navMenu &&
    navMenu.classList.contains("active")
  ) {
    navMenu.classList.remove("active");
    if (hamburger) {
      hamburger.classList.remove("active");
    }
  }
});

// Set active nav link based on current page
function setActiveNavLink() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    link.classList.remove("active");

    // Check if link href matches current path
    const linkPath = new URL(link.href).pathname;
    if (linkPath === currentPath) {
      link.classList.add("active");
    }
  });
}

// Functions from index.html (using SaaSUtils)
function loadProjectData(projectId) {
    return SaaSUtils.apiRequest(`/api/projects/${projectId}`)
        .then(result => {
            if (result.project) {
                // Update page title
                document.title = `${result.project.title || 'Proyecto'} - SaaSGenius`;
                
                // Display analysis results
                if (result.project.analysis_data) {
                    app.showResults(result.project.analysis_data);
                    showNotification('Proyecto cargado exitosamente', 'success');
                } else {
                    showNotification('El proyecto no tiene datos de análisis', 'warning');
                }
            } else {
                throw new Error('Error al cargar el proyecto');
            }
        })
        .catch(error => {
            console.error('Error loading project:', error);
            showNotification('Error al cargar el proyecto: ' + error.message, 'error');
            // Redirect to dashboard after error
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        });
}

// Functions from dashboard.html (using SaaSUtils)
function toggleFavorite(projectId) {
    SaaSUtils.apiRequest(`/api/projects/${projectId}/favorite`, {
        method: 'POST'
    })
    .then(result => {
        // Update UI - toggle favorite icon
        const favoriteBtn = document.querySelector(`[data-project-id="${projectId}"] .favorite-btn`);
        if (favoriteBtn) {
            const icon = favoriteBtn.querySelector('i');
            if (result.is_favorite) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                favoriteBtn.classList.add('active');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                favoriteBtn.classList.remove('active');
            }
        }
        showNotification(result.is_favorite ? 'Agregado a favoritos' : 'Removido de favoritos', 'success');
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        showNotification('Error al actualizar favorito: ' + error.message, 'error');
    });
}

function deleteProject(projectId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este proyecto? Esta acción no se puede deshacer.')) {
        return;
    }
    
    SaaSUtils.apiRequest(`/api/projects/${projectId}`, {
        method: 'DELETE'
    })
    .then(result => {
        // Remove project from UI
        const projectCard = document.querySelector(`[data-project-id="${projectId}"]`);
        if (projectCard) {
            projectCard.remove();
        }
        
        // Check if no projects left and show empty state
        const projectsGrid = document.querySelector('.projects-grid');
        if (projectsGrid && projectsGrid.children.length === 0) {
            const emptyState = document.querySelector('.empty-state');
            if (emptyState) {
                emptyState.style.display = 'block';
            }
        }
        
        showNotification('Proyecto eliminado exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error deleting project:', error);
        showNotification('Error al eliminar el proyecto: ' + error.message, 'error');
    });
}

function viewAnalysis(projectId) {
    window.location.href = `/analysis?id=${projectId}`;
}

function exportAllProjects() {
    // Simulate export functionality
    showNotification('Preparando exportación...', 'info');
    
    // Get all projects data (this would typically come from an API)
    const projects = document.querySelectorAll('.project-card');
    let exportData = 'Exportación de Proyectos SaaSGenius\n';
    exportData += '=====================================\n\n';
    
    projects.forEach((card, index) => {
        const title = card.querySelector('.project-title')?.textContent || `Proyecto ${index + 1}`;
        const date = card.querySelector('.project-date')?.textContent || 'Fecha no disponible';
        exportData += `${index + 1}. ${title}\n`;
        exportData += `   Fecha: ${date}\n\n`;
    });
    
    // Create and download file
    const blob = new Blob([exportData], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `proyectos_saasgenius_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification('Proyectos exportados exitosamente', 'success');
}

function showSettings() {
    // Create settings modal
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Configuración de Usuario</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="settings-section">
                    <h4>Preferencias</h4>
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" id="emailNotifications"> 
                            Recibir notificaciones por email
                        </label>
                    </div>
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" id="autoSave"> 
                            Guardar automáticamente
                        </label>
                    </div>
                </div>
                <div class="settings-section">
                    <h4>Tema</h4>
                    <div class="setting-item">
                        <select id="themeSelect">
                            <option value="light">Claro</option>
                            <option value="dark">Oscuro</option>
                            <option value="auto">Automático</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancelar</button>
                <button class="btn btn-primary" onclick="saveSettings()">Guardar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function saveSettings() {
    // This would typically save to backend
    showNotification('Configuración guardada', 'success');
    document.querySelector('.modal-overlay').remove();
}

function logout() {
    if (!confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        return;
    }
    
    SaaSUtils.apiRequest('/auth/logout', {
        method: 'POST'
    })
    .then(result => {
        showNotification('Sesión cerrada exitosamente', 'success');
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 1000);
    })
    .catch(error => {
        console.error('Logout error:', error);
        showNotification('Error al cerrar sesión: ' + error.message, 'error');
    });
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app.init();
    setActiveNavLink();
    
    // Handle URL parameters for view functionality (from index.html)
    const urlParams = new URLSearchParams(window.location.search);
    const viewProjectId = urlParams.get('view');
    
    if (viewProjectId) {
        loadProjectData(viewProjectId);
    }
});

console.log('SaaSGenius script loaded successfully');
