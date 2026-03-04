"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  ShieldAlert,
  TrendingUp,
  Lightbulb,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Download,
  Plus
} from 'lucide-react';
import axios from 'axios';

interface AnalysisResult {
  executive_summary: string[];
  key_risks: string[];
  opportunities: string[];
  strategic_recommendations: string[];
  filename: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setError(null);

      // Cleanup previous preview URL
      if (previewUrl) URL.revokeObjectURL(previewUrl);

      if (selectedFile.type === 'application/pdf') {
        const url = URL.createObjectURL(selectedFile);
        setPreviewUrl(url);
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Uploading file:', file.name);
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minute timeout
      });
      console.log('Response received:', response.data);
      setResult(response.data);
    } catch (err: any) {
      console.error('Upload error:', err);
      
      let errorMessage = 'Failed to analyze the document.';
      
      if (err.code === 'ECONNREFUSED') {
        errorMessage = '❌ Backend not running. Start it with: python main.py (in backend folder)';
      } else if (err.message === 'timeout of 120000ms exceeded') {
        errorMessage = '⏱️ Request timed out. Backend may be slow. Check logs: python main.py';
      } else if (err.response?.status === 400) {
        errorMessage = `Invalid file: ${err.response?.data?.detail || 'Only PDF and DOCX files are supported'}`;
      } else if (err.response?.status === 500) {
        errorMessage = `Server error: ${err.response?.data?.detail || 'Check backend logs for details'}`;
      } else if (err.message?.includes('Network')) {
        errorMessage = '🌐 Network error. Is the backend running on port 8000?';
      } else {
        errorMessage = err.response?.data?.detail || err.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setResult(null);
    setError(null);
    setPreviewUrl(null);
  };

  return (
    <main className="h-screen w-screen bg-white dark:bg-gray-950 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-16 px-6 flex items-center justify-between border-b border-gray-200 dark:border-gray-800 shrink-0 bg-white dark:bg-gray-900 z-10">
        <div className="flex items-center gap-4">
          <motion.h1
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-xl font-bold text-gray-900 dark:text-white"
          >
            Enterprise <span className="text-blue-600 dark:text-blue-400">Intelligence</span>
          </motion.h1>
          <div className="h-4 w-px bg-gray-200 dark:bg-gray-800 hidden md:block" />
          <motion.p
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="text-gray-500 dark:text-gray-400 text-xs hidden md:block"
          >
            Document Workspace
          </motion.p>
        </div>

        <div className="flex items-center gap-3">
          {(result || file) && (
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={reset}
              className="flex items-center gap-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-all shadow-sm"
            >
              <Plus className="w-4 h-4" />
              New Analysis
            </motion.button>
          )}
        </div>
      </header>

      <div className="flex-1 flex min-h-0">
        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div
              key="upload-landing"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02 }}
              className="w-full h-full flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950 p-12 text-center"
            >
              <div className="max-w-2xl">
                <div className="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 rounded-2xl flex items-center justify-center mb-8 mx-auto rotate-3 shadow-inner">
                  <Upload className="w-10 h-10 text-blue-600 dark:text-blue-400" />
                </div>
                <h2 className="text-3xl font-bold mb-4 dark:text-white">Start Intelligence Generation</h2>
                <p className="text-gray-500 dark:text-gray-400 mb-10 leading-relaxed">
                  Upload an Annual Report, Contract, or Strategic Plan.
                  Our AI will extract metrics and provide actionable recommendations in a full-screen workspace.
                </p>

                <label className="cursor-pointer group flex flex-col items-center">
                  <div className="bg-blue-600 hover:bg-blue-700 text-white px-12 py-4 rounded-xl font-bold text-lg transition-all shadow-lg shadow-blue-500/30 group-hover:scale-105 active:scale-95">
                    Select Business File
                  </div>
                  <input type="file" className="hidden" accept=".pdf,.docx" onChange={handleFileChange} />
                </label>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-8 flex items-center gap-3 text-red-600 bg-red-50 dark:bg-red-900/10 px-6 py-3 rounded-xl shrink-0 justify-center"
                  >
                    <AlertCircle className="w-5 h-5" />
                    <p className="text-sm font-medium">{error}</p>
                  </motion.div>
                )}
              </div>
            </motion.div>
          ) : (
            // Split View Layout
            <div key="split-view" className="w-full flex-1 grid grid-cols-2 min-h-0">
              {/* Left Side: Strategic Insights */}
              <div className="flex flex-col min-h-0 border-r border-gray-200 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-900/30">
                <AnimatePresence mode="wait">
                  {!result && !analyzing ? (
                    <motion.div
                      key="ready-to-analyze"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className="h-full flex flex-col items-center justify-center p-8 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 text-center shadow-lg"
                    >
                      <div className="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-6">
                        <Lightbulb className="w-10 h-10 text-blue-600 dark:text-blue-400" />
                      </div>
                      <h3 className="text-xl font-bold mb-4 dark:text-white">Begin Analysis</h3>
                      <p className="text-gray-500 mb-8 max-w-xs mx-auto text-sm">
                        Ready to extract strategic intelligence from {file?.name}.
                      </p>
                      <button
                        onClick={handleUpload}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-500/20 active:scale-95 flex items-center gap-2 text-sm"
                      >
                        <Lightbulb className="w-4 h-4" />
                        Generate Insights
                      </button>
                    </motion.div>
                  ) : analyzing ? (
                    <motion.div
                      key="analyzing"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="h-full flex flex-col items-center justify-center p-8 text-center"
                    >
                      <div className="relative mb-6">
                        <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
                      </div>
                      <h3 className="text-xl font-bold mb-2 dark:text-white">Analyzing Strategy</h3>
                      <p className="text-gray-500 text-xs max-w-[240px] mx-auto animate-pulse">
                        Processing document semantic layers...
                      </p>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="results-content"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex-1 flex flex-col min-h-0 gap-4 p-6 overflow-y-auto custom-scrollbar"
                    >
                      {/* Executive Summary Card */}
                      <section className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm shrink-0">
                        <div className="flex items-center gap-3 mb-5">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <h2 className="text-sm font-bold dark:text-white uppercase tracking-wider">Executive Summary</h2>
                        </div>
                        <div className="space-y-4">
                          {result?.executive_summary.map((point, i) => (
                            <div key={i} className="flex gap-4 items-start bg-blue-50/30 dark:bg-blue-900/5 p-4 rounded-lg border border-blue-100/30 dark:border-blue-900/20">
                              <div className="mt-2 w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" />
                              <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-base font-medium">
                                {point}
                              </p>
                            </div>
                          ))}
                        </div>
                      </section>

                      {/* Risks & Opportunities Grid */}
                      <div className="grid grid-cols-1 gap-4">
                        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                          <div className="flex items-center gap-3 mb-4">
                            <ShieldAlert className="w-5 h-5 text-red-600" />
                            <h3 className="text-sm font-bold dark:text-white uppercase tracking-wider">Critical Risks</h3>
                          </div>
                          <ul className="space-y-3">
                            {result?.key_risks.map((risk, i) => (
                              <li key={i} className="flex gap-3 text-base text-gray-700 dark:text-gray-300 bg-red-50/30 dark:bg-red-900/5 p-3 rounded-lg border border-red-100/50 dark:border-red-900/20 font-medium">
                                <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
                                {risk}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                          <div className="flex items-center gap-3 mb-4">
                            <TrendingUp className="w-5 h-5 text-green-600" />
                            <h3 className="text-sm font-bold dark:text-white uppercase tracking-wider">Growth Opportunities</h3>
                          </div>
                          <ul className="space-y-3">
                            {result?.opportunities.map((opp, i) => (
                              <li key={i} className="flex gap-3 text-base text-gray-700 dark:text-gray-300 bg-green-50/30 dark:bg-green-900/5 p-3 rounded-lg border border-green-100/50 dark:border-green-900/20 font-medium">
                                <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-green-400 shrink-0" />
                                {opp}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* Recommendations */}
                      <section className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm mb-4">
                        <div className="flex items-center gap-3 mb-4">
                          <Lightbulb className="w-5 h-5 text-amber-600" />
                          <h3 className="text-sm font-bold dark:text-white uppercase tracking-wider">Strategic Recommendations</h3>
                        </div>
                        <div className="space-y-3">
                          {result?.strategic_recommendations.map((rec, i) => (
                            <div key={i} className="flex gap-3 text-base text-gray-700 dark:text-gray-300 bg-amber-50/50 dark:bg-amber-900/10 p-3 rounded-lg border border-amber-100/50 dark:border-amber-900/20 font-medium">
                              <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                              {rec}
                            </div>
                          ))}
                        </div>
                      </section>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-full flex flex-col min-h-0 bg-gray-100 dark:bg-gray-950 relative"
              >
                <div className="absolute inset-0">
                  {previewUrl ? (
                    <iframe
                      src={`${previewUrl}#view=FitH&toolbar=0&navpanes=0`}
                      className="w-full h-full border-none"
                      title="Document Preview"
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center p-12 text-center text-gray-500 bg-white dark:bg-gray-900">
                      <div className="p-6 bg-gray-50 dark:bg-gray-950 rounded-full mb-4">
                        <FileText className="w-12 h-12 text-gray-300" />
                      </div>
                      <p className="font-medium text-gray-400">Preview not available for .docx files</p>
                    </div>
                  )}
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
