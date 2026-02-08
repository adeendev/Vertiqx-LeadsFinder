import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { MoreHorizontal, Globe, Zap, Mail, Pencil, Trash2, RefreshCw } from 'lucide-react';

interface LeadActionsProps {
  lead: any;
  isAnalyzing: boolean;
  onEnrich: (id: number) => void;
  onAnalyze: (id: number) => void;
  onEmail: (lead: any) => void;
  onEdit: (lead: any) => void;
  onDelete: (id: number) => void;
}

export default function LeadActions({ 
  lead, 
  isAnalyzing, 
  onEnrich, 
  onAnalyze, 
  onEmail, 
  onEdit, 
  onDelete 
}: LeadActionsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [dropDirection, setDropDirection] = useState<'down' | 'up'>('down');
  const [coords, setCoords] = useState({ top: 0, bottom: 0, right: 0 });
  const [mounted, setMounted] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    setMounted(true);
    
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node) && !buttonRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    
    // Close on scroll to prevent detached menu
    function handleScroll() {
        if (isOpen) setIsOpen(false);
    }

    document.addEventListener("mousedown", handleClickOutside);
    window.addEventListener("scroll", handleScroll, true);
    
    return () => {
        document.removeEventListener("mousedown", handleClickOutside);
        window.removeEventListener("scroll", handleScroll, true);
    };
  }, [isOpen]);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isOpen && buttonRef.current) {
        const rect = buttonRef.current.getBoundingClientRect();
        const spaceBelow = window.innerHeight - rect.bottom;
        
        // Calculate precise position
        const newCoords = {
            top: rect.bottom + 8,
            bottom: window.innerHeight - rect.top + 8,
            right: window.innerWidth - rect.right
        };
        
        // If less than 350px space below, open upwards
        if (spaceBelow < 350) {
            setDropDirection('up');
        } else {
            setDropDirection('down');
        }
        setCoords(newCoords);
    }
    setIsOpen(!isOpen);
  };

  return (
    <>
      <button 
        ref={buttonRef}
        onClick={handleToggle}
        className={`p-2 rounded-xl transition-all duration-200 ${isOpen ? 'bg-slate-100 text-slate-900 shadow-inner' : 'text-slate-400 hover:text-slate-900 hover:bg-slate-100'}`}
      >
        <MoreHorizontal size={20} />
      </button>

      {isOpen && mounted && createPortal(
        <div 
            ref={menuRef}
            style={{
                position: 'fixed',
                right: coords.right,
                top: dropDirection === 'down' ? coords.top : undefined,
                bottom: dropDirection === 'up' ? coords.bottom : undefined,
                zIndex: 9999
            }}
            className={`w-64 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl shadow-slate-200/50 border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200 ring-1 ring-slate-200 ${
                dropDirection === 'up' 
                ? 'origin-bottom-right' 
                : 'origin-top-right'
            }`}
            onClick={(e) => e.stopPropagation()}
        >
          <div className="p-2">
            <div className="px-3 py-2 text-[10px] font-extrabold text-slate-400 uppercase tracking-widest border-b border-slate-50 mb-1">
                Actions
            </div>

            <button
              onClick={() => { onEnrich(lead.id); setIsOpen(false); }}
              disabled={isAnalyzing}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-semibold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-xl transition-colors disabled:opacity-50 text-left group"
            >
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-100 transition-colors shadow-sm">
                 {isAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Globe size={16} />}
              </div>
              <div className="flex flex-col">
                <span>Enrich Data</span>
                <span className="text-[10px] font-medium text-slate-400 group-hover:text-indigo-400/80">Find email & website</span>
              </div>
            </button>

            <button
              onClick={() => { onAnalyze(lead.id); setIsOpen(false); }}
              disabled={isAnalyzing}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 rounded-xl transition-colors disabled:opacity-50 text-left group"
            >
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg group-hover:bg-blue-100 transition-colors shadow-sm">
                {isAnalyzing ? <RefreshCw size={16} className="animate-spin" /> : <Zap size={16} />}
              </div>
              <div className="flex flex-col">
                <span>Analyze Site</span>
                <span className="text-[10px] font-medium text-slate-400 group-hover:text-blue-400/80">Scan for opportunities</span>
              </div>
            </button>

            <button
              onClick={() => { onEmail(lead); setIsOpen(false); }}
              disabled={!lead.email}
              className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-xl transition-colors text-left group ${
                lead.email 
                  ? 'text-slate-700 hover:bg-emerald-50 hover:text-emerald-700' 
                  : 'text-slate-300 cursor-not-allowed'
              }`}
            >
              <div className={`p-2 rounded-lg transition-colors shadow-sm ${lead.email ? 'bg-emerald-50 text-emerald-600 group-hover:bg-emerald-100' : 'bg-slate-50 text-slate-300'}`}>
                <Mail size={16} />
              </div>
              <div className="flex flex-col">
                <span>Send Email</span>
                <span className={`text-[10px] font-medium ${lead.email ? 'text-slate-400 group-hover:text-emerald-400/80' : 'text-slate-300'}`}>
                    {lead.email ? 'Outreach via SMTP' : 'No email found'}
                </span>
              </div>
            </button>
            
            <div className="h-px bg-slate-100 my-1 mx-2"></div>

            <button
              onClick={() => { onEdit(lead); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-semibold text-slate-700 hover:bg-amber-50 hover:text-amber-700 rounded-xl transition-colors text-left group"
            >
              <div className="p-2 bg-amber-50 text-amber-600 rounded-lg group-hover:bg-amber-100 transition-colors shadow-sm">
                <Pencil size={16} />
              </div>
              Edit Details
            </button>

            <button
              onClick={() => { onDelete(lead.id); setIsOpen(false); }}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-semibold text-rose-600 hover:bg-rose-50 hover:text-rose-700 rounded-xl transition-colors text-left group"
            >
              <div className="p-2 bg-rose-50 text-rose-600 rounded-lg group-hover:bg-rose-100 transition-colors shadow-sm">
                <Trash2 size={16} />
              </div>
              Delete Lead
            </button>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
