"use client";

import React, { useState, useEffect, useMemo } from 'react';
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
  Plus,
  Search,
  History,
  ChevronLeft,
  ChevronRight,
  Calendar,
  ExternalLink,
  MoreVertical,
  Trash2,
  Pin,
  Highlighter,
  Eraser,
  StickyNote,
  Bot,
  Send,
  Download,
  LogOut
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';

interface AnalysisResult {
  id?: number;
  executive_summary: string[];
  key_risks: string[];
  opportunities: string[];
  strategic_recommendations: string[];
  filename: string;
  pdf_file_url?: string;
  preview_url?: string;
  extracted_text?: string;
}

interface HistoryItem {
  id: number;
  filename: string;
  is_pinned: boolean;
  created_at: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [askDocAIOpen, setAskDocAIOpen] = useState(false);
  const [docAIQuestion, setDocAIQuestion] = useState("");
  const [isNotePopupOpen, setIsNotePopupOpen] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [selectedText, setSelectedText] = useState("");
  const [toast, setToast] = useState<{ message: string, type: 'success' | 'error' } | null>(null);
  const [activeMode, setActiveMode] = useState<'analyze' | 'ask'>('analyze');
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [notes, setNotes] = useState<any[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { token, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();

  // AUTH PROTECTION: Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Auth header config - REMOVED (Handled by api interceptor)

  // Auto-clear toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // Fetch notes when document changes
  useEffect(() => {
    if (selectedDocument?.id) {
      fetchNotes(selectedDocument.id);
    }
  }, [selectedDocument?.id]);

  const fetchNotes = async (analysisId: number) => {
    try {
      console.log(`🔍 Fetching notes for analysis: ${analysisId}`);
      const response = await api.get(`http://localhost:8000/notes/${analysisId}`);
      
      if (response.data && response.data.length > 0) {
        console.log("✅ Note found:", response.data[0].note_text);
        setNotes(response.data);
        setNoteText(response.data[0].note_text || "");
      } else {
        console.log("ℹ️ No note found for this analysis.");
        setNotes([]);
        setNoteText("");
      }
    } catch (err) {
      console.error("❌ Error fetching notes:", err);
      setNoteText("");
    }
  };
  const [activeMenuId, setActiveMenuId] = useState<number | null>(null);

  // History Sidebar States
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Fetch history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Debugging: selectedDocument state update
  useEffect(() => {
    if (selectedDocument) {
      console.log('🔄 selectedDocument state updated:', selectedDocument);
      console.log('📄 PDF File Path loaded into viewer:', selectedDocument.pdf_file_url);
    }
  }, [selectedDocument]);

  // Handle click outside to close menu
  useEffect(() => {
    const handleClickOutside = () => setActiveMenuId(null);
    window.addEventListener('click', handleClickOutside);
    return () => window.removeEventListener('click', handleClickOutside);
  }, []);

  const fetchHistory = async () => {
    try {
      setLoadingHistory(true);
      const response = await api.get('http://localhost:8000/analyses');
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const togglePin = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await api.post(`http://localhost:8000/analysis/${id}/pin`, {});
      fetchHistory();
      setActiveMenuId(null);
    } catch (err) {
      console.error('Pin error:', err);
    }
  };

  const deleteAnalysis = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this analysis? This will also remove the PDF file from the database.")) {
      try {
        await api.delete(`http://localhost:8000/analysis/${id}`);
        if (selectedDocument?.id === id) {
          setSelectedDocument(null);
        }
        fetchHistory();
        setActiveMenuId(null);
      } catch (err) {
        console.error('Delete error:', err);
      }
    }
  };

