'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const [market, setMarket] = useState('ID'); // 'US' or 'ID'
  const [risk, setRisk] = useState(1); // 0 = Low, 1 = Medium, 2 = High
  const [budget, setBudget] = useState('10000000');
  const [sector, setSector] = useState('Technology');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [limit, setLimit] = useState(5); // 3, 5, 10, 15
  const [showSettings, setShowSettings] = useState(false);
  const router = useRouter();

  const riskLevels = ['Low', 'Medium', 'High'];

  useEffect(() => {
    const sessionId = localStorage.getItem('wealth_ai_session_id');
    if (sessionId) {
      fetch(`/api/history/${sessionId}`)
        .then((res) => res.json())
        .then((data) => setHistory(data.history || []))
        .catch((err) => console.error('Error fetching history:', err));
    }
  }, []);

  const handleMarketChange = (newMarket) => {
    setMarket(newMarket);
    setBudget(newMarket === 'US' ? '1000' : '10000000');
  };

  const handleClearHistory = async () => {
    const sessionId = localStorage.getItem('wealth_ai_session_id');
    if (!sessionId) return;
    
    if (!confirm('Are you sure you want to clear your recent runs?')) return;
    
    try {
      const response = await fetch(`/api/history/${sessionId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setHistory([]);
      } else {
        alert('Failed to clear history.');
      }
    } catch (err) {
      console.error(err);
      alert('Error clearing history.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let sessionId = localStorage.getItem('wealth_ai_session_id');
      if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substring(2, 11) + Date.now();
        localStorage.setItem('wealth_ai_session_id', sessionId);
      }
      
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          risk_level: riskLevels[risk],
          budget: parseFloat(budget) || (market === 'US' ? 1000 : 10000000),
          sector: sector,
          market: market,
          limit: limit
        }),
      });
      const data = await response.json();
      localStorage.setItem('wealth_ai_last_results', JSON.stringify(data.recommendations));
      router.push('/results');
    } catch (err) {
      console.error(err);
      alert('Failed to get recommendations. Ensure the backend is active.');
      setLoading(false);
    }
  };

  return (
    <div className="w-full mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 flex-grow flex flex-col justify-center">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <h1 className="text-4xl font-extrabold sm:text-5xl lg:text-6xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          Personalized Investing,
          <span className="block text-emerald-400 font-black">Powered by Scratch AI</span>
        </h1>
        <p className="mt-4 text-lg text-slate-400">
          Input your profile and let our custom Cosine Recommender and Logistic Predictor optimize your portfolio trends.
        </p>
      </div>

      <div className="w-full grid grid-cols-1 lg:grid-cols-5 gap-8 items-stretch">
        {/* Input Form */}
        <form onSubmit={handleSubmit} className="lg:col-span-3 bg-slate-800/50 backdrop-blur-md border border-slate-700/80 rounded-2xl p-6 sm:p-8 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4 border-b border-slate-700 pb-3">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <span className="text-emerald-400">01</span> Investment Profile
            </h2>
            <button
              type="button"
              onClick={() => setShowSettings(!showSettings)}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-750 hover:bg-slate-950 text-slate-300 hover:text-white transition duration-200 cursor-pointer flex items-center gap-1.5"
            >
              <span>⚙️</span> Settings
            </button>
          </div>

          {/* Collapsible Advanced Settings */}
          {showSettings && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 mb-4 transition duration-300">
              <h3 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">Advanced Settings</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Market selection */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Market Index</label>
                  <select
                    value={market}
                    onChange={(e) => handleMarketChange(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2 px-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 cursor-pointer"
                  >
                    <option value="US">🇺🇸 US Index (S&P 500)</option>
                    <option value="ID">🇮🇩 Indonesian Index (IDX)</option>
                  </select>
                </div>
                {/* Recommendation Limit selection */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Recommendation Limit</label>
                  <select
                    value={limit}
                    onChange={(e) => setLimit(parseInt(e.target.value))}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2 px-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 cursor-pointer"
                  >
                    <option value={3}>Show Top 3 Stocks</option>
                    <option value={5}>Show Top 5 Stocks</option>
                    <option value={10}>Show Top 10 Stocks</option>
                    <option value={15}>Show Top 15 Stocks</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Risk Level Selector Buttons (Replaces slider) */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-300 mb-3">Risk Tolerance</label>
            <div className="grid grid-cols-3 gap-3">
              {riskLevels.map((level, index) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setRisk(index)}
                  className={`py-3 px-4 rounded-xl text-sm font-bold border transition duration-200 cursor-pointer text-center ${
                    risk === index
                      ? index === 0
                        ? 'bg-blue-500/20 text-blue-400 border-blue-500/50 shadow-md shadow-blue-500/10'
                        : index === 1
                        ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50 shadow-md shadow-yellow-500/10'
                        : 'bg-red-500/20 text-red-400 border-red-500/50 shadow-md shadow-red-500/10'
                      : 'bg-slate-900/40 text-slate-400 border-slate-700/60 hover:border-slate-600 hover:text-slate-200'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-2.5 min-h-[40px] flex items-center">
              {risk === 0 && '💡 Low: seeks conservative, low-volatility stability.'}
              {risk === 1 && '💡 Medium: seeks balanced, moderate-volatility growth.'}
              {risk === 2 && '💡 High: seeks aggressive, high-volatility capital gains.'}
            </p>
          </div>

          {/* Budget Input */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Available Budget ({market === 'US' ? '$' : 'Rp'})
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                {market === 'US' ? '$' : 'Rp'}
              </span>
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder={market === 'US' ? '1000' : '10000000'}
                min="1"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                required
              />
            </div>
          </div>

          {/* Sector Selector */}
          <div className="mb-8">
            <label className="block text-sm font-semibold text-slate-300 mb-2">Preferred Sector</label>
            <select
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 cursor-pointer"
            >
              <option value="Technology">Technology (Software, Semiconductors)</option>
              <option value="Energy">Energy (Oil, gas, exploration)</option>
              <option value="Healthcare">Healthcare (Biotech, pharma, clinics)</option>
              <option value="Financials">Financials (Banking, payments)</option>
              <option value="Consumer">Consumer (Retail, beverages)</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 px-6 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 disabled:from-slate-700 disabled:to-slate-700 text-slate-900 font-extrabold text-lg rounded-xl shadow-lg shadow-emerald-500/10 hover:shadow-emerald-500/20 active:scale-[0.98] transition duration-200 cursor-pointer flex justify-center items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-slate-900" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing Stocks...
              </>
            ) : 'Generate Recommendations'}
          </button>
        </form>

        {/* History Panel */}
        <div className="lg:col-span-2 bg-slate-800/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl flex flex-col">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center justify-between">
            <span className="flex items-center gap-2">
              Recent Runs
              <span className="text-xs bg-slate-700/85 text-slate-300 font-normal px-2 py-0.5 rounded-full border border-slate-700/60">
                {history.length} logged
              </span>
            </span>
            {history.length > 0 && (
              <button
                type="button"
                onClick={handleClearHistory}
                className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 border border-red-500/20 hover:border-red-500/30 transition cursor-pointer"
              >
                Clear All
              </button>
            )}
          </h2>

          <div className={`w-full flex-grow overflow-y-auto space-y-3 pr-2 custom-scrollbar lg:h-0 lg:max-h-none ${showSettings ? 'h-[390px]' : 'h-[300px]'} ${history.length === 0 ? 'flex flex-col justify-center items-center' : ''}`}>
            {history.length === 0 ? (
              <div className="text-center text-slate-500 text-sm max-w-xs px-4">
                No past recommendation runs found. Submit the form to generate suggestions!
              </div>
            ) : (
              history.map((item, index) => (
                <div key={index} className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center justify-between text-sm hover:border-slate-700/60 transition">
                  <div>
                    <span className="font-bold text-white block">{item.ticker}</span>
                    <span className="text-xs text-slate-500">{new Date(item.timestamp).toLocaleDateString()}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs bg-slate-800 px-2 py-0.5 rounded border border-slate-700 text-slate-300 block mb-1">
                      {item.match_score}% Match
                    </span>
                    <span className={`text-xs font-bold ${
                      item.prediction === 'Up' ? 'text-emerald-400' :
                      item.prediction === 'Down' ? 'text-red-400' :
                      'text-yellow-400'
                    }`}>
                      {item.prediction === 'Up' ? '🟢' : item.prediction === 'Down' ? '🔴' : '🟡'} {item.prediction}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
