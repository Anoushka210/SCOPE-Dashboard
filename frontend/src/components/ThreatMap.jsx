import React, { useState, useEffect, useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import Map from 'react-map-gl/maplibre';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

// Explicitly configure MapLibre Web Worker URL for Vite dev/build
const maplibreWorkerUrl = new URL(
  'maplibre-gl/dist/maplibre-gl-worker.mjs',
  import.meta.url
).href;

if (typeof maplibregl.setWorkerUrl === 'function') {
  maplibregl.setWorkerUrl(maplibreWorkerUrl);
}
import { motion, AnimatePresence } from 'framer-motion';
import apiClient from '../api/client';
import { useFilters } from '../context/FilterContext';
import { Layers, Flame, Eye, AlertTriangle, X, Shield, MapPin, Calendar, Crosshair, RefreshCw, Info } from 'lucide-react';

// Free open-source CartoDB Dark Matter map style JSON
const CARTO_DARK_MATTER = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: 15.0,
  latitude: 15.0,
  zoom: 1.8,
  minZoom: 1,
  maxZoom: 14,
  pitch: 0,
  bearing: 0
};

const CRIME_COLORS = {
  'Political violence': [0, 212, 255],
  'Battles': [255, 51, 51],
  'Violence against civilians': [255, 149, 0],
  'Explosions/Remote violence': [255, 0, 128],
  'Protests': [57, 255, 20],
  'Riots': [255, 204, 0],
  'Terrorism': [220, 38, 38],
  'Maritime Piracy': [14, 165, 233],
  'Cartel Violence': [168, 85, 247],
  'Strategic developments': [148, 163, 184]
};

const getCrimeColor = (crime) => {
  return CRIME_COLORS[crime] || [0, 212, 255];
};

