import React from 'react';
import { ShieldCheck, AlertTriangle, Database, Scale, BookOpen, Cpu, Info, CheckCircle2 } from 'lucide-react';

export const DataEthics = () => {
  const modelMetrics = [
    { class: 'Low (0)', score: 'Score ≤ 2.0', precision: '0.8122', recall: '0.7370', f1: '0.7728', support: '155,450' },
    { class: 'Medium (1)', score: '2.0 < Score ≤ 5.0', precision: '0.3304', recall: '0.3018', f1: '0.3154', support: '49,256' },
    { class: 'High (2)', score: '5.0 < Score ≤ 15.0', precision: '0.3093', recall: '0.3302', f1: '0.3194', support: '35,363' },
    { class: 'Critical (3)', score: 'Score > 15.0', precision: '0.4357', recall: '0.6988', f1: '0.5367', support: '26,946' }
  ];

  return (
    <div className="space-y-6">
      {/* Disclaimer Banner */}
      <div className="p-4 rounded-lg bg-[#ff9500]/10 border border-[#ff9500]/40 text-[#ff9500] shadow-[0_0_15px_rgba(255,149,0,0.15)] flex items-start space-x-3">
        <AlertTriangle className="flex-shrink-0 mt-0.5" size={20} />
        <div>
          <h4 className="font-orbitron font-bold text-sm tracking-wider">
            MANDATED ETHICAL & METHODOLOGICAL DISCLAIMER
          </h4>
          <p className="text-xs font-share-tech mt-1 text-[#e2e8f0] leading-relaxed">
            "This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."
          </p>
        </div>
      </div>

      {/* Main Governance Content */}
      <div className="scifi-panel p-6 border border-[#00d4ff]/30 space-y-8">
        {/* Section 1: Data Sources & Provenance */}
        <div>
          <h3 className="font-orbitron font-bold text-base text-[#00d4ff] flex items-center mb-3">
            <Database className="mr-2" size={18} />
            1. MULTI-SOURCE INTEGRATION & DATA PROVENANCE
          </h3>
          <p className="text-xs font-share-tech text-[#94a3b8] leading-relaxed mb-4">
            SCOPE reconciles heterogeneous global conflict, maritime threat, and synthetic trafficking indicators into a unified taxonomy:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="font-orbitron font-bold text-xs text-[#00d4ff] block mb-1">
                ACLED (Armed Conflict Location & Event Data)
              </span>
              <p className="text-xs font-share-tech text-[#cbd5e1] leading-relaxed">
                Global coverage of political violence, civil disorder, and armed clashes. ACLED aggregates weekly clusters; counting the EVENTS multiplier expands 968,024 clusters into 3,109,601 security events.
              </p>
            </div>

            <div className="p-4 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="font-orbitron font-bold text-xs text-[#00d4ff] block mb-1">
                GTD (Global Terrorism Database)
              </span>
              <p className="text-xs font-share-tech text-[#cbd5e1] leading-relaxed">
                Systematic historical records of international and domestic terrorism events from 1970–2020 (START / University of Maryland). Primary source for named organized perpetrator groups.
              </p>
            </div>

            <div className="p-4 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="font-orbitron font-bold text-xs text-[#00d4ff] block mb-1">
                ASAM (Anti-Shipping Activity Messages - NGA)
              </span>
              <p className="text-xs font-share-tech text-[#cbd5e1] leading-relaxed">
                Geographic coordinates and hostility profiles of maritime vessel boardings, piracy attacks, and hijackings worldwide (1978–2024).
              </p>
            </div>

            <div className="p-4 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="font-orbitron font-bold text-xs text-[#00d4ff] block mb-1">
                CTDC (Counter Trafficking Data Collaborative)
              </span>
              <p className="text-xs font-share-tech text-[#cbd5e1] leading-relaxed">
                Demographic patterns and exploitation routes. <strong className="text-[#ff9500]">Crucial Note:</strong> CTDC data consists of algorithmically generated synthetic records, not direct individual victim cases.
              </p>
            </div>
          </div>
        </div>

        {/* Section 2: Critical Biases & Null Governance */}
        <div className="pt-4 border-t border-[#00d4ff]/15">
          <h3 className="font-orbitron font-bold text-base text-[#ff9500] flex items-center mb-3">
            <Scale className="mr-2" size={18} />
            2. DATA LIMITATIONS, REPORTING BIAS & FATALITY NULLS
          </h3>

          <div className="space-y-3 text-xs font-share-tech text-[#cbd5e1] leading-relaxed">
            <div className="p-3.5 rounded bg-[#0a0f1e] border border-[#ff9500]/30">
              <span className="font-bold text-[#ff9500] block mb-1">⚠️ ASAM Fatality Nulls Rationale:</span>
              Maritime ASAM reports document tactical vessel incidents without explicit casualty records (100% null/NaN). ASAM fatalities are strictly preserved as null and excluded from aggregate fatality totals to prevent misleading 0-fatality misrepresentations.
            </div>

            <div className="p-3.5 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
              <span className="font-bold text-[#00d4ff] block mb-1">🌐 Conflict Zone Reporting Disparities:</span>
              Reporting densities skew higher in areas with active open-source monitoring and press freedom. Underreporting occurs in active combat theaters, remote maritime corridors, and state-controlled information spaces.
            </div>
          </div>
        </div>

        {/* Section 3: Severity Formula & Scale Truth */}
        <div className="pt-4 border-t border-[#00d4ff]/15">
          <h3 className="font-orbitron font-bold text-base text-[#39ff14] flex items-center mb-3">
            <BookOpen className="mr-2" size={18} />
            3. MATHEMATICAL SEVERITY FORMULA & CONTINUOUS SCALE
          </h3>

          <div className="p-4 rounded bg-[#0a0f1e] border border-[#39ff14]/30 space-y-2 text-xs font-share-tech">
            <div className="text-sm font-bold text-[#39ff14] font-share-tech">
              Severity Score = (Fatalities × 3.0) + (Wounded / Events × 1.0) + Baseline Operational Weight
            </div>
            <p className="text-[#cbd5e1] leading-relaxed">
              <strong>Scale Clarification:</strong> Raw severity scores are NOT bounded to 1–5 integers; they form an unbounded continuous scale spanning from 1.0 up to 36,825.0 depending on mass-casualty events and cluster event counts. Scores are partitioned into four discrete threat classes for machine learning:
            </p>
            <ul className="list-disc list-inside space-y-1 text-[#e2e8f0] pt-1">
              <li><strong className="text-[#39ff14]">Low (Class 0):</strong> Score ≤ 2.0 (Low operational disruption, 0 fatalities)</li>
              <li><strong className="text-[#ff9500]">Medium (Class 1):</strong> 2.0 &lt; Score ≤ 5.0 (Moderate violence / property confrontation)</li>
              <li><strong className="text-[#ea580c]">High (Class 2):</strong> 5.0 &lt; Score ≤ 15.0 (Armed clash / multiple casualties)</li>
              <li><strong className="text-[#ff3333]">Critical (Class 3):</strong> Score &gt; 15.0 (Mass violence, severe casualties, major conflict)</li>
            </ul>
          </div>
        </div>

        {/* Section 4: Leakage-Free Model Performance */}
        <div className="pt-4 border-t border-[#00d4ff]/15">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <h3 className="font-orbitron font-bold text-base text-[#e2e8f0] flex items-center">
              <Cpu className="text-[#00d4ff] mr-2" size={18} />
              4. HONEST LEAKAGE-FREE LIGHTGBM EVALUATION (TEST 2024+)
            </h3>
            <span className="text-xs font-share-tech text-[#00d4ff] px-2.5 py-1 rounded bg-[#00d4ff]/10 border border-[#00d4ff]/30">
              Macro F1: 0.4861 | Accuracy: 59.90%
            </span>
          </div>

          <div className="p-3 mb-4 rounded bg-[#39ff14]/10 border border-[#39ff14]/30 text-xs font-share-tech text-[#e2e8f0]">
            <CheckCircle2 size={15} className="inline mr-1.5 text-[#39ff14]" />
            <strong>Target Leakage Audited & Removed:</strong> All target-defining indicators (fatalities, nkill, nwound, and EVENTS) have been completely removed from model training. Encoders are fitted strictly on pre-2024 training years. The model predicts purely from pre-event contextual signals.
          </div>

          {/* Model Metrics Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-share-tech border border-[#00d4ff]/20">
              <thead className="bg-[#0a0f1e] text-[#00d4ff] font-orbitron border-b border-[#00d4ff]/20">
                <tr>
                  <th className="py-2.5 px-3 text-left">THREAT CLASS</th>
                  <th className="py-2.5 px-3 text-left">SCORE RANGE</th>
                  <th className="py-2.5 px-3 text-right">PRECISION</th>
                  <th className="py-2.5 px-3 text-right">RECALL</th>
                  <th className="py-2.5 px-3 text-right">F1 SCORE</th>
                  <th className="py-2.5 px-3 text-right">TEST SUPPORT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#00d4ff]/10">
                {modelMetrics.map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#00d4ff]/5 transition-colors">
                    <td className="py-2.5 px-3 font-bold text-[#e2e8f0]">{row.class}</td>
                    <td className="py-2.5 px-3 text-[#94a3b8]">{row.score}</td>
                    <td className="py-2.5 px-3 text-right text-[#e2e8f0]">{row.precision}</td>
                    <td className="py-2.5 px-3 text-right text-[#e2e8f0]">{row.recall}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-[#00d4ff]">{row.f1}</td>
                    <td className="py-2.5 px-3 text-right text-[#94a3b8]">{row.support}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 p-4 rounded bg-[#0a0f1e] border border-[#00d4ff]/20 text-[#cbd5e1] text-xs font-share-tech leading-relaxed">
            <span className="font-bold text-[#00d4ff] block mb-1">ASSESSMENT & CLASS RECALL:</span>
            Without target leakage from casualties, overall Macro F1 is <strong>0.4861</strong> across 267,015 held-out test events. The model maintains strong recall on Critical severity events (69.88% recall, F1 = 0.5367) and Low severity events (73.70% recall, F1 = 0.7728). Medium and High classes exhibit overlap (F1 ~0.31-0.32) because tactical indicators prior to an event cannot always disambiguate whether an engagement will escalate into moderate vs severe clashes.
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataEthics;
