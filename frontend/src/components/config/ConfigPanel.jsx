import React, { useState, useEffect, useRef } from 'react';
import { Sliders, RotateCcw, ChevronDown, ChevronUp, Info, HardDrive, Check, Loader2, Zap, Cpu } from 'lucide-react';
import { configApi, ocrApi } from '../../api/client';

const ConfigPanel = ({ docType, config, setConfig }) => {
  const [factoryDefaults, setFactoryDefaults] = useState({});
  const [availableEngines, setAvailableEngines] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState('saved'); // 'saved' | 'saving' | 'error'
  const [isCustom, setIsCustom] = useState(false);
  const debounceTimerRef = useRef(null);

  const localKey = `doc_blur_config_${docType}`;

  // Initial load: Fetch active defaults and OCR engine availability
  useEffect(() => {
    ocrApi.getEngines().then(res => {
      if (Array.isArray(res.data)) setAvailableEngines(res.data);
    }).catch(() => {});
  }, []);

  // Initial load: Fetch active defaults from backend & reconcile with localStorage
  useEffect(() => {
    const fetchConfig = async () => {
      setLoading(true);
      try {
        const response = await configApi.getDefaults(docType);
        const serverConfig = response.data;
        const serverIsCustom = !!serverConfig._is_custom;

        const factoryRes = await configApi.getFactoryDefaults(docType);
        setFactoryDefaults(factoryRes.data);

        const localCached = localStorage.getItem(localKey);
        let activeConfig = serverConfig;

        if (localCached) {
          try {
            const parsed = JSON.parse(localCached);
            activeConfig = { ...factoryRes.data, ...parsed };
            setIsCustom(true);
          } catch (e) {
            console.error('Failed to parse local cached config', e);
          }
        } else {
          setIsCustom(serverIsCustom);
        }

        setConfig(activeConfig);
        setSaveStatus('saved');
      } catch (error) {
        console.error('Failed to fetch config defaults', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, [docType]);

  // Debounced auto-save to backend custom_config.json + instant localStorage sync
  const triggerAutoSave = (updatedConfig) => {
    try {
      localStorage.setItem(localKey, JSON.stringify(updatedConfig));
    } catch (e) {
      console.error('Failed to persist to localStorage', e);
    }

    setSaveStatus('saving');
    setIsCustom(true);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(async () => {
      try {
        await configApi.saveConfig(docType, updatedConfig);
        setSaveStatus('saved');
      } catch (err) {
        console.error('Failed to save config to server', err);
        setSaveStatus('error');
      }
    }, 600);
  };

  const handleFieldChange = (field, value) => {
    const updated = { ...config, [field]: value };
    setConfig(updated);
    triggerAutoSave(updated);
  };

  const handleResetToFactory = async () => {
    setSaveStatus('saving');
    try {
      await configApi.resetConfig(docType);
      localStorage.removeItem(localKey);
      setConfig({ ...factoryDefaults });
      setIsCustom(false);
      setSaveStatus('saved');
    } catch (error) {
      console.error('Failed to reset config', error);
      localStorage.removeItem(localKey);
      setConfig({ ...factoryDefaults });
      setIsCustom(false);
      setSaveStatus('saved');
    }
  };

  if (loading) {
    return (
      <div className="brutal-card p-4 mb-6 text-xs font-mono font-bold flex items-center gap-2 bg-white">
        <Loader2 className="w-4 h-4 text-[#3C1A47] animate-spin" />
        <span>LOADING CALIBRATION MATRIX...</span>
      </div>
    );
  }

  const fieldCategories = {
    'Resolution & Luma Checks': [
      'enable_resolution_check',
      'min_resolution_long_edge_px',
      'enable_brightness_check',
      'brightness_min',
      'brightness_max',
      'canonical_resize_width_px',
      'enable_denoise',
      'denoise_kernel_size',
    ],
    'Tiled Sharpness Scoring': [
      'enable_sharpness_check',
      'sharpness_algorithm',
      'sharp_pass_threshold',
      'blurry_reject_threshold',
      'sharpness_percentile',
      'tile_grid_rows',
      'tile_grid_cols',
      'blank_tile_variance_threshold',
    ],
    'Boundary & Glare Masking': [
      'enable_boundary_detection',
      'boundary_confidence_threshold',
      'fallback_center_crop_pct',
      'enable_glare_mask',
      'glare_value_threshold',
      'glare_saturation_threshold',
      'glare_max_area_pct',
      'enable_anisotropy_check',
      'anisotropy_ratio_flag_threshold',
    ],
    'OCR Text & Field Verification': [
      'enable_ocr',
      'ocr_engine',
      'ocr_confidence_threshold',
      'pdf_pages_to_check',
      'pdf_max_pages_checked',
    ],
  };

  const toggleDependencyMap = {
    // Resolution check
    min_resolution_long_edge_px: 'enable_resolution_check',
    // Brightness check
    brightness_min: 'enable_brightness_check',
    brightness_max: 'enable_brightness_check',
    // Denoise
    denoise_kernel_size: 'enable_denoise',
    // Sharpness scoring
    sharpness_algorithm: 'enable_sharpness_check',
    sharp_pass_threshold: 'enable_sharpness_check',
    blurry_reject_threshold: 'enable_sharpness_check',
    sharpness_percentile: 'enable_sharpness_check',
    tile_grid_rows: 'enable_sharpness_check',
    tile_grid_cols: 'enable_sharpness_check',
    blank_tile_variance_threshold: 'enable_sharpness_check',
    // Boundary detection
    boundary_confidence_threshold: 'enable_boundary_detection',
    fallback_center_crop_pct: 'enable_boundary_detection',
    // Glare mask
    glare_value_threshold: 'enable_glare_mask',
    glare_saturation_threshold: 'enable_glare_mask',
    glare_max_area_pct: 'enable_glare_mask',
    // Anisotropy check
    anisotropy_ratio_flag_threshold: 'enable_anisotropy_check',
    // OCR verification
    ocr_engine: 'enable_ocr',
    ocr_confidence_threshold: 'enable_ocr',
    pdf_pages_to_check: 'enable_ocr',
    pdf_max_pages_checked: 'enable_ocr',
    ocr_field_set: 'enable_ocr',
  };

  return (
    <div className="brutal-card p-0 mb-6 overflow-hidden">
      {/* Header Bar */}
      <div
        className="flex flex-col sm:flex-row sm:items-center justify-between px-5 py-4 cursor-pointer select-none bg-white hover:bg-[#FAF7F0] transition-colors gap-3 border-b-[3px] border-[#2A2312]"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="p-1.5 bg-[#FFBE0B] border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312]">
            <Sliders className="w-4 h-4 text-[#2A2312] stroke-[2.5]" />
          </div>
          <h3 className="text-sm font-black text-[#2A2312] uppercase tracking-tight font-heading">
            Pipeline Thresholds & Calibration
          </h3>

          <span className="text-[11px] bg-[#3C1A47] text-white px-2 py-0.5 border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] font-mono font-bold uppercase">
            {docType === 'general' ? 'General Doc' : 'ID & Passport'}
          </span>

          {isCustom ? (
            <span className="text-[10px] font-black text-[#2A2312] bg-[#B6FF00] border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] px-2 py-0.5 font-mono flex items-center gap-1">
              <HardDrive className="w-3 h-3 stroke-[2.5]" /> CUSTOM OVERRIDES
            </span>
          ) : (
            <span className="text-[10px] font-bold text-[#2A2312]/80 bg-[#F5F0E6] border-2 border-[#2A2312] px-2 py-0.5 font-mono">
              FACTORY DEFAULTS
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {saveStatus === 'saving' && (
            <span className="text-xs font-mono font-bold text-[#2A2312] bg-[#FFBE0B] border-2 border-[#2A2312] px-2 py-0.5 flex items-center gap-1 shadow-[2px_2px_0px_#2A2312]">
              <Loader2 className="w-3 h-3 animate-spin stroke-[3]" /> SAVING...
            </span>
          )}
          {saveStatus === 'saved' && isCustom && (
            <span className="text-xs font-mono font-bold text-[#2A2312] bg-[#B6FF00] border-2 border-[#2A2312] px-2 py-0.5 flex items-center gap-1 shadow-[2px_2px_0px_#2A2312]">
              <Check className="w-3 h-3 stroke-[3]" /> SYNCED
            </span>
          )}
          <span className="text-xs font-mono font-black text-[#2A2312] uppercase flex items-center gap-1 bg-white px-2 py-1 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312]">
            {isExpanded ? (
              <>
                <ChevronUp className="w-3.5 h-3.5 stroke-[2.5]" /> COLLAPSE
              </>
            ) : (
              <>
                <ChevronDown className="w-3.5 h-3.5 stroke-[2.5]" /> CONFIGURE
              </>
            )}
          </span>
        </div>
      </div>

      {/* Accordion Body */}
      {isExpanded && (
        <div className="p-5 bg-[#F5F0E6] space-y-5 border-t border-[#2A2312]/20">
          {/* Top Info Bar */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-white p-3.5 border-2 border-[#2A2312] shadow-[3px_3px_0px_#2A2312]">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-[#3C1A47] flex-shrink-0" />
              <span className="text-xs text-[#2A2312] font-mono leading-relaxed">
                <strong>HYBRID STORAGE ACTIVE:</strong> Changes persist immediately to browser localStorage and sync to <code>custom_config.json</code> on host.
              </span>
            </div>
            <div className="flex items-center gap-2 self-end sm:self-auto">
              <button
                type="button"
                onClick={handleResetToFactory}
                className="brutal-btn-sm bg-[#FFBE0B] hover:bg-[#f5b300] text-[#2A2312] px-3 py-1.5 text-xs font-mono font-black flex items-center gap-1.5 uppercase"
                title="Restore pre-calibrated defaults"
              >
                <RotateCcw className="w-3 h-3 stroke-[2.5]" /> RESET FACTORY
              </button>
            </div>
          </div>

          {/* Configuration Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {Object.entries(fieldCategories).map(([category, fields]) => {
              const relevantFields = fields.filter((k) => k in (config || factoryDefaults) || k === 'ocr_engine');
              if (relevantFields.length === 0) return null;

              return (
                <div key={category} className="bg-white border-2 border-[#2A2312] shadow-[3.5px_3.5px_0px_#2A2312] p-4 space-y-3">
                  <h4 className="text-xs font-black uppercase tracking-wider text-[#3C1A47] border-b-2 border-[#2A2312] pb-2 flex items-center justify-between font-mono">
                    <span>{category}</span>
                    <span className="text-[10px] text-[#2A2312]/60 font-bold">[{relevantFields.length} KEYS]</span>
                  </h4>

                  <div className="space-y-3">
                    {relevantFields.map((key) => {
                      const value = config[key] ?? factoryDefaults[key];
                      const isDefault = value === factoryDefaults[key];
                      const parentToggle = toggleDependencyMap[key];
                      const isParentDisabled = parentToggle ? !(config[parentToggle] ?? factoryDefaults[parentToggle]) : false;

                      return (
                        <div
                          key={key}
                          className={`flex flex-col gap-1 transition-opacity ${
                            isParentDisabled ? 'opacity-40' : ''
                          }`}
                        >
                          <div className="flex justify-between items-center">
                            <label
                              className={`text-xs font-bold uppercase font-mono tracking-tight ${
                                isParentDisabled ? 'text-[#2A2312]/40 line-through' : 'text-[#2A2312]'
                              }`}
                            >
                              {key.replace(/_/g, ' ')}
                            </label>
                            {isParentDisabled ? (
                              <span
                                className="text-[9px] font-black text-[#2A2312]/60 bg-[#E5DFD1] border border-[#2A2312]/30 px-1.5 py-0.2 font-mono"
                                title={`Disabled because ${parentToggle.replace(/_/g, ' ')} is OFF`}
                              >
                                DISABLED
                              </span>
                            ) : !isDefault ? (
                              <span className="text-[9px] font-black text-[#2A2312] bg-[#FFBE0B] border border-[#2A2312] px-1.5 py-0.2 font-mono">
                                MODIFIED
                              </span>
                            ) : null}
                          </div>

                          {key === 'ocr_engine' ? (
                            <div className={`space-y-1.5 mt-1 ${isParentDisabled ? 'pointer-events-none' : ''}`}>
                              <div className="grid grid-cols-2 gap-2">
                                {[
                                  { id: 'auto', label: 'Auto Detect' },
                                  { id: 'tesseract', label: 'Tesseract' },
                                  { id: 'doctr', label: 'docTR (Mindee)' },
                                  { id: 'paddleocr', label: 'PaddleOCR' },
                                ].map((eng) => {
                                  const isSelected = (value || 'auto') === eng.id;
                                  const engineInfo = availableEngines.find((e) => e.id === eng.id);
                                  const isAvail = engineInfo ? engineInfo.available : (eng.id === 'auto' || eng.id === 'tesseract');

                                  return (
                                    <button
                                      key={eng.id}
                                      type="button"
                                      disabled={isParentDisabled}
                                      onClick={() => !isParentDisabled && handleFieldChange('ocr_engine', eng.id)}
                                      className={`brutal-btn-sm p-2 text-left flex flex-col justify-between transition ${
                                        isParentDisabled
                                          ? 'bg-[#E5DFD1] text-[#2A2312]/40 border-2 border-[#2A2312]/30 cursor-not-allowed'
                                          : isSelected
                                          ? 'bg-[#B6FF00] text-[#2A2312] border-2 border-[#2A2312]'
                                          : 'bg-white text-[#2A2312] border-2 border-[#2A2312] hover:bg-[#FAF7F0]'
                                      }`}
                                    >
                                      <div className="flex items-center justify-between">
                                        <span className="font-mono text-xs font-black uppercase tracking-tight">
                                          {eng.label}
                                        </span>
                                        {isSelected && (
                                          <span className="w-2.5 h-2.5 bg-[#2A2312] border border-black inline-block" />
                                        )}
                                      </div>
                                      <span
                                        className={`text-[9px] font-mono font-bold mt-1.5 inline-block px-1.5 py-0.5 border self-start ${
                                          isParentDisabled
                                            ? 'bg-gray-100 text-gray-500 border-gray-300'
                                            : isAvail
                                            ? 'bg-emerald-100 text-emerald-900 border-emerald-600'
                                            : 'bg-[#FFBE0B]/40 text-[#2A2312] border-[#2A2312]'
                                        }`}
                                      >
                                        {isAvail ? '✓ READY' : '⚠ FALLBACK'}
                                      </span>
                                    </button>
                                  );
                                })}
                              </div>
                              <p className="text-[10px] font-mono text-[#2A2312]/70 italic">
                                Graceful Fallback: If docTR or PaddleOCR is selected but not installed, system automatically falls back to Tesseract.
                              </p>
                            </div>
                          ) : typeof value === 'boolean' ? (
                            <div className="flex items-center gap-2 mt-0.5">
                              <button
                                type="button"
                                onClick={() => handleFieldChange(key, !value)}
                                className={`brutal-btn-sm px-3 py-1 text-[11px] font-mono font-black flex items-center gap-1.5 uppercase ${
                                  value
                                    ? 'bg-[#B6FF00] text-[#2A2312]'
                                    : 'bg-[#F5F0E6] text-[#2A2312]/60'
                                }`}
                              >
                                <span className={`w-2 h-2 border border-[#2A2312] ${value ? 'bg-[#2A2312]' : 'bg-white'}`} />
                                {value ? 'ENABLED' : 'DISABLED'}
                              </button>
                            </div>
                          ) : typeof factoryDefaults[key] === 'number' ? (
                            <input
                              type="number"
                              disabled={isParentDisabled}
                              step={Number.isInteger(factoryDefaults[key]) ? '1' : '0.01'}
                              value={value !== undefined ? value : ''}
                              onChange={(e) => {
                                if (isParentDisabled) return;
                                const parsed = parseFloat(e.target.value);
                                handleFieldChange(key, isNaN(parsed) ? '' : parsed);
                              }}
                              className={`brutal-input px-2.5 py-1.5 text-xs font-mono font-bold ${
                                isParentDisabled
                                  ? 'bg-[#E5DFD1] cursor-not-allowed text-[#2A2312]/40 border-dashed border-[#2A2312]/40 shadow-none'
                                  : ''
                              }`}
                            />
                          ) : (
                            <input
                              type="text"
                              disabled={isParentDisabled}
                              value={typeof value === 'object' ? JSON.stringify(value) : value || ''}
                              onChange={(e) => !isParentDisabled && handleFieldChange(key, e.target.value)}
                              className={`brutal-input px-2.5 py-1.5 text-xs font-mono font-bold ${
                                isParentDisabled
                                  ? 'bg-[#E5DFD1] cursor-not-allowed text-[#2A2312]/40 border-dashed border-[#2A2312]/40 shadow-none'
                                  : ''
                              }`}
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigPanel;
