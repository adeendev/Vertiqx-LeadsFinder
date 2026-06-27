import React, { useState } from 'react';
import { X, Save, Building, Mail, Phone, Globe, MapPin, PlusCircle } from 'lucide-react';
import axios from 'axios';
import { useToast } from './Toast';

interface AddLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: () => void;
  currentProject: string | null;
}

export default function AddLeadModal({ isOpen, onClose, onAdd, currentProject }: AddLeadModalProps) {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_name: '',
    email: '',
    phone: '',
    domain: '',
    city: '',
    tier: 'New Lead'
  });

  if (!isOpen) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentProject) {
        addToast("Please select a project first", "error");
        return;
    }

    setLoading(true);

    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/leads`, {
          ...formData,
          project_name: currentProject
      });
      addToast('Lead added successfully', 'success');
      setFormData({
        business_name: '',
        email: '',
        phone: '',
        domain: '',
        city: '',
        tier: 'New Lead'
      });
      onAdd();
      onClose();
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Failed to add lead';
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-teal-600 p-6 flex justify-between items-center text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <PlusCircle size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold">Add New Lead</h2>
              <p className="text-green-100 text-sm">Manually add a business to {currentProject}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto flex-1">
          <form onSubmit={handleSubmit} className="space-y-5">
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <Building size={14} /> Business Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="business_name"
                value={formData.business_name}
                onChange={handleChange}
                className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g. Acme Plumbing"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <Globe size={14} /> Website / Domain
              </label>
              <input
                type="text"
                name="domain"
                value={formData.domain}
                onChange={handleChange}
                className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g. acmeplumbing.com"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                    <Mail size={14} /> Email
                </label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="info@acme.com"
                />
                </div>

                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                    <Phone size={14} /> Phone
                </label>
                <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="(555) 123-4567"
                />
                </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <MapPin size={14} /> City / Location
              </label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g. Chicago, IL"
              />
            </div>
            
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Initial Status</label>
                 <select
                    name="tier"
                    value={formData.tier}
                    onChange={handleChange}
                    className="w-full p-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                >
                    <option value="New Lead">New Lead</option>
                    <option value="No Website">No Website</option>
                    <option value="Tier-1">Tier-1</option>
                    <option value="Tier-1 Gold">Tier-1 Gold</option>
                    <option value="Tier-2">Tier-2</option>
                    <option value="Ignore">Ignore</option>
                </select>
            </div>

            {/* Footer Actions */}
            <div className="pt-4 border-t border-gray-100 flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2.5 text-gray-600 font-medium hover:bg-gray-50 rounded-xl transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2.5 bg-green-600 text-white font-medium rounded-xl hover:bg-green-700 transition shadow-lg shadow-green-600/20 flex items-center gap-2 disabled:opacity-70"
              >
                {loading ? 'Adding...' : (
                  <>
                    <PlusCircle size={18} />
                    Add Lead
                  </>
                )}
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}
