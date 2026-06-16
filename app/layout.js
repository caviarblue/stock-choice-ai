import "./globals.css";

export const metadata = {
  title: "Stocks Choice AI | Stock Recommender & Predictor",
  description: "AI-powered stock recommendations and trend prediction built from scratch using NumPy.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full scroll-smooth">
      <body className="min-h-full flex flex-col bg-[#0f172a] text-[#f8fafc] antialiased">
        <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#0f172a]/80 backdrop-blur-md">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-slate-900 text-lg shadow-md shadow-emerald-500/20">
                S
              </div>
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                Stocks Choice AI
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Stocks Choice AI Engine Active
            </div>
          </div>
        </header>

        <main className="w-full flex-grow flex flex-col">
          {children}
        </main>

        <footer className="border-t border-slate-800/80 bg-[#0f172a]/60 py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center text-sm text-slate-400">
            &copy; {new Date().getFullYear()} Stocks Choice AI. All rights reserved. Powered by custom NumPy AI algorithms.
          </div>
        </footer>
      </body>
    </html>
  );
}
