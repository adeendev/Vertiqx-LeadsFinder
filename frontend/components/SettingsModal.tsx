import React, { useState, useEffect } from 'react';
import { X, Save, Settings, Server, Shield, User, Globe } from 'lucide-react';
import axios from 'axios';
import { useToast } from './Toast';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    SMTP_HOST: '',
    SMTP_PORT: '465',
    SMTP_USER: '',
    SMTP_PASS: '',
    SMTP_FROM: '',
    COMPANY_NAME: '',
    COMPANY_WEBSITE: '',
    COMPANY_LOGO: '',
    TEMPLATE_TYPE: 'html',
    APIFY_API_TOKEN: ''
  });

  const [provider, setProvider] = useState('custom');

  // Fetch settings when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchSettings();
    }
  }, [isOpen]);

  const fetchSettings = async () => {
    try {
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/settings`);
      if (res.data) {
        setSettings(prev => ({ ...prev, ...res.data }));
        if (res.data.SMTP_HOST?.includes('hostinger')) setProvider('hostinger');
        else if (res.data.SMTP_HOST?.includes('gmail')) setProvider('gmail');
        else setProvider('custom');
      }
    } catch (error) {
      console.error("Failed to fetch settings", error);
    }
  };

  const handleProviderChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProvider = e.target.value;
    setProvider(newProvider);
    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/settings/load_provider`, { provider: newProvider });
      setSettings(prev => ({ ...prev, ...res.data.settings }));
    } catch (error) {
      console.error("Failed to load provider settings", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/settings`, settings);
      addToast('Settings saved successfully!', 'success');
      onClose();
    } catch (error) {
      console.error("Failed to save settings", error);
      addToast('Failed to save settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setSettings(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-6 flex justify-between items-center text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <Settings size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold">Email Configuration</h2>
              <p className="text-gray-300 text-sm">Configure SMTP and Company details</p>
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
            
            {/* Provider & Template Selection */}
            <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-xl border border-gray-100">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Email Provider</label>
                <select
                  value={provider}
                  onChange={handleProviderChange}
                  className="w-full p-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-medium"
                >
                  <option value="custom">Custom SMTP</option>
                  <option value="hostinger">Hostinger</option>
                  <option value="gmail">Gmail</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Email Template</label>
                <select
                  name="TEMPLATE_TYPE"
                  value={settings.TEMPLATE_TYPE}
                  onChange={handleChange}
                  className="w-full p-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-medium"
                >
                  <option value="html">Professional HTML</option>
                  <option value="simple">Simple Text</option>
                </select>
              </div>
            </div>

            {/* Apify Configuration */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider border-b pb-2 flex items-center gap-2">
                <Globe size={16} /> Apify Configuration
              </h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Apify API Token</label>
                <input
                  type="password"
                  name="APIFY_API_TOKEN"
                  value={settings.APIFY_API_TOKEN || ''}
                  onChange={handleChange}
                  placeholder="Enter your Apify API Token"
                  className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
                <p className="text-xs text-gray-500 mt-1">Required for automated Google Places search.</p>
              </div>
            </div>

            {/* SMTP Settings - Hidden as per request */}
            {/* 
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider border-b pb-2 flex items-center gap-2">
                <Server size={16} /> SMTP Server
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">SMTP Host</label>
                  <input
                    type="text"
                    name="SMTP_HOST"
                    value={settings.SMTP_HOST}
                    onChange={handleChange}
                    placeholder="smtp.gmail.com"
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Port</label>
                  <input
                    type="number"
                    name="SMTP_PORT"
                    value={settings.SMTP_PORT}
                    onChange={handleChange}
                    placeholder="465"
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider border-b pb-2 flex items-center gap-2">
                <Shield size={16} /> Authentication
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email / User</label>
                  <input
                    type="email"
                    name="SMTP_USER"
                    value={settings.SMTP_USER}
                    onChange={handleChange}
                    placeholder="user@example.com"
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password (App Password)</label>
                  <input
                    type="password"
                    name="SMTP_PASS"
                    value={settings.SMTP_PASS}
                    onChange={handleChange}
                    placeholder="••••••••••••"
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider border-b pb-2 flex items-center gap-2">
                <User size={16} /> Sender Information
              </h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">From Email (Optional)</label>
                <input
                  type="email"
                  name="SMTP_FROM"
                  value={settings.SMTP_FROM}
                  onChange={handleChange}
                  placeholder="Defaults to SMTP User if empty"
                  className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>
            */}

            {/* Company Branding - Hidden as per request */}
            {/*
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider border-b pb-2 flex items-center gap-2">
                <Globe size={16} /> Branding
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                  <input
                    type="text"
                    name="COMPANY_NAME"
                    value={settings.COMPANY_NAME}
                    onChange={handleChange}
                    placeholder="My Company Inc."
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Website URL</label>
                  <input
                    type="url"
                    name="COMPANY_WEBSITE"
                    value={settings.COMPANY_WEBSITE}
                    onChange={handleChange}
                    placeholder="https://example.com"
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Logo URL</label>
                  <input
                    type="url"
                    name="COMPANY_LOGO"
                    value={settings.COMPANY_LOGO}
                    onChange={handleChange}
                    placeholder="https://example.com/logo.png"
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>
            </div>
            */}

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
                className="px-6 py-2.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    Save Settings
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
