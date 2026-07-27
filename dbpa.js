// DBPA Frontend Engine
const DBPAEngine = {
  charts: {},
  currentTab: 'analysis',
  
  init() {
    this.setupSliders();
    this.setupEventListeners();
    this.setupTabNavigation();
  },
  
  setupTabNavigation() {
    const tags = document.querySelectorAll('.tag');
    tags.forEach(tag => {
      tag.addEventListener('click', () => {
        const tab = tag.dataset.tab;
        this.switchTab(tab);
      });
    });
  },
  
  switchTab(tabName) {
    // Update tab active state
    document.querySelectorAll('.tag').forEach(t => t.classList.remove('tag--active'));
    document.querySelector(`.tag[data-tab="${tabName}"]`).classList.add('tag--active');
    
    // Hide all sections
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'none';
    document.getElementById('reportsSection').style.display = 'none';
    
    // Show selected section
    if (tabName === 'analysis') {
      document.getElementById('resultsSection').style.display = 'block';
    } else if (tabName === 'history') {
      document.getElementById('historySection').style.display = 'block';
      this.loadHistory();
    } else if (tabName === 'reports') {
      document.getElementById('reportsSection').style.display = 'block';
    }
    
    this.currentTab = tabName;
  },
  
  setupSliders() {
    const sliders = [
      { id: 'sleepHours', display: 'sleepVal', suffix: 'hrs' },
      { id: 'screenHours', display: 'screenVal', suffix: 'hrs' },
      { id: 'workHours', display: 'workVal', suffix: 'hrs' },
      { id: 'exerciseHours', display: 'exerciseVal', suffix: 'hrs' },
      { id: 'socialMedia', display: 'socialVal', suffix: 'hrs' },
      { id: 'mealQuality', display: 'mealVal', suffix: '/ 10' },
      { id: 'averageScore', display: 'averageScoreVal', suffix: '%' },
      { id: 'procrastination', display: 'procrastinationVal', suffix: '/ 10' },
      { id: 'attentionSpan', display: 'attentionSpanVal', suffix: '/ 10' }
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
      let username = document.getElementById('username').value.trim();
      
      // Auto-assign username if not provided
      if (!username) {
        username = this.generateUsername();
      }
      
      const inputData = {
        sleepHours: parseFloat(document.getElementById('sleepHours').value),
        screenHours: parseFloat(document.getElementById('screenHours').value),
        workHours: parseFloat(document.getElementById('workHours').value),
        exerciseHours: parseFloat(document.getElementById('exerciseHours').value),
        socialMedia: parseFloat(document.getElementById('socialMedia').value),
        mealQuality: parseFloat(document.getElementById('mealQuality').value),
        averageScore: parseFloat(document.getElementById('averageScore').value),
        procrastination: parseFloat(document.getElementById('procrastination').value),
        attentionSpan: parseFloat(document.getElementById('attentionSpan').value),
        ageRange: document.getElementById('ageRange').value,
        username: username
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
        // Store user ID for reference
        this.currentUserId = result.userId;
        
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
  },
  
  async loadHistory() {
    const historyGrid = document.getElementById('historyGrid');
    historyGrid.innerHTML = '<div class="history-empty"><span class="history-empty-icon">◈</span><p>Loading history...</p></div>';
    
    try {
      const response = await fetch('/api/reports/history');
      const result = await response.json();
      
      if (result.success && result.history && result.history.length > 0) {
        // Store full reports for quick access
        this.reportsCache = {};
        result.history.forEach(report => {
          this.reportsCache[report.userId] = report;
        });
        this.displayHistory(result.history);
      } else {
        historyGrid.innerHTML = '<div class="history-empty"><span class="history-empty-icon">◈</span><p>No analysis history yet. Run an analysis to see your history here.</p></div>';
      }
    } catch (error) {
      console.error('Error loading history:', error);
      historyGrid.innerHTML = '<div class="history-empty"><span class="history-empty-icon">◈</span><p>Error loading history. Please try again.</p></div>';
    }
  },
  
  displayHistory(history) {
    const historyGrid = document.getElementById('historyGrid');
    historyGrid.innerHTML = '';
    
    history.forEach(report => {
      const card = document.createElement('div');
      card.className = 'history-card';
      card.onclick = () => this.showReportDetail(report.userId);
      
      const date = new Date(report.timestamp);
      const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      
      card.innerHTML = `
        <div class="history-card__header">
          <div>
            <span class="history-card__username">${report.username || 'Anonymous'}</span>
            <span class="history-card__id">ID: ${report.userId}</span>
          </div>
          <span class="history-card__date">${formattedDate}</span>
        </div>
        <div class="history-card__scores">
          <div class="history-card__score">
            <div class="history-card__score-label">Stress</div>
            <div class="history-card__score-value stress">${report.results.stressIndex}</div>
          </div>
          <div class="history-card__score">
            <div class="history-card__score-label">Anxiety</div>
            <div class="history-card__score-value anxiety">${report.results.anxietyIndex}</div>
          </div>
          <div class="history-card__score">
            <div class="history-card__score-label">Productivity</div>
            <div class="history-card__score-value productivity">${report.results.productivityRate}</div>
          </div>
          <div class="history-card__score">
            <div class="history-card__score-label">Wellbeing</div>
            <div class="history-card__score-value wellbeing">${report.results.overallWellbeing}</div>
          </div>
        </div>
      `;
      
      historyGrid.appendChild(card);
    });
  },
  
  async showReportDetail(userId) {
    const reportsDetail = document.getElementById('reportsDetail');
    reportsDetail.innerHTML = '<div class="reports-empty"><span class="reports-empty-icon">◫</span><p>Loading report details...</p></div>';
    
    // Switch to reports tab
    document.querySelectorAll('.tag').forEach(t => t.classList.remove('tag--active'));
    document.querySelector('.tag[data-tab="reports"]').classList.add('tag--active');
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'none';
    document.getElementById('reportsSection').style.display = 'block';
    
    try {
      // Check if report is in cache first
      let report = null;
      if (this.reportsCache && this.reportsCache[userId]) {
        report = this.reportsCache[userId];
      } else {
        // Fetch from API if not in cache
        const response = await fetch(`/api/reports/${userId}`);
        const result = await response.json();
        report = result.success ? result.report : null;
      }
      
      if (report) {
        this.displayReportDetail(report);
      } else {
        reportsDetail.innerHTML = '<div class="reports-empty"><span class="reports-empty-icon">◫</span><p>Report not found.</p></div>';
      }
    } catch (error) {
      console.error('Error loading report:', error);
      reportsDetail.innerHTML = '<div class="reports-empty"><span class="reports-empty-icon">◫</span><p>Error loading report. Please try again.</p></div>';
    }
  },
  
  displayReportDetail(report) {
    const reportsDetail = document.getElementById('reportsDetail');
    const date = new Date(report.timestamp);
    const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    
    const input = report.inputParameters;
    const results = report.results;
    const insights = report.detailedInsights || {};
    
    let html = `
      <div class="report-header">
        <div>
          <div class="report-user-id">User ID: ${report.userId}</div>
          <div class="report-username">Username: ${report.username || 'Anonymous'}</div>
          <div class="report-timestamp">${formattedDate}</div>
        </div>
      </div>
      
      <div class="report-section">
        <h3 class="report-section-title">Input Parameters</h3>
        <div class="report-params-grid">
          <div class="report-param">
            <div class="report-param__label">Sleep Hours</div>
            <div class="report-param__value">${input.sleepHours} hrs</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Screen Time</div>
            <div class="report-param__value">${input.screenHours} hrs</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Work/Study Hours</div>
            <div class="report-param__value">${input.workHours} hrs</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Exercise Hours</div>
            <div class="report-param__value">${input.exerciseHours} hrs</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Social Media</div>
            <div class="report-param__value">${input.socialMedia} hrs</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Meal Quality</div>
            <div class="report-param__value">${input.mealQuality}/10</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Average Score</div>
            <div class="report-param__value">${input.averageScore}%</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Procrastination</div>
            <div class="report-param__value">${input.procrastination}/10</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Attention Span</div>
            <div class="report-param__value">${input.attentionSpan}/10</div>
          </div>
          <div class="report-param">
            <div class="report-param__label">Age Range</div>
            <div class="report-param__value">${input.ageRange || 'All Ages'}</div>
          </div>
        </div>
      </div>
      
      <div class="report-section">
        <h3 class="report-section-title">Analysis Results</h3>
        <div class="report-results-grid">
          <div class="report-result-card stress">
            <div class="report-result-card__label">Stress Index</div>
            <div class="report-result-card__value">${results.stressIndex}</div>
            <div class="report-result-card__level">${results.stressLevel}</div>
          </div>
          <div class="report-result-card anxiety">
            <div class="report-result-card__label">Anxiety Index</div>
            <div class="report-result-card__value">${results.anxietyIndex}</div>
            <div class="report-result-card__level">${results.anxietyLevel}</div>
          </div>
          <div class="report-result-card productivity">
            <div class="report-result-card__label">Productivity Rate</div>
            <div class="report-result-card__value">${results.productivityRate}</div>
            <div class="report-result-card__level">${results.productivityLevel}</div>
          </div>
          <div class="report-result-card wellbeing">
            <div class="report-result-card__label">Overall Wellbeing</div>
            <div class="report-result-card__value">${results.overallWellbeing}</div>
            <div class="report-result-card__level">${results.wellbeingLevel}</div>
          </div>
        </div>
      </div>
    `;
    
    // Add recommendations
    if (report.recommendations && report.recommendations.length > 0) {
      html += `
        <div class="report-section">
          <h3 class="report-section-title">AI Recommendations</h3>
          <div class="report-recommendations">
      `;
      
      report.recommendations.forEach(reco => {
        html += `
          <div class="report-reco">
            <div class="report-reco__category">${reco.category}</div>
            <div class="report-reco__title">${reco.title}</div>
            <div class="report-reco__desc">${reco.description}</div>
            <span class="report-reco__badge ${reco.impact.toLowerCase()}">${reco.impact}</span>
          </div>
        `;
      });
      
      html += `</div></div>`;
    }
    
    // Add detailed insights
    if (insights.percentiles) {
      html += `
        <div class="report-section">
          <h3 class="report-section-title">Detailed Insights</h3>
          <div class="report-insights">
      `;
      
      const percentiles = insights.percentiles;
      if (percentiles.stress !== null && percentiles.stress !== undefined) {
        html += `
          <div class="report-insight">
            <div class="report-insight__label">Stress Percentile</div>
            <div class="report-insight__value">Your stress level is higher than ${percentiles.stress}% of users in the dataset.</div>
          </div>
        `;
      }
      if (percentiles.productivity !== null && percentiles.productivity !== undefined) {
        html += `
          <div class="report-insight">
            <div class="report-insight__label">Productivity Percentile</div>
            <div class="report-insight__value">Your productivity is higher than ${percentiles.productivity}% of users in the dataset.</div>
          </div>
        `;
      }
      if (percentiles.sleep !== null && percentiles.sleep !== undefined) {
        html += `
          <div class="report-insight">
            <div class="report-insight__label">Sleep Percentile</div>
            <div class="report-insight__value">Your sleep duration is higher than ${percentiles.sleep}% of users in the dataset.</div>
          </div>
        `;
      }
      if (percentiles.phone_usage !== null && percentiles.phone_usage !== undefined) {
        html += `
          <div class="report-insight">
            <div class="report-insight__label">Phone Usage Percentile</div>
            <div class="report-insight__value">Your phone usage is higher than ${percentiles.phone_usage}% of users in the dataset.</div>
          </div>
        `;
      }
      
      html += `</div></div>`;
    }
    
    // Add similar users section
    if (insights.similarUsers && insights.similarUsers.length > 0) {
      html += `
        <div class="report-section">
          <h3 class="report-section-title">Similar Users in Dataset</h3>
          <div class="similar-users-detail">
      `;
      
      insights.similarUsers.forEach(user => {
        html += `
          <div class="similar-user-detail-card">
            <div class="similar-user-detail-header">
              <span class="similar-user-detail-id">${user.user_id}</span>
              <span class="similar-user-detail-match">${(100 - (user.similarity_score || 0) * 10).toFixed(0)}% Match</span>
            </div>
            <div class="similar-user-detail-info">
              <span>Age: ${user.age}</span> · <span>${user.occupation}</span> · <span>${user.device}</span>
            </div>
            <div class="similar-user-detail-metrics">
              <div class="similar-user-metric">
                <span class="label">Phone</span>
                <span class="value">${user.daily_phone_hours}h</span>
              </div>
              <div class="similar-user-metric">
                <span class="label">Social</span>
                <span class="value">${user.social_media_hours}h</span>
              </div>
              <div class="similar-user-metric">
                <span class="label">Sleep</span>
                <span class="value">${user.sleep_hours}h</span>
              </div>
              <div class="similar-user-metric">
                <span class="label">Stress</span>
                <span class="value">${user.stress_level}</span>
              </div>
              <div class="similar-user-metric">
                <span class="label">Productivity</span>
                <span class="value">${user.productivity_score}</span>
              </div>
            </div>
          </div>
        `;
      });
      
      html += `</div></div>`;
    }
    
    // Add comprehensive analysis summary
    html += `
      <div class="report-section">
        <h3 class="report-section-title">Analysis Summary</h3>
        <div class="report-summary">
          <p><strong>Stress Analysis:</strong> ${this.getStressSummary(results.stressIndex, results.stressLevel)}</p>
          <p><strong>Anxiety Analysis:</strong> ${this.getAnxietySummary(results.anxietyIndex, results.anxietyLevel)}</p>
          <p><strong>Productivity Analysis:</strong> ${this.getProductivitySummary(results.productivityRate, results.productivityLevel)}</p>
          <p><strong>Overall Wellbeing:</strong> ${this.getWellbeingSummary(results.overallWellbeing, results.wellbeingLevel)}</p>
        </div>
      </div>
    `;
    
    reportsDetail.innerHTML = html;
  },
  
  getStressSummary(value, level) {
    if (value < 20) return `Your stress level is LOW (${value}). You're managing stress well with healthy habits.`;
    if (value < 40) return `Your stress level is MODERATE (${value}). Some areas could be improved to reduce stress.`;
    if (value < 60) return `Your stress level is ELEVATED (${value}). Consider implementing stress management techniques.`;
    if (value < 80) return `Your stress level is HIGH (${value}). Immediate attention to lifestyle factors is recommended.`;
    return `Your stress level is CRITICAL (${value}). Urgent changes to your daily habits are needed.`;
  },
  
  getAnxietySummary(value, level) {
    if (value < 20) return `Your anxiety level is CALM (${value}). You're handling situations well.`;
    if (value < 40) return `Your anxiety level is MILD (${value}). Minor concerns exist but are manageable.`;
    if (value < 60) return `Your anxiety level is MODERATE (${value}). Some triggers may need attention.`;
    if (value < 80) return `Your anxiety level is SEVERE (${value}). Consider seeking strategies to manage anxiety.`;
    return `Your anxiety level is ACUTE (${value}). Professional support may be beneficial.`;
  },
  
  getProductivitySummary(value, level) {
    if (value < 30) return `Your productivity is LOW (${value}). Focus on building consistent habits.`;
    if (value < 50) return `Your productivity is BELOW AVERAGE (${value}). Room for improvement with better time management.`;
    if (value < 70) return `Your productivity is AVERAGE (${value}). You're doing well but can optimize further.`;
    if (value < 85) return `Your productivity is HIGH (${value}). You're performing above average.`;
    return `Your productivity is PEAK (${value}). Excellent work on maintaining high productivity!`;
  },
  
  getWellbeingSummary(value, level) {
    if (value >= 80) return `Your overall wellbeing is EXCELLENT (${value}). Keep up the great work!`;
    if (value >= 65) return `Your overall wellbeing is GOOD (${value}). Maintain healthy habits.`;
    if (value >= 50) return `Your overall wellbeing is FAIR (${value}). Some areas need attention.`;
    if (value >= 35) return `Your overall wellbeing is POOR (${value}). Consider lifestyle changes.`;
    return `Your overall wellbeing is CRITICAL (${value}). Immediate action recommended.`;
  },
  
  generateUsername() {
    const adjectives = ['Digital', 'Smart', 'Focused', 'Balanced', 'Productive', 'Mindful', 'Active', 'Calm', 'Efficient', 'Adaptive'];
    const nouns = ['User', 'Analyst', 'Explorer', 'Thinker', 'Learner', 'Creator', 'Builder', 'Solver', 'Navigator', 'Observer'];
    
    const randomAdjective = adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
    const randomNumber = Math.floor(Math.random() * 999) + 1;
    
    return `${randomAdjective}${randomNoun}${randomNumber}`;
  },
  
  async exportReports() {
    try {
      const response = await fetch('/api/reports/export');
      if (response.ok) {
        // Create a blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dbpa_reports_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      } else {
        const result = await response.json();
        alert('Export failed: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error exporting reports:', error);
      alert('Error exporting reports: ' + error.message);
    }
  },

  async clearAllHistory() {
    // Ask for confirmation
    const confirmed = confirm('⚠ Are you sure you want to clear ALL analysis history? This cannot be undone.');
    
    if (!confirmed) {
      return;
    }
    
    try {
      const response = await fetch('/api/reports/clear', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert('✓ All history cleared successfully');
        this.loadHistory(); // Refresh the history display
      } else {
        alert('Error: ' + (result.error || 'Failed to clear history'));
      }
    } catch (error) {
      console.error('Error clearing history:', error);
      alert('Error clearing history: ' + error.message);
    }
  },
  
  async clearHistory() {
    if (!confirm('Are you sure you want to clear all history? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch('/api/reports/clear', {
        method: 'DELETE'
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert('History cleared successfully!');
        this.loadHistory(); // Refresh the history view
        this.reportsCache = {}; // Clear cache
      } else {
        alert('Failed to clear history: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error clearing history:', error);
      alert('Error clearing history: ' + error.message);
    }
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  DBPAEngine.init();
});
