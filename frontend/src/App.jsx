import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { FilterProvider, useFilters } from './context/FilterContext';
import Sidebar from './components/Sidebar';
import {
  Radar,
  Activity,
  Map as MapIcon,
  Cpu,
  TrendingUp,
  Network as NetworkIcon,
  FileText,
  Scale,
  AlertTriangle,
  Loader2
} from 'lucide-react';

// Code-split route components via React.lazy for optimized bundle size
const KPIPanel = lazy(() => import('./components/KPIPanel'));
const ThreatMap = lazy(() => import('./components/ThreatMap'));
const PredictForm = lazy(() => import('./components/PredictForm'));
const ForecastChart = lazy(() => import('./components/ForecastChart'));
const NetworkGraph = lazy(() => import('./components/NetworkGraph'));
const Briefings = lazy(() => import('./components/Briefings'));
const DataEthics = lazy(() => import('./components/DataEthics'));

const RouteLoadingFallback = () => (
  <div className="w-full h-96 flex flex-col items-center justify-center space-y-3">
    <div className="w-10 h-10 border-2 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
    <span className="font-orbitron text-xs text-[#00d4ff] tracking-widest animate-pulse">
      INITIALIZING TELEMETRY MODULE...
    </span>
  </div>
);

const PageWrapper = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3 }}
      className="w-full"
    >
      {children}
    </motion.div>
  );
};

const AnimatedRoutes = () => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Suspense fallback={<RouteLoadingFallback />}>
        <Routes location={location} key={location.pathname}>
          {/* Overview / KPIs */}
          <Route
            path="/"
            element={
              <PageWrapper>
                <div className="space-y-6">
                  <KPIPanel />
                  <ThreatMap />
                </div>
              </PageWrapper>
            }
          />

          {/* Global Threat Map */}
          <Route
            path="/map"
            element={
              <PageWrapper>
                <ThreatMap />
              </PageWrapper>
            }
          />

          {/* Predictive Threat Modeling */}
          <Route
            path="/predict"
            element={
              <PageWrapper>
                <PredictForm />
              </PageWrapper>
            }
          />

          {/* Time-Series Forecasting */}
          <Route
            path="/forecast"
            element={
              <PageWrapper>
                <ForecastChart />
              </PageWrapper>
            }
          />

          {/* Actor Network Graph */}
          <Route
            path="/network"
            element={
              <PageWrapper>
                <NetworkGraph />
              </PageWrapper>
            }
          />

          {/* Automated Intelligence Briefings */}
          <Route
            path="/briefings"
            element={
              <PageWrapper>
                <Briefings />
              </PageWrapper>
            }
          />

          {/* Data Governance & Ethics */}
          <Route
            path="/ethics"
            element={
              <PageWrapper>
                <DataEthics />
              </PageWrapper>
            }
          />
        </Routes>
      </Suspense>
    </AnimatePresence>
  );
};

