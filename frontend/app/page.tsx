"use client";

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { Search, Filter, Download, ExternalLink, RefreshCw, Trash2, Activity, Terminal, Zap, Folder, Facebook, Instagram, Linkedin, Globe, Square, Mail, PlusCircle, ArrowRight } from 'lucide-react';
import Navbar from '@/components/Navbar';
import ProjectSelector from '@/components/ProjectSelector';
import EmailModal from '@/components/EmailModal';
import EditLeadModal from '@/components/EditLeadModal';
import AddLeadModal from '@/components/AddLeadModal';
import LeadActions from '@/components/LeadActions';
import DashboardStats from '@/components/DashboardStats';
import { useToast } from '@/components/Toast';

// Types matching backend
interface Lead {
  id: number;
  business_name: string;
  domain: string;
  phone: string;
  email: string;
  email_quality: string;
  builder: string;
  builder_type: string;
  technical_score: number;
  final_priority: number;
  tier: string;
  city: string;
  keyword: string;
  notes: string;
  project_name: string;
  facebook: string;
  instagram: string;
  linkedin: string;
  pain_points: string;
  email_sent?: boolean;
  email_sent_at?: string;
  email_status?: string;
}

interface Log {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export default function Home() {
  const [currentProject, setCurrentProject] = useState<string | null>(null);
  const [isProjectLoading, setIsProjectLoading] = useState(true);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [limit, setLimit] = useState(120);
  const [filterMode, setFilterMode] = useState<string>('');
  const [analyzingIds, setAnalyzingIds] = useState<number[]>([]);
  const [isBulkAnalyzing, setIsBulkAnalyzing] = useState(false);
  const [selectedLeads, setSelectedLeads] = useState<number[]>([]);
  const [emailLead, setEmailLead] = useState<Lead | null>(null);
  const [editLead, setEditLead] = useState<Lead | null>(null);
  const [isAddLeadOpen, setIsAddLeadOpen] = useState(false);
  const [searchMode, setSearchMode] = useState<'manual' | 'apify'>('manual');
  const [isRunning, setIsRunning] = useState(false);
  const { addToast } = useToast();
  const logsEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const API_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api';

  const [searchQuery, setSearchQuery] = useState('');

