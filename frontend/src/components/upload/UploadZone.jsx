import React, { useState, useRef } from 'react';
import { UploadCloud, File, X, AlertCircle, ArrowUpRight, Check, Layers, Image as ImageIcon, Sparkles } from 'lucide-react';
import { verifyApi } from '../../api/client';

const MAX_FILE_SIZE_MB = 15;
const MAX_BULK_FILES = 25;

const UploadZone = ({ docType, config, onResultsReceived }) => {
  const [files, setFiles] = useState([]);
  const [isBulk, setIsBulk] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const fileInputRef = useRef(null);

  const handleFiles = (incomingFiles) => {
    setErrorMsg(null);
    const fileList = Array.from(incomingFiles);

    if (isBulk && files.length + fileList.length > MAX_BULK_FILES) {
      setErrorMsg(`Cannot exceed maximum of ${MAX_BULK_FILES} files in bulk mode.`);
      return;
    }

    const validated = [];
    const oversized = [];

    fileList.forEach((file) => {
      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > MAX_FILE_SIZE_MB) {
        oversized.push(file.name);
      } else {
        validated.push(file);
      }
    });

    if (oversized.length > 0) {
      setErrorMsg(`Skipped ${oversized.length} file(s) exceeding ${MAX_FILE_SIZE_MB}MB limit.`);
    }

    if (isBulk) {
      setFiles((prev) => [...prev, ...validated]);
    } else {
      setFiles(validated.slice(0, 1));
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setFiles([]);
    setErrorMsg(null);
  };

  const handleSubmit = async () => {
    if (files.length === 0) return;
    setUploading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('doc_type', docType);
    if (config) {
      formData.append('config', JSON.stringify(config));
    }

    try {
      if (isBulk) {
        files.forEach((file) => formData.append('files', file));
        const response = await verifyApi.verifyBulk(formData);
        onResultsReceived(response.data);
      } else {
        formData.append('file', files[0]);
        const response = await verifyApi.verifySingle(formData);
        onResultsReceived([response.data]);
      }
    } catch (error) {
      console.error('Verification failed', error);
      const detail = error.response?.data?.detail;
      const message = typeof detail === 'object' ? JSON.stringify(detail) : (detail || error.message);
      setErrorMsg(`Analysis failed: ${message}`);
    } finally {
      setUploading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="brutal-card p-6 mb-8">
      {/* Upload Mode Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b-[3px] border-[#2A2312] gap-3">
        <div className="flex gap-2.5">
          <button
            type="button"
            onClick={() => { setIsBulk(false); setFiles(files.slice(0, 1)); }}
            className={`brutal-btn-sm px-4 py-2 text-xs font-mono font-black flex items-center gap-2 uppercase ${
              !isBulk
                ? 'bg-[#3C1A47] text-[#B6FF00]'
                : 'bg-white text-[#2A2312] hover:bg-[#FAF7F0]'
            }`}
          >
            <ImageIcon className="w-4 h-4 stroke-[2.5]" /> SINGLE DOCUMENT
          </button>

          <button
            type="button"
            onClick={() => { setIsBulk(true); }}
            className={`brutal-btn-sm px-4 py-2 text-xs font-mono font-black flex items-center gap-2 uppercase ${
              isBulk
                ? 'bg-[#3C1A47] text-[#B6FF00]'
                : 'bg-white text-[#2A2312] hover:bg-[#FAF7F0]'
            }`}
          >
            <Layers className="w-4 h-4 stroke-[2.5]" /> BULK MULTI-UPLOAD
          </button>
        </div>

        {files.length > 0 && (
          <button
            type="button"
            onClick={clearAll}
            className="brutal-btn-sm bg-[#FFBE0B] hover:bg-[#f5b300] text-[#2A2312] px-3 py-1.5 text-xs font-mono font-black self-start sm:self-auto uppercase"
          >
            CLEAR QUEUE ({files.length})
          </button>
        )}
      </div>

      {/* Drop Zone Box */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`mt-6 border-[3px] border-dashed border-[#2A2312] p-8 sm:p-10 text-center transition-all cursor-pointer select-none ${
          dragActive
            ? 'bg-[#B6FF00]/30 shadow-[4px_4px_0px_#2A2312]'
            : 'bg-[#FAF7F0] hover:bg-[#FFFDF8] hover:shadow-[3px_3px_0px_#2A2312]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple={isBulk}
          accept=".pdf,.jpg,.jpeg,.png,.webp,.tiff,.bmp"
          onChange={(e) => {
            if (e.target.files) handleFiles(e.target.files);
            e.target.value = '';
          }}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center">
          <div className="p-4 bg-[#3C1A47] text-[#FFBE0B] border-[2.5px] border-[#2A2312] shadow-[3px_3px_0px_#2A2312] mb-3.5">
            <UploadCloud className="w-8 h-8 stroke-[2.5]" />
          </div>
          <p className="text-base font-black text-[#2A2312] uppercase tracking-tight font-heading">
            {isBulk ? 'DRAG & DROP MULTIPLE DOCUMENTS HERE' : 'DRAG & DROP DOCUMENT HERE'}
          </p>
          <p className="text-xs font-mono font-bold text-[#2A2312]/70 mt-1 uppercase">
            OR CLICK TO BROWSE LOCAL FILES (MAX {MAX_FILE_SIZE_MB}MB PER FILE)
          </p>
          <div className="flex flex-wrap justify-center gap-1.5 mt-3 font-mono text-[10px] font-bold">
            {['PDF', 'JPG', 'PNG', 'WEBP', 'TIFF'].map((fmt) => (
              <span key={fmt} className="bg-white text-[#2A2312] border-2 border-[#2A2312] px-2 py-0.5 shadow-[1.5px_1.5px_0px_#2A2312]">
                .{fmt}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Error Alert Banner */}
      {errorMsg && (
        <div className="mt-4 p-3.5 bg-[#FFBE0B] border-2 border-[#2A2312] shadow-[3px_3px_0px_#2A2312] flex items-center gap-2.5 text-xs font-mono font-bold text-[#2A2312]">
          <AlertCircle className="w-5 h-5 flex-shrink-0 stroke-[2.5]" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* File Queue List */}
      {files.length > 0 && (
        <div className="mt-5 space-y-2.5 max-h-60 overflow-y-auto pr-1">
          <div className="text-xs font-mono font-black text-[#2A2312] uppercase tracking-wider px-1 flex items-center justify-between">
            <span>QUEUED FOR VERIFICATION:</span>
            <span>{files.length} {files.length === 1 ? 'DOCUMENT' : 'DOCUMENTS'}</span>
          </div>
          {files.map((file, idx) => (
            <div
              key={`${file.name}-${idx}`}
              className="flex items-center justify-between p-3 bg-white border-2 border-[#2A2312] shadow-[2.5px_2.5px_0px_#2A2312] text-xs font-mono"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="p-1.5 bg-[#FFBE0B] border border-[#2A2312] text-[#2A2312]">
                  <File className="w-4 h-4 stroke-[2.5]" />
                </div>
                <div className="truncate">
                  <p className="text-[#2A2312] font-bold truncate">{file.name}</p>
                  <p className="text-[#2A2312]/60 text-[10px] font-bold">{formatBytes(file.size)}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(idx);
                }}
                className="brutal-btn-sm bg-rose-500 hover:bg-rose-600 text-white p-1"
                title="Remove file"
              >
                <X className="w-3.5 h-3.5 stroke-[3]" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* High-Voltage CTA Verification Button */}
      <div className="mt-6">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={files.length === 0 || uploading}
          className={`w-full py-4 px-6 font-black text-sm sm:text-base flex items-center justify-center gap-3 uppercase tracking-wider font-heading ${
            files.length === 0 || uploading
              ? 'bg-[#E5DFD1] text-[#2A2312]/40 border-[3px] border-[#2A2312]/40 shadow-none cursor-not-allowed'
              : 'brutal-btn bg-[#B6FF00] hover:bg-[#a5f000] text-[#2A2312] border-[3.5px] border-[#2A2312] shadow-[6px_6px_0px_#2A2312]'
          }`}
        >
          {uploading ? (
            <>
              <div className="w-5 h-5 border-[3px] border-[#2A2312] border-t-transparent rounded-full animate-spin" />
              <span>RUNNING CV QUALITY PIPELINE & OCR...</span>
            </>
          ) : (
            <>
              <span>EXECUTE VERIFICATION PIPELINE</span>
              <ArrowUpRight className="w-5 h-5 stroke-[3]" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default UploadZone;
