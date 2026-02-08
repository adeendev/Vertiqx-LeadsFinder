"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Folder, Plus, ArrowRight, Database, Edit2, Trash2, X, Check, Search, Calendar } from 'lucide-react';
import axios from 'axios';
import Navbar from '@/components/Navbar';
import { useToast } from '@/components/Toast';

export default function ProjectsPage() {
  const router = useRouter();
  const { addToast } = useToast();
  const [projects, setProjects] = useState<string[]>([]);
  const [newProject, setNewProject] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingProject, setEditingProject] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/projects');
      setProjects(res.data);
    } catch (error) {
      console.error("Failed to fetch projects", error);
      addToast('Failed to load projects', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newProject.trim()) {
      try {
        await axios.post('http://localhost:8000/api/projects', { name: newProject.trim() });
        fetchProjects();
        setNewProject('');
        addToast('Project created successfully!', 'success');
      } catch (error: any) {
        console.error("Failed to create project", error);
        addToast(error.response?.data?.detail || 'Failed to create project', 'error');
      }
    }
  };

  const handleDelete = async (e: React.MouseEvent, name: string) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${name}"? All associated leads will be deleted permanently.`)) {
        try {
            await axios.delete(`http://localhost:8000/api/projects/${name}`);
            fetchProjects();
            addToast('Project deleted', 'success');
            
            // If current project is deleted, clear local storage
            if (localStorage.getItem('currentProject') === name) {
                localStorage.removeItem('currentProject');
            }
        } catch (error) {
            console.error("Failed to delete project", error);
            addToast('Failed to delete project', 'error');
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
              
              // Update local storage if needed
              if (localStorage.getItem('currentProject') === editingProject) {
                  localStorage.setItem('currentProject', editName.trim());
              }

              setEditingProject(null);
              fetchProjects();
              addToast('Project renamed successfully', 'success');
          } catch (error) {
              console.error("Failed to rename project", error);
              addToast('Failed to rename project', 'error');
          }
      } else {
          setEditingProject(null);
      }
  };

  const handleSelectProject = (name: string) => {
      localStorage.setItem('currentProject', name);
      router.push('/');
  };

  const filteredProjects = projects.filter(p => p.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
                <p className="text-gray-500 mt-1">Manage your lead generation campaigns</p>
            </div>
            
            <form onSubmit={handleCreate} className="flex gap-3 w-full md:w-auto">
                <input
                    type="text"
                    value={newProject}
                    onChange={(e) => setNewProject(e.target.value)}
                    placeholder="New Project Name..."
                    className="flex-1 md:w-64 p-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                />
                <button 
                    type="submit"
                    disabled={!newProject.trim()}
                    className="px-4 py-2.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
                >
                    <Plus size={18} /> Create
                </button>
            </form>
        </div>

        {/* Search */}
        <div className="relative mb-8">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input 
                type="text" 
                placeholder="Search projects..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
            />
        </div>

        {/* Grid */}
        {loading ? (
            <div className="flex justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        ) : filteredProjects.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-gray-200">
                <div className="bg-gray-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
                    <Folder size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900">No projects found</h3>
                <p className="text-gray-500 mt-1">Create a new project to get started</p>
            </div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredProjects.map((proj, i) => (
                    <div 
                        key={i}
                        onClick={() => handleSelectProject(proj)}
                        className="group bg-white p-6 rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-xl hover:shadow-blue-500/5 transition-all cursor-pointer relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                             <button 
                                onClick={(e) => startEdit(e, proj)}
                                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                                title="Rename"
                            >
                                <Edit2 size={16} />
                            </button>
                            <button 
                                onClick={(e) => handleDelete(e, proj)}
                                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                                title="Delete"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>

                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                <Folder size={24} />
                            </div>
                        </div>

                        {editingProject === proj ? (
                             <div className="flex items-center gap-2 mb-2" onClick={e => e.stopPropagation()}>
                                <input 
                                    value={editName}
                                    onChange={(e) => setEditName(e.target.value)}
                                    className="flex-1 p-1 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-bold text-lg"
                                    autoFocus
                                />
                                <button onClick={saveEdit} className="p-1 text-green-600 hover:bg-green-50 rounded"><Check size={18}/></button>
                                <button onClick={cancelEdit} className="p-1 text-gray-400 hover:bg-gray-100 rounded"><X size={18}/></button>
                            </div>
                        ) : (
                            <h3 className="text-lg font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">{proj}</h3>
                        )}
                        
                        <p className="text-sm text-gray-500 flex items-center gap-2">
                            <Calendar size={14} /> Active Campaign
                        </p>

                        <div className="mt-6 flex items-center text-sm font-medium text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0">
                            Open Dashboard <ArrowRight size={16} className="ml-1" />
                        </div>
                    </div>
                ))}
            </div>
        )}
      </div>
    </div>
  );
}