  // Filter leads based on search query
  const filteredLeads = leads.filter(lead => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
        lead.business_name?.toLowerCase().includes(query) ||
        lead.city?.toLowerCase().includes(query) ||
        lead.domain?.toLowerCase().includes(query)
    );
  });

  const displayedLeads = filteredLeads;

  // Persist project selection
  useEffect(() => {
    const savedProject = localStorage.getItem('currentProject');
    if (savedProject) {
      setCurrentProject(savedProject);
    }
    setIsProjectLoading(false);
  }, []);

  useEffect(() => {
    if (isProjectLoading) return;

    if (currentProject) {
      localStorage.setItem('currentProject', currentProject);
    } else {
      localStorage.removeItem('currentProject');
    }
  }, [currentProject, isProjectLoading]);

  const fetchLeads = async () => {
    if (!currentProject) return;
    
    try {
      const params: any = { project_name: currentProject };
      if (filterMode) params.filter_mode = filterMode;
      
      const res = await axios.get(`${API_URL}/leads`, { params });
      setLeads(res.data);
    } catch (error) {
      console.error("Failed to fetch leads", error);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API_URL}/status`);
      if (JSON.stringify(res.data) !== JSON.stringify(logs)) {
         setLogs(res.data);
      }
    } catch (error) {
      console.error("Failed to fetch logs", error);
    }
  };

  useEffect(() => {
    if (currentProject) {
      fetchLeads();
      const interval = setInterval(() => {
        fetchLeads();
        fetchLogs();
      }, 2000); 
      return () => clearInterval(interval);
    }
  }, [filterMode, currentProject]);

  const handleApifySearch = async () => {
    if (!keyword || !location) {
      addToast('Please enter both keyword and location', 'error');
      return;
    }
    if (!currentProject) {
      addToast('No project selected', 'error');
      return;
    }
    
    setLoading(true);
    setIsRunning(true);
    addToast('Starting Apify search...', 'info');
    
    try {
      await axios.post(`${API_URL}/apify/run`, {
        search_terms: [keyword],
        location: location,
        max_places: limit, 
        project_name: currentProject
      });
      addToast('Apify task started in background!', 'success');
    } catch (error: any) {
      console.error("Apify search failed", error);
      if (error.response?.status === 400) {
          addToast(error.response.data.detail || 'Configuration error', 'error');
      } else {
          addToast('Failed to start Apify search. Check backend logs.', 'error');
      }
      setLoading(false);
      setIsRunning(false);
    }
    setTimeout(() => setLoading(false), 2000);
  };

  const handleScan = async () => {
    if (!keyword || !location) {
      addToast('Please enter both keyword and location', 'error');
      return;
    }
    if (!currentProject) {
      addToast('No project selected', 'error');
      return;
    }
    setLoading(true);
    setIsRunning(true);
    addToast('Starting scan...', 'info');
    try {
      await axios.post(`${API_URL}/scan`, null, {
        params: { 
          keyword, 
          location,
          limit,
          project_name: currentProject
        }
      });
      addToast('Scan started in background!', 'success');
    } catch (error) {
      console.error("Scan failed", error);
      addToast('Failed to start scan. Check backend.', 'error');
      setLoading(false);
      setIsRunning(false);
    }
    setTimeout(() => setLoading(false), 2000);
  };

  const handleStop = async () => {
    if (!confirm('Are you sure you want to stop all active tasks?')) return;
    setLoading(true);
    try {
      await axios.post(`${API_URL}/stop`);
      addToast('Stop signal sent. Workers terminating...', 'warning');
      setLoading(false);
      setIsRunning(false);
      setIsBulkAnalyzing(false);
      setAnalyzingIds([]);
    } catch (error) {
      console.error("Stop failed", error);
      addToast('Failed to stop tasks', 'error');
      setLoading(false);
    }
  };

  const handleAnalyze = async (id: number) => {
    setAnalyzingIds(prev => [...prev, id]);
    addToast('Starting analysis...', 'info');
    try {
      await axios.post(`${API_URL}/leads/${id}/analyze`);
      addToast('Analysis started in background', 'success');
    } catch (error) {
      console.error("Analysis failed", error);
      addToast('Failed to start analysis', 'error');
    }
    
    // Clear loading state after delay (status will update via polling)
    setTimeout(() => {
        setAnalyzingIds(prev => prev.filter(pid => pid !== id));
    }, 2000);
  };

  const handleEnrich = async (id: number) => {
    setAnalyzingIds(prev => [...prev, id]);
    addToast('Enriching lead details...', 'info');
    try {
      await axios.post(`${API_URL}/enrich_batch`, { lead_ids: [id] });
      addToast('Enrichment started in background', 'success');
    } catch (error) {
      console.error("Enrichment failed", error);
      addToast('Failed to start enrichment', 'error');
    }
    
    setTimeout(() => {
        setAnalyzingIds(prev => prev.filter(pid => pid !== id));
    }, 2000);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this lead?')) return;
    
    try {
      await axios.delete(`${API_URL}/leads/${id}`);
      addToast('Lead deleted successfully', 'success');
      fetchLeads(); // Refresh list
    } catch (error) {
      console.error("Delete failed", error);
      addToast('Failed to delete lead', 'error');
    }
  };

  const handleAnalyzeAll = async () => {
    if (!currentProject) return;
    if (!confirm(`Are you sure you want to analyze ALL leads in "${currentProject}"? This will open many browser windows sequentially.`)) return;
    
    setIsBulkAnalyzing(true);
    addToast('Starting bulk analysis...', 'info');
    
    try {
      const res = await axios.post(`${API_URL}/analyze_all`, {
        project_name: currentProject
      });
      addToast(`Queued ${res.data.count} leads for analysis!`, 'success');
    } catch (error) {
      console.error("Bulk analysis failed", error);
      addToast('Failed to start bulk analysis', 'error');
    }
    
    setTimeout(() => setIsBulkAnalyzing(false), 3000);
  };

  const handleBulkAnalyze = async () => {
      if (selectedLeads.length === 0) return;
      if (!confirm(`Analyze ${selectedLeads.length} selected leads?`)) return;

      setIsBulkAnalyzing(true);
      addToast(`Starting analysis for ${selectedLeads.length} leads...`, 'info');

      try {
          await axios.post(`${API_URL}/analyze_batch`, { lead_ids: selectedLeads });
          addToast('Analysis started! (Processing 5 windows at a time)', 'success');
          setSelectedLeads([]); // Clear selection
      } catch (error) {
          console.error("Batch analysis failed", error);
          addToast('Failed to start batch analysis', 'error');
      }
      setTimeout(() => setIsBulkAnalyzing(false), 2000);
  };

  const handleBulkEnrich = async () => {
      if (selectedLeads.length === 0) return;
      if (!confirm(`Find missing details (website/email) for ${selectedLeads.length} leads?`)) return;

      setIsBulkAnalyzing(true);
      addToast(`Searching Google for ${selectedLeads.length} leads...`, 'info');

      try {
          await axios.post(`${API_URL}/enrich_batch`, { lead_ids: selectedLeads });
          addToast('Enrichment started!', 'success');
          setSelectedLeads([]); // Clear selection
      } catch (error) {
          console.error("Batch enrichment failed", error);
          addToast('Failed to start enrichment', 'error');
      }
      setTimeout(() => setIsBulkAnalyzing(false), 2000);
  };

  const handleBulkDelete = async () => {
      if (selectedLeads.length === 0) return;
      if (!confirm(`Delete ${selectedLeads.length} selected leads? This cannot be undone.`)) return;

      try {
          await axios.post(`${API_URL}/delete_batch`, { lead_ids: selectedLeads });
          addToast(`Deleted ${selectedLeads.length} leads`, 'success');
          setSelectedLeads([]); // Clear selection
          fetchLeads();
      } catch (error) {
          console.error("Batch delete failed", error);
          addToast('Failed to delete leads', 'error');
      }
  };

  const handleBulkEmail = async () => {
      if (selectedLeads.length === 0) return;
      if (!confirm(`Send automated emails to ${selectedLeads.length} selected leads? This will use the best template for each lead.`)) return;

      setIsBulkAnalyzing(true);
      addToast(`Queuing ${selectedLeads.length} emails...`, 'info');

      try {
          await axios.post(`${API_URL}/email_batch`, { lead_ids: selectedLeads });
          addToast('Emails are being sent in the background!', 'success');
          setSelectedLeads([]);
      } catch (error) {
          console.error("Batch email failed", error);
          addToast('Failed to start batch email', 'error');
      }
      setTimeout(() => setIsBulkAnalyzing(false), 2000);
  };

  const handleEmailAll = async () => {
    if (!currentProject) return;
    const count = leads.length;
    const targetDescription = filterMode ? `${count} leads filtered by "${filterMode}"` : `ALL ${count} suitable leads`;
    
    if (!confirm(`Are you sure you want to email ${targetDescription} in "${currentProject}"? This will only email leads that have an email and HAVEN'T been emailed yet.`)) return;
    
    setIsBulkAnalyzing(true);
    addToast('Starting email blast...', 'info');
    
    try {
      await axios.post(`${API_URL}/email_all`, {
        project_name: currentProject,
        filter_mode: filterMode || null
      });
      addToast(`Email blast started! Check logs for progress.`, 'success');
    } catch (error) {
      console.error("Email blast failed", error);
      addToast('Failed to start email blast', 'error');
    }
    
    setTimeout(() => setIsBulkAnalyzing(false), 3000);
  };

  const toggleSelectAll = () => {
      if (selectedLeads.length === leads.length) {
          setSelectedLeads([]);
      } else {
          setSelectedLeads(leads.map(l => l.id));
      }
  };

  const toggleSelect = (id: number) => {
      if (selectedLeads.includes(id)) {
          setSelectedLeads(prev => prev.filter(l => l !== id));
      } else {
          setSelectedLeads(prev => [...prev, id]);
      }
  };

  const handleExport = () => {
    window.open(`${API_URL}/leads/export`, '_blank');
    addToast('Export started', 'success');
  };

  const handleAddLead = () => {
    setIsAddLeadOpen(true);
  };

  const cleanEmail = (email: string | null) => {
    if (!email) return null;
    let cleaned = email.toLowerCase().trim();
    
    // URL decode
    try {
        cleaned = decodeURIComponent(cleaned);
    } catch (e) {}
    
    // Remove unicode garbage
    cleaned = cleaned.replace(/u003e/g, '');
    
    // Remove leading/trailing punctuation
    cleaned = cleaned.replace(/^[/>:.<]+|[/>:.<]+$/g, '');
    
    // Filter images
    if (/\.(png|jpg|jpeg|gif|webp|svg|bmp|ico)$/.test(cleaned)) return null;
    
    return cleaned;
  };

  const handleTest = async () => {
    try {
      await axios.post(`${API_URL}/debug/seed`);
      addToast('Test data injected!', 'success');
      fetchLeads();
    } catch (error) {
      console.error(error);
      addToast('Backend connection failed', 'error');
    }
  };

  // Render Project Selector if no project selected
  if (isProjectLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3 animate-fade-in-up">
          <RefreshCw className="animate-spin text-blue-600" size={32} />
          <p className="text-slate-500 font-medium tracking-wide">Initializing Vertiqx...</p>
        </div>
      </div>
    );
  }

  if (!currentProject) {
    // Redirect to projects page or show empty state
    return (
        <main className="min-h-screen bg-slate-50/50">
            <Navbar onLogoClick={() => {}} />
            <div className="flex flex-col items-center justify-center h-[80vh] text-center px-4 animate-fade-in-up">
                <div className="bg-white p-12 rounded-[2rem] shadow-2xl shadow-blue-900/5 border border-slate-100 max-w-lg w-full">
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8 text-blue-600 shadow-inner ring-1 ring-blue-100">
                        <Folder size={48} />
                    </div>
                    <h2 className="text-3xl font-extrabold text-slate-900 mb-3 tracking-tight">No Project Selected</h2>
                    <p className="text-slate-500 mb-10 text-lg">Please select a project to view the dashboard and manage leads.</p>
                    <button 
                        onClick={() => router.push('/projects')}
                        className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-2xl hover:shadow-lg hover:shadow-blue-600/25 transition-all transform hover:-translate-y-0.5 active:translate-y-0 w-full flex items-center justify-center gap-2 group"
                    >
                        Go to Projects <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            </div>
        </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50/50 pb-20">
      <Navbar onLogoClick={() => setCurrentProject(null)} />
      
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in-up">
        
        {/* Project Header */}
        <div className="flex items-center justify-between bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-xl shadow-lg shadow-blue-600/20">
              <Folder size={24} />
            </div>
            <div>
              <div className="flex items-center gap-3">
                  <h1 className="text-xl font-bold text-slate-900 tracking-tight">{currentProject}</h1>
                  <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] font-bold rounded-full border border-emerald-100 uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Active
                  </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5 font-medium">Manage and analyze your lead generation campaign</p>
            </div>
          </div>
          <div className="flex gap-3">
             <button 
                onClick={handleAddLead}
                className="flex items-center gap-2 text-xs bg-slate-900 text-white font-semibold px-4 py-2.5 hover:bg-black rounded-xl transition-all shadow-xl shadow-slate-900/10 hover:shadow-slate-900/20 active:scale-[0.98]"
             >
                <PlusCircle size={16} /> Add Lead
             </button>
             <button 
                onClick={() => router.push('/projects')}
                className="text-xs text-slate-600 hover:text-blue-600 font-semibold px-4 py-2.5 hover:bg-white rounded-xl transition border border-transparent hover:border-slate-200 hover:shadow-sm"
             >
                Switch Project
             </button>
          </div>
        </div>

        {/* Stats Overview */}
        <DashboardStats leads={leads} />

        {/* Top Controls Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Search Controls */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white p-5 rounded-[2rem] shadow-sm border border-slate-100 relative overflow-hidden group">
              {/* Subtle accent background */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-blue-50/50 to-transparent rounded-bl-[4rem] -z-0 pointer-events-none"></div>

              <button 
                onClick={handleTest}
                className="absolute top-6 right-6 text-[10px] font-bold bg-slate-100 hover:bg-slate-200 text-slate-500 px-3 py-1.5 rounded-full transition uppercase tracking-wider"
              >
                Test Connection
              </button>
              
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 bg-blue-50 rounded-xl text-blue-600 shadow-sm ring-1 ring-blue-100">
                    <Search size={22} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">New Search</h2>
                    <p className="text-xs text-slate-400 font-medium">Discover new business leads</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wide ml-1">Keyword</label>
                    <input 
                      type="text" 
                      value={keyword}
                      onChange={(e) => setKeyword(e.target.value)}
                      placeholder="e.g. Roofers"
                      className="w-full p-3 bg-slate-50 border border-slate-100 focus:bg-white focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 rounded-2xl transition-all outline-none font-medium text-slate-900 placeholder:text-slate-400"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wide ml-1">Location</label>
                    <input 
                      type="text" 
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="e.g. Austin, TX"
                      className="w-full p-3 bg-slate-50 border border-slate-100 focus:bg-white focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 rounded-2xl transition-all outline-none font-medium text-slate-900 placeholder:text-slate-400"
                    />
                  </div>
                </div>
                
                <div className="mt-4">
                   <div className="flex justify-between items-center mb-2">
                       <label className="text-xs font-bold text-slate-500 uppercase tracking-wide ml-1">Leads Limit</label>
                       <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 font-bold rounded-lg text-xs">{limit} results</span>
                   </div>
                   <input 
                      type="range" 
                      min="1" 
                      max="120" 
                      value={limit} 
                      onChange={(e) => setLimit(parseInt(e.target.value))}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 hover:accent-blue-700"
                    />
                </div>

                <div className="mt-5 flex gap-4">
                  <div className="w-1/3 min-w-[140px]">
                    <select 
                      value={searchMode}
                      onChange={(e) => setSearchMode(e.target.value as 'manual' | 'apify')}
                      className="w-full h-full p-3 bg-white border-2 border-slate-100 rounded-2xl focus:border-blue-500 focus:ring-0 outline-none text-slate-600 font-bold cursor-pointer hover:border-slate-200 transition-colors"
                    >
                      <option value="manual">Manual Google Map Search</option>
                      <option value="apify">Apify Search</option>
                    </select>
                  </div>

                  <button 
                    onClick={isRunning ? handleStop : (searchMode === 'manual' ? handleScan : handleApifySearch)}
                    disabled={loading}
                    className={`flex-1 flex justify-center items-center gap-2 p-3 rounded-2xl font-bold transition-all shadow-lg active:scale-[0.98] active:shadow-sm ${
                        isRunning
                            ? 'bg-white border-2 border-red-100 text-red-500 hover:bg-red-50 hover:text-red-600'
                            : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white shadow-blue-600/25'
                    } ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
                  >
                    {loading ? (
                        <RefreshCw className="animate-spin" size={20} />
                    ) : isRunning ? (
                        <Square size={20} fill="currentColor" />
                    ) : searchMode === 'manual' ? (
                        <Zap size={20} fill="currentColor" />
                    ) : (
                        <Globe size={20} />
                    )}
                    
                    {loading 
                        ? (isRunning ? 'Stopping...' : 'Starting...') 
                        : isRunning 
                            ? 'Stop Search' 
                            : searchMode === 'manual' ? 'Start Scan' : 'Start Apify Search'
                    }
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* System Status Card */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 h-full flex flex-col relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 via-blue-500 to-purple-600"></div>
              
              <div className="flex items-center justify-between mb-6 mt-2">
                <div className="flex items-center gap-3 text-slate-900">
                  <div className="p-2 bg-slate-50 rounded-xl text-slate-700">
                     <Activity size={20} />
                  </div>
                  <h3 className="font-bold text-lg">Activity Log</h3>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 bg-green-50 text-green-700 rounded-full text-[10px] font-bold border border-green-100 uppercase tracking-wide">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  Live
                </div>
              </div>
              
              <div className="flex-1 flex flex-col justify-center items-center text-center space-y-4 py-2 relative bg-slate-50/50 rounded-2xl border border-slate-100/50">
                {/* Scrollable logs history */}
                <div className="absolute inset-0 overflow-y-auto px-3 py-3 space-y-2 pointer-events-auto custom-scrollbar" style={{ maxHeight: '300px' }}>
                  {logs.map((log, i) => (
                    <div key={i} className={`p-3 rounded-xl text-left text-sm border shadow-sm ${
                        log.type === 'error' ? 'bg-white border-red-100 text-red-700' :
                        log.type === 'success' ? 'bg-white border-green-100 text-green-700' :
                        log.type === 'warning' ? 'bg-white border-yellow-100 text-yellow-700' :
                        'bg-white border-slate-100 text-slate-600'
                    }`}>
                        <div className="flex items-center justify-between mb-1.5">
                            <span className={`font-extrabold text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded ${
                                log.type === 'error' ? 'bg-red-50' :
                                log.type === 'success' ? 'bg-green-50' :
                                log.type === 'warning' ? 'bg-yellow-50' :
                                'bg-slate-50'
                            }`}>{log.type}</span>
                            <span className="text-[10px] text-slate-400 font-mono">{log.timestamp}</span>
                        </div>
                        <p className="font-medium leading-relaxed text-xs">{log.message}</p>
                    </div>
                  ))}
                  {logs.length === 0 && (
                     <div className="h-full flex flex-col items-center justify-center text-slate-300 gap-3">
                        <div className="p-4 bg-white rounded-full shadow-sm">
                          <Terminal size={24} />
                        </div>
                        <p className="font-medium text-sm">Waiting for tasks...</p>
                     </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results Table */}
        <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-white">
            <div className="flex items-center gap-4">
              <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl">
                <Activity size={22} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Lead Database</h3>
                <p className="text-sm text-slate-500 font-medium">
                    {selectedLeads.length > 0 ? (
                        <span className="text-blue-600">{selectedLeads.length} selected</span>
                    ) : (
                        <span>{leads.length} businesses found</span>
                    )}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
                <div className="relative group">
                    <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" size={18} />
                    <input 
                        type="text" 
                        placeholder="Search leads..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 pr-4 py-2.5 border border-slate-200 bg-slate-50 focus:bg-white rounded-xl text-sm w-72 focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all font-medium"
                    />
                </div>
                
                <div className="w-[180px]">
                    <select 
                      value={filterMode}
                      onChange={(e) => setFilterMode(e.target.value)}
                      className="w-full h-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:border-blue-500 focus:ring-0 outline-none text-slate-600 font-bold cursor-pointer hover:bg-white hover:border-slate-300 transition text-sm"
                    >
                      <option value="">All Leads</option>
                      <option value="analyzed">Analyzed Leads</option>
                      <option value="potential">Potential Leads (>50)</option>
                      <option value="good_potential">Good Potential (>75)</option>
                      <option value="good_leads">Tier 1 & Gold</option>
                      <option value="potential_no_website">Potential (No Website)</option>
                      <option value="has_email">Has Email</option>
                      <option value="ready_to_email">Ready to Email</option>
                      <option value="email_sent">Email Sent</option>
                    </select>
                </div>
            
                <div className="flex gap-2">
                  {selectedLeads.length > 0 ? (
                  <>
                    <button 
                        onClick={handleBulkDelete}
                        className="flex items-center gap-2 px-4 py-2.5 bg-red-50 border border-red-100 text-red-600 rounded-xl hover:bg-red-100 transition shadow-sm text-sm font-bold"
                    >
                        <Trash2 size={16} /> Delete ({selectedLeads.length})
                    </button>
                    <button 
                        onClick={handleBulkEnrich}
                        disabled={isBulkAnalyzing}
                        className="flex items-center gap-2 px-4 py-2.5 bg-indigo-50 border border-indigo-100 text-indigo-600 rounded-xl hover:bg-indigo-100 transition shadow-sm text-sm font-bold disabled:opacity-50"
                    >
                        {isBulkAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Search size={16} />}
                        Enrich ({selectedLeads.length})
                    </button>
                    <button 
                        onClick={handleBulkAnalyze}
                        disabled={isBulkAnalyzing}
                        className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 border border-blue-600 text-white rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 text-sm font-bold disabled:opacity-50"
                    >
                        {isBulkAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Zap size={16} fill="currentColor" />}
                        Analyze ({selectedLeads.length})
                    </button>
                    <button 
                        onClick={handleBulkEmail}
                        disabled={isBulkAnalyzing}
                        className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 border border-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition shadow-lg shadow-emerald-600/20 text-sm font-bold disabled:opacity-50"
                    >
                        {isBulkAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Mail size={16} />}
                        Email ({selectedLeads.length})
                    </button>
                  </>
              ) : (
                  <>
                    <button 
                        onClick={handleAnalyzeAll}
                        disabled={isBulkAnalyzing || leads.length === 0}
                        className="flex items-center gap-2 px-5 py-2.5 bg-slate-50 border border-slate-200 text-slate-700 rounded-xl hover:bg-white hover:border-slate-300 transition shadow-sm text-sm font-bold disabled:opacity-50"
                    >
                        {isBulkAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Zap size={16} fill="currentColor" />}
                        Analyze All
                    </button>
                    <button 
                        onClick={handleEmailAll}
                        disabled={isBulkAnalyzing || leads.length === 0}
                        className="flex items-center gap-2 px-5 py-2.5 bg-emerald-50 border border-emerald-100 text-emerald-700 rounded-xl hover:bg-white hover:border-emerald-200 transition shadow-sm text-sm font-bold disabled:opacity-50"
                    >
                        {isBulkAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Mail size={16} />}
                        Email All
                    </button>
                    <button 
                        onClick={handleExport}
                        className="flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 hover:border-slate-300 transition shadow-sm text-sm font-bold"
                    >
                        <Download size={16} /> Export CSV
                    </button>
                  </>
              )}
            </div>
            </div>
          </div>
          
          <div className="">
            <table className="w-full table-fixed text-left border-collapse">
              <thead className="bg-slate-50/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
                <tr>
                  <th className="p-5 w-[60px] text-center">
                      <input 
                        type="checkbox" 
                        checked={leads.length > 0 && selectedLeads.length === leads.length}
                        onChange={toggleSelectAll}
                        className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer accent-blue-600"
                      />
                  </th>
                  <th className="p-5 w-[30%] font-extrabold text-xs uppercase tracking-wider text-slate-400">Company Profile</th>
                  <th className="p-5 w-[20%] font-extrabold text-xs uppercase tracking-wider text-slate-400">Performance</th>
                  <th className="p-5 w-[25%] font-extrabold text-xs uppercase tracking-wider text-slate-400">Insights</th>
                  <th className="p-5 w-[15%] font-extrabold text-xs uppercase tracking-wider text-slate-400">Contact</th>
                  <th className="p-5 w-[10%] font-extrabold text-xs uppercase tracking-wider text-slate-400 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {displayedLeads.map((lead) => (
                  <tr key={lead.id} className={`transition-colors duration-200 group ${selectedLeads.includes(lead.id) ? 'bg-blue-50/40' : 'hover:bg-slate-50/50'}`}>
                    {/* Checkbox */}
                    <td className="p-5 align-top text-center">
                        <input 
                            type="checkbox" 
                            checked={selectedLeads.includes(lead.id)}
                            onChange={() => toggleSelect(lead.id)}
                            className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer mt-1.5 accent-blue-600"
                        />
                    </td>

                    {/* Company Profile */}
                    <td className="p-5 align-top">
                      <div className="flex flex-col gap-2">
                        <div>
                            <div className="font-bold text-slate-900 text-[15px] leading-tight truncate flex items-center gap-2" title={lead.business_name}>
                                {lead.business_name}
                                {lead.domain && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>}
                            </div>
                            <div className="text-xs text-slate-500 flex items-center gap-1.5 mt-1 truncate font-medium">
                                <span className="opacity-70">{lead.city || 'Unknown Location'}</span>
                                {lead.phone && <span className="opacity-30">•</span>}
                                {lead.phone && <span>{lead.phone}</span>}
                            </div>
                        </div>
                        
                        <div className="flex items-center gap-3 mt-1">
                            {lead.domain ? (
                                <a 
                                    href={lead.domain.startsWith('http') ? lead.domain : `http://${lead.domain}`} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-[11px] font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 bg-blue-50/80 px-2.5 py-1 rounded-md transition-colors max-w-fit truncate border border-blue-100 hover:border-blue-200"
                                >
                                    <Globe size={12} />
                                    <span className="truncate max-w-[140px]">
                                        {new URL(lead.domain.startsWith('http') ? lead.domain : `http://${lead.domain}`).hostname.replace('www.', '')}
                                    </span>
                                </a>
                            ) : (
                                <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded-md border border-slate-200">No Website</span>
                            )}
                            
                            <div className="flex items-center gap-2 pl-2 border-l border-slate-100">
                                {lead.facebook && (
                                    <a href={lead.facebook} target="_blank" className="text-slate-300 hover:text-blue-600 transition hover:scale-110"><Facebook size={14} /></a>
                                )}
                                {lead.instagram && (
                                    <a href={lead.instagram} target="_blank" className="text-slate-300 hover:text-pink-600 transition hover:scale-110"><Instagram size={14} /></a>
                                )}
                                {lead.linkedin && (
                                    <a href={lead.linkedin} target="_blank" className="text-slate-300 hover:text-blue-700 transition hover:scale-110"><Linkedin size={14} /></a>
                                )}
                            </div>
                        </div>
                      </div>
                    </td>

                    {/* Performance */}
                    <td className="p-5 align-top">
                      <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-4">
                            <div className="relative w-12 h-12 flex items-center justify-center shrink-0">
                                <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 36 36">
                                    <path className="text-slate-100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                                    <path 
                                        className={`${lead.final_priority >= 75 ? 'text-emerald-500 drop-shadow-sm' : lead.final_priority >= 50 ? 'text-amber-500' : 'text-rose-500'} transition-all duration-1000`}
                                        strokeDasharray={`${lead.final_priority}, 100`}
                                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                                        fill="none" 
                                        stroke="currentColor" 
                                        strokeWidth="3" 
                                        strokeLinecap="round"
                                    />
                                </svg>
                                <span className={`absolute text-xs font-bold ${
                                    lead.final_priority >= 75 ? 'text-emerald-700' : lead.final_priority >= 50 ? 'text-amber-700' : 'text-rose-700'
                                }`}>{Math.round(lead.final_priority)}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className={`text-[10px] font-extrabold uppercase tracking-widest ${
                                    lead.final_priority >= 75 ? 'text-emerald-600' : lead.final_priority >= 50 ? 'text-amber-600' : 'text-rose-600'
                                }`}>
                                    {lead.final_priority >= 75 ? 'Excellent' : lead.final_priority >= 50 ? 'Potential' : 'Low Priority'}
                                </span>
                                <span className={`text-[10px] px-2 py-0.5 rounded-full border w-fit mt-1 font-bold ${
                                    lead.tier.includes('Tier-1') ? 'bg-amber-50 text-amber-700 border-amber-200' :
                                    lead.tier.includes('Tier-2') ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                    'bg-slate-50 text-slate-500 border-slate-200'
                                }`}>
                                    {lead.tier}
                                </span>
                            </div>
                        </div>
                      </div>
                    </td>

                    {/* Insights */}
                    <td className="p-5 align-top">
                      <div className="flex flex-col gap-2.5">
                        {lead.builder && (
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Tech</span>
                                <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold border ${
                                    lead.builder_type === 'AI' ? 'bg-purple-50 text-purple-700 border-purple-100' : 'bg-slate-50 text-slate-600 border-slate-200'
                                }`}>
                                    {lead.builder}
                                </span>
                            </div>
                        )}
                        
                        {lead.pain_points ? (
                            <div className="flex flex-wrap gap-1.5">
                                {lead.pain_points.split(' | ').slice(0, 2).map((point, i) => (
                                    <span key={i} className="text-[10px] px-2 py-1 bg-rose-50 text-rose-600 border border-rose-100 rounded-md font-medium whitespace-nowrap">
                                        {point}
                                    </span>
                                ))}
                                {lead.pain_points.split(' | ').length > 2 && (
                                    <span className="text-[10px] text-slate-400 px-1 py-0.5 font-bold" title={lead.pain_points}>
                                        +{lead.pain_points.split(' | ').length - 2} more
                                    </span>
                                )}
                            </div>
                        ) : (
                            <span className="text-xs text-slate-400 italic">No issues detected</span>
                        )}
                      </div>
                    </td>

                    {/* Contact */}
                    <td className="p-5 align-top">
                        {(() => {
                            const cleanedEmail = cleanEmail(lead.email);
                            return cleanedEmail ? (
                            <div className="flex flex-col">
                                <div className="text-sm font-bold text-slate-800 truncate" title={cleanedEmail}>
                                    {cleanedEmail}
                                </div>
                                <div className={`text-[10px] uppercase tracking-wide mt-1 font-bold flex items-center gap-1 ${
                                    lead.email_quality === 'Personal' || lead.email_quality === 'Named' ? 'text-emerald-600' : 'text-slate-400'
                                }`}>
                                    {lead.email_quality}
                                    {(lead.email_quality === 'Personal' || lead.email_quality === 'Named') && <div className="w-1 h-1 rounded-full bg-emerald-500"></div>}
                                </div>
                            </div>
                        ) : (
                            <span className="text-sm text-slate-300 italic font-medium">Not found</span>
                        );
                        })()}
                    </td>

                    {/* Actions */}
                    <td className="p-5 align-top text-right">
                        <LeadActions 
                          lead={lead}
                          isAnalyzing={analyzingIds.includes(lead.id)}
                          onEnrich={handleEnrich}
                          onAnalyze={handleAnalyze}
                          onEmail={setEmailLead}
                          onEdit={setEditLead}
                          onDelete={handleDelete}
                        />
                    </td>
                  </tr>
                ))}
                {leads.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-20 text-center">
                      <div className="flex flex-col items-center justify-center gap-4 text-slate-400">
                        <div className="p-6 bg-slate-50 rounded-full border border-slate-100">
                          <Search size={32} className="opacity-40" />
                        </div>
                        <div>
                            <p className="font-bold text-lg text-slate-600">No leads found yet</p>
                            <p className="text-sm mt-1">Start a scan to begin populating your database</p>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <EmailModal 
        isOpen={!!emailLead}
        onClose={() => {
          setEmailLead(null);
          fetchLeads(); // Refresh to show sent status
        }}
        lead={emailLead}
      />

      <EditLeadModal
        isOpen={!!editLead}
        onClose={() => setEditLead(null)}
        lead={editLead}
        onUpdate={fetchLeads}
      />

      <AddLeadModal
        isOpen={isAddLeadOpen}
        onClose={() => setIsAddLeadOpen(false)}
        onAdd={fetchLeads}
        currentProject={currentProject}
      />
    </main>
  );
}
