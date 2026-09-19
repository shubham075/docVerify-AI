import React, { useState } from 'react';
import Header from './components/layout/Header';
import DocumentTypeSelector from './components/layout/DocumentTypeSelector';
import ConfigPanel from './components/config/ConfigPanel';
import UploadZone from './components/upload/UploadZone';
import ResultsPanel from './components/results/ResultsPanel';
import { Zap, Terminal, Code2 } from 'lucide-react';

const App = () => {
  const [docType, setDocType] = useState('general');
  const [pipelineConfig, setPipelineConfig] = useState({});
  const [results, setResults] = useState([]);

  const handleDocTypeChange = (newType) => {
    setDocType(newType);
    setResults([]);
  };

  return (
    <div className="brutal-canvas min-h-screen text-[#2A2312] flex flex-col justify-between py-6 px-4 sm:px-6 lg:px-8 relative selection:bg-[#B6FF00] selection:text-[#2A2312]">
      {/* Top Brutalist Marquee Tape */}
      <div className="max-w-5xl mx-auto w-full mb-6">
        <div className="bg-[#3C1A47] text-[#B6FF00] border-[3px] border-[#2A2312] shadow-[4px_4px_0px_#2A2312] px-4 py-2 flex items-center font-mono text-xs font-bold tracking-wider overflow-hidden">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#FFBE0B] fill-[#FFBE0B]" />
            <span className="uppercase">DOC_VERIFY // CV BLUR ENGINE & OCR MICROSERVICE</span>
          </div>
        </div>
      </div>

      <main className="max-w-5xl mx-auto w-full space-y-6">
        {/* Header */}
        <Header />

        {/* Pipeline / Document Type Selector */}
        <DocumentTypeSelector
          docType={docType}
          onChange={handleDocTypeChange}
        />

        {/* Threshold Configuration Panel */}
        <ConfigPanel
          docType={docType}
          config={pipelineConfig}
          setConfig={setPipelineConfig}
        />

        {/* Upload & Run Action Zone */}
        <UploadZone
          docType={docType}
          config={pipelineConfig}
          onResultsReceived={setResults}
        />

        {/* Results Section */}
        <ResultsPanel results={results} />
      </main>

      <footer className="mt-14 max-w-5xl mx-auto w-full pt-6 border-t-[3px] border-[#2A2312] flex flex-col sm:flex-row items-center justify-between text-xs font-mono font-bold text-[#2A2312]/80 gap-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 bg-[#B6FF00] border-2 border-[#2A2312] inline-block" />
          <span>DOC_VERIFY CORE v1.0 // FAST CV PIPELINE & OCR HEURISTICS</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="bg-[#FFBE0B] text-[#2A2312] border-2 border-[#2A2312] px-2 py-0.5 shadow-[2px_2px_0px_#2A2312]">
            ICAO DOC 9303 / TESSERACT
          </span>
          <span className="bg-[#3C1A47] text-white border-2 border-[#2A2312] px-2 py-0.5 shadow-[2px_2px_0px_#2A2312]">
            HYBRID MODE
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
