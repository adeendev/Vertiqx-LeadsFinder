"use client";

import { useState, useEffect } from 'react';
import { Folder, Plus, ArrowRight, Database, Edit2, Trash2, X, Check } from 'lucide-react';
import axios from 'axios';

interface ProjectSelectorProps {
  onSelect: (projectName: string) => void;
}

export default function ProjectSelector({ onSelect }: ProjectSelectorProps) {
  const [projects, setProjects] = useState<string[]>([]);
  const [newProject, setNewProject] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingProject, setEditingProject] = useState<string | null>(null);
  const [editName, setEditName] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/projects');
      setProjects(res.data);
    } catch (error) {
      console.error("Failed to fetch projects", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (newProject.trim()) {
      try {
        await axios.post('http://localhost:8000/api/projects', { name: newProject.trim() });
        // Refresh list
        fetchProjects();
        setNewProject('');
      } catch (error) {
        console.error("Failed to create project", error);
      }
    }
  };

  const handleDelete = async (e: React.MouseEvent, name: string) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${name}"? All associated leads will be deleted permanently.`)) {
        try {
            await axios.delete(`http://localhost:8000/api/projects/${name}`);
            fetchProjects();
        } catch (error) {
            console.error("Failed to delete project", error);
        }
    }
  };

  const startEdit = (e: React.MouseEvent, name: string) => {
      e.stopPropagation();
      setEditingProject(name);
      setEditName(name);
  };

  const cancelEdit = (e: React.MouseEvent) => {
      e.stopPropagation();
      setEditingProject(null);
  };

  const saveEdit = async (e: React.MouseEvent) => {
      e.stopPropagation();
      if (editName.trim() && editName !== editingProject) {
          try {
              await axios.put(`http://localhost:8000/api/projects/${editingProject}`, { name: editName.trim() });
              setEditingProject(null);
              fetchProjects();
          } catch (error) {
              console.error("Failed to rename project", error);
              alert("Failed to rename project. Name might already exist.");
          }
      } else {
          setEditingProject(null);
      }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8 space-y-8">
        <div className="text-center space-y-2">
          <div className="bg-blue-50 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 text-blue-600">
            <Database size={32} />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome to Vertiqx</h1>
          <p className="text-gray-500">Select an existing project or create a new one to start gathering leads.</p>
        </div>

        <div className="space-y-4">
          {/* Existing Projects List */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Existing Projects</label>
            <div className="max-h-48 overflow-y-auto space-y-2 pr-2 scrollbar-thin">
              {loading ? (
                <div className="text-center py-4 text-gray-400 text-sm">Loading projects...</div>
              ) : projects.length === 0 ? (
                <div className="text-center py-4 text-gray-400 text-sm bg-gray-50 rounded-xl border border-dashed border-gray-200">
                  No projects found
                </div>
              ) : (
                projects.map((proj, i) => (
                  <div
                    key={i}
                    onClick={() => {
                        if (editingProject !== proj) onSelect(proj);
                    }}
                    className={`w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-xl transition group text-left ${editingProject !== proj ? 'hover:border-blue-500 hover:bg-blue-50 cursor-pointer' : ''}`}
                  >
                    {editingProject === proj ? (
                        <div className="flex items-center gap-2 w-full">
                            <input 
                                value={editName}
                                onChange={(e) => setEditName(e.target.value)}
                                className="flex-1 p-1 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                                autoFocus
                                onClick={(e) => e.stopPropagation()}
                            />
                            <button onClick={saveEdit} className="p-1 text-green-600 hover:bg-green-50 rounded"><Check size={16}/></button>
                            <button onClick={cancelEdit} className="p-1 text-gray-400 hover:bg-gray-100 rounded"><X size={16}/></button>
                        </div>
                    ) : (
                        <>
                            <div className="flex items-center gap-3">
                            <Folder size={18} className="text-gray-400 group-hover:text-blue-500" />
                            <span className="font-medium text-gray-700 group-hover:text-gray-900">{proj}</span>
                            </div>
                            
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button 
                                    onClick={(e) => startEdit(e, proj)}
                                    className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-100 rounded-lg transition"
                                    title="Rename"
                                >
                                    <Edit2 size={14} />
                                </button>
                                <button 
                                    onClick={(e) => handleDelete(e, proj)}
                                    className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded-lg transition"
                                    title="Delete"
                                >
                                    <Trash2 size={14} />
                                </button>
                                <ArrowRight size={16} className="text-gray-300 group-hover:text-blue-500 ml-1" />
                            </div>
                        </>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">or create new</span>
            </div>
          </div>

          {/* New Project Input */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">New Project Name</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newProject}
                onChange={(e) => setNewProject(e.target.value)}
                placeholder="e.g. Roofers Miami 2024"
                className="flex-1 p-3 bg-gray-50 border-transparent focus:bg-white focus:border-blue-500 focus:ring-0 rounded-xl transition-all outline-none font-medium"
                onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              />
              <button
                onClick={handleCreate}
                disabled={!newProject.trim()}
                className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg shadow-blue-600/20"
              >
                <Plus size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
