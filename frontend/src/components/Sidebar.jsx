import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFilters } from '../context/FilterContext';
import { Sliders, RefreshCw, ChevronLeft, ChevronRight, ShieldAlert, Globe, Calendar, Filter, ToggleLeft, ToggleRight } from 'lucide-react';

const SEVERITY_LEVEL_LABELS = {
  0: 'All (Score ≥ 1.0)',
  1: 'Medium+ (Score > 2.0)',
  2: 'High+ (Score > 5.0)',
  3: 'Critical (Score > 15.0)'
};

export const Sidebar = () => {
  const {
    filters,
    filterOptions,
    updateFilter,
    resetFilters,
    isSidebarOpen,
    toggleSidebar
  } = useFilters();

  return (
    <aside className="relative z-30 select-none">
      {/* Collapse/Expand Toggle Tab */}
      <button
        onClick={toggleSidebar}
        className="fixed top-20 left-0 z-40 bg-[#0d1b2a] border border-[#00d4ff]/40 text-[#00d4ff] hover:text-white p-2 rounded-r-md shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all flex items-center justify-center cursor-pointer"
        title={isSidebarOpen ? "Collapse Filter Console" : "Expand Filter Console"}
      >
        {isSidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
      </button>

      {/* Animated Sidebar Drawer */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 220 }}
            className="w-72 lg:w-80 h-[calc(100vh-4rem)] fixed top-16 left-0 bg-[#0d1b2a]/95 backdrop-blur-md border-r border-[#00d4ff]/30 shadow-[5px_0_25px_rgba(0,212,255,0.12)] p-5 overflow-y-auto flex flex-col justify-between"
          >
            <div>
              {/* Header */}
              <div className="flex items-center justify-between pb-4 border-b border-[#00d4ff]/20 mb-5">
                <div className="flex items-center space-x-2">
                  <Sliders className="text-[#00d4ff]" size={18} />
                  <span className="font-orbitron font-semibold text-sm tracking-wider text-[#e2e8f0]">
                    GLOBAL MATRIX
                  </span>
                </div>
                <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-[#39ff14]/10 border border-[#39ff14]/30">
                  <span className="w-2 h-2 rounded-full bg-[#39ff14] animate-pulse"></span>
                  <span className="text-[10px] font-share-tech text-[#39ff14] tracking-widest">LIVE</span>
                </div>
              </div>

              {/* Filters Form */}
              <div className="space-y-5">
                {/* Region Filter */}
                <div>
                  <label className="flex items-center text-xs font-orbitron tracking-wider text-[#94a3b8] mb-1.5">
                    <Globe size={13} className="mr-1.5 text-[#00d4ff]" /> REGION SELECTION
                  </label>
                  <select
                    value={filters.region}
                    onChange={(e) => updateFilter('region', e.target.value)}
                    className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff] focus:shadow-[0_0_12px_rgba(0,212,255,0.4)] transition-all cursor-pointer"
                  >
                    <option value="All">All Global Regions</option>
                    {filterOptions.regions.map((reg) => (
                      <option key={reg} value={reg}>
                        {reg}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Threat Category Filter */}
                <div>
                  <label className="flex items-center text-xs font-orbitron tracking-wider text-[#94a3b8] mb-1.5">
                    <ShieldAlert size={13} className="mr-1.5 text-[#00d4ff]" /> THREAT CATEGORY
                  </label>
                  <select
                    value={filters.crime_type}
                    onChange={(e) => updateFilter('crime_type', e.target.value)}
                    className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff] focus:shadow-[0_0_12px_rgba(0,212,255,0.4)] transition-all cursor-pointer"
                  >
                    <option value="All">All Threat Types</option>
                    {filterOptions.crime_types.map((crime) => (
                      <option key={crime} value={crime}>
                        {crime}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Non-Violent Events Toggle (Off by default) */}
                <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-orbitron text-[#e2e8f0]">
                      CIVIL & STRATEGIC DEVELOPMENTS
                    </span>
                    <button
                      type="button"
                      onClick={() => updateFilter('include_non_violent', !filters.include_non_violent)}
                      className="cursor-pointer text-[#00d4ff]"
                    >
                      {filters.include_non_violent ? (
                        <ToggleRight size={24} className="text-[#39ff14]" />
                      ) : (
                        <ToggleLeft size={24} className="text-[#94a3b8]" />
                      )}
                    </button>
                  </div>
                  <p className="text-[10px] font-share-tech text-[#94a3b8] mt-1">
                    {filters.include_non_violent
                      ? "Including Protests and Strategic developments"
                      : "Filtered OFF by default: Focuses on violent/armed confrontations"}
                  </p>
                </div>

                {/* Severity Class Threshold Slider */}
                <div>
                  <div className="flex justify-between items-center text-xs font-orbitron text-[#94a3b8] mb-1.5">
                    <span className="flex items-center">
                      <Filter size={13} className="mr-1.5 text-[#00d4ff]" /> MIN SEVERITY
                    </span>
                    <span className="font-share-tech text-[#00d4ff] font-bold text-xs">
                      {SEVERITY_LEVEL_LABELS[filters.severity_min] || 'All'}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="3"
                    step="1"
                    value={filters.severity_min}
                    onChange={(e) => updateFilter('severity_min', parseInt(e.target.value, 10))}
                    className="w-full accent-[#00d4ff] cursor-pointer bg-[#0a0f1e] h-2 rounded-lg"
                  />
                  <div className="flex justify-between text-[10px] font-share-tech text-[#94a3b8] mt-1">
                    <span>All (&ge;1)</span>
                    <span>Med (&gt;2)</span>
                    <span>High (&gt;5)</span>
                    <span>Crit (&gt;15)</span>
                  </div>
                </div>

                {/* Observation Date Range */}
                <div className="space-y-2">
                  <label className="flex items-center text-xs font-orbitron tracking-wider text-[#94a3b8]">
                    <Calendar size={13} className="mr-1.5 text-[#00d4ff]" /> OBSERVATION WINDOW
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="text-[10px] font-share-tech text-[#94a3b8] block mb-0.5">FROM</span>
                      <input
                        type="date"
                        value={filters.date_start}
                        onChange={(e) => updateFilter('date_start', e.target.value)}
                        className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-2 py-1 text-xs text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
                      />
                    </div>
                    <div>
                      <span className="text-[10px] font-share-tech text-[#94a3b8] block mb-0.5">TO</span>
                      <input
                        type="date"
                        value={filters.date_end}
                        onChange={(e) => updateFilter('date_end', e.target.value)}
                        className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-2 py-1 text-xs text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="pt-6 border-t border-[#00d4ff]/20">
              <button
                onClick={resetFilters}
                className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded bg-[#00d4ff]/10 hover:bg-[#00d4ff]/20 border border-[#00d4ff]/40 text-[#00d4ff] hover:text-white font-orbitron text-xs tracking-wider transition-all shadow-[0_0_10px_rgba(0,212,255,0.15)] cursor-pointer"
              >
                <RefreshCw size={14} />
                <span>RESET MATRIX</span>
              </button>

              <div className="mt-4 p-2.5 rounded bg-[#0a0f1e]/80 border border-[#00d4ff]/10 text-[10px] text-[#94a3b8] font-share-tech leading-relaxed">
                <span className="text-[#00d4ff] font-bold">INFO:</span> Global filter updates dynamically synchronize Map, Forecasts, and Threat Intelligence counters.
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </aside>
  );
};

export default Sidebar;
