import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import apiClient from '../api/client';
import { useFilters } from '../context/FilterContext';
import { Cpu, Send, CheckCircle, AlertTriangle, HelpCircle, BarChart3, TrendingUp, ShieldAlert, Info } from 'lucide-react';

const SEVERITY_BADGES = {
  0: { label: 'Low Severity (Class 0)', color: '#39ff14', bg: 'rgba(57, 255, 20, 0.15)', border: '#39ff14' },
  1: { label: 'Medium Severity (Class 1)', color: '#ff9500', bg: 'rgba(255, 149, 0, 0.15)', border: '#ff9500' },
  2: { label: 'High Severity (Class 2)', color: '#ea580c', bg: 'rgba(234, 88, 12, 0.15)', border: '#ea580c' },
  3: { label: 'Critical Severity (Class 3)', color: '#ff3333', bg: 'rgba(255, 51, 51, 0.15)', border: '#ff3333' }
};

export const PredictForm = () => {
  const { filterOptions } = useFilters();

  const [formData, setFormData] = useState({
    region: 'Western Africa',
    crime_type: 'Battles',
    sub_type: 'Armed clash',
    country: 'Nigeria',
    year: 2026,
    month: 6,
    actor_group: 'Boko Haram',
    latitude: 9.082,
    longitude: 8.6753
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'year' || name === 'month' ? Number(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post('/api/predict', formData);
      setResult(res.data);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(err.response?.data?.detail || 'Machine learning model inference failed. Please check input parameters.');
    } finally {
      setLoading(false);
    }
  };

  const probData = result?.probabilities_breakdown || (result?.class_probabilities ? [
    { class_name: 'Low', class_label: 'Low (<=2)', probability: result.class_probabilities[0] },
    { class_name: 'Medium', class_label: 'Medium (2-5)', probability: result.class_probabilities[1] },
    { class_name: 'High', class_label: 'High (5-15)', probability: result.class_probabilities[2] },
    { class_name: 'Critical', class_label: 'Critical (>15)', probability: result.class_probabilities[3] }
  ] : []);

  const probColors = ['#39ff14', '#ff9500', '#ea580c', '#ff3333'];

  const shapData = result?.shap_features?.slice(0, 8).map(item => ({
    feature: item.feature.length > 20 ? item.feature.substring(0, 18) + '...' : item.feature,
    impact: Math.round(item.impact * 1000) / 1000,
    fullFeature: item.feature
  })) || [];

  return (
    <div className="space-y-6">
      {/* Leakage-Free Architecture Notice */}
      <div className="p-3.5 rounded bg-[#0d1b2a] border border-[#39ff14]/30 text-xs font-share-tech flex items-start space-x-2.5">
        <CheckCircle size={16} className="text-[#39ff14] flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-orbitron font-bold text-[#39ff14]">LEAKAGE-FREE INFERENCE ENGINE:</span>
          <p className="text-[#cbd5e1] mt-0.5 leading-relaxed">
            Inference evaluates pre-event tactical and contextual indicators only (region, country, sub-event classification, actor group, spatial coordinates, seasonality). Target-defining outcomes like casualty counts are strictly excluded.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Column */}
        <div className="lg:col-span-5">
          <form onSubmit={handleSubmit} className="scifi-panel p-5 border border-[#00d4ff]/30 space-y-4">
            <div className="pb-3 border-b border-[#00d4ff]/20 flex items-center justify-between">
              <span className="text-xs font-orbitron font-semibold text-[#00d4ff] tracking-wider">
                TACTICAL INPUT MATRIX
              </span>
              <span className="text-[11px] font-share-tech text-[#94a3b8]">LIGHTGBM V2.0</span>
            </div>

            {/* Region */}
            <div>
              <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">REGION</label>
              <select
                name="region"
                value={formData.region}
                onChange={handleChange}
                className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
                required
              >
                {filterOptions.regions.length > 0 ? (
                  filterOptions.regions.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))
                ) : (
                  <option value="Western Africa">Western Africa</option>
                )}
              </select>
            </div>

            {/* Crime Type */}
            <div>
              <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">THREAT TYPE</label>
              <select
                name="crime_type"
                value={formData.crime_type}
                onChange={handleChange}
                className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
                required
              >
                {filterOptions.crime_types.length > 0 ? (
                  filterOptions.crime_types.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))
                ) : (
                  <option value="Battles">Battles</option>
                )}
              </select>
            </div>

            {/* Country */}
            <div>
              <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">COUNTRY</label>
              <select
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
              >
                {filterOptions.countries && filterOptions.countries.length > 0 ? (
                  filterOptions.countries.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))
                ) : (
                  <option value="Nigeria">Nigeria</option>
                )}
              </select>
            </div>

            {/* Sub Type */}
            <div>
              <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">SUB-EVENT TYPE</label>
              <input
                type="text"
                name="sub_type"
                value={formData.sub_type}
                onChange={handleChange}
                placeholder="Armed clash / Suicide bomb / Kidnapping"
                className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
              />
            </div>

            {/* Actor Group */}
            <div>
              <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">ACTOR GROUP</label>
              <input
                type="text"
                name="actor_group"
                value={formData.actor_group}
                onChange={handleChange}
                placeholder="e.g. Boko Haram, Al-Shabaab, Taliban, Sinaloa Cartel"
                className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
              />
            </div>

            {/* Temporal Coordinates */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">YEAR</label>
                <input
                  type="number"
                  name="year"
                  min="2020"
                  max="2030"
                  value={formData.year}
                  onChange={handleChange}
                  className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
                />
              </div>
              <div>
                <label className="text-xs font-orbitron text-[#94a3b8] block mb-1">MONTH (1-12)</label>
                <input
                  type="number"
                  name="month"
                  min="1"
                  max="12"
                  value={formData.month}
                  onChange={handleChange}
                  className="w-full bg-[#0a0f1e] border border-[#00d4ff]/30 rounded px-3 py-2 text-sm text-[#e2e8f0] font-share-tech focus:outline-none focus:border-[#00d4ff]"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 py-3 rounded bg-[#00d4ff] hover:bg-[#00d4ff]/80 text-[#0a0f1e] font-orbitron font-bold text-sm tracking-wider transition-all shadow-[0_0_15px_rgba(0,212,255,0.4)] disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-[#0a0f1e] border-t-transparent rounded-full animate-spin"></div>
                  <span>EVALUATING MODEL INFERENCE...</span>
                </>
              ) : (
                <>
                  <Send size={15} />
                  <span>EXECUTE THREAT INFERENCE</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results & Visualizations Column */}
        <div className="lg:col-span-7">
          {error && (
            <div className="p-4 rounded bg-[#ff3333]/15 border border-[#ff3333] text-[#ff3333] text-sm font-share-tech mb-4">
              <AlertTriangle className="inline mr-2" size={16} />
              {error}
            </div>
          )}

          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="prediction-result"
                initial={{ opacity: 0, x: 25 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -25 }}
                transition={{ duration: 0.4 }}
                className="space-y-6"
              >
                {/* Predicted Severity Class Badge */}
                <div className="scifi-panel p-6 border border-[#00d4ff]/40">
                  <span className="text-xs font-orbitron text-[#94a3b8] tracking-widest block mb-2">
                    MODEL CLASSIFICATION OUTCOME
                  </span>
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div>
                      <div className="text-2xl sm:text-3xl font-orbitron font-bold tracking-wider" style={{ color: SEVERITY_BADGES[result.predicted_class]?.color || '#00d4ff' }}>
                        {result.class_label}
                      </div>
                      <p className="text-xs font-share-tech text-[#94a3b8] mt-1">
                        Assessed via LightGBM multi-class probability thresholding (Macro F1 = 0.486)
                      </p>
                    </div>

                    <div
                      className="px-4 py-2 rounded-lg border font-orbitron font-bold text-sm tracking-wider"
                      style={{
                        backgroundColor: SEVERITY_BADGES[result.predicted_class]?.bg,
                        borderColor: SEVERITY_BADGES[result.predicted_class]?.border,
                        color: SEVERITY_BADGES[result.predicted_class]?.color,
                        boxShadow: `0 0 15px ${SEVERITY_BADGES[result.predicted_class]?.color}30`
                      }}
                    >
                      CLASS {result.predicted_class}
                    </div>
                  </div>
                </div>

                {/* Probability Distribution Chart */}
                <div className="scifi-panel p-5 border border-[#00d4ff]/30">
                  <div className="flex items-center justify-between pb-3 border-b border-[#00d4ff]/15 mb-3">
                    <span className="text-xs font-orbitron text-[#e2e8f0] tracking-wider flex items-center">
                      <BarChart3 size={15} className="text-[#00d4ff] mr-2" />
                      PREDICTION CLASS PROBABILITY DISTRIBUTION
                    </span>
                    <span className="text-[10px] font-share-tech text-[#94a3b8]">SOFTMAX WEIGHTS</span>
                  </div>

                  <div className="h-44 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={probData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <XAxis dataKey="class_name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#0d1b2a',
                            borderColor: 'rgba(0, 212, 255, 0.4)',
                            borderRadius: '6px',
                            fontFamily: 'Share Tech Mono'
                          }}
                          formatter={(v, name, item) => [`${(v * 100).toFixed(2)}%`, item.payload.class_label || name]}
                        />
                        <Bar dataKey="probability" radius={[4, 4, 0, 0]}>
                          {probData.map((_, idx) => (
                            <Cell key={`prob-cell-${idx}`} fill={probColors[idx % probColors.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* SHAP Feature Importance */}
                <div className="scifi-panel p-5 border border-[#00d4ff]/30">
                  <div className="flex items-center justify-between pb-3 border-b border-[#00d4ff]/15 mb-3">
                    <span className="text-xs font-orbitron text-[#e2e8f0] tracking-wider flex items-center">
                      <TrendingUp size={15} className="text-[#39ff14] mr-2" />
                      TOP SHAP FEATURE IMPACTS (PRE-INCIDENT INDICATORS)
                    </span>
                    <span className="text-[10px] font-share-tech text-[#39ff14]">SHAP VALUES</span>
                  </div>

                  {shapData.length > 0 ? (
                    <div className="h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={shapData}
                          layout="vertical"
                          margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
                        >
                          <XAxis type="number" stroke="#94a3b8" fontSize={10} tickLine={false} />
                          <YAxis dataKey="feature" type="category" stroke="#94a3b8" fontSize={10} tickLine={false} width={90} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#0d1b2a',
                              borderColor: 'rgba(0, 212, 255, 0.4)',
                              borderRadius: '6px',
                              fontFamily: 'Share Tech Mono'
                            }}
                            formatter={(v, _, item) => [`Impact: ${v}`, item.payload.fullFeature]}
                          />
                          <Bar dataKey="impact" fill="#00d4ff" radius={[0, 4, 4, 0]}>
                            {shapData.map((entry, idx) => (
                              <Cell
                                key={`shap-cell-${idx}`}
                                fill={entry.impact >= 0 ? '#00d4ff' : '#ff9500'}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="text-xs font-share-tech text-[#94a3b8] py-4 text-center">
                      SHAP impact details calculated directly for the winning class.
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <div className="scifi-panel p-12 border border-[#00d4ff]/20 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
                <Cpu size={48} className="text-[#00d4ff]/30 mb-4 animate-pulse" />
                <h4 className="font-orbitron font-semibold text-base text-[#e2e8f0] mb-2">
                  AWAITING INFERENCE PARAMETERS
                </h4>
                <p className="text-xs font-share-tech text-[#94a3b8] max-w-md leading-relaxed">
                  Select incident parameters in the tactical input matrix and click "Execute Threat Inference" to run the LightGBM classifier.
                </p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default PredictForm;
