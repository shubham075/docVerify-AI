import React, { useState, useEffect } from 'react';
import { ShieldCheck, Terminal, BookOpen, ExternalLink, Activity } from 'lucide-react';
import { systemApi } from '../../api/client';
import config from '../../config';

const Header = () => {
  const [backendOnline, setBackendOnline] = useState(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await systemApi.checkHealth();
        setBackendOnline(!!res);
      } catch (e) {
        setBackendOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="brutal-card p-5 sm:p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
        {/* Brand Section */}
        <div className="flex items-center gap-4">
          <div className="p-3.5 bg-[#3C1A47] text-[#B6FF00] border-[3px] border-[#2A2312] shadow-[4px_4px_0px_#2A2312] flex items-center justify-center shrink-0">
            <ShieldCheck className="w-8 h-8 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-[#3C1A47] uppercase font-heading">
                DocVerify <span className="bg-[#FFBE0B] text-[#2A2312] px-2 py-0.5 border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] inline-block -rotate-1">AI</span>
              </h1>
              <span className="bg-[#B6FF00] text-[#2A2312] border-2 border-[#2A2312] px-2.5 py-0.5 font-mono text-xs font-black shadow-[2px_2px_0px_#2A2312] uppercase tracking-wider">
                v{config.appVersion} LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm font-medium text-[#2A2312]/80 mt-1">
              Industrial Document Quality, Blur, Glare & OCR Entity Extraction Engine
            </p>
          </div>
        </div>

        {/* Status & Utility Pills */}
        <div className="flex items-center gap-3 self-start sm:self-auto flex-wrap">
          {/* Backend Status Indicator */}
          <div className="flex items-center gap-2 px-3.5 py-2 bg-white border-2 border-[#2A2312] shadow-[3px_3px_0px_#2A2312] text-xs font-mono font-bold">
            <span
              className={`w-3 h-3 border-2 border-[#2A2312] ${
                backendOnline === true
                  ? 'bg-[#B6FF00] animate-pulse'
                  : backendOnline === false
                  ? 'bg-rose-500'
                  : 'bg-[#FFBE0B]'
              }`}
            />
            <span className="text-[#2A2312] tracking-wide">
              {backendOnline === true ? `API: ONLINE (PORT ${config.backendPort})` : backendOnline === false ? 'API: OFFLINE' : 'CHECKING...'}
            </span>
          </div>

          {/* Microservice Badge */}
          <div className="hidden md:flex items-center gap-1.5 px-3 py-2 bg-[#3C1A47] text-white border-2 border-[#2A2312] shadow-[3px_3px_0px_#2A2312] text-xs font-mono font-bold">
            <Activity className="w-3.5 h-3.5 text-[#B6FF00]" />
            <span>STANDALONE SERVICE</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
