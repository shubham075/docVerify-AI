import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Download,
  FileText,
  Copy,
  Check,
  Layers,
  Calendar,
  User,
  Hash,
  CreditCard,
  Terminal,
  FileCheck
} from 'lucide-react';

const OcrDataBox = ({ ocrData }) => {
  const [activeTab, setActiveTab] = useState('fields');
  const [copied, setCopied] = useState(false);

  if (!ocrData || ocrData.status === 'skipped' || !ocrData.raw_text) return null;

  const fields = ocrData.extracted_fields || {};
  const hasFields = Object.keys(fields).length > 0;

  const handleCopy = () => {
    navigator.clipboard.writeText(ocrData.raw_text || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-5 border-[3px] border-[#2A2312] bg-[#FAF7F0] shadow-[4px_4px_0px_#2A2312] overflow-hidden">
      {/* Header with Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between px-4 py-3.5 bg-[#3C1A47] text-white border-b-[3px] border-[#2A2312] gap-3">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="p-1 bg-[#B6FF00] text-[#2A2312] border border-[#2A2312]">
            <FileText className="w-4 h-4 stroke-[2.5]" />
          </div>
          <span className="text-xs font-black uppercase tracking-wider font-heading text-white">
            EXTRACTED OCR ENTITIES & DATA
          </span>
          {ocrData.engine && (
            <span className="bg-white text-[#2A2312] border border-[#2A2312] px-2 py-0.5 text-[10px] font-mono font-black uppercase">
              {ocrData.engine}
            </span>
          )}
          <span className="bg-[#B6FF00] text-[#2A2312] border border-[#2A2312] px-2 py-0.5 text-[10px] font-mono font-black">
            {ocrData.total_words || 0} WORDS
          </span>
          {ocrData.avg_word_confidence > 0 && (
            <span className="bg-[#FFBE0B] text-[#2A2312] border border-[#2A2312] px-2 py-0.5 text-[10px] font-mono font-black">
              {ocrData.avg_word_confidence}% CONF
            </span>
          )}
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex gap-1.5">
            <button
              type="button"
              onClick={() => setActiveTab('fields')}
              className={`brutal-btn-sm px-2.5 py-1 text-[11px] font-mono font-black flex items-center gap-1 uppercase ${
                activeTab === 'fields'
                  ? 'bg-[#B6FF00] text-[#2A2312]'
                  : 'bg-white text-[#2A2312] hover:bg-[#F5F0E6]'
              }`}
            >
              <Layers className="w-3 h-3 stroke-[2.5]" /> ENTITIES {hasFields ? `(${Object.keys(fields).length})` : ''}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('raw')}
              className={`brutal-btn-sm px-2.5 py-1 text-[11px] font-mono font-black flex items-center gap-1 uppercase ${
                activeTab === 'raw'
                  ? 'bg-[#B6FF00] text-[#2A2312]'
                  : 'bg-white text-[#2A2312] hover:bg-[#F5F0E6]'
              }`}
            >
              <Terminal className="w-3 h-3 stroke-[2.5]" /> RAW TEXT
            </button>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="brutal-btn-sm bg-[#FFBE0B] hover:bg-[#f5b300] text-[#2A2312] px-2.5 py-1 text-[11px] font-mono font-black flex items-center gap-1 uppercase"
            title="Copy full OCR raw text"
          >
            {copied ? <Check className="w-3 h-3 stroke-[3]" /> : <Copy className="w-3 h-3 stroke-[2.5]" />}
            {copied ? 'COPIED' : 'COPY'}
          </button>
        </div>
      </div>

      {/* Warning Alert if Engine Fallback Occurred */}
      {ocrData.warning && (
        <div className="bg-[#FFBE0B] text-[#2A2312] px-4 py-2 border-b-[2.5px] border-[#2A2312] text-xs font-mono font-bold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 stroke-[2.5] flex-shrink-0 text-[#2A2312]" />
          <span>{ocrData.warning}</span>
        </div>
      )}

      {/* Content Area */}
      <div className="p-4 sm:p-5">
        {activeTab === 'fields' ? (
          hasFields ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {fields.full_name && (
                <div className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between">
                  <span className="text-[10px] uppercase font-black text-[#3C1A47] flex items-center gap-1 font-mono">
                    <User className="w-3 h-3 stroke-[2.5] text-[#3C1A47]" /> FULL NAME
                  </span>
                  <span className="text-xs font-bold text-[#2A2312] font-mono mt-1.5 bg-[#FAF7F0] p-1.5 border border-[#2A2312]/30">
                    {fields.full_name}
                  </span>
                </div>
              )}

              {fields.document_number && (
                <div className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between">
                  <span className="text-[10px] uppercase font-black text-[#3C1A47] flex items-center gap-1 font-mono">
                    <CreditCard className="w-3 h-3 stroke-[2.5] text-[#3C1A47]" /> DOCUMENT NUMBER
                  </span>
                  <span className="text-xs font-black text-[#2A2312] font-mono mt-1.5 bg-[#B6FF00]/30 p-1.5 border border-[#2A2312]">
                    {fields.document_number}
                  </span>
                </div>
              )}

              {fields.nationality && (
                <div className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between">
                  <span className="text-[10px] uppercase font-black text-[#3C1A47] font-mono">
                    NATIONALITY
                  </span>
                  <span className="text-xs font-bold text-[#2A2312] font-mono mt-1.5 bg-[#FAF7F0] p-1.5 border border-[#2A2312]/30">
                    {fields.nationality}
                  </span>
                </div>
              )}

              {fields.dates_found && fields.dates_found.length > 0 && (
                <div className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between sm:col-span-2">
                  <span className="text-[10px] uppercase font-black text-[#3C1A47] flex items-center gap-1 font-mono">
                    <Calendar className="w-3 h-3 stroke-[2.5] text-[#FFBE0B]" /> DATES DETECTED
                  </span>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {fields.dates_found.map((date, idx) => (
                      <span key={idx} className="text-[11px] bg-[#FFBE0B] text-[#2A2312] border border-[#2A2312] px-2 py-0.5 font-mono font-bold shadow-[1px_1px_0px_#2A2312]">
                        {date}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {fields.invoice_number && (
                <div className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between">
                  <span className="text-[10px] uppercase font-black text-[#3C1A47] flex items-center gap-1 font-mono">
                    <Hash className="w-3 h-3 stroke-[2.5]" /> INVOICE / PO #
                  </span>
                  <span className="text-xs font-black text-[#2A2312] font-mono mt-1.5 bg-[#B6FF00]/40 p-1.5 border border-[#2A2312]">
                    {fields.invoice_number}
                  </span>
                </div>
              )}

              {fields.amounts_found && fields.amounts_found.length > 0 && (
                <div className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between">
                  <span className="text-[10px] uppercase font-black text-[#3C1A47] font-mono">
                    AMOUNTS DETECTED
                  </span>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {fields.amounts_found.map((amt, idx) => (
                      <span key={idx} className="text-[11px] bg-[#B6FF00] text-[#2A2312] border border-[#2A2312] px-2 py-0.5 font-mono font-bold shadow-[1px_1px_0px_#2A2312]">
                        {amt}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Render any additional fields */}
              {Object.entries(fields)
                .filter(([k]) => !['full_name', 'document_number', 'nationality', 'dates_found', 'invoice_number', 'amounts_found', 'mrz', 'surname', 'given_names'].includes(k))
                .map(([k, v]) => (
                  <div key={k} className="bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-black text-[#3C1A47] font-mono">
                      {k.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs font-bold text-[#2A2312] font-mono mt-1.5 bg-[#FAF7F0] p-1.5 border border-[#2A2312]/30 truncate">
                      {Array.isArray(v) ? v.join(', ') : String(v)}
                    </span>
                  </div>
                ))}

              {/* MRZ Block if present */}
              {fields.mrz && (
                <div className="sm:col-span-2 lg:col-span-3 bg-[#3C1A47] border-[2.5px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312] p-3.5">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[11px] uppercase font-black text-[#B6FF00] tracking-wider font-mono">
                      MACHINE READABLE ZONE ({fields.mrz.format})
                    </span>
                    <span className="text-[10px] bg-[#FFBE0B] text-[#2A2312] px-2 py-0.5 border border-[#2A2312] font-mono font-black">
                      ICAO DOC 9303
                    </span>
                  </div>
                  <div className="font-mono text-xs bg-[#2A2312] p-3 border-2 border-[#2A2312] text-[#B6FF00] tracking-widest leading-relaxed overflow-x-auto whitespace-pre">
                    {fields.mrz.lines ? fields.mrz.lines.join('\n') : JSON.stringify(fields.mrz, null, 2)}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs font-mono font-bold text-[#2A2312]/70 italic py-3 text-center bg-white border-2 border-[#2A2312]">
              NO STRUCTURED REGEX ENTITIES DETECTED. SWITCH TO "RAW TEXT" TAB TO VIEW COMPLETE OCR OUTPUT.
            </div>
          )
        ) : (
          <div className="relative">
            <pre className="text-xs font-mono text-[#B6FF00] bg-[#2A2312] p-4 border-[2.5px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312] overflow-x-auto max-h-72 leading-relaxed whitespace-pre-wrap select-text">
              {ocrData.raw_text}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

const FileResultCard = ({ result }) => {
  const statusConfig = {
    PASS: {
      badge: 'bg-[#B6FF00] text-[#2A2312] border-[2.5px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312]',
      icon: <CheckCircle2 className="w-6 h-6 stroke-[2.5] text-[#2A2312]" />,
      headerBg: 'bg-[#B6FF00]/20',
      border: 'border-[#2A2312]',
    },
    BORDERLINE: {
      badge: 'bg-[#FFBE0B] text-[#2A2312] border-[2.5px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312]',
      icon: <AlertTriangle className="w-6 h-6 stroke-[2.5] text-[#2A2312]" />,
      headerBg: 'bg-[#FFBE0B]/20',
      border: 'border-[#2A2312]',
    },
    REJECT: {
      badge: 'bg-rose-500 text-white border-[2.5px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312]',
      icon: <XCircle className="w-6 h-6 stroke-[2.5] text-rose-600" />,
      headerBg: 'bg-rose-50',
      border: 'border-[#2A2312]',
    },
  };

  const currentStatus = statusConfig[result.status] || statusConfig.REJECT;

  return (
    <div className={`brutal-card p-5 sm:p-6 mb-5`}>
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b-[3px] border-[#2A2312]">
        <div className="flex items-center gap-3.5">
          <div className="p-2 bg-white border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312]">
            {currentStatus.icon}
          </div>
          <div>
            <h4 className="font-black text-[#2A2312] text-base uppercase font-heading">
              {result.filename || 'Uploaded Document'}
            </h4>
            <p className="text-xs font-mono font-bold text-[#2A2312]/80 mt-0.5">
              {result.final_reason}
            </p>
          </div>
        </div>

        <div>
          <span className={`inline-flex items-center px-3.5 py-1.5 text-xs font-black uppercase font-mono tracking-wider ${currentStatus.badge}`}>
            {result.status}
          </span>
        </div>
      </div>

      {/* Diagnostic Stage Breakdown */}
      {result.stages && Object.keys(result.stages).length > 0 && (
        <div className="mt-5">
          <div className="text-xs font-mono font-black text-[#3C1A47] uppercase tracking-wider mb-2.5 flex items-center justify-between">
            <span>STAGE DIAGNOSTIC MATRIX</span>
            <span className="text-[10px] text-[#2A2312]/60">[{Object.keys(result.stages).length} STAGES]</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(result.stages).map(([stage, data]) => {
              const isPass = data && (data.status === 'pass' || data.status === 'PASS');
              const isSkipped = data && (data.status === 'skipped');
              return (
                <div
                  key={stage}
                  className="bg-[#FAF7F0] border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] p-3 text-xs flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-[#2A2312]/30">
                    <span className="font-black text-[#3C1A47] uppercase font-mono">
                      {stage.replace(/_/g, ' ')}
                    </span>
                    <span
                      className={`font-black uppercase text-[10px] px-2 py-0.5 border border-[#2A2312] font-mono shadow-[1px_1px_0px_#2A2312] ${
                        isSkipped
                          ? 'text-[#2A2312]/60 bg-[#E5DFD1]'
                          : isPass
                          ? 'text-[#2A2312] bg-[#B6FF00]'
                          : 'text-white bg-rose-500'
                      }`}
                    >
                      {data?.status || 'N/A'}
                    </span>
                  </div>

                  <div className="text-[11px] font-mono space-y-1">
                    {typeof data === 'object' && data !== null ? (
                      Object.entries(data)
                        .filter(([k]) => k !== 'status' && k !== 'raw_text' && k !== 'extracted_fields' && k !== 'words')
                        .map(([k, v]) => (
                          <div key={k} className="flex justify-between items-center text-[#2A2312]/80 gap-2">
                            <span className="uppercase font-medium text-[10px] flex-shrink-0">{k.replace(/_/g, ' ')}:</span>
                            <span className="font-bold text-[#2A2312] bg-white px-1 border border-[#2A2312]/40 text-right truncate max-w-[200px]" title={String(v)}>
                              {typeof v === 'number'
                                ? (Number.isInteger(v) ? v : v.toFixed(2))
                                : Array.isArray(v)
                                ? (v.every(item => typeof item === 'string' || typeof item === 'number') ? (v.length > 0 ? v.join(', ') : 'none') : `${v.length} items`)
                                : (typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v))}
                            </span>
                          </div>
                        ))
                    ) : (
                      <span>{String(data)}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Extracted OCR Data Box (Structured Fields & Raw Text) */}
      {result.stages?.ocr && <OcrDataBox ocrData={result.stages.ocr} />}
    </div>
  );
};

const ResultsPanel = ({ results }) => {
  if (!results || results.length === 0) return null;

  const stats = {
    total: results.length,
    PASS: results.filter((r) => r.status === 'PASS').length,
    BORDERLINE: results.filter((r) => r.status === 'BORDERLINE').length,
    REJECT: results.filter((r) => r.status === 'REJECT').length,
  };

  const exportReport = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(results, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `docverify_report_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-2xl font-black text-[#3C1A47] uppercase tracking-tight font-heading">
            Verification Results
          </h3>
          <p className="text-xs font-mono font-bold text-[#2A2312]/80 mt-0.5">
            PROCESSED {stats.total} DOCUMENT{stats.total > 1 ? 'S' : ''} ACROSS HEURISTICS & OCR
          </p>
        </div>

        <button
          type="button"
          onClick={exportReport}
          className="brutal-btn bg-[#FFBE0B] hover:bg-[#f5b300] text-[#2A2312] px-4 py-2.5 text-xs font-mono font-black flex items-center gap-2 uppercase tracking-wide"
        >
          <Download className="w-4 h-4 stroke-[2.5]" /> EXPORT JSON REPORT
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="bg-[#3C1A47] text-white border-[3px] border-[#2A2312] shadow-[4px_4px_0px_#2A2312] p-4">
          <span className="text-[10px] uppercase font-mono font-black text-gray-300">TOTAL ANALYZED</span>
          <p className="text-3xl font-black font-heading mt-1">{stats.total}</p>
        </div>
        <div className="bg-[#B6FF00] text-[#2A2312] border-[3px] border-[#2A2312] shadow-[4px_4px_0px_#2A2312] p-4">
          <span className="text-[10px] uppercase font-mono font-black text-[#2A2312]">PASSED</span>
          <p className="text-3xl font-black font-heading mt-1">{stats.PASS}</p>
        </div>
        <div className="bg-[#FFBE0B] text-[#2A2312] border-[3px] border-[#2A2312] shadow-[4px_4px_0px_#2A2312] p-4">
          <span className="text-[10px] uppercase font-mono font-black text-[#2A2312]">BORDERLINE</span>
          <p className="text-3xl font-black font-heading mt-1">{stats.BORDERLINE}</p>
        </div>
        <div className="bg-rose-500 text-white border-[3px] border-[#2A2312] shadow-[4px_4px_0px_#2A2312] p-4">
          <span className="text-[10px] uppercase font-mono font-black text-rose-100">REJECTED</span>
          <p className="text-3xl font-black font-heading mt-1">{stats.REJECT}</p>
        </div>
      </div>

      {/* Result Cards List */}
      <div className="space-y-4">
        {results.map((result, index) => (
          <FileResultCard key={result.filename || index} result={result} />
        ))}
      </div>
    </div>
  );
};

export default ResultsPanel;