  const handleHighlight = () => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || selection.toString().trim() === "") {
        setToast({ message: "Please select some text first", type: "error" });
        return;
    }

    const range = selection.getRangeAt(0);
    
    // Check if any part of the selection is already inside a highlight
    let container = range.commonAncestorContainer;
    if (container.nodeType === 3) container = container.parentNode!;
    
    // If the selection itself is inside a highlight, or contains highlights, stop
    const isInsideHighlight = (node: Node | null): boolean => {
      while (node && node !== document.body) {
        if (node instanceof HTMLElement && node.classList.contains('doc-highlight')) return true;
        node = node.parentNode;
      }
      return false;
    };

    if (isInsideHighlight(container)) {
      setToast({ message: "This text is already highlighted", type: "error" });
      return;
    }

    // Check if selection contains any highlights
    const div = document.createElement("div");
    div.appendChild(range.cloneContents());
    if (div.querySelector('.doc-highlight')) {
      setToast({ message: "Selection contains existing highlights", type: "error" });
      return;
    }

    // NEW: Prevent highlighting across multiple block elements (bullets, paragraphs)
    const getBlockParent = (node: Node | null): HTMLElement | null => {
      while (node && node !== document.body) {
        if (node instanceof HTMLElement && ['LI', 'P', 'H1', 'H2', 'H3', 'DIV'].includes(node.tagName)) {
           return node;
        }
        node = node.parentNode;
      }
      return null;
    };

    const startBlock = getBlockParent(range.startContainer);
    const endBlock = getBlockParent(range.endContainer);

    if (!startBlock || !endBlock || startBlock !== endBlock) {
      setToast({ message: "Please highlight within a single bullet point or section.", type: "error" });
      return;
    }

    try {
        const span = document.createElement("span");
        span.className = "doc-highlight";
        
        range.surroundContents(span);
        
        setToast({ message: "Text highlighted", type: "success" });
        selection.removeAllRanges();
    } catch (e) {
        console.error("Highlight error:", e);
        setToast({ message: "Highlighting failed. Try a smaller selection within the same sentence.", type: "error" });
    }
  };

  const handleEraseHighlight = () => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;
    
    let node = selection.anchorNode;
    while (node && node !== document.body) {
        if (node instanceof HTMLElement && node.classList.contains('doc-highlight')) {
            const parent = node.parentNode;
            while (node.firstChild) parent?.insertBefore(node.firstChild, node);
            parent?.removeChild(node);
            setToast({ message: "Highlight removed", type: "success" });
            return;
        }
        node = node.parentNode;
    }
    setToast({ message: "No highlight found at cursor", type: "error" });
  };

  const openNotePopup = async () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim() || "";
    setSelectedText(text);
    
    // Explicitly fetch notes when opening to ensure they are loaded
    if (selectedDocument?.id) {
      await fetchNotes(selectedDocument.id);
    }
    
    console.log("📂 Opening note popup with text:", noteText);
    setIsNotePopupOpen(true);
  };

  const saveNoteToDB = async () => {
    if (!selectedDocument?.id) return;
    
    try {
      await api.post("http://localhost:8000/notes", {
        analysis_id: selectedDocument.id,
        selected_text: selectedText,
        note_text: noteText
      });
      
      setToast({ message: "Note updated successfully", type: "success" });
      setIsNotePopupOpen(false);
      // We keep noteText in state if it's per-document
      fetchNotes(selectedDocument.id);
    } catch (err) {
        setToast({ message: "Failed to save note", type: "error" });
    }
  };

  const handleExportPDF = async () => {
    if (!selectedDocument) return;

    try {
      const { jsPDF } = await import('jspdf');
      const autoTable = (await import('jspdf-autotable')).default;
      
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      
      // Title
      doc.setFontSize(22);
      doc.setTextColor(37, 99, 235); // Blue
      doc.text("Strategic Document Analysis", pageWidth / 2, 20, { align: 'center' });
      
      // Metadata
      doc.setFontSize(12);
      doc.setTextColor(100);
      doc.text(`Document: ${selectedDocument.filename}`, 14, 30);
      doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 36);
      
      doc.setDrawColor(200);
      doc.line(14, 42, pageWidth - 14, 42);
      
      let currentY = 50;

      // Executive Summary
      doc.setFontSize(16);
      doc.setTextColor(0);
      doc.text("Executive Summary", 14, currentY);
      currentY += 10;
      doc.setFontSize(10);
      const summaryItems = selectedDocument.executive_summary.map(item => [item]);
      autoTable(doc, {
        startY: currentY,
        body: summaryItems,
        theme: 'plain',
        styles: { fontSize: 10, cellPadding: 2 },
        columnStyles: { 0: { cellWidth: pageWidth - 28 } }
      });
      currentY = (doc as any).lastAutoTable.finalY + 15;

      // Key Risks
      doc.setFontSize(16);
      doc.text("Critical Risks", 14, currentY);
      currentY += 10;
      const riskItems = selectedDocument.key_risks.map(item => [item]);
      autoTable(doc, {
        startY: currentY,
        body: riskItems,
        theme: 'plain',
        styles: { fontSize: 10, cellPadding: 2 },
        columnStyles: { 0: { cellWidth: pageWidth - 28 } }
      });
      currentY = (doc as any).lastAutoTable.finalY + 15;

      // Opportunities
      doc.setFontSize(16);
      doc.text("Strategic Opportunities", 14, currentY);
      currentY += 10;
      const opportunityItems = selectedDocument.opportunities.map(item => [item]);
      autoTable(doc, {
        startY: currentY,
        body: opportunityItems,
        theme: 'plain',
        styles: { fontSize: 10, cellPadding: 2 },
        columnStyles: { 0: { cellWidth: pageWidth - 28 } }
      });
      currentY = (doc as any).lastAutoTable.finalY + 15;

      // Strategic Recommendations
      if (selectedDocument.strategic_recommendations.length > 0) {
        if (currentY > 240) doc.addPage();
        doc.setFontSize(16);
        doc.text("Strategic Recommendations", 14, currentY);
        currentY += 10;
        const recoItems = selectedDocument.strategic_recommendations.map(item => [item]);
        autoTable(doc, {
          startY: currentY,
          body: recoItems,
          theme: 'plain',
          styles: { fontSize: 10, cellPadding: 2 },
          columnStyles: { 0: { cellWidth: pageWidth - 28 } }
        });
        currentY = (doc as any).lastAutoTable.finalY + 15;
      }

      // Notes
      if (notes.length > 0) {
        if (currentY > 240) doc.addPage();
        doc.setFontSize(16);
        doc.setTextColor(16, 185, 129); // Emerald
        doc.text("User Annotations & Notes", 14, currentY);
        currentY += 10;
        
        const noteItems = notes.map(note => [
          `Text: "${note.selected_text}"\nNote: ${note.note_content}`
        ]);
        
        autoTable(doc, {
          startY: currentY,
          body: noteItems,
          theme: 'striped',
          styles: { fontSize: 9, cellPadding: 4 },
          columnStyles: { 0: { cellWidth: pageWidth - 28 } },
          headStyles: { fillColor: [16, 185, 129] }
        });
      }

      doc.save(`document_analysis_report.pdf`);
      setToast({ message: "Report downloaded successfully", type: "success" });
    } catch (err) {
      console.error("PDF Export error:", err);
      setToast({ message: "Failed to generate PDF", type: "error" });
    }
  };

  const handleAskDocAI = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!docAIQuestion.trim() || isAsking) return;

    const userMsg = docAIQuestion.trim();
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setDocAIQuestion("");
    setIsAsking(true);

    try {
      const response = await api.post('http://localhost:8000/ask', { question: userMsg });
      setChatMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
    } catch (err) {
      console.error('RAG Error:', err);
      setChatMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error while processing your request." }]);
    } finally {
      setIsAsking(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setSelectedDocument(null);
      setError(null);

      // For new local files, we create a temporary preview URL
      if (selectedFile.type === 'application/pdf') {
        const url = URL.createObjectURL(selectedFile);
        console.log('📂 New local PDF file selected:', selectedFile.name);
        setSelectedDocument({
          filename: selectedFile.name,
          executive_summary: [],
          key_risks: [],
          opportunities: [],
          strategic_recommendations: [],
          pdf_file_url: url
        });
      } else {
        console.log('📂 New local file selected (non-PDF):', selectedFile.name);
        setSelectedDocument({
          filename: selectedFile.name,
          executive_summary: [],
          key_risks: [],
          opportunities: [],
          strategic_recommendations: [],
          pdf_file_url: undefined // No preview for non-PDFs
        });
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('📤 Uploading document for analysis...');
      const response = await api.post('http://localhost:8000/analyze', formData);

      const data = response.data;
      console.log('✅ Analysis complete:', data);

      // Reset note state for new document
      setNoteText("");
      setNotes([]);

      // Update with the official server-side URL and analysis
      setSelectedDocument({
        ...data,
        pdf_file_url: data.pdf_file_url?.replace('127.0.0.1', 'localhost'),
        preview_url: data.preview_url?.replace('127.0.0.1', 'localhost')
      });

      // Reset UI state for new document
      setActiveMode('analyze');
      setChatMessages([]);

      fetchHistory(); // Refresh history list
    } catch (err: any) {
      console.error('Upload error:', err);
      let errorMessage = err.response?.data?.detail || err.message || 'Failed to analyze the document.';
      if (err.code === 'ECONNREFUSED') errorMessage = '❌ Backend not running.';
      setError(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadFromHistory = async (id: number) => {
    // Debugging: document id clicked
    console.log('🖱️ History item clicked. ID:', id);

    setAnalyzing(true);
    setError(null);
    setFile(null);

    try {
      const response = await api.get(`http://localhost:8000/analysis/${id}`);
      const data = response.data;

      // Ensure the URL uses localhost for consistency
      const updatedData = {
        ...data,
        pdf_file_url: data.pdf_file_url?.replace('127.0.0.1', 'localhost'),
        preview_url: data.preview_url?.replace('127.0.0.1', 'localhost')
      };

      setSelectedDocument(updatedData);
      
      // Reset UI state for new document
      setActiveMode('analyze');
      setChatMessages([]);
    } catch (err: any) {
      console.error('History load error:', err);
      setError('Failed to load historical analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    console.log('🧹 Resetting workspace for new analysis');
    setFile(null);
    setSelectedDocument(null);
    setError(null);
    setNoteText("");
    setNotes([]);
    setActiveMode('analyze');
    setChatMessages([]);
  };

  const filteredHistory = useMemo(() => {
    return history.filter(item =>
      item.filename.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [history, searchQuery]);

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-white">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
        <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">Initializing Secure Session...</p>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <main className="h-screen w-screen bg-white flex flex-col overflow-hidden text-gray-900 font-sans">
      {/* Header */}
      <header className="h-14 px-4 flex items-center justify-between border-b border-gray-200 shrink-0 bg-white/80 backdrop-blur-md z-20">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-1.5 hover:bg-gray-100 rounded-md transition-colors"
            title={isSidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
          >
            {isSidebarOpen ? <ChevronLeft className="w-5 h-5 text-gray-500" /> : <ChevronRight className="w-5 h-5 text-gray-500" />}
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <h1 className="flex items-center gap-2 tracking-tight">
              <span className="text-xl font-extrabold uppercase tracking-tight">Doc<span className="text-blue-600">AI</span></span>
              <span className="text-gray-300 font-light">—</span>
              <span className="text-[13px] text-gray-500 font-medium uppercase tracking-[0.1em] mt-0.5">Enterprise Document Intelligence</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {selectedDocument && (
            <div className="flex items-center bg-gray-100 p-1 rounded-xl border border-gray-200 mr-2">
              <button
                onClick={() => setActiveMode('analyze')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeMode === 'analyze' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Analyze
              </button>
              <button
                onClick={() => setActiveMode('ask')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeMode === 'ask' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Ask DocAI
              </button>
            </div>
          )}
          
          {selectedDocument && (
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={reset}
              className="flex items-center gap-2 bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-all shadow-md active:scale-95"
            >
              <Plus className="w-4 h-4" />
              New Analysis
            </motion.button>
          )}

          <button
            onClick={logout}
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-red-500 transition-all ml-1"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="flex-1 flex min-h-0 relative overflow-hidden">
        {/* Sidebar: History */}
        <motion.aside
          initial={false}
          animate={{
            width: isSidebarOpen ? 260 : 0,
            opacity: isSidebarOpen ? 1 : 0,
            x: isSidebarOpen ? 0 : -260
          }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="h-full border-r border-gray-200 bg-gray-50 flex flex-col shrink-0 overflow-hidden"
        >
          <div className="p-4 w-[260px] flex-1 flex flex-col min-h-0">
            <div className="flex items-center gap-2 mb-4 text-gray-500">
              <History className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-widest">Previous Analyses</span>
            </div>

            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search past analyses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
              />
            </div>

            {/* History List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pb-10">
              {loadingHistory ? (
                <div className="flex items-center justify-center py-10">
                  <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
                </div>
              ) : filteredHistory.length > 0 ? (
                filteredHistory.map((item) => (
                  <div key={item.id} className="relative group/item">
                    <button
                      onClick={() => loadFromHistory(item.id)}
                      className={`w-full text-left p-3 rounded-xl border transition-all ${selectedDocument?.id === item.id
                        ? 'border-blue-500/50 bg-blue-50/50'
                        : 'border-transparent hover:bg-white'
                        }`}
                    >
                      <div className="flex items-start gap-3">
                        <FileText className={`w-4 h-4 mt-0.5 shrink-0 ${selectedDocument?.id === item.id ? 'text-blue-500' : 'text-gray-400'}`} />
                        <div className="flex-1 min-w-0 pr-6">
                          <p className={`text-sm font-semibold truncate ${selectedDocument?.id === item.id ? 'text-blue-600' : 'text-gray-700'}`}>
                            {item.filename}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] text-gray-400 font-medium uppercase">{item.created_at}</span>
                            {item.is_pinned && <Pin className="w-3 h-3 text-blue-500 shrink-0" />}
                          </div>
                        </div>
                      </div>
                    </button>

                    {/* Actions Menu Trigger */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveMenuId(activeMenuId === item.id ? null : item.id);
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 opacity-0 group-hover/item:opacity-100 hover:bg-gray-100 rounded-md transition-all text-gray-400 hover:text-gray-600 z-10"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </button>

                    {/* Action Popover */}
                    <AnimatePresence>
                      {activeMenuId === item.id && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95, y: 5 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.95, y: 5 }}
                          className="absolute right-0 top-full mt-1 w-32 bg-white border border-gray-200 rounded-xl shadow-xl z-[100] py-1.5"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            onClick={(e) => togglePin(e, item.id)}
                            className="w-full flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors"
                          >
                            <Pin className={`w-3.5 h-3.5 ${item.is_pinned ? 'fill-blue-500 text-blue-500' : ''}`} />
                            {item.is_pinned ? 'Unpin' : 'Pin'}
                          </button>
                          <button
                            onClick={(e) => deleteAnalysis(e, item.id)}
                            className="w-full flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-red-500 hover:bg-red-50 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            Delete
                          </button>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))
              ) : (
                <div className="py-10 text-center text-gray-500">
                  <p className="text-xs">No history found</p>
                </div>
              )}
            </div>

            <div className="mt-auto pt-4 border-t border-gray-100 bg-gray-50">
              <button
                onClick={reset}
                className="w-full flex items-center justify-center gap-2 py-2 text-xs font-bold text-gray-500 hover:text-blue-600 transition-colors"
              >
                <Plus className="w-3 h-3" />
                NEW ANALYSIS
              </button>
            </div>
          </div>
        </motion.aside>

        {/* Workspace: Content Area */}
        <div className="flex-1 flex flex-col min-w-0 bg-white relative">
          {!selectedDocument && !analyzing ? (
            <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center">
              <div className="max-w-md w-full">
                <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>
                <h2 className="text-2xl font-extrabold mb-3">Enterprise Insight Engine</h2>
                <p className="text-sm text-gray-500 mb-8 leading-relaxed">
                  Upload your business documents or select a past analysis to generate strategic intelligence.
                </p>

                <label className="cursor-pointer group">
                  <div className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-bold transition-all shadow-xl shadow-blue-500/20 group-hover:scale-[1.02] active:scale-95">
                    Upload Document
                  </div>
                  <input type="file" className="hidden" accept=".pdf,.docx,.pptx" onChange={handleFileChange} />
                </label>

                {error && (
                  <div className="mt-6 p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3 text-left">
                    <AlertCircle className="w-5 h-5 text-red-500 translate-y-0.5" />
                    <p className="text-xs font-medium text-red-700 leading-tight">{error}</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex min-h-0">
              {/* Split View: Insights (Left) and PDF (Right) */}
              <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 min-h-0 bg-white">

                {/* Insights Panel */}
                <div className="h-full flex flex-col min-h-0 border-r border-gray-200 bg-gray-50/50 overflow-hidden">
                  <AnimatePresence mode="wait">
                    {analyzing ? (
                      <motion.div
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="h-full flex flex-col items-center justify-center p-8"
                      >
                        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-4" />
                        <p className="text-sm font-bold animate-pulse text-gray-600">Synthesizing intelligence...</p>
                      </motion.div>
                    ) : selectedDocument?.executive_summary.length === 0 ? (
                      <motion.div
                        key="action"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="h-full flex flex-col items-center justify-center p-8 text-center"
                      >
                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                          <Lightbulb className="w-8 h-8 text-blue-600" />
                        </div>
                        <h3 className="font-bold text-lg mb-2 truncate max-w-full px-4">{selectedDocument?.filename}</h3>
                        <p className="text-xs text-gray-500 mb-6 font-medium">Ready to process document for strategic insights.</p>
                        <button
                          onClick={handleUpload}
                          className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:bg-blue-700 transition-all active:scale-95"
                        >
                          Run Full Analysis
                        </button>
                      </motion.div>
                    ) : (
                      <motion.div
                        key="insights"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-1 overflow-y-auto p-4 lg:p-6 custom-scrollbar space-y-4"
                      >
                        {activeMode === 'analyze' ? (
                          <>
                            {/* Annotation Toolbar */}
                            <div className={`bg-gray-100/80 backdrop-blur-sm p-2 rounded-xl border border-gray-200 shadow-sm sticky top-0 z-10 transition-all duration-300 w-full flex items-center ${!isSidebarOpen ? 'justify-between' : ''}`}>
                              <div className="flex-1 flex flex-wrap items-center gap-2.5 w-full toolbar-actions">
                                <button 
                                  onClick={handleHighlight}
                                  className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-white rounded-lg text-xs font-bold text-gray-700 border border-gray-200 hover:border-blue-500 hover:shadow-md hover:-translate-y-0.5 transition-all active:scale-95 flex-grow max-w-[180px]"
                                >
                                  <Highlighter className="w-3.5 h-3.5 text-yellow-500" /> Highlight
                                </button>
                                <button 
                                  onClick={handleEraseHighlight}
                                  className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-white rounded-lg text-xs font-bold text-gray-700 border border-gray-200 hover:border-red-500 hover:shadow-md hover:-translate-y-0.5 transition-all active:scale-95 flex-grow max-w-[180px]"
                                >
                                  <Eraser className="w-3.5 h-3.5 text-gray-500" /> Erase
                                </button>
                                <button 
                                  onClick={openNotePopup}
                                  className={`flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95 flex-grow max-w-[180px] hover:shadow-md hover:-translate-y-0.5 ${noteText ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-white text-gray-700 border-gray-200 hover:border-emerald-500'}`}
                                >
                                  {noteText ? (
                                    <><StickyNote className="w-3.5 h-3.5 text-emerald-500" /> Add Note</>
                                  ) : (
                                    <><Plus className="w-3.5 h-3.5 text-emerald-500" /> Add Note</>
                                  )}
                                </button>
                                
                                <button 
                                  onClick={handleExportPDF}
                                  className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-white rounded-lg text-xs font-bold text-gray-700 border border-gray-200 hover:border-blue-500 hover:shadow-md hover:-translate-y-0.5 transition-all active:scale-95 flex-grow max-w-[180px]"
                                >
                                  <Download className="w-3.5 h-3.5 text-blue-600" /> Export PDF
                                </button>
                              </div>
                            </div>

                            {/* Summary */}
                            <section className="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm">
                              <div className="flex items-center gap-2.5 mb-5">
                                <FileText className="w-4 h-4 text-blue-600" />
                                <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-400">Executive Summary</h4>
                              </div>
                              <div className="space-y-3">
                                {selectedDocument?.executive_summary.map((point, i) => (
                                  <div key={i} className="flex gap-4 p-3.5 bg-gray-50 rounded-xl text-sm font-medium leading-relaxed">
                                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" />
                                    <div className="flex-1">{point}</div>
                                  </div>
                                ))}
                              </div>
                            </section>

                            <div className="grid grid-cols-1 gap-4">
                              <section className="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm">
                                <div className="flex items-center gap-2.5 mb-4">
                                  <ShieldAlert className="w-4 h-4 text-red-600" />
                                  <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-400">Critical Risks</h4>
                                </div>
                                <div className="space-y-2">
                                  {selectedDocument?.key_risks.map((risk, i) => (
                                    <div key={i} className="text-xs p-3 bg-red-50/50 text-red-700 rounded-lg border border-red-100 font-semibold flex gap-2">
                                      <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                                      <div className="flex-1">{risk}</div>
                                    </div>
                                  ))}
                                </div>
                              </section>

                              <section className="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm">
                                <div className="flex items-center gap-2.5 mb-4">
                                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                                  <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-400">Growth Opportunities</h4>
                                </div>
                                <div className="space-y-2">
                                  {selectedDocument?.opportunities.map((opp, i) => (
                                    <div key={i} className="text-xs p-3 bg-emerald-50/50 text-emerald-700 rounded-lg border border-emerald-100 font-semibold flex gap-2">
                                      <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                                      <div className="flex-1">{opp}</div>
                                    </div>
                                  ))}
                                </div>
                              </section>
                            </div>

                            <section className="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm">
                              <div className="flex items-center gap-2.5 mb-4">
                                <Lightbulb className="w-4 h-4 text-amber-600" />
                                <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-400">Strategic Recommendations</h4>
                              </div>
                              <div className="space-y-2.5">
                                {selectedDocument?.strategic_recommendations.map((rec, i) => (
                                  <div key={i} className="text-sm p-3.5 bg-amber-50/30 text-gray-700 rounded-xl border border-amber-100 font-medium">
                                    {rec}
                                  </div>
                                ))}
                              </div>
                            </section>
                          </>
                        ) : (
                          <div className="h-full flex flex-col min-h-0 bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-lg">
                            {/* Chat Header */}
                            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                  <Bot className="w-5 h-5 text-white" />
                                </div>
                                <div className="min-w-0">
                                  <h3 className="text-sm font-bold truncate">Ask DocAI</h3>
                                  <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest truncate">Active Document: {selectedDocument?.filename}</p>
                                </div>
                              </div>
                              {chatMessages.length > 0 && (
                                <button 
                                  onClick={() => setChatMessages([])}
                                  className="text-[10px] font-bold text-gray-400 hover:text-red-500 uppercase tracking-widest transition-colors flex items-center gap-1.5 shrink-0"
                                >
                                  <Trash2 className="w-3 h-3" />
                                  Clear Chat
                                </button>
                              )}
                            </div>

                            {/* Message List */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                              {chatMessages.length === 0 && (
                                <div className="h-full flex flex-col items-center justify-center text-center p-8">
                                  <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                                    <Bot className="w-6 h-6 text-blue-600" />
                                  </div>
                                  <p className="text-sm font-bold text-gray-700 mb-2">Ask anything about this document</p>
                                  <p className="text-xs text-gray-400 font-medium leading-relaxed">
                                    I'll use the document content to provide accurate answers.
                                  </p>
                                </div>
                              )}
                              {chatMessages.map((msg, i) => (
                                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                  <div className={`${msg.role === 'user' ? 'max-w-[65%] p-2.5 px-4 bg-blue-600 text-white rounded-2xl rounded-tr-none' : 'max-w-[75%] p-3 bg-gray-50 border border-gray-100 text-gray-700 rounded-2xl rounded-tl-none shadow-sm'} text-sm font-medium leading-relaxed`}>
                                    {msg.content}
                                  </div>
                                </div>
                              ))}
                              {isAsking && (
                                <div className="flex justify-start">
                                  <div className="bg-gray-50 border border-gray-100 p-3.5 rounded-2xl shadow-sm">
                                    <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Chat Input */}
                            <form onSubmit={handleAskDocAI} className="p-4 border-t border-gray-100 bg-gray-50/50">
                              <div className="relative">
                                <input
                                  type="text"
                                  placeholder="Ask about this document..."
                                  value={docAIQuestion}
                                  onChange={(e) => setDocAIQuestion(e.target.value)}
                                  disabled={isAsking}
                                  className="w-full bg-white border border-gray-200 rounded-xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all shadow-sm"
                                />
                                <button 
                                  type="submit"
                                  disabled={!docAIQuestion.trim() || isAsking}
                                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all disabled:bg-gray-200 shadow-md shadow-blue-500/10"
                                >
                                  {isAsking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                </button>
                              </div>
                            </form>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* PDF Viewer Panel */}
                <div className="h-full bg-gray-100 flex flex-col min-h-0 relative">
                  {/* Debugging: Preview Viewer Render event */}
                  {(selectedDocument?.preview_url || selectedDocument?.pdf_file_url) ? (
                    <div className="h-full flex flex-col">
                      <div className="px-4 py-2 border-b border-gray-200 bg-white flex items-center justify-between text-[11px] font-bold text-gray-400 uppercase tracking-widest shrink-0">
                        <div className="flex items-center gap-2 truncate pr-4">
                          <FileText className="w-3 h-3" />
                          <span className="truncate">{selectedDocument.filename}</span>
                        </div>
                        <a
                          href={selectedDocument.preview_url || selectedDocument.pdf_file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-blue-500 transition-colors flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" /> OPEN FULL
                        </a>
                      </div>
                      <div className="flex-1 bg-white overflow-hidden">
                        <iframe
                          src={`${selectedDocument.preview_url || selectedDocument.pdf_file_url}#view=FitH&toolbar=0`}
                          className="w-full h-full border-none"
                          title="Document Viewer"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center p-12 text-center text-gray-500 bg-white">
                      <FileText className="w-12 h-12 text-gray-200 mb-6" />
                      <p className="font-bold text-gray-300 uppercase tracking-[0.2em] text-xs">No PDF Loaded</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer / Status */}
      <footer className="h-8 border-t border-gray-200 px-4 flex items-center justify-between bg-gray-50 text-[10px] font-bold text-gray-400 uppercase tracking-widest shrink-0">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full ${loadingHistory ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} />
            PostgreSQL: Connected
          </span>
          <span className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Engine: Active
          </span>
        </div>
        <div className="flex items-center gap-3">
          {selectedDocument && <span className="text-gray-500">{selectedDocument?.filename}</span>}
          <span className="text-blue-500">
            {analyzing ? 'ANALYSIS IN PROGRESS...' : 'SYSTEM READY'}
          </span>
        </div>
      </footer>

      {/* Add Note Modal */}
      <AnimatePresence>
        {isNotePopupOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsNotePopupOpen(false)}
              className="absolute inset-0 bg-gray-950/40 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-gray-200 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                    <StickyNote className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">Add Note</h3>
                    <p className="text-xs text-gray-500 italic">Write a quick note about the selected document or text.</p>
                  </div>
                </div>

                <textarea
                  autoFocus
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Write your thoughts, insights, or reminders..."
                  className="w-full h-48 mt-4 p-4 bg-gray-50 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none"
                />

                <div className="flex gap-3 mt-6">
                  <button
                    onClick={() => {
                      setIsNotePopupOpen(false);
                    }}
                    className="flex-1 py-3 px-4 rounded-xl font-bold text-sm text-gray-500 hover:bg-gray-100 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={saveNoteToDB}
                    className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:bg-blue-700 transition-all active:scale-95"
                  >
                    Save Note
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className={`fixed bottom-8 left-1/2 -translate-x-1/2 z-[200] px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3 font-bold text-sm border ${
              toast.type === 'success' 
                ? 'bg-emerald-600 text-white border-emerald-500 shadow-emerald-500/20' 
                : 'bg-red-600 text-white border-red-500 shadow-red-500/20'
            }`}
          >
            {toast.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
