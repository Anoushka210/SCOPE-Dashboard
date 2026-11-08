import React, { useState, useEffect } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import apiClient from '../api/client';
import { useFilters } from '../context/FilterContext';
import { AlertCircle, Skull, Users, Calendar, Activity, Zap, Database, Info } from 'lucide-react';

const AnimatedCounter = ({ value, duration = 1.2 }) => {
  const count = useMotionValue(0);
  const [displayValue, setDisplayValue] = useState('0');

  useEffect(() => {
    const numericValue = typeof value === 'number' ? value : parseInt(String(value).replace(/,/g, ''), 10) || 0;
    const controls = animate(count, numericValue, {
      duration,
      ease: 'easeOut',
      onUpdate: (latest) => {
        setDisplayValue(Math.round(latest).toLocaleString());
      }
    });
    return controls.stop;
  }, [value, count, duration]);

  return <span className="font-share-tech font-bold">{displayValue}</span>;
};

export const KPIPanel = () => {
  const { filters } = useFilters();
  const [kpis, setKpis] = useState({
    total_incidents: 0,
    total_events_expanded: 0,
    total_fatalities: 0,
    active_actor_groups: 0,
    date_range_min: '...',
    date_range_max: '...',
    sample_scope: '150k Stratified Deployed Dataset',
    incidents_by_crime_type: {},
    incidents_by_region: {},
    full_database_summary: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        if (filters.region && filters.region !== 'All') params.append('region', filters.region);
        if (filters.crime_type && filters.crime_type !== 'All') params.append('crime_type', filters.crime_type);
        if (filters.severity_min > 0) params.append('severity_min', filters.severity_min);
        if (filters.date_start) params.append('date_start', filters.date_start);
        if (filters.date_end) params.append('date_end', filters.date_end);
        params.append('include_non_violent', String(filters.include_non_violent));

        const res = await apiClient.get(`/api/kpis?${params.toString()}`);
        if (res.data) {
          setKpis(res.data);
        }
      } catch (err) {
        console.error('Failed to fetch KPIs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
  }, [filters]);

  const crimeChartData = Object.entries(kpis.incidents_by_crime_type || {})
    .map(([crime, count]) => ({
      crime: crime.length > 16 ? crime.substring(0, 14) + '...' : crime,
      fullCrime: crime,
      count
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  const crimeColors = ['#00d4ff', '#ff3333', '#ff9500', '#ea580c', '#39ff14', '#b5179e'];

  return (
    <div className="space-y-6">
      {/* Scope & Methodology Indicator Banner */}
      <div className="p-3.5 rounded bg-[#0d1b2a] border border-[#00d4ff]/30 text-xs font-share-tech flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-sm">
        <div className="flex items-center space-x-2 text-[#00d4ff]">
          <Database size={15} />
          <span className="font-orbitron font-bold">SAMPLE CONTEXT:</span>
          <span className="text-[#e2e8f0]">150,000 Stratified Deployed Records</span>
        </div>
        <div className="text-[#94a3b8] flex items-center space-x-3 text-[11px]">
          <span>Full Multilateral DB: <strong className="text-[#39ff14]">3.33M Events</strong> / <strong className="text-[#ff3333]">3.07M Fatalities</strong></span>
          <span className="px-2 py-0.5 rounded bg-[#00d4ff]/10 border border-[#00d4ff]/20 text-[#00d4ff]">
            {filters.include_non_violent ? "All Categories" : "Violent Crimes Only"}
          </span>
        </div>
      </div>

      {/* 4 KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Card 1: Total Incidents & Expanded Count */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="scifi-panel p-5 relative overflow-hidden group border border-[#00d4ff]/30 hover:border-[#00d4ff]/60"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-orbitron tracking-wider text-[#94a3b8] flex items-center">
              <Activity size={14} className="text-[#00d4ff] mr-1.5" /> TOTAL INCIDENTS
            </span>
            <div className="p-2 rounded-lg bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/20">
              <Zap size={16} />
            </div>
          </div>
          <div className="text-2xl lg:text-3xl font-share-tech text-[#00d4ff] tracking-tight">
            {loading ? <span className="animate-pulse">...</span> : <AnimatedCounter value={kpis.total_incidents} />}
          </div>
          <p className="text-[11px] font-share-tech text-[#94a3b8] mt-2 flex items-center justify-between">
            <span>Clusters in sample: {kpis.total_incidents.toLocaleString()}</span>
            <span className="text-[#39ff14] font-bold" title="ACLED events expanded by weekly EVENTS multiplier">
              ≈ {kpis.total_events_expanded.toLocaleString()} events
            </span>
          </p>
        </motion.div>

        {/* Card 2: Total Fatalities */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="scifi-panel p-5 relative overflow-hidden group border border-[#ff3333]/30 hover:border-[#ff3333]/60"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-orbitron tracking-wider text-[#94a3b8] flex items-center">
              <Skull size={14} className="text-[#ff3333] mr-1.5" /> TOTAL FATALITIES
            </span>
            <div className="p-2 rounded-lg bg-[#ff3333]/10 text-[#ff3333] border border-[#ff3333]/20">
              <AlertCircle size={16} />
            </div>
          </div>
          <div className="text-2xl lg:text-3xl font-share-tech text-[#ff3333] tracking-tight">
            {loading ? <span className="animate-pulse">...</span> : <AnimatedCounter value={kpis.total_fatalities} />}
          </div>
          <p className="text-[11px] font-share-tech text-[#ff9500] mt-2 flex items-center">
            <span className="font-bold mr-1">⚠️</span> Excludes ASAM maritime null reports
          </p>
        </motion.div>

        {/* Card 3: Active Actor Groups */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="scifi-panel p-5 relative overflow-hidden group border border-[#ff9500]/30 hover:border-[#ff9500]/60"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-orbitron tracking-wider text-[#94a3b8] flex items-center">
              <Users size={14} className="text-[#ff9500] mr-1.5" /> NAMED ACTOR GROUPS
            </span>
            <div className="p-2 rounded-lg bg-[#ff9500]/10 text-[#ff9500] border border-[#ff9500]/20">
              <Users size={16} />
            </div>
          </div>
          <div className="text-2xl lg:text-3xl font-share-tech text-[#ff9500] tracking-tight">
            {loading ? <span className="animate-pulse">...</span> : <AnimatedCounter value={kpis.active_actor_groups} />}
          </div>
          <p className="text-[11px] font-share-tech text-[#94a3b8] mt-2 flex items-center">
            Organized insurgent, terror & cartel groups (GTD/Cartel)
          </p>
        </motion.div>

        {/* Card 4: Date Range Covered */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
          className="scifi-panel p-5 relative overflow-hidden group border border-[#39ff14]/30 hover:border-[#39ff14]/60"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-orbitron tracking-wider text-[#94a3b8] flex items-center">
              <Calendar size={14} className="text-[#39ff14] mr-1.5" /> OBSERVATION COVERAGE
            </span>
            <div className="p-2 rounded-lg bg-[#39ff14]/10 text-[#39ff14] border border-[#39ff14]/20">
              <Calendar size={16} />
            </div>
          </div>
          <div className="text-lg lg:text-xl font-share-tech text-[#39ff14] tracking-tight pt-1">
            {kpis.date_range_min} <span className="text-white/60">→</span> {kpis.date_range_max}
          </div>
          <p className="text-[11px] font-share-tech text-[#94a3b8] mt-2 flex items-center">
            Multi-decade multilateral dataset integration
          </p>
        </motion.div>
      </div>

      {/* Inline Threat Breakdown by Crime Type */}
      <div className="scifi-panel p-5 border border-[#00d4ff]/30">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-3 border-b border-[#00d4ff]/15 mb-4">
          <div>
            <h3 className="font-orbitron text-sm font-semibold text-[#e2e8f0] tracking-wider flex items-center">
              <span className="w-2 h-2 bg-[#00d4ff] rounded-full mr-2"></span>
              INCIDENT COUNTS BY THREAT VECTOR
            </h3>
            <p className="text-xs font-share-tech text-[#94a3b8] mt-0.5">
              {filters.include_non_violent
                ? "Displaying all operational classifications including protests and strategic developments"
                : "Violent threat vectors (non-violent protests and strategic developments toggled OFF by default)"}
            </p>
          </div>
          <span className="text-[11px] font-share-tech text-[#00d4ff] px-2.5 py-1 rounded bg-[#00d4ff]/10 border border-[#00d4ff]/30 mt-2 sm:mt-0">
            {filters.include_non_violent ? "CIVIL + VIOLENT" : "VIOLENT ONLY"}
          </span>
        </div>

        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={crimeChartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 30, bottom: 5 }}
            >
              <XAxis
                type="number"
                stroke="#94a3b8"
                fontSize={11}
                tickFormatter={(v) => v.toLocaleString()}
                tickLine={false}
              />
              <YAxis
                dataKey="crime"
                type="category"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: '#00d4ff', strokeOpacity: 0.2 }}
                width={120}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0d1b2a',
                  borderColor: 'rgba(0, 212, 255, 0.4)',
                  borderRadius: '6px',
                  boxShadow: '0 0 15px rgba(0, 212, 255, 0.2)',
                  fontFamily: 'Share Tech Mono'
                }}
                formatter={(val, name, item) => [
                  `${val.toLocaleString()} events`,
                  item.payload.fullCrime
                ]}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {crimeChartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={crimeColors[index % crimeColors.length]}
                    style={{
                      filter: `drop-shadow(0 0 6px ${crimeColors[index % crimeColors.length]}40)`
                    }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default KPIPanel;
