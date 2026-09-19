import React from 'react';
import { FileText, CreditCard, ShieldCheck, Check, Sparkles } from 'lucide-react';

const DocumentTypeSelector = ({ docType, onChange }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
      {/* General Documents Card */}
      <button
        type="button"
        onClick={() => onChange('general')}
        className={`text-left p-5 transition-all duration-150 cursor-pointer flex flex-col justify-between select-none ${
          docType === 'general'
            ? 'bg-[#3C1A47] text-white border-[3.5px] border-[#2A2312] shadow-[6px_6px_0px_#2A2312] -translate-y-1'
            : 'bg-white text-[#2A2312] border-[3px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312] hover:shadow-[5px_5px_0px_#2A2312] hover:-translate-y-0.5'
        }`}
      >
        <div>
          <div className="flex items-start justify-between w-full">
            <div className="flex items-center gap-3.5">
              <div
                className={`p-3 border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] ${
                  docType === 'general' ? 'bg-[#B6FF00] text-[#2A2312]' : 'bg-[#FFBE0B] text-[#2A2312]'
                }`}
              >
                <FileText className="w-6 h-6 stroke-[2.5]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-black text-lg uppercase tracking-tight font-heading">
                    General Documents
                  </h3>
                </div>
                <p
                  className={`text-xs font-medium mt-0.5 ${
                    docType === 'general' ? 'text-gray-200' : 'text-[#2A2312]/80'
                  }`}
                >
                  Invoices, receipts, tax forms, letters, PDF contracts
                </p>
              </div>
            </div>

            {docType === 'general' ? (
              <span className="bg-[#B6FF00] text-[#2A2312] border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] px-2.5 py-1 text-[11px] font-black uppercase tracking-wider flex items-center gap-1 font-mono">
                <Check className="w-3.5 h-3.5 stroke-[3]" /> ACTIVE
              </span>
            ) : (
              <span className="bg-[#F5F0E6] text-[#2A2312]/70 border-2 border-[#2A2312] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider font-mono">
                SELECT
              </span>
            )}
          </div>
        </div>

        <div
          className={`mt-5 pt-3.5 border-t-2 flex flex-wrap gap-1.5 font-mono text-[10px] font-bold ${
            docType === 'general' ? 'border-[#B6FF00]/40' : 'border-[#2A2312]/20'
          }`}
        >
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'general' ? 'bg-[#FFBE0B] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            RESOLUTION CHECK
          </span>
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'general' ? 'bg-[#FFBE0B] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            LUMA SANITY
          </span>
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'general' ? 'bg-[#FFBE0B] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            TILED LAPLACIAN
          </span>
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'general' ? 'bg-[#B6FF00] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            OCR CONFIDENCE
          </span>
        </div>
      </button>

      {/* ID & Passports Card */}
      <button
        type="button"
        onClick={() => onChange('id_passport')}
        className={`text-left p-5 transition-all duration-150 cursor-pointer flex flex-col justify-between select-none ${
          docType === 'id_passport'
            ? 'bg-[#3C1A47] text-white border-[3.5px] border-[#2A2312] shadow-[6px_6px_0px_#2A2312] -translate-y-1'
            : 'bg-white text-[#2A2312] border-[3px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312] hover:shadow-[5px_5px_0px_#2A2312] hover:-translate-y-0.5'
        }`}
      >
        <div>
          <div className="flex items-start justify-between w-full">
            <div className="flex items-center gap-3.5">
              <div
                className={`p-3 border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] ${
                  docType === 'id_passport' ? 'bg-[#B6FF00] text-[#2A2312]' : 'bg-[#FFBE0B] text-[#2A2312]'
                }`}
              >
                <CreditCard className="w-6 h-6 stroke-[2.5]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-black text-lg uppercase tracking-tight font-heading">
                    ID & Passport Cards
                  </h3>
                </div>
                <p
                  className={`text-xs font-medium mt-0.5 ${
                    docType === 'id_passport' ? 'text-gray-200' : 'text-[#2A2312]/80'
                  }`}
                >
                  Passports, national ID cards, driver licenses, ICAO cards
                </p>
              </div>
            </div>

            {docType === 'id_passport' ? (
              <span className="bg-[#B6FF00] text-[#2A2312] border-2 border-[#2A2312] shadow-[2px_2px_0px_#2A2312] px-2.5 py-1 text-[11px] font-black uppercase tracking-wider flex items-center gap-1 font-mono">
                <Check className="w-3.5 h-3.5 stroke-[3]" /> ACTIVE
              </span>
            ) : (
              <span className="bg-[#F5F0E6] text-[#2A2312]/70 border-2 border-[#2A2312] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider font-mono">
                SELECT
              </span>
            )}
          </div>
        </div>

        <div
          className={`mt-5 pt-3.5 border-t-2 flex flex-wrap gap-1.5 font-mono text-[10px] font-bold ${
            docType === 'id_passport' ? 'border-[#B6FF00]/40' : 'border-[#2A2312]/20'
          }`}
        >
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'id_passport' ? 'bg-[#FFBE0B] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            BOUNDARY WARP
          </span>
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'id_passport' ? 'bg-[#FFBE0B] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            HSV GLARE MASK
          </span>
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'id_passport' ? 'bg-[#FFBE0B] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            TENENGRAD + ANISOTROPY
          </span>
          <span
            className={`px-2 py-0.5 border-2 border-[#2A2312] shadow-[1.5px_1.5px_0px_#2A2312] ${
              docType === 'id_passport' ? 'bg-[#B6FF00] text-[#2A2312]' : 'bg-[#F5F0E6] text-[#2A2312]'
            }`}
          >
            MRZ PARSER
          </span>
        </div>
      </button>
    </div>
  );
};

export default DocumentTypeSelector;