const NavigationBar = () => {
  const navItems = [
    { to: '/', label: 'OVERVIEW', icon: Activity },
    { to: '/map', label: 'THREAT MAP', icon: MapIcon },
    { to: '/predict', label: 'PREDICTION', icon: Cpu },
    { to: '/forecast', label: 'FORECAST', icon: TrendingUp },
    { to: '/network', label: 'NETWORK', icon: NetworkIcon },
    { to: '/briefings', label: 'BRIEFINGS', icon: FileText },
    { to: '/ethics', label: 'DATA & ETHICS', icon: Scale },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-[#0a0f1e]/90 backdrop-blur-md border-b border-[#00d4ff]/30 z-50 flex items-center justify-between px-4 lg:px-6 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
      <div className="flex items-center space-x-3">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-[#00d4ff]/10 border border-[#00d4ff]/50 shadow-[0_0_15px_rgba(0,212,255,0.4)]">
          <Radar className="text-[#00d4ff] animate-spin" style={{ animationDuration: '8s' }} size={22} />
          <span className="absolute w-2 h-2 rounded-full bg-[#00d4ff] animate-ping"></span>
        </div>
        <div>
          <div className="font-orbitron font-extrabold text-lg tracking-wider text-white flex items-center">
            SCOPE<span className="text-[#00d4ff] ml-0.5">_</span>
          </div>
          <span className="text-[10px] font-share-tech text-[#94a3b8] tracking-widest hidden sm:inline-block">
            STRATEGIC CRIME OBSERVATION & PREDICTION ENGINE
          </span>
        </div>
      </div>

      <nav className="hidden xl:flex items-center space-x-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-orbitron tracking-wider transition-all ${
                  isActive
                    ? 'bg-[#00d4ff]/15 text-[#00d4ff] border border-[#00d4ff]/40 shadow-[0_0_12px_rgba(0,212,255,0.3)]'
                    : 'text-[#94a3b8] hover:text-[#e2e8f0] hover:bg-[#0d1b2a]'
                }`
              }
            >
              <Icon size={14} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#0d1b2a] border border-[#00d4ff]/30 text-[11px] font-share-tech text-[#e2e8f0]">
        <span className="w-2 h-2 rounded-full bg-[#39ff14] animate-pulse"></span>
        <span className="hidden sm:inline">ENGINE STATUS:</span>
        <strong className="text-[#39ff14]">ACTIVE</strong>
      </div>
    </header>
  );
};

const AppContent = () => {
  const { isSidebarOpen } = useFilters();

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-[#e2e8f0] flex flex-col relative selection:bg-[#00d4ff]/30 selection:text-[#00d4ff]">
      <div className="scifi-grid-bg"></div>
      <NavigationBar />
      <Sidebar />

      <div className="xl:hidden fixed top-16 left-0 right-0 h-10 bg-[#0d1b2a]/95 border-b border-[#00d4ff]/20 z-30 flex items-center overflow-x-auto px-4 space-x-3 text-[11px] font-orbitron">
        <NavLink to="/" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>OVERVIEW</NavLink>
        <NavLink to="/map" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>MAP</NavLink>
        <NavLink to="/predict" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>PREDICTION</NavLink>
        <NavLink to="/forecast" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>FORECAST</NavLink>
        <NavLink to="/network" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>NETWORK</NavLink>
        <NavLink to="/briefings" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>BRIEFINGS</NavLink>
        <NavLink to="/ethics" className={({ isActive }) => isActive ? 'text-[#00d4ff] font-bold' : 'text-[#94a3b8]'}>ETHICS</NavLink>
      </div>

      <main
        className={`flex-1 transition-all duration-300 pt-28 xl:pt-22 pb-12 px-4 sm:px-6 lg:px-8 relative z-10 ${
          isSidebarOpen ? 'lg:ml-80' : 'ml-0'
        }`}
      >
        <div className="max-w-7xl mx-auto">
          <AnimatedRoutes />
        </div>
      </main>

      <footer
        className={`relative z-20 py-4 px-6 border-t border-[#00d4ff]/20 bg-[#0d1b2a]/95 backdrop-blur-md text-center text-xs font-share-tech text-[#94a3b8] transition-all duration-300 ${
          isSidebarOpen ? 'lg:ml-80' : 'ml-0'
        }`}
      >
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2 text-[#ff9500]">
            <AlertTriangle size={14} className="flex-shrink-0" />
            <span className="font-bold">MANDATED DISCLAIMER:</span>
            <span className="text-left text-[11px] text-[#e2e8f0]">
              "This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."
            </span>
          </div>
          <div className="text-[10px] text-[#94a3b8] font-orbitron tracking-wider">
            SCOPE SYSTEM V2.0 // FASTAPI + REACT
          </div>
        </div>
      </footer>
    </div>
  );
};

export const App = () => {
  return (
    <Router>
      <FilterProvider>
        <AppContent />
      </FilterProvider>
    </Router>
  );
};

export default App;
