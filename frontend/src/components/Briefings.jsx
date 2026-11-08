import React, { useState } from 'react';
import { motion } from 'framer-motion';
import apiClient from '../api/client';
import { useFilters } from '../context/FilterContext';
import { FileText, Download, Play, ShieldAlert, CheckCircle, AlertTriangle, Printer, Terminal } from 'lucide-react';

export const Briefings = () => {
  const { filterOptions, filters } = useFilters();

  const [region, setRegion] = useState(filters.region !== 'All' ? filters.region : 'Western Africa');
  const [crimeType, setCrimeType] = useState(filters.crime_type !== 'All' ? filters.crime_type : 'All');
  const [dateStart, setDateStart] = useState(filters.date_start || '2020-01-01');
  const [dateEnd, setDateEnd] = useState(filters.date_end || '2026-06-30');

  const [briefing, setBriefing] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const payload = {
        region: region === 'All' ? null : region,
        crime_type: crimeType === 'All' ? null : crimeType,
        date_start: dateStart,
        date_end: dateEnd
      };
      const res = await apiClient.post('/api/briefing', payload);
      setBriefing(res.data);
    } catch (err) {
      console.error('Failed to generate briefing:', err);
      setError('Briefing synthesis failed. Please ensure the backend is responsive.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const params = new URLSearchParams();
      if (region && region !== 'All') params.append('region', region);
      if (crimeType && crimeType !== 'All') params.append('crime_type', crimeType);
      if (dateStart) params.append('date_start', dateStart);
      if (dateEnd) params.append('date_end', dateEnd);

      const res = await apiClient.get(`/api/pdf?${params.toString()}`, {
        responseType: 'blob'
      });

      // Create download anchor
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `SCOPE_Briefing_${(region || 'Global').replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('PDF generation encountered an issue.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Control Panel */}
      <div className="scifi-panel p-6 border border-[#00d4ff]/30">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-[#00d4ff]/20">
          <div>
            <h2 className="font-orbitron font-bold text-lg text-[#e2e8f0] flex items-center">
              <FileText className="text-[#00d4ff] mr-2.5" size={20} />
              EXECUTIVE INTELLIGENCE SYNTHESIS & REPORT GENERATOR
            </h2>
            <p className="text-xs font-share-tech text-[#94a3b8] mt-1">
              Rule-based deterministic strategic threat briefs formatted for command review and PDF export
            </p>
          </div>
          <div className="flex items-center space-x-2 text-xs font-share-tech text-[#39ff14] px-3 py-1.5 rounded bg-[#39ff14]/10 border border-[#39ff14]/30">
            <CheckCircle size={14} />
            <span>REPORTLAB ENGINE READY</span>
          </div>
        </div>

        {/* Filters Matrix */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-5">
          <div>
            <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">REGION</label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
            >
              <option value="All">All Global Regions</option>
              {filterOptions.regions.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">CRIME TYPE</label>
            <select
              value={crimeType}
              onChange={(e) => setCrimeType(e.target.value)}
              className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
            >
              <option value="All">All Threat Types</option>
              {filterOptions.crime_types.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">START DATE</label>
            <input
              type="date"
              value={dateStart}
              onChange={(e) => setDateStart(e.target.value)}
              className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
            />
          </div>

          <div>
            <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">END DATE</label>
            <input
              type="date"
              value={dateEnd}
              onChange={(e) => setDateEnd(e.target.value)}
              className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
            />
          </div>
        </div>

        {/* Action Trigger Buttons */}
        <div className="flex flex-wrap items-center gap-4 mt-6 pt-4 border-t border-[#00d4ff]/15">
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center space-x-2 px-5 py-2.5 rounded bg-[#00d4ff] hover:bg-[#00d4ff]/80 text-[#0a0f1e] font-orbitron font-bold text-xs tracking-wider transition-all shadow-[0_0_15px_rgba(0,212,255,0.3)] disabled:opacity-50 cursor-pointer"
          >
            {generating ? (
              <>
                <div className="w-4 h-4 border-2 border-[#0a0f1e] border-t-transparent rounded-full animate-spin"></div>
                <span>SYNTHESIZING INTELLIGENCE...</span>
              </>
            ) : (
              <>
                <Play size={14} fill="currentColor" />
                <span>GENERATE EXECUTIVE BRIEFING</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownloadPdf}
            disabled={downloadingPdf || !briefing}
            className="flex items-center space-x-2 px-5 py-2.5 rounded bg-[#0d1b2a] hover:bg-[#00d4ff]/10 border border-[#00d4ff]/40 text-[#00d4ff] hover:text-white font-orbitron font-semibold text-xs tracking-wider transition-all disabled:opacity-40 cursor-pointer"
          >
            {downloadingPdf ? (
              <>
                <div className="w-4 h-4 border-2 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
                <span>COMPILING PDF...</span>
              </>
            ) : (
              <>
                <Download size={15} />
                <span>EXPORT REPORT (PDF)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 rounded bg-[#ff3333]/15 border border-[#ff3333] text-[#ff3333] text-sm font-share-tech">
          <AlertTriangle className="inline mr-2" size={16} />
          {error}
        </div>
      )}

      {/* Loading Scanline Animation */}
      {generating && (
        <div className="scifi-panel p-10 border border-[#00d4ff]/40 text-center relative scanline">
          <div className="flex flex-col items-center justify-center space-y-3">
            <Terminal size={32} className="text-[#00d4ff] animate-pulse" />
            <span className="font-orbitron text-sm text-[#00d4ff] tracking-widest animate-pulse">
              [SYSTEM] RECONSTRUCTING TEMPORAL VECTORS & STATISTICAL METRICS...
            </span>
            <p className="text-xs font-share-tech text-[#94a3b8]">
              Executing rule-based narrative synthesis engine across stratified security occurrences.
            </p>
          </div>
        </div>
      )}

      {/* Briefing Display Area */}
      {briefing && !generating && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="scifi-panel p-6 border border-[#00d4ff]/40 space-y-6"
        >
          {/* Header Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pb-5 border-b border-[#00d4ff]/20">
            <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="text-[10px] font-orbitron text-[#94a3b8] block">TOTAL INCIDENTS</span>
              <span className="text-lg font-share-tech text-[#00d4ff] font-bold">
                {briefing.kpi_summary?.total_incidents || 'N/A'}
              </span>
            </div>
            <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="text-[10px] font-orbitron text-[#94a3b8] block">TOTAL FATALITIES</span>
              <span className="text-lg font-share-tech text-[#ff3333] font-bold">
                {briefing.kpi_summary?.total_fatalities || 'N/A'}
              </span>
            </div>
            <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="text-[10px] font-orbitron text-[#94a3b8] block">PRIMARY THREAT DRIVER</span>
              <span className="text-sm font-share-tech text-[#ff9500] font-bold truncate block">
                {briefing.kpi_summary?.primary_driver || 'N/A'}
              </span>
            </div>
            <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="text-[10px] font-orbitron text-[#94a3b8] block">REGION COVERED</span>
              <span className="text-sm font-share-tech text-[#39ff14] font-bold truncate block">
                {briefing.kpi_summary?.region || 'Global'}
              </span>
            </div>
          </div>

          {/* Formatted Narrative Sections */}
          <div className="space-y-4">
            <h4 className="font-orbitron font-semibold text-sm text-[#00d4ff] tracking-wider pb-2 border-b border-[#00d4ff]/15">
              STRATEGIC THREAT ASSESSMENT NARRATIVE
            </h4>

            {briefing.narrative_text.split('\n\n').map((paragraph, index) => {
              const colonIndex = paragraph.indexOf(':');
              const header = colonIndex !== -1 ? paragraph.substring(0, colonIndex) : null;
              const content = colonIndex !== -1 ? paragraph.substring(colonIndex + 1) : paragraph;

              return (
                <div key={index} className="p-4 rounded bg-[#0a0f1e]/80 border border-[#00d4ff]/15 leading-relaxed">
                  {header && (
                    <span className="font-orbitron font-bold text-xs text-[#00d4ff] block mb-1 tracking-wider">
                      {header.toUpperCase()}
                    </span>
                  )}
                  <p className="font-share-tech text-sm text-[#e2e8f0]">
                    {content.trim()}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Mandated Disclaimer Footer Banner */}
          <div className="p-3 rounded bg-[#0a0f1e] border border-[#ff9500]/30 text-xs font-share-tech text-[#ff9500] text-center leading-relaxed">
            <span className="font-bold mr-1">⚠️ MANDATED DISCLAIMER:</span>
            "This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Briefings;

