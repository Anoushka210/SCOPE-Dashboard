import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

const FilterContext = createContext();

export const FilterProvider = ({ children }) => {
  const [filterOptions, setFilterOptions] = useState({
    regions: [],
    crime_types: [],
    date_min: '1970-01-01',
    date_max: '2026-06-27',
    countries: [],
    sub_types: [],
    actor_groups: []
  });

  const [filters, setFilters] = useState({
    region: 'All',
    crime_type: 'All',
    severity_min: 0, // 0: All, 1: Medium+ (score>2), 2: High+ (score>5), 3: Critical (score>15)
    date_start: '1970-01-01',
    date_end: '2026-06-27',
    include_non_violent: false // Off by default as required
  });

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [loadingFilters, setLoadingFilters] = useState(true);

  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        setLoadingFilters(true);
        const res = await apiClient.get('/api/filters');
        if (res.data) {
          setFilterOptions(res.data);
          setFilters(prev => ({
            ...prev,
            date_start: res.data.date_min || prev.date_start,
            date_end: res.data.date_max || prev.date_end
          }));
        }
      } catch (err) {
        console.error('Failed to fetch filter options from backend:', err);
      } finally {
        setLoadingFilters(false);
      }
    };

    fetchFilterOptions();
  }, []);

  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const resetFilters = () => {
    setFilters({
      region: 'All',
      crime_type: 'All',
      severity_min: 0,
      date_start: filterOptions.date_min || '1970-01-01',
      date_end: filterOptions.date_max || '2026-06-27',
      include_non_violent: false
    });
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  return (
    <FilterContext.Provider
      value={{
        filters,
        filterOptions,
        loadingFilters,
        isSidebarOpen,
        updateFilter,
        resetFilters,
        toggleSidebar
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

export default FilterContext;
