"use client";

import React, { useState, useEffect } from 'react';
import { Save, Settings as SettingsIcon, Server, Shield, User, Globe, Mail, ArrowLeft, LayoutTemplate } from 'lucide-react';
import axios from 'axios';
import { useToast } from '@/components/Toast';
import Navbar from '@/components/Navbar';
import Link from 'next/link';

export default function SettingsPage() {
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
    APIFY_API_TOKEN: '',
    TEMPLATE_NO_WEBSITE_SUBJECT: '',
    TEMPLATE_NO_WEBSITE_BODY: '',
    TEMPLATE_NOT_WORKING_SUBJECT: '',
    TEMPLATE_NOT_WORKING_BODY: '',
    TEMPLATE_WITH_ISSUES_SUBJECT: '',
    TEMPLATE_WITH_ISSUES_BODY: ''
  });

  const [provider, setProvider] = useState('hostinger');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/settings');
      setSettings(response.data);
      
      // Infer provider
      const host = response.data.SMTP_HOST;
      if (host === 'smtp.gmail.com') setProvider('gmail');
      else setProvider('hostinger'); // Default to hostinger
      
    } catch (error) {
      console.error("Failed to fetch settings", error);
      addToast('Failed to load settings', 'error');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setSettings(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleProviderChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProvider = e.target.value;
    setProvider(newProvider);
    
    setLoading(true);
    try {
        const res = await axios.post('http://localhost:8000/api/settings/load_provider', { provider: newProvider });
        // Update local state with the returned settings
        setSettings(prev => ({
            ...prev,
            ...res.data.settings
        }));
        addToast(`${newProvider} settings loaded from env`, 'success');
    } catch (error) {
        console.error("Failed to load provider settings", error);
        addToast('Failed to load provider settings', 'error');
    } finally {
        setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post('http://localhost:8000/api/settings', settings);
      addToast('Settings saved successfully', 'success');
    } catch (error) {
      console.error(error);
      addToast('Failed to save settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      {/* Simple Header for Settings Page */}
      <nav className="sticky top-0 z-40 w-full backdrop-blur-md bg-white/70 border-b border-gray-100 mb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition">
              <ArrowLeft size={20} />
              <span className="font-medium">Back to Dashboard</span>
            </Link>
            <div className="flex items-center gap-2">
              <SettingsIcon size={20} className="text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">System Configuration</h1>
            </div>
            <div className="w-20"></div> {/* Spacer for centering */}
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <form onSubmit={handleSubmit} className="space-y-8">
          
          {/* Email Templates Section */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                <LayoutTemplate size={20} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">Email Templates</h2>
                <p className="text-sm text-gray-500">Configure automated email content for different lead statuses</p>
              </div>
            </div>
            
            <div className="p-6 grid gap-8">
              {/* No Website Template */}
              <div className="space-y-4">
                <h3 className="font-bold text-gray-800 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-500"></span>
                  No Website Found
                </h3>
                <div className="grid gap-4 pl-4 border-l-2 border-gray-100 ml-1">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Subject Line</label>
                    <input
                      type="text"
                      name="TEMPLATE_NO_WEBSITE_SUBJECT"
                      value={settings.TEMPLATE_NO_WEBSITE_SUBJECT || ''}
                      onChange={handleChange}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="e.g. Question about {business_name}"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email Body</label>
                    <textarea
                      name="TEMPLATE_NO_WEBSITE_BODY"
                      value={settings.TEMPLATE_NO_WEBSITE_BODY || ''}
                      onChange={handleChange}
                      rows={4}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-sans text-sm"
                      placeholder="Use {business_name} as placeholder"
                    />
                  </div>
                </div>
              </div>

              {/* Working with Issues Template */}
              <div className="space-y-4">
                <h3 className="font-bold text-gray-800 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                  Website With Issues
                </h3>
                <div className="grid gap-4 pl-4 border-l-2 border-gray-100 ml-1">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Subject Line</label>
                    <input
                      type="text"
                      name="TEMPLATE_WITH_ISSUES_SUBJECT"
                      value={settings.TEMPLATE_WITH_ISSUES_SUBJECT || ''}
                      onChange={handleChange}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email Body</label>
                    <textarea
                      name="TEMPLATE_WITH_ISSUES_BODY"
                      value={settings.TEMPLATE_WITH_ISSUES_BODY || ''}
                      onChange={handleChange}
                      rows={4}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-sans text-sm"
                      placeholder="Use {business_name} and {diagnosis} as placeholders"
                    />
                    <p className="text-xs text-gray-500 mt-1">Available placeholders: <code>{`{business_name}`}</code>, <code>{`{diagnosis}`}</code></p>
                  </div>
                </div>
              </div>

              {/* Not Working Template */}
              <div className="space-y-4">
                <h3 className="font-bold text-gray-800 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                  Website Not Working / Down
                </h3>
                <div className="grid gap-4 pl-4 border-l-2 border-gray-100 ml-1">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Subject Line</label>
                    <input
                      type="text"
                      name="TEMPLATE_NOT_WORKING_SUBJECT"
                      value={settings.TEMPLATE_NOT_WORKING_SUBJECT || ''}
                      onChange={handleChange}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email Body</label>
                    <textarea
                      name="TEMPLATE_NOT_WORKING_BODY"
                      value={settings.TEMPLATE_NOT_WORKING_BODY || ''}
                      onChange={handleChange}
                      rows={4}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-sans text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* General Configuration */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* SMTP Configuration */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden h-fit">
              <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg text-purple-600">
                  <Mail size={20} />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">SMTP Settings</h2>
                  <p className="text-sm text-gray-500">Email server configuration</p>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Provider</label>
                  <select
                    value={provider}
                    onChange={handleProviderChange}
                    className="w-full p-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-medium"
                  >
                    <option value="hostinger">Hostinger (Vertiqx)</option>
                    <option value="gmail">Gmail</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-2">
                    Settings are loaded automatically from environment variables.
                  </p>
                </div>

                <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">Current Configuration</span>
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full font-bold">Active</span>
                    </div>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-gray-500">Host:</span>
                            <span className="font-medium text-gray-900">{settings.SMTP_HOST || 'Not set'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">Port:</span>
                            <span className="font-medium text-gray-900">{settings.SMTP_PORT || 'Not set'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">User:</span>
                            <span className="font-medium text-gray-900">{settings.SMTP_USER || 'Not set'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">From:</span>
                            <span className="font-medium text-gray-900">{settings.SMTP_FROM || 'Not set'}</span>
                        </div>
                    </div>
                </div>
              </div>
            </div>

            {/* Other Configs */}
            <div className="space-y-8">
              {/* Apify */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg text-green-600">
                    <Globe size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Apify Configuration</h2>
                    <p className="text-sm text-gray-500">Google Maps scraper API</p>
                  </div>
                </div>
                <div className="p-6">
                  <label className="block text-sm font-medium text-gray-700 mb-1">API Token</label>
                  <input
                    type="password"
                    name="APIFY_API_TOKEN"
                    value={settings.APIFY_API_TOKEN || ''}
                    onChange={handleChange}
                    className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Company Info */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-3">
                  <div className="p-2 bg-orange-100 rounded-lg text-orange-600">
                    <User size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Company Details</h2>
                    <p className="text-sm text-gray-500">Sender information</p>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                    <input
                      type="text"
                      name="COMPANY_NAME"
                      value={settings.COMPANY_NAME || ''}
                      onChange={handleChange}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Website URL</label>
                    <input
                      type="text"
                      name="COMPANY_WEBSITE"
                      value={settings.COMPANY_WEBSITE || ''}
                      onChange={handleChange}
                      className="w-full p-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-8 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 disabled:opacity-70"
            >
              <Save size={20} />
              {loading ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>

        </form>
      </main>
    </div>
  );
}
