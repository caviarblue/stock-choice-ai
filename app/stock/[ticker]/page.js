'use client';

import { useEffect, useState, use } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function StockDetailPage() {
  const params = useParams();
  const ticker = params.ticker;
  const router = useRouter();
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!ticker) return;
    const sessionId = localStorage.getItem('wealth_ai_session_id') || '';
    
    fetch(`/api/stock/${ticker}?session_id=${sessionId}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load stock data');
        return res.json();
      })
      .then((resData) => {
        setData(resData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [ticker]);

  if (loading) return <div className="text-center py-20 text-slate-500">Loading stock details...</div>;
  if (error) return <div className="text-center py-20 text-red-500">{error}</div>;

  const { stock, history, explanation } = data;

  const chartData = {
    labels: history.map((h) => h.date),
    datasets: [
      {
        label: 'Price',
        data: history.map((h) => h.price),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.2,
        pointRadius: 2,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8', maxTicksLimit: 8 } },
      y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
    },
  };

  const isId = stock.market === 'ID';

  const formatCurrency = (val) => {
    if (isId) {
      if (val >= 1e12) return `Rp ${(val / 1e12).toFixed(2)}T`; // Trillion IDR
      if (val >= 1e9) return `Rp ${(val / 1e9).toFixed(2)}B`;   // Billion IDR
      return `Rp ${val.toLocaleString()}`;
    } else {
      if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
      if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
      return `$${val.toLocaleString()}`;
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 flex-grow">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 uppercase tracking-wider">
            {stock.sector}
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white mt-2 flex items-baseline gap-2">
            {stock.company} <span className="text-slate-500 text-2xl font-semibold">({stock.ticker})</span>
          </h1>
        </div>
        <button
          onClick={() => router.back()}
          className="inline-flex items-center justify-center px-4 py-2 border border-slate-700 bg-slate-800/80 hover:bg-slate-700/80 text-sm font-semibold rounded-xl text-white transition cursor-pointer"
        >
          &larr; Back to Results
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Chart Column */}
        <div className="lg:col-span-2 bg-slate-800/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl h-[400px] flex flex-col">
          <h2 className="text-lg font-bold text-white mb-4">30-Day Price History</h2>
          <div className="flex-grow relative">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        {/* Metrics Column */}
        <div className="bg-slate-800/40 border border-slate-800/80 rounded-2xl p-6 shadow-xl flex flex-col">
          <h2 className="text-lg font-bold text-white mb-4">Key Metrics</h2>
          <div className="divide-y divide-slate-800 flex-grow text-sm">
            <div className="flex justify-between py-3">
              <span className="text-slate-400">Current Price</span>
              <span className="font-extrabold text-white">
                {isId ? `Rp ${Math.round(stock.current_price).toLocaleString()}` : `$${stock.current_price.toFixed(2)}`}
              </span>
            </div>
            <div className="flex justify-between py-3">
              <span className="text-slate-400">Market Cap</span>
              <span className="font-extrabold text-white">{formatCurrency(stock.market_cap)}</span>
            </div>
            <div className="flex justify-between py-3">
              <span className="text-slate-400">P/E Ratio</span>
              <span className="font-extrabold text-white">{stock.pe_ratio}</span>
            </div>
            <div className="flex justify-between py-3">
              <span className="text-slate-400">Volatility (Annualized)</span>
              <span className="font-extrabold text-white">{(stock.volatility * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between py-3">
              <span className="text-slate-400">52-Week Range</span>
              <span className="font-extrabold text-white">
                {isId 
                  ? `Rp ${Math.round(stock.week_52_low).toLocaleString()} - Rp ${Math.round(stock.week_52_high).toLocaleString()}` 
                  : `$${stock.week_52_low.toFixed(2)} - $${stock.week_52_high.toFixed(2)}`}
              </span>
            </div>
            <div className="flex justify-between py-3">
              <span className="text-slate-400">Average Volume</span>
              <span className="font-extrabold text-white">{(stock.avg_volume / 1e6).toFixed(1)}M</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Explanation */}
      <div className="bg-slate-800/50 border border-slate-700/80 rounded-2xl p-6 sm:p-8 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
          <span className="text-emerald-400">AI</span> Recommendation Justification
        </h2>
        <p className="text-slate-300 leading-relaxed text-base">{explanation}</p>
      </div>
    </div>
  );
}
