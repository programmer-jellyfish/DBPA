// DBPA Frontend Engine
const DBPAEngine = {
  charts: {},
  
  init() {
    this.setupSliders();
    this.setupEventListeners();
  },
  
  setupSliders() {
    const sliders = [
      { id: 'sleepHours', display: 'sleepVal', suffix: 'hrs' },
      { id: 'screenHours', display: 'screenVal', suffix: 'hrs' },
      { id: 'workHours', display: 'workVal', suffix: 'hrs' },
      { id: 'exerciseHours', display: 'exerciseVal', suffix: 'hrs' },
      { id: 'socialMedia', display: 'socialVal', suffix: 'hrs' },
      { id: 'mealQuality', display: 'mealVal', suffix: '/ 10' }
    ];
    
    sliders.forEach(slider => {
      const element = document.getElementById(slider.id);
      const display = document.getElementById(slider.display);
      
      element.addEventListener('input', () => {
        const value = parseFloat(element.value);
        const displayValue = slider.id === 'mealQuality' ? 
          Math.round(value) : 
          value.toFixed(1);
        display.textContent = displayValue + ' ' + slider.suffix;
      });
    });
  },
  
  setupEventListeners() {
    const btn = document.getElementById('analyzeBtn');
    btn.addEventListener('click', () => this.analyze());
  },
  
  async analyze() {
    const btn = document.getElementById('analyzeBtn');
    const loader = document.getElementById('btnLoader');
    
    // Disable button and show loader
    btn.disabled = true;
    loader.style.display = 'inline-block';
    btn.style.opacity = '0.6';
    
    try {
      const inputData = {
        sleepHours: parseFloat(document.getElementById('sleepHours').value),
        screenHours: parseFloat(document.getElementById('screenHours').value),
        workHours: parseFloat(document.getElementById('workHours').value),
        exerciseHours: parseFloat(document.getElementById('exerciseHours').value),
        socialMedia: parseFloat(document.getElementById('socialMedia').value),
        mealQuality: parseFloat(document.getElementById('mealQuality').value)
      };
      
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(inputData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        this.displayResults(result);
        this.initializeCharts(result.chartData);
        
        // Display dataset insights if available
        if (result.dataset && result.dataset.similarUsers) {
          this.displayDatasetInsights(result.dataset);
        }
      } else {
        alert('Analysis failed: ' + result.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to backend: ' + error.message);
    } finally {
      // Re-enable button and hide loader
      btn.disabled = false;
      loader.style.display = 'none';
      btn.style.opacity = '1';
    }
  },
  
  displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    const scores = result.scores;
    
    // Update Stress Card
    document.getElementById('stressNumber').textContent = scores.stress;
    document.getElementById('stressLevel').textContent = scores.stressLevel;
    document.getElementById('stressBar').style.width = scores.stress + '%';
    document.getElementById('stressBar').style.backgroundColor = this.getStressColor(scores.stress);
    document.getElementById('stressDesc').textContent = 'Stress level: ' + scores.stressLevel;
    
    // Update Anxiety Card
    document.getElementById('anxietyNumber').textContent = scores.anxiety;
    document.getElementById('anxietyLevel').textContent = scores.anxietyLevel;
    document.getElementById('anxietyBar').style.width = scores.anxiety + '%';
    document.getElementById('anxietyBar').style.backgroundColor = this.getAnxietyColor(scores.anxiety);
    document.getElementById('anxietyDesc').textContent = 'Anxiety level: ' + scores.anxietyLevel;
    
    // Update Productivity Card
    document.getElementById('productivityNumber').textContent = scores.productivity;
    document.getElementById('productivityLevel').textContent = scores.productivityLevel;
    document.getElementById('productivityBar').style.width = scores.productivity + '%';
    document.getElementById('productivityBar').style.backgroundColor = '#44ff88';
    document.getElementById('productivityDesc').textContent = 'Productivity: ' + scores.productivityLevel;
    
    // Update Overall Card
    document.getElementById('overallNumber').textContent = scores.overall;
    document.getElementById('overallLevel').textContent = this.getWellbeingLevel(scores.overall);
    this.updateRingChart(scores.overall);
    
    // Update Recommendations
    this.displayRecommendations(result.recommendations);
  },
  
  displayRecommendations(recommendations) {
    const recoGrid = document.getElementById('recoGrid');
    recoGrid.innerHTML = '';
    
    recommendations.forEach(reco => {
      const card = document.createElement('div');
      card.className = 'reco-card';
      card.setAttribute('data-impact', reco.impact.toLowerCase());
      
      card.innerHTML = `
        <div class="reco-icon">${reco.icon}</div>
        <div class="reco-content">
          <div class="reco-category">${reco.category}</div>
          <h3 class="reco-title">${reco.title}</h3>
          <p class="reco-desc">${reco.description}</p>
          <span class="reco-badge reco-badge--${reco.impact.toLowerCase()}">${reco.impact}</span>
        </div>
      `;
      
      recoGrid.appendChild(card);
    });
  },
  
  getStressColor(value) {
    if (value < 20) return '#44ff88';
    if (value < 40) return '#88ff44';
    if (value < 60) return '#ffff44';
    if (value < 80) return '#ff8844';
    return '#ff4444';
  },
  
  getAnxietyColor(value) {
    if (value < 20) return '#44ccff';
    if (value < 40) return '#4488ff';
    if (value < 60) return '#8844ff';
    if (value < 80) return '#ff4488';
    return '#ff0044';
  },
  
  getWellbeingLevel(value) {
    if (value >= 80) return 'EXCELLENT';
    if (value >= 65) return 'GOOD';
    if (value >= 50) return 'FAIR';
    if (value >= 35) return 'POOR';
    return 'CRITICAL';
  },
  
  updateRingChart(overallScore) {
    const canvas = document.getElementById('ringChart');
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 45;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background circle
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fill();
    
    // Draw score arc
    const scorePercent = overallScore / 100;
    const color = this.getStressColor(100 - overallScore);
    ctx.strokeStyle = color;
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * scorePercent);
    ctx.stroke();
    
    // Draw text
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 24px Syne';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(Math.round(overallScore), centerX, centerY);
  },
  
  initializeCharts(chartData) {
    // Destroy existing charts
    Object.keys(this.charts).forEach(key => {
      if (this.charts[key]) {
        this.charts[key].destroy();
      }
    });
    
    // Radar Chart
    const radarCtx = document.getElementById('radarChart').getContext('2d');
    this.charts.radar = new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: chartData.radar.labels,
        datasets: chartData.radar.datasets
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: { color: '#fff', font: { size: 12 } }
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#aaa' }
          }
        }
      }
    });
    
    // Polar Chart
    const polarCtx = document.getElementById('polarChart').getContext('2d');
    this.charts.polar = new Chart(polarCtx, {
      type: 'polarArea',
      data: {
        labels: chartData.polar.labels,
        datasets: chartData.polar.datasets
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: { color: '#fff', font: { size: 12 } }
          }
        },
        scales: {
          r: {
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#aaa' }
          }
        }
      }
    });
    
    // Bar Chart
    const barCtx = document.getElementById('barChart').getContext('2d');
    this.charts.bar = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: chartData.bar.labels,
        datasets: chartData.bar.datasets
      },
      options: {
        responsive: true,
        indexAxis: 'x',
        plugins: {
          legend: {
            labels: { color: '#fff', font: { size: 12 } }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#aaa' }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#aaa' }
          }
        }
      }
    });
    
    // Line Chart
    const lineCtx = document.getElementById('lineChart').getContext('2d');
    this.charts.line = new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: chartData.line.labels,
        datasets: chartData.line.datasets
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: { color: '#fff', font: { size: 12 } }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#aaa' }
          },
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#aaa' }
          }
        }
      }
    });
  },
  
  displayDatasetInsights(dataset) {
    if (!dataset.similarUsers || dataset.similarUsers.length === 0) {
      return;
    }
    
    // Add insights section HTML if it doesn't exist
    let insightsSection = document.getElementById('datasetInsights');
    if (!insightsSection) {
      const resultsSection = document.getElementById('resultsSection');
      insightsSection = document.createElement('div');
      insightsSection.id = 'datasetInsights';
      insightsSection.innerHTML = `
        <div class="panel-header" style="margin-top:60px">
          <span class="panel-badge">05</span>
          <h2 class="panel-title">Dataset Comparison</h2>
          <span class="panel-line"></span>
        </div>
        
        <div class="comparison-grid" id="comparisonGrid"></div>
        
        <div class="panel-header" style="margin-top:60px">
          <span class="panel-badge">06</span>
          <h2 class="panel-title">Similar Users in Dataset</h2>
          <span class="panel-line"></span>
        </div>
        
        <div class="similar-users-grid" id="similarUsersGrid"></div>
      `;
      resultsSection.appendChild(insightsSection);
    }
    
    // Display percentiles
    if (dataset.percentiles) {
      const comparisonGrid = document.getElementById('comparisonGrid');
      comparisonGrid.innerHTML = `
        <div class="percentile-card">
          <div class="percentile-label">Stress Percentile</div>
          <div class="percentile-number">${dataset.percentiles.stress || 'N/A'}%</div>
          <div class="percentile-desc">Higher is worse</div>
        </div>
        <div class="percentile-card">
          <div class="percentile-label">Productivity Percentile</div>
          <div class="percentile-number">${dataset.percentiles.productivity || 'N/A'}%</div>
          <div class="percentile-desc">Higher is better</div>
        </div>
        <div class="percentile-card">
          <div class="percentile-label">Sleep Percentile</div>
          <div class="percentile-number">${dataset.percentiles.sleep || 'N/A'}%</div>
          <div class="percentile-desc">Context dependent</div>
        </div>
        <div class="percentile-card">
          <div class="percentile-label">Phone Usage Percentile</div>
          <div class="percentile-number">${dataset.percentiles.phone_usage || 'N/A'}%</div>
          <div class="percentile-desc">Lower is better</div>
        </div>
      `;
    }
    
    // Display similar users
    const similarUsersGrid = document.getElementById('similarUsersGrid');
    similarUsersGrid.innerHTML = '';
    
    dataset.similarUsers.forEach((user, index) => {
      const userCard = document.createElement('div');
      userCard.className = 'similar-user-card';
      userCard.innerHTML = `
        <div class="user-header">
          <div class="user-id">${user.user_id}</div>
          <div class="user-similarity">
            <span class="similarity-badge">${(100 - user.similarity_score * 10).toFixed(0)}% Match</span>
          </div>
        </div>
        <div class="user-info">
          <div class="user-detail"><span class="label">Age:</span> ${user.age}</div>
          <div class="user-detail"><span class="label">Occupation:</span> ${user.occupation}</div>
          <div class="user-detail"><span class="label">Device:</span> ${user.device}</div>
        </div>
        <div class="user-metrics">
          <div class="metric">
            <span class="metric-label">Phone</span>
            <span class="metric-value">${user.daily_phone_hours.toFixed(1)}h</span>
          </div>
          <div class="metric">
            <span class="metric-label">Social</span>
            <span class="metric-value">${user.social_media_hours.toFixed(1)}h</span>
          </div>
          <div class="metric">
            <span class="metric-label">Sleep</span>
            <span class="metric-value">${user.sleep_hours.toFixed(1)}h</span>
          </div>
          <div class="metric">
            <span class="metric-label">Stress</span>
            <span class="metric-value">${user.stress_level}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Productivity</span>
            <span class="metric-value">${user.productivity_score}</span>
          </div>
        </div>
      `;
      similarUsersGrid.appendChild(userCard);
    });
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  DBPAEngine.init();
});
