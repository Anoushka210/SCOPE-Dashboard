import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import apiClient from '../api/client';
import { useFilters } from '../context/FilterContext';
import { TrendingUp, Activity, BarChart2, CheckCircle2, Sliders } from 'lucide-react';

export const ForecastChart = () => {
  const { filterOptions } = useFilters();
  const [selectedRegion, setSelectedRegion] = useState('Western Africa');
  const [selectedCrime, setSelectedCrime] = useState('Battles');
  const [forecastData, setForecastData] = useState([]);
  const [metrics, setMetrics] = useState({ val_mae: 0, val_rmse: 0 });
  const [modelUsed, setModelUsed] = useState('SARIMA (statsmodels)');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get(
          `/api/forecast?region=${encodeURIComponent(selectedRegion)}&crime_type=${encodeURIComponent(selectedCrime)}&steps=12`
        );
        if (res.data) {
          const { dates, actual, forecast, lower_ci, upper_ci, is_forecast } = res.data;
          const chartPoints = dates.map((d, i) => {
            const isFuture = is_forecast ? is_forecast[i] : (actual[i] === null);
            return {
              date: d,
              // Only display actual where historical data exists
              actual: actual[i],
              // Forecast value
              forecast: forecast[i],
              // Confidence interval range as [min, max]
              ci_range: [lower_ci[i], upper_ci[i]],
              lower_ci: lower_ci[i],
              upper_ci: upper_ci[i],
              isFuture
            };
          });

          // Focus display on the most recent 36 months + 12 forecast months for clarity
          const trimmedPoints = chartPoints.length > 48 ? chartPoints.slice(-48) : chartPoints;
          setForecastData(trimmedPoints);
          setMetrics(res.data.validation_metrics || { val_mae: 0, val_rmse: 0 });
          setModelUsed(res.data.model_used || 'SARIMA (statsmodels)');
        }
      } catch (err) {
        console.error('Failed to fetch forecast:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [selectedRegion, selectedCrime]);

  return (
    <div className="scifi-panel p-6 border border-[#00d4ff]/30 space-y-6">
      {/* Header and Filter Selectors */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-[#00d4ff]/20">
        <div>
          <h3 className="font-orbitron font-bold text-base text-[#e2e8f0] flex items-center">
            <TrendingUp className="text-[#00d4ff] mr-2" size={18} />
            TIME-SERIES INCIDENT VELOCITY & SARIMA PROJECTION
          </h3>
          <p className="text-xs font-share-tech text-[#94a3b8] mt-0.5">
            12-Month forward projection with 80% confidence intervals fitted on monthly aggregate security occurrences
          </p>
        </div>

        {/* Region & Crime Type Selectors */}
        <div className="flex items-center gap-3">
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-1.5 text-xs text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
          >
            {filterOptions.regions.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>

          <select
            value={selectedCrime}
            onChange={(e) => setSelectedCrime(e.target.value)}
            className="bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-1.5 text-xs text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
          >
            {filterOptions.crime_types.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Validation Metrics Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20 flex items-center justify-between">
          <span className="text-xs font-orbitron text-[#94a3b8]">ALGORITHM</span>
          <span className="text-xs font-share-tech text-[#00d4ff] font-bold">{modelUsed}</span>
        </div>
        <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20 flex items-center justify-between">
          <span className="text-xs font-orbitron text-[#94a3b8]">VAL MEAN ABS ERROR (MAE)</span>
          <span className="text-xs font-share-tech text-[#39ff14] font-bold">±{metrics.val_mae} events</span>
        </div>
        <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20 flex items-center justify-between">
          <span className="text-xs font-orbitron text-[#94a3b8]">VAL ROOT MEAN SQ (RMSE)</span>
          <span className="text-xs font-share-tech text-[#ff9500] font-bold">{metrics.val_rmse}</span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-80 w-full relative">
        {loading ? (
          <div className="h-full flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={forecastData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#00d4ff" strokeOpacity={0.1} />
              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                fontSize={11}
                tickFormatter={(d) => d.substring(0, 7)}
                tickLine={false}
              />
              <YAxis
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: '#00d4ff', strokeOpacity: 0.2 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0d1b2a',
                  borderColor: 'rgba(0, 212, 255, 0.4)',
                  borderRadius: '6px',
                  boxShadow: '0 0 15px rgba(0, 212, 255, 0.2)',
                  fontFamily: 'Share Tech Mono'
                }}
                formatter={(val, name) => {
                  if (name === 'Historical Occurrences') return [`${val} incidents`, name];
                  if (name === 'SARIMA Forecast') return [`${val} incidents`, name];
                  if (name === '80% Confidence Interval') return [`[${val[0]} - ${val[1]}]`, name];
                  return [val, name];
                }}
              />
              <Legend
                wrapperStyle={{
                  paddingTop: '15px',
                  fontFamily: 'Orbitron',
                  fontSize: '11px'
                }}
              />

              {/* Shaded Confidence Interval Band */}
              <Area
                dataKey="ci_range"
                fill="#00d4ff"
                fillOpacity={0.12}
                stroke="none"
                name="80% Confidence Interval"
              />

              {/* Historical Actual Line */}
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#39ff14"
                strokeWidth={2}
                dot={{ r: 2, fill: '#39ff14' }}
                activeDot={{ r: 5, fill: '#39ff14', stroke: '#ffffff' }}
                name="Historical Occurrences"
                isAnimationActive={true}
              />

              {/* Forecast Projected Line */}
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#00d4ff"
                strokeWidth={2.5}
                strokeDasharray="4 4"
                dot={false}
                activeDot={{ r: 5, fill: '#00d4ff', stroke: '#ffffff' }}
                name="SARIMA Forecast"
                isAnimationActive={true}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default ForecastChart;

