import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3001';

// Preset sample links to help the user test easily
const SAMPLE_LINKS = [
  { name: "IPOWatch - Subscription Live", url: "https://ipowatch.in/ipo-subscription/" },
  { name: "InvestorGain - Live GMP", url: "https://www.investorgain.com/report/live-ipo-gmp/331/" },
  { name: "Chittorgarh - IPO Info", url: "https://www.chittorgarh.com/" }
];

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0); // 0: Idle, 1: Scraping, 2: AI extraction, 3: Rubric analysis
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [showJson, setShowJson] = useState(false);
  const [history, setHistory] = useState([]);

  // Load history on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('ipo_analysis_history');
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  }, []);

  // Save item to history
  const saveToHistory = (item) => {
    try {
      const updated = [item, ...history.filter(h => h.url !== item.url)].slice(0, 10);
      setHistory(updated);
      localStorage.setItem('ipo_analysis_history', JSON.stringify(updated));
    } catch (err) {
      console.error("Failed to save history:", err);
    }
  };

  const handleAnalyze = async (targetUrl) => {
    const inputUrl = targetUrl || url;
    if (!inputUrl) return;

    setIsLoading(true);
    setError(null);
    setResult(null);
    setLoadingStep(1); // 1. Scraping

    // Step-by-step progress simulation to feel incredibly premium
    const stepInterval = setInterval(() => {
      setLoadingStep((prev) => {
        if (prev === 1) return 2; // Move to AI extraction after 2s
        if (prev === 2) return 3; // Move to Rubric scoring after 4s
        return prev;
      });
    }, 1800);

    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: inputUrl })
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || `HTTP error ${response.status}`);
      }

      const data = await response.json();
      setLoadingStep(4); // Finished
      
      // Delay slightly so the user sees the "Completed" step checkmark
      setTimeout(() => {
        setResult(data);
        saveToHistory({
          url: data.url,
          score: data.score,
          decision: data.decision,
          badge: data.badge,
          date: new Date().toLocaleDateString()
        });
        setIsLoading(false);
        setLoadingStep(0);
      }, 600);

    } catch (err) {
      clearInterval(stepInterval);
      console.error(err);
      setError(err.message || 'Failed to analyze the URL. Please verify your OpenRouter key and try again.');
      setIsLoading(false);
      setLoadingStep(0);
    }
  };

  // Radial progress parameters
  const radius = 75;
  const circumference = 2 * Math.PI * radius;
  const score = result ? result.score : 0;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Determine colors based on decision
  const getDecisionColorClass = (decision) => {
    if (!decision) return '';
    const norm = decision.toLowerCase();
    if (norm.includes('strong')) return 'rec-strong-apply';
    if (norm.includes('apply')) return 'rec-apply';
    if (norm.includes('risky')) return 'rec-risky';
    return 'rec-avoid';
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header animate-fade-in">
        <h1 className="h1 gradient-text">🛡️ IPO Scoring Engine</h1>
        <p>Analyze subscription metrics, GMP premium, financials, and market sentiment instantly</p>
      </header>

      {/* Main Analyzer Form */}
      <section className="glass-card analyzer-form animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <h2 className="h3">Paste IPO Link</h2>
        <div className="input-row">
          <input
            type="url"
            className="glass-input"
            placeholder="e.g. https://www.chittorgarh.com/ipo/company-details..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
          />
          <button
            className="btn-primary"
            onClick={() => handleAnalyze()}
            disabled={isLoading || !url}
          >
            {isLoading ? 'Analyzing...' : '🚀 Analyze Listing'}
          </button>
        </div>

        {/* Sandbox Quick Links */}
        <div className="quick-links">
          <span>Try a sample link:</span>
          {SAMPLE_LINKS.map((link, idx) => (
            <button
              key={idx}
              className="quick-btn"
              onClick={() => {
                setUrl(link.url);
                handleAnalyze(link.url);
              }}
              disabled={isLoading}
            >
              {link.name}
            </button>
          ))}
        </div>
      </section>

      {/* Error Message */}
      {error && (
        <div className="glass-card animate-fade-in" style={{ borderColor: 'var(--color-danger-border)', background: 'var(--color-danger-bg)', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
            <span style={{ fontSize: '2rem', flexShrink: 0 }}>⚠️</span>
            <div style={{ flex: 1 }}>
              <h4 style={{ fontWeight: '700', marginBottom: '8px', fontSize: '1.05rem', color: 'var(--color-danger)' }}>Analysis Failed</h4>
              <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: '1.7' }}>{error}</p>
              <div style={{ background: 'rgba(0,0,0,0.25)', borderRadius: '10px', padding: '14px 18px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.9' }}>
                <strong style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>💡 Tips for best results:</strong>
                <span>• Use direct IPO detail pages from <strong style={{color:'var(--text-primary)'}}>Chittorgarh</strong> or <strong style={{color:'var(--text-primary)'}}>IPOWatch</strong></span><br/>
                <span>• Avoid Zerodha links — they require login and JavaScript</span><br/>
                <span>• Make sure the URL starts with <code style={{fontSize:'0.82rem', background:'rgba(255,255,255,0.07)', padding:'1px 6px', borderRadius:'4px'}}>https://</code></span><br/>
                <span>• Try the sample links above to confirm the tool is working</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading Stepper Panel */}
      {isLoading && (
        <section className="glass-card loading-panel animate-fade-in">
          <div className="loading-spinner"></div>
          <h3 className="h3">Running IPO Scoring Engine</h3>
          <div className="loading-steps">
            <div className={`loading-step ${loadingStep === 1 ? 'active' : ''} ${loadingStep > 1 ? 'completed' : ''}`}>
              <div className="step-indicator">1</div>
              <span>Scraping IPO listing page text</span>
            </div>
            <div className={`loading-step ${loadingStep === 2 ? 'active' : ''} ${loadingStep > 2 ? 'completed' : ''}`}>
              <div className="step-indicator">2</div>
              <span>Extracting metrics using OpenRouter Gemini</span>
            </div>
            <div className={`loading-step ${loadingStep === 3 ? 'active' : ''} ${loadingStep > 3 ? 'completed' : ''}`}>
              <div className="step-indicator">3</div>
              <span>Applying 100-point subscription rubric</span>
            </div>
          </div>
        </section>
      )}

      {/* Main Results Board */}
      {result && !isLoading && (
        <div className="result-layout animate-fade-in">
          {/* Left Panel: Circular Progress & Verdict */}
          <section className="glass-card score-card">
            <h3 className="h3" style={{ marginBottom: '24px' }}>Overall Score</h3>
            
            <div className="radial-container">
              <svg width="180" height="180" className="progress-ring">
                {/* Background track */}
                <circle
                  stroke="rgba(255, 255, 255, 0.04)"
                  fill="transparent"
                  strokeWidth="10"
                  r={radius}
                  cx="90"
                  cy="90"
                />
                {/* Glowing front arc */}
                <circle
                  className="progress-ring-circle"
                  stroke={`url(#gradient-${result.decision.replace(/\s+/g, '')})`}
                  fill="transparent"
                  strokeWidth="10"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  r={radius}
                  cx="90"
                  cy="90"
                />
                
                {/* Gradient Definitions */}
                <defs>
                  <linearGradient id="gradient-StrongApply" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#10B981" />
                    <stop offset="100%" stopColor="#059669" />
                  </linearGradient>
                  <linearGradient id="gradient-Apply" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#06B6D4" />
                    <stop offset="100%" stopColor="#0891B2" />
                  </linearGradient>
                  <linearGradient id="gradient-Risky" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#F59E0B" />
                    <stop offset="100%" stopColor="#D97706" />
                  </linearGradient>
                  <linearGradient id="gradient-Avoid" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#EF4444" />
                    <stop offset="100%" stopColor="#DC2626" />
                  </linearGradient>
                </defs>
              </svg>
              
              <div className="radial-label">
                <span className="radial-score">{result.score}</span>
                <span className="radial-max">points</span>
              </div>
            </div>

            <div className={`rec-badge ${getDecisionColorClass(result.decision)}`}>
              <span>{result.badge}</span>
              <span>{result.decision}</span>
            </div>

            <p className="rec-description">
              {result.score >= 80 && "This listing scores exceptionally high across subscription interest and GMP. It represents an excellent primary market listing opportunity."}
              {result.score >= 60 && result.score < 80 && "Strong metrics in multiple sectors makes this a reasonable applying candidate. Do check final day subscription levels."}
              {result.score >= 40 && result.score < 60 && "Sub-par subscription multiples or weak GMP suggests a risky entry. Apply only with capital you can afford to lock in."}
              {result.score < 40 && "Poor subscription demand combined with unfavorable financials or expensive pricing. Avoid subscribing to this IPO."}
            </p>
          </section>

          {/* Right Panel: Metric Details Grid */}
          <section className="metrics-dashboard">
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 className="h3" style={{ marginBottom: '16px' }}>Rubric Breakdowns</h3>
              <div className="metrics-grid">
                {Object.entries(result.breakdown).map(([key, data]) => (
                  <div key={key} className="glass-card metric-card">
                    <div className="metric-header">
                      <span className="metric-title">{key}</span>
                      <span className="metric-subscore">+{data.score}</span>
                    </div>
                    <div>
                      <div className="metric-value">{data.value}</div>
                      <div className="progress-bar-bg">
                        <div 
                          className="progress-bar-fill"
                          style={{ 
                            width: `${(data.score / data.max) * 100}%`,
                            background: data.score === 0 ? 'rgba(255,255,255,0.1)' : undefined
                          }}
                        />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        <span>Score Contribution</span>
                        <span>Max {data.max}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Collapsible raw details */}
            <div className="glass-card collapsible-container">
              <div 
                className="collapsible-header" 
                onClick={() => setShowJson(!showJson)}
              >
                <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>📄 View AI Extracted Data</span>
                <span>{showJson ? '▲' : '▼'}</span>
              </div>
              {showJson && (
                <div className="collapsible-content">
                  <pre>{JSON.stringify(result.raw_metrics, null, 2)}</pre>
                </div>
              )}
            </div>
          </section>
        </div>
      )}

      {/* History List */}
      {history.length > 0 && (
        <section className="glass-card animate-fade-in" style={{ padding: '24px', animationDelay: '0.2s' }}>
          <h3 className="h3" style={{ marginBottom: '16px' }}>Recent Searches</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {history.map((item, idx) => (
              <div 
                key={idx} 
                className="glass-card" 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between', 
                  padding: '12px 20px', 
                  background: 'rgba(255, 255, 255, 0.01)',
                  flexWrap: 'wrap',
                  gap: '12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '200px' }}>
                  <span className={`rec-badge ${getDecisionColorClass(item.decision)}`} style={{ fontSize: '0.85rem', padding: '4px 10px', margin: 0 }}>
                    {item.badge} {item.score} pts
                  </span>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', maxWidth: '350px' }}>
                    {item.url}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.date}</span>
                  <button 
                    className="quick-btn" 
                    style={{ padding: '4px 8px', fontSize: '0.75rem' }} 
                    onClick={() => {
                      setUrl(item.url);
                      handleAnalyze(item.url);
                    }}
                    disabled={isLoading}
                  >
                    Re-Analyze
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
