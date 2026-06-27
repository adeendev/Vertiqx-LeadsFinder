import React, { useState, useEffect } from 'react';
import { X, Save, Building, Mail, Phone, Globe, AlertCircle, FileText, MapPin, Tag } from 'lucide-react';
import axios from 'axios';
import { useToast } from './Toast';

interface EditLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  lead: any;
  onUpdate: () => void;
}

export default function EditLeadModal({ isOpen, onClose, lead, onUpdate }: EditLeadModalProps) {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_name: '',
    email: '',
    phone: '',
    domain: '',
    pain_points: '',
    notes: '',
    city: '',
    tier: '',
    email_quality: ''
  });

  useEffect(() => {
    if (lead) {
      setFormData({
        business_name: lead.business_name || '',
        email: lead.email || '',
        phone: lead.phone || '',
        domain: lead.domain || '',
        pain_points: lead.pain_points || '',
        notes: lead.notes || '',
        city: lead.city || '',
        tier: lead.tier || '',
        email_quality: lead.email_quality || ''
      });
    }
  }, [lead]);

  if (!isOpen || !lead) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.put(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/leads/${lead.id}`, formData);
      addToast('Lead updated successfully', 'success');
      onUpdate();
      onClose();
    } catch (error) {
      console.error(error);
      addToast('Failed to update lead', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-6 flex justify-between items-center text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <Building size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold">Edit Lead Details</h2>
              <p className="text-gray-300 text-sm">Update information for {lead.business_name}</p>
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
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                    <Building size={14} /> Business Name
                </label>
                <input
                  type="text"
                  name="business_name"
                  value={formData.business_name}
                  onChange={handleChange}
                  className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />
              </div>

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
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                    <Tag size={14} /> Email Quality
                </label>
                <select
                    name="email_quality"
                    value={formData.email_quality}
                    onChange={handleChange}
                    className="w-full p-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                >
                    <option value="">Unknown</option>
                    <option value="Generic">Generic (info@, etc.)</option>
                    <option value="Personal">Personal (gmail, etc.)</option>
                    <option value="Named">Named (john@company.com)</option>
                    <option value="Verified">Verified</option>
                </select>
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
                />
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
                />
              </div>

               <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                    <Tag size={14} /> Tier / Status
                </label>
                 <select
                    name="tier"
                    value={formData.tier}
                    onChange={handleChange}
                    className="w-full p-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                >
                    <option value="New Lead">New Lead</option>
                    <option value="Processing...">Processing...</option>
                    <option value="No Website">No Website</option>
                    <option value="Tier-1">Tier-1</option>
                    <option value="Tier-1 Gold">Tier-1 Gold</option>
                    <option value="Tier-2">Tier-2</option>
                    <option value="Ignore">Ignore</option>
                </select>
              </div>
            </div>

            {/* Detailed Info */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <AlertCircle size={14} /> Pain Points / Diagnosis
              </label>
              <textarea
                name="pain_points"
                value={formData.pain_points}
                onChange={handleChange}
                rows={3}
                className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-sans text-sm"
                placeholder="e.g. Slow load time | No SSL | Broken Links"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <FileText size={14} /> Internal Notes
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={3}
                className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-sans text-sm"
                placeholder="Internal notes about this lead..."
              />
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
                className="px-6 py-2.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 flex items-center gap-2 disabled:opacity-70"
              >
                {loading ? 'Saving...' : (
                  <>
                    <Save size={18} />
                    Save Changes
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
