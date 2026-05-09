import React, { useState } from 'react';
import { X, FolderPlus, Building, Layers } from 'lucide-react';
import axios from 'axios';
import { useToast } from './Toast';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export default function CreateProjectModal({ isOpen, onClose, onCreated }: CreateProjectModalProps) {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [projectName, setProjectName] = useState('');
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api';

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      addToast("Please enter a project name", "error");
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_BASE}/projects`, { name: projectName.trim() });
      addToast('Project created successfully', 'success');
      setProjectName('');
      onCreated();
      onClose();
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Failed to create project';
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all scale-100">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 flex justify-between items-start text-white">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-md shadow-inner">
              <FolderPlus size={28} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight">New Project</h2>
              <p className="text-blue-100 text-sm mt-0.5 font-medium">Create a workspace for your leads</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-blue-100 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <Layers size={16} className="text-blue-600" /> Project Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                    type="text"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="e.g. Roofers Miami 2024"
                    className="w-full pl-4 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all font-medium text-gray-900 placeholder:text-gray-400"
                    autoFocus
                />
              </div>
              <p className="text-xs text-gray-500 mt-2 ml-1">
                Give your project a descriptive name to keep your leads organized.
              </p>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-gray-600 font-medium hover:bg-gray-100 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/30 disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Creating...
                </>
              ) : (
                <>
                  <FolderPlus size={18} />
                  Create Project
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