export const ThreatMap = () => {
  const { filters } = useFilters();
  const [points, setPoints] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isCapped, setIsCapped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isHeatmap, setIsHeatmap] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    const fetchMapPoints = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        if (filters.region && filters.region !== 'All') params.append('region', filters.region);
        if (filters.crime_type && filters.crime_type !== 'All') params.append('crime_type', filters.crime_type);
        if (filters.severity_min > 0) params.append('severity_min', filters.severity_min);
        if (filters.date_start) params.append('date_start', filters.date_start);
        if (filters.date_end) params.append('date_end', filters.date_end);

        const res = await apiClient.get(`/api/map-data?${params.toString()}`);
        if (res.data) {
          setPoints(res.data);
          const rawTotal = res.headers['x-total-count'];
          const totalVal = rawTotal ? parseInt(rawTotal, 10) : res.data.length;
          setTotalCount(totalVal);
          setIsCapped(totalVal > 1000 || res.headers['x-is-capped'] === 'true');
        }
      } catch (err) {
        console.error('Failed to fetch map data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMapPoints();
  }, [filters]);

  const layers = useMemo(() => {
    if (isHeatmap) {
      return [
        new HeatmapLayer({
          id: 'threat-heatmap',
          data: points,
          getPosition: d => [d.lon, d.lat],
          getWeight: d => Math.max(1, d.severity_score || 1),
          radiusPixels: 45,
          intensity: 1.8,
          threshold: 0.05,
          aggregation: 'SUM'
        })
      ];
    }

    return [
      new ScatterplotLayer({
        id: 'threat-scatterplot',
        data: points,
        pickable: true,
        opacity: 0.85,
        stroked: true,
        filled: true,
        radiusUnits: 'pixels',
        radiusScale: 1,
        radiusMinPixels: 4,
        radiusMaxPixels: 22,
        lineWidthMinPixels: 1,
        getPosition: d => [d.lon, d.lat],
        getRadius: d => Math.max(4, Math.min(22, (d.severity_score || 1) * 3.2)),
        getFillColor: d => [...getCrimeColor(d.crime_type), 200],
        getLineColor: [255, 255, 255, 180],
        onClick: info => {
          if (info.object) {
            setSelectedIncident(info.object);
          }
        }
      })
    ];
  }, [points, isHeatmap]);

  const getTooltip = ({ object }) => {
    if (!object || isHeatmap) return null;
    return {
      html: `
        <div style="background: #0d1b2a; border: 1px solid rgba(0,212,255,0.4); border-radius: 6px; padding: 10px 14px; box-shadow: 0 0 15px rgba(0,212,255,0.25); color: #e2e8f0; font-family: 'Share Tech Mono', monospace; font-size: 12px; line-height: 1.5; pointer-events: none; max-width: 320px;">
          <div style="font-family: 'Orbitron', monospace; font-size: 10px; color: #ff9500; font-weight: bold; letter-spacing: 0.08em; margin-bottom: 2px;">
            [SYNTHESIZED SUMMARY]
          </div>
          <div style="font-family: 'Orbitron', monospace; font-weight: bold; color: #00d4ff; font-size: 13px; margin-bottom: 4px;">
            ${object.crime_type}
          </div>
          <div><b style="color: #94a3b8;">Country:</b> ${object.country}</div>
          <div><b style="color: #94a3b8;">Actor:</b> ${object.actor_group}</div>
          <div><b style="color: #94a3b8;">Date:</b> ${object.date}</div>
          <div><b style="color: #94a3b8;">Severity Score:</b> <span style="color: ${object.severity_score > 5 ? '#ff3333' : '#ff9500'}; font-weight: bold;">${object.severity_score.toFixed(1)}</span></div>
          <div style="font-size: 11px; color: #cbd5e1; margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(0,212,255,0.2); font-style: italic;">
            ${object.description}
          </div>
        </div>
      `,
      style: {
        backgroundColor: 'transparent',
        padding: '0px'
      }
    };
  };

  return (
    <div className="scifi-panel relative w-full h-[650px] overflow-hidden border border-[#00d4ff]/30">
      {/* Top Map Control Bar */}
      <div className="absolute top-4 left-4 z-20 flex flex-wrap items-center gap-2 pointer-events-auto">
        {/* Heatmap Toggle Button */}
        <button
          onClick={() => setIsHeatmap(!isHeatmap)}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-orbitron tracking-wider transition-all cursor-pointer backdrop-blur-md border ${
            isHeatmap
              ? 'bg-[#ff3333]/20 border-[#ff3333] text-[#ff3333] shadow-[0_0_15px_rgba(255,51,51,0.4)]'
              : 'bg-[#0d1b2a]/90 border-[#00d4ff]/40 text-[#00d4ff] hover:bg-[#00d4ff]/10 shadow-[0_0_12px_rgba(0,212,255,0.2)]'
          }`}
        >
          {isHeatmap ? <Flame size={14} className="animate-pulse" /> : <Layers size={14} />}
          <span>{isHeatmap ? 'DENSITY HEATMAP: ON' : 'HEATMAP VIEW'}</span>
        </button>
      </div>

      {/* Point Cap & Status Warning Badge */}
      <div className="absolute top-4 right-4 z-20 pointer-events-none flex flex-col items-end gap-1.5">
        <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#0d1b2a]/90 border border-[#00d4ff]/30 text-xs font-share-tech text-[#e2e8f0] backdrop-blur-md shadow-md">
          <span className="w-2 h-2 rounded-full bg-[#00d4ff] animate-ping"></span>
          <span>
            EVENTS PLOTTED: <strong className="text-[#00d4ff]">{points.length.toLocaleString()}</strong>
          </span>
        </div>

        {isCapped && (
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded bg-[#ff9500]/15 border border-[#ff9500]/40 text-[#ff9500] text-xs font-share-tech backdrop-blur-md shadow-[0_0_10px_rgba(255,149,0,0.2)]">
            <AlertTriangle size={13} />
            <span>
              Cap applied: Sampled 1,000 of {totalCount.toLocaleString()} total points (severity-weighted)
            </span>
          </div>
        )}
      </div>

      {/* DeckGL Map Canvas with synchronized MapLibre CartoDB Dark Matter Basemap */}
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={{ doubleClickZoom: false, dragRotate: false }}
        layers={layers}
        getTooltip={getTooltip}
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
      >
        <Map
          mapLib={maplibregl}
          mapStyle={CARTO_DARK_MATTER}
          style={{ width: '100%', height: '100%' }}
          reuseMaps
        />
      </DeckGL>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-[#0a0f1e]/60 backdrop-blur-sm z-30 flex items-center justify-center pointer-events-none">
          <div className="flex flex-col items-center space-y-2">
            <div className="w-8 h-8 border-2 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
            <span className="font-orbitron text-xs text-[#00d4ff] tracking-widest">
              QUERYING GEOSPATIAL TELEMETRY...
            </span>
          </div>
        </div>
      )}

      {/* Slide-in Detail Panel on Incident Click */}
      <AnimatePresence>
        {selectedIncident && (
          <motion.div
            initial={{ x: 380, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 380, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 220 }}
            className="absolute top-0 right-0 w-80 md:w-96 h-full bg-[#0d1b2a]/95 backdrop-blur-lg border-l border-[#00d4ff]/40 p-5 z-40 overflow-y-auto shadow-[-10px_0_30px_rgba(0,0,0,0.8)]"
          >
            <div className="flex items-center justify-between pb-3 border-b border-[#00d4ff]/20 mb-4">
              <div className="flex items-center space-x-2">
                <Shield size={18} className="text-[#00d4ff]" />
                <h4 className="font-orbitron font-semibold text-sm text-[#e2e8f0] tracking-wider">
                  INCIDENT TELEMETRY
                </h4>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="text-[#94a3b8] hover:text-[#ff3333] p-1 rounded hover:bg-[#ff3333]/10 transition-all cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Threat Classification & Badge */}
              <div>
                <span className="text-[10px] font-orbitron text-[#94a3b8] tracking-widest block mb-1">
                  THREAT CATEGORY
                </span>
                <div className="flex items-center justify-between">
                  <span className="font-orbitron font-bold text-base text-[#00d4ff]">
                    {selectedIncident.crime_type}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded text-xs font-share-tech font-bold border ${
                    selectedIncident.severity_score > 15
                      ? 'bg-[#ff3333]/20 border-[#ff3333] text-[#ff3333]'
                      : selectedIncident.severity_score > 5
                      ? 'bg-[#ff9500]/20 border-[#ff9500] text-[#ff9500]'
                      : 'bg-[#39ff14]/20 border-[#39ff14] text-[#39ff14]'
                  }`}>
                    SEVERITY {selectedIncident.severity_score.toFixed(1)}
                  </span>
                </div>
              </div>

              {/* Geographic Coordinates */}
              <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                <div className="flex items-center text-xs font-orbitron text-[#94a3b8] mb-1">
                  <MapPin size={13} className="text-[#00d4ff] mr-1.5" /> GEOGRAPHIC ANCHOR
                </div>
                <div className="text-sm font-share-tech text-[#e2e8f0] font-semibold">
                  {selectedIncident.country}
                </div>
                <div className="text-xs font-share-tech text-[#94a3b8] mt-1">
                  LAT: {selectedIncident.lat.toFixed(4)}° | LON: {selectedIncident.lon.toFixed(4)}°
                </div>
              </div>

              {/* Actor Group */}
              <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                <div className="flex items-center text-xs font-orbitron text-[#94a3b8] mb-1">
                  <Crosshair size={13} className="text-[#ff9500] mr-1.5" /> RECORDED ACTOR STRING
                </div>
                <div className="text-sm font-share-tech text-[#ff9500] font-semibold">
                  {selectedIncident.actor_group}
                </div>
              </div>

              {/* Temporal Timestamp */}
              <div className="p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                <div className="flex items-center text-xs font-orbitron text-[#94a3b8] mb-1">
                  <Calendar size={13} className="text-[#39ff14] mr-1.5" /> RECORDED TIMESTAMP
                </div>
                <div className="text-sm font-share-tech text-[#e2e8f0]">
                  {selectedIncident.date || 'Unspecified'}
                </div>
              </div>

              {/* Templated Summary Note */}
              <div>
                <span className="text-[10px] font-orbitron text-[#ff9500] tracking-widest block mb-1">
                  SYNTHESIZED EVENT SUMMARY (NOT VERBATIM RAW TEXT)
                </span>
                <p className="text-xs font-share-tech text-[#cbd5e1] leading-relaxed p-3 rounded bg-[#0a0f1e] border border-[#00d4ff]/15">
                  {selectedIncident.description}
                </p>
              </div>

              {/* Footer Note */}
              <div className="pt-2 text-[10px] font-share-tech text-[#94a3b8] border-t border-[#00d4ff]/15">
                SOURCE DATASET STRATIFIED TELEMETRY
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ThreatMap;
