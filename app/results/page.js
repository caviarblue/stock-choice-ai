'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ResultsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const data = localStorage.getItem('wealth_ai_last_results');
    if (data) {
      setRecommendations(JSON.parse(data));
    } else {
      router.push('/');
    }
  }, [router]);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 flex-grow">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            AI Stock Matches
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Top {recommendations.length} stocks recommended based on your preferences and predicted trends.
          </p>
        </div>
        <Link
          href="/"
          className="inline-flex items-center justify-center px-4 py-2 border border-slate-700 bg-slate-800/80 hover:bg-slate-700/80 text-sm font-semibold rounded-xl text-white transition cursor-pointer"
        >
          &larr; Refine Profile
        </Link>
      </div>


      {recommendations.length === 0 ? (
        <div className="text-center py-20 text-slate-500">
          Loading recommendations...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((rec, index) => {
            const maxScore = recommendations.length > 0 ? Math.max(...recommendations.map(r => r.match_score)) : 0;
            const isTopMatch = rec.match_score === maxScore && maxScore > 0;
            return (
              <div
                key={rec.ticker}
                className={`relative group flex flex-col backdrop-blur-md border rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] cursor-pointer ${
                  isTopMatch 
                    ? 'bg-slate-800/70 border-emerald-500/60 shadow-emerald-500/5 ring-1 ring-emerald-500/20 hover:border-emerald-400' 
                    : 'bg-slate-800/40 border-slate-850 hover:border-slate-700'
                }`}
              >
                {isTopMatch && (
                  <span className="absolute -top-2.5 left-4 bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500 text-slate-950 text-[9px] font-black uppercase tracking-widest px-3 py-0.5 rounded-full shadow-md shadow-emerald-500/20 z-10">
                    ⭐ MOST RECOMMENDED
                  </span>
                )}
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-grow">
                  <h2 className="text-xl font-black text-white tracking-tight flex justify-between items-baseline pr-2">
                    <span className="flex items-center gap-1">
                      {rec.ticker}
                      {isTopMatch && <span className="text-amber-400 text-sm">★</span>}
                    </span>
                    <span className="text-sm font-extrabold text-emerald-400">
                      {rec.market === 'ID'
                        ? `Rp ${Math.round(rec.current_price).toLocaleString()}`
                        : `$${rec.current_price.toFixed(2)}`}
                    </span>
                  </h2>
                  <p className="text-xs text-slate-400 line-clamp-1">{rec.company}</p>
                </div>
                <span className="text-xs font-semibold px-2 py-1 rounded bg-slate-900/80 text-slate-400 border border-slate-800 shrink-0">
                  {rec.sector}
                </span>
              </div>

              {/* Match Score */}
              <div className="mb-5">
                <div className="flex justify-between items-baseline mb-1">
                  <span className="text-xs text-slate-400">Recommendation Match</span>
                  <span className="text-sm font-extrabold text-emerald-400">{rec.match_score}%</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 transition-all duration-1000"
                    style={{ width: `${rec.match_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Most Recommended Info Badge */}
              {isTopMatch && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-start gap-2">
                  <span className="text-sm shrink-0">💡</span>
                  <span>
                    <strong>Top Choice:</strong> This stock represents the highest-scoring recommendation aligned with your risk tolerance, budget, and selected sector.
                  </span>
                </div>
              )}

              {/* Divider */}
              <div className="border-t border-slate-800/80 my-2"></div>

              {/* Predictor Badge & Confidence */}
              <div className="flex items-center justify-between py-2 mb-4">
                <div>
                  <span className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">Predicted Trend</span>
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                    rec.prediction === 'Up' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                    rec.prediction === 'Down' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                    'bg-yellow-505/10 text-yellow-400 border border-yellow-500/20'
                  }`}>
                    {rec.prediction === 'Up' ? '🟢' : rec.prediction === 'Down' ? '🔴' : '🟡'} {rec.prediction}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">AI Confidence</span>
                  <span className="text-sm font-extrabold text-slate-200">{rec.confidence}%</span>
                </div>
              </div>

              {/* Footer View Details */}
              <div className="mt-auto pt-2">
                <Link
                  href={`/stock/${rec.ticker}`}
                  className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-950 text-slate-200 hover:text-white border border-slate-800 hover:border-slate-700 font-bold text-sm rounded-xl text-center transition block group-hover:border-emerald-500/30"
                >
                  View Live Chart &amp; Metrics
                </Link>
              </div>
            </div>
          );
        })}
        </div>
      )}
    </div>
  );
}
